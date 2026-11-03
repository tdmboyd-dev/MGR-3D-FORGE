"""Non-destructive CPU morph revisions of bounded static, self-contained GLBs.

Reuses the original Forge deformation field. Original BIN bytes remain an exact
prefix; new position/normal/tangent data is appended. Materials, image bytes,
UVs, indices, part names and scene transforms are preserved. Skins, animations,
existing morph targets and unsupported geometry semantics refuse explicitly.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import struct

from .character_glb import parse_character_glb
from .morph_engine import morph_point, normalize_morph

MAX_BYTES = 80_000_000
MAX_VERTICES = 250_000
MAX_TRIANGLES = 500_000
MAX_NODES = 10_000
_MATERIAL_EXTENSIONS = {
    'KHR_materials_unlit', 'KHR_materials_clearcoat', 'KHR_materials_ior',
    'KHR_materials_specular', 'KHR_materials_transmission', 'KHR_materials_volume',
    'KHR_materials_sheen', 'KHR_materials_emissive_strength',
    'KHR_materials_iridescence', 'KHR_materials_anisotropy',
    'KHR_texture_transform', 'KHR_texture_basisu', 'EXT_texture_webp',
}
_IDENTITY = (1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1.)


def _finite(values, count):
    return (isinstance(values, (list, tuple)) and len(values) == count and
            all(type(v) in (int, float) and math.isfinite(v) for v in values))


def _multiply(a, b):
    return tuple(sum(a[r * 4 + k] * b[k * 4 + c] for k in range(4))
                 for r in range(4) for c in range(4))


def _inverse3(a):
    aa, b, c, d, e, f, g, h, i = a
    det = aa * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    scale = max(abs(v) for v in a)
    if not math.isfinite(det) or not scale or abs(det) <= 1e-12 * scale ** 3:
        raise ValueError('static morph refuses singular or ill-conditioned transforms')
    return tuple(v / det for v in (e*i-f*h, c*h-b*i, b*f-c*e,
                 f*g-d*i, aa*i-c*g, c*d-aa*f, d*h-e*g, b*g-aa*h, aa*e-b*d))


def _linear(matrix):
    return tuple(matrix[r * 4 + c] for r in range(3) for c in range(3))


def _vector(matrix, value):
    return tuple(sum(matrix[r * 3 + k] * value[k] for k in range(3)) for r in range(3))


def _transpose_vector(matrix, value):
    return tuple(sum(matrix[k * 3 + c] * value[k] for k in range(3)) for c in range(3))


def _point(matrix, value):
    return tuple(sum(matrix[r * 4 + k] * value[k] for k in range(3)) + matrix[r * 4 + 3] for r in range(3))


def _unit(value):
    length = math.sqrt(sum(v * v for v in value))
    if not math.isfinite(length) or length < 1e-12:
        raise ValueError('static morph refuses zero/nonfinite normal or tangent')
    return tuple(v / length for v in value)


def _node_matrix(node):
    if not isinstance(node, dict) or node.get('extensions') or 'skin' in node or 'weights' in node:
        raise ValueError('static morph refuses skinned, weighted or extended nodes')
    if 'matrix' in node:
        if any(key in node for key in ('translation', 'rotation', 'scale')) or not _finite(node['matrix'], 16):
            raise ValueError('node matrix must be finite and separate from TRS')
        # glTF serializes matrices in column-major order; math here is row-major.
        result = tuple(node['matrix'][c * 4 + r] for r in range(4) for c in range(4))
        if any(abs(result[12 + i] - v) > 1e-10 for i, v in enumerate((0, 0, 0, 1))):
            raise ValueError('static morph requires affine node transforms')
    else:
        t, q, s = node.get('translation', [0, 0, 0]), node.get('rotation', [0, 0, 0, 1]), node.get('scale', [1, 1, 1])
        if not _finite(t, 3) or not _finite(q, 4) or not _finite(s, 3) or abs(sum(v*v for v in q) - 1) > 1e-5:
            raise ValueError('invalid static node translation, scale or unit quaternion')
        x, y, z, w = q
        r = (1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w),
             2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w),
             2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y))
        result = tuple(r[row*3+col] * s[col] if col < 3 else t[row]
                       for row in range(3) for col in range(4)) + (0., 0., 0., 1.)
    _inverse3(_linear(result))
    return result


def _mesh_transforms(doc):
    nodes, scenes = doc.get('nodes'), doc.get('scenes')
    if (not isinstance(nodes, list) or not 1 <= len(nodes) <= MAX_NODES or
            not isinstance(scenes, list) or len(scenes) != 1 or doc.get('scene', 0) != 0 or
            not isinstance(scenes[0], dict) or not isinstance(scenes[0].get('nodes'), list)):
        raise ValueError('static morph requires one bounded explicit scene')
    roots = scenes[0]['nodes']
    if not roots or len(set(roots)) != len(roots):
        raise ValueError('static scene root identities invalid')
    found, seen = {}, set()
    stack = [(index, _IDENTITY, 0) for index in roots]
    while stack:
        index, parent, depth = stack.pop()
        if type(index) is not int or not 0 <= index < len(nodes) or index in seen or depth > 256:
            raise ValueError('static morph refuses cycles, shared nodes or invalid/deep hierarchy')
        seen.add(index)
        node = nodes[index]
        matrix = _multiply(parent, _node_matrix(node))
        if 'mesh' in node:
            mesh = node['mesh']
            if type(mesh) is not int or not 0 <= mesh < len(doc['meshes']):
                raise ValueError('invalid static mesh reference')
            if mesh in found and any(abs(a-b) > 1e-10 for a, b in zip(found[mesh], matrix)):
                raise ValueError('static morph refuses differently transformed instances of one mesh')
            found[mesh] = matrix
        children = node.get('children', [])
        if not isinstance(children, list):
            raise ValueError('static node children must be an array')
        stack.extend((child, matrix, depth + 1) for child in children)
    # Do not silently leave hidden meshes or geometry in other scenes unchanged.
    if len(found) != len(doc['meshes']) or any('mesh' in node and i not in seen for i, node in enumerate(nodes)):
        raise ValueError('all static meshes must belong to the selected scene')
    return found


def _accessor(doc, binary, index, *, kind='VEC3', component=5126):
    if type(index) is not int or not 0 <= index < len(doc['accessors']):
        raise ValueError('static morph attribute reference invalid')
    acc = doc['accessors'][index]
    if acc.get('type') != kind or acc.get('componentType') != component or acc.get('normalized', False):
        raise ValueError('static morph needs explicit unnormalized float geometry attributes')
    view = doc['bufferViews'][acc['bufferView']]
    if view.get('buffer', 0) != 0:
        raise ValueError('static morph requires local single-buffer attributes')
    width = 4 * (4 if kind == 'VEC4' else 3)
    stride = view.get('byteStride', width)
    offset = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    if offset % 4 or stride % 4:
        raise ValueError('static float attributes must be aligned')
    values = [struct.unpack_from('<' + ('4f' if kind == 'VEC4' else '3f'), binary, offset + i*stride)
              for i in range(acc['count'])]
    if not all(math.isfinite(v) for row in values for v in row):
        raise ValueError('static source geometry contains nonfinite values')
    return values


def _indices(doc, binary, primitive, count):
    if 'indices' not in primitive:
        return range(count)
    acc = doc['accessors'][primitive['indices']]
    view = doc['bufferViews'][acc['bufferView']]
    if view.get('buffer', 0) != 0:
        raise ValueError('static indices must use the embedded buffer')
    size, code = {5121: (1, 'B'), 5123: (2, 'H'), 5125: (4, 'I')}[acc['componentType']]
    start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    return [struct.unpack_from('<' + code, binary, start + i*view.get('byteStride', size))[0]
            for i in range(acc['count'])]


def _triangles(points, indices):
    for offset in range(0, len(indices), 3):
        a, b, c = (points[i] for i in indices[offset:offset+3])
        u, v = tuple(b[i]-a[i] for i in range(3)), tuple(c[i]-a[i] for i in range(3))
        cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        if sum(n*n for n in cross) <= 1e-24 * max(sum(n*n for n in u)*sum(n*n for n in v), 1e-60):
            raise ValueError('static morph refuses collapsed source or output triangles')


def _jacobian(point, recipe, pivot, extent):
    x, y, z = point[0]-pivot[0], point[1]-pivot[1], point[2]-pivot[2]
    phase = max(0., min(1., y/extent))
    dp = 1/extent if 0 <= y <= extent else 0.
    taper = 1 + (recipe['taper']-1)*phase
    dt = (recipe['taper']-1)*dp
    angle = math.radians(recipe['twist_degrees'])*y/extent
    da = math.radians(recipe['twist_degrees'])/extent
    cs, sn = math.cos(angle), math.sin(angle)
    length, width, height = recipe['length'], recipe['width'], recipe['height']
    u, v = length*x*taper, width*z*taper
    bend = 2*extent*height*math.tan(math.radians(recipe['bend_degrees']))*phase*dp
    return (length*taper*cs, length*x*dt*cs-width*z*dt*sn-(u*sn+v*cs)*da+bend, -width*taper*sn,
            0., height, 0.,
            length*taper*sn, length*x*dt*sn+width*z*dt*cs+(u*cs-v*sn)*da, width*taper*cs)


def _morph_glb_bytes(blob, morph=None, *, expected_sha256=None):
    """Validate and return derived GLB bytes plus a source-bound receipt; no IO."""
    if type(blob) is not bytes or not 28 <= len(blob) <= MAX_BYTES:
        raise ValueError('static morph requires bounded original GLB bytes')
    source_sha = hashlib.sha256(blob).hexdigest()
    if expected_sha256 is not None and (type(expected_sha256) is not str or source_sha != expected_sha256):
        raise ValueError('static morph original SHA-256 changed; preserve and reconcile source')
    recipe = normalize_morph(morph)
    doc, source_geometry = parse_character_glb(blob)
    if (doc.get('skins') or doc.get('animations') or 'uri' in doc['buffers'][0] or
            any(name not in _MATERIAL_EXTENSIONS for name in doc.get('extensionsUsed', []) + doc.get('extensionsRequired', []))):
        raise ValueError('static morph refuses skins, animations, external buffers or unsupported extensions')
    if (source_geometry['vertices'] > MAX_VERTICES or source_geometry['triangles'] > MAX_TRIANGLES or
            source_geometry['primitives'] > 2048):
        raise ValueError('static morph vertex budget exceeded')
    json_size = struct.unpack_from('<I', blob, 12)[0]
    binary = blob[28 + json_size:]
    # Character parser bounds all views against bytes; also enforce the declared buffer.
    if doc.get('extensions') or any(acc.get('extensions') for acc in doc['accessors']):
        raise ValueError('static morph refuses extended root/accessor geometry semantics')
    for view in doc['bufferViews']:
        if view.get('extensions'):
            raise ValueError('static morph refuses compressed/extended buffer views')
        if view.get('buffer', 0) != 0 or view.get('byteOffset', 0) + view['byteLength'] > doc['buffers'][0]['byteLength']:
            raise ValueError('static view escapes the original declared buffer')
    for image in doc.get('images', []):
        if not isinstance(image, dict) or ('uri' in image and not image['uri'].startswith('data:')):
            raise ValueError('static morph requires embedded image data, never external URLs/files')
        if 'bufferView' in image and (type(image['bufferView']) is not int or not 0 <= image['bufferView'] < len(doc['bufferViews'])):
            raise ValueError('embedded image view invalid')
    transforms = _mesh_transforms(doc)
    groups, world_points = [], []
    for mi, mesh in enumerate(doc['meshes']):
        if mesh.get('weights') or mesh.get('extensions') or not isinstance(mesh.get('primitives'), list):
            raise ValueError('static morph refuses weighted or malformed meshes')
        matrix = transforms[mi]
        for pi, primitive in enumerate(mesh['primitives']):
            if 'targets' in primitive or primitive.get('extensions'):
                raise ValueError('existing shape targets/primitive extensions require a dedicated morph-aware path')
            attrs = primitive['attributes']
            if 'NORMAL' not in attrs or any(not (name in ('POSITION', 'NORMAL', 'TANGENT') or
                    re.fullmatch(r'(?:TEXCOORD|COLOR)_[0-9]+', name)) for name in attrs):
                raise ValueError('static morph requires normals and refuses joints/weights/custom attributes')
            position_index = attrs['POSITION']
            count = doc['accessors'][position_index]['count']
            if count < 1 or count > MAX_VERTICES:
                raise ValueError('static position attribute count outside budget')
            for name, index in attrs.items():
                if type(index) is not int or not 0 <= index < len(doc['accessors']) or doc['accessors'][index]['count'] != count:
                    raise ValueError('static attribute counts/references differ')
            positions = _accessor(doc, binary, position_index)
            normals = _accessor(doc, binary, attrs['NORMAL'])
            tangents = _accessor(doc, binary, attrs['TANGENT'], kind='VEC4') if 'TANGENT' in attrs else None
            if tangents and any(abs(abs(t[3])-1) > 1e-6 for t in tangents):
                raise ValueError('static tangent handedness invalid')
            indices = _indices(doc, binary, primitive, len(positions))
            _triangles(positions, indices)
            world = [_point(matrix, p) for p in positions]
            world_points.extend(world)
            groups.append((mi, pi, primitive, matrix, positions, normals, tangents, indices, world))
    if not world_points:
        raise ValueError('static source contains no editable vertices')
    low = [min(p[i] for p in world_points) for i in range(3)]
    high = [max(p[i] for p in world_points) for i in range(3)]
    pivot = [(low[0]+high[0])/2, low[1], (low[2]+high[2])/2]
    extent = max(high[1]-low[1], max(high[i]-low[i] for i in range(3))*.01, 1e-6)
    target = copy.deepcopy(doc)
    result_binary = bytearray(binary)
    final_world = []

    def append_attribute(original, values, kind, *, position=False):
        width = 4 if kind == 'VEC4' else 3
        raw = b''.join(struct.pack('<' + 'f'*width, *value) for value in values)
        offset = len(result_binary)
        result_binary.extend(raw)
        target['bufferViews'].append({'buffer': 0, 'byteOffset': offset, 'byteLength': len(raw), 'target': 34962})
        acc = copy.deepcopy(doc['accessors'][original])
        acc.update({'bufferView': len(target['bufferViews'])-1, 'byteOffset': 0})
        if 'min' in acc or 'max' in acc or position:
            acc['min'] = [min(row[i] for row in values) for i in range(width)]
            acc['max'] = [max(row[i] for row in values) for i in range(width)]
        target['accessors'].append(acc)
        return len(target['accessors'])-1

    for mi, pi, primitive, matrix, positions, normals, tangents, indices, world in groups:
        linear, inverse = _linear(matrix), _inverse3(_linear(matrix))
        moved, moved_normals, moved_tangents = [], [], []
        for index, point in enumerate(world):
            local = morph_point((point[0]-pivot[0], point[1], point[2]-pivot[2]), recipe,
                                pivot_y=pivot[1], axis_extent=extent)
            new_world = (local[0]+pivot[0], local[1], local[2]+pivot[2])
            translated = tuple(new_world[i]-matrix[i*4+3] for i in range(3))
            local_point = _vector(inverse, translated)
            try:
                local_point = struct.unpack('<3f', struct.pack('<3f', *local_point))
            except (OverflowError, struct.error) as error:
                raise ValueError('static morph exceeds finite float32 range') from error
            if not all(math.isfinite(v) for v in local_point):
                raise ValueError('static morph exceeds finite float32 range')
            moved.append(local_point)
            final_world.append(_point(matrix, local_point))
            jacobian = _jacobian(point, recipe, pivot, extent)
            world_normal = _transpose_vector(inverse, _unit(normals[index]))
            new_world_normal = _transpose_vector(_inverse3(jacobian), world_normal)
            moved_normals.append(_unit(_transpose_vector(linear, new_world_normal)))
            if tangents is not None:
                direction = _vector(inverse, _vector(jacobian, _vector(linear, tangents[index][:3])))
                moved_tangents.append((*_unit(direction), tangents[index][3]))
        _triangles(moved, indices)
        new_attrs = target['meshes'][mi]['primitives'][pi]['attributes']
        new_attrs['POSITION'] = append_attribute(primitive['attributes']['POSITION'], moved, 'VEC3', position=True)
        new_attrs['NORMAL'] = append_attribute(primitive['attributes']['NORMAL'], moved_normals, 'VEC3')
        if tangents is not None:
            new_attrs['TANGENT'] = append_attribute(primitive['attributes']['TANGENT'], moved_tangents, 'VEC4')
    target['buffers'][0]['byteLength'] = len(result_binary)
    encoded = json.dumps(target, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf8')
    encoded += b' ' * (-len(encoded) % 4)
    result_binary.extend(b'\0' * (-len(result_binary) % 4))
    size = 28 + len(encoded) + len(result_binary)
    if size > MAX_BYTES:
        raise ValueError('derived static GLB exceeds byte budget')
    output = (struct.pack('<4sII', b'glTF', 2, size) + struct.pack('<I4s', len(encoded), b'JSON') + encoded +
              struct.pack('<I4s', len(result_binary), b'BIN\0') + bytes(result_binary))
    _, geometry = parse_character_glb(output)
    if geometry != source_geometry:
        raise ValueError('static morph changed original geometry counts')
    receipt = {'schema': 'mgr.forge.imported-morph.v1', 'status': 'NATIVE_STATIC_GLB_MORPH',
               'source_sha256': source_sha, 'source_bytes': len(blob),
               'artifact_sha256': hashlib.sha256(output).hexdigest(), 'artifact_bytes': len(output),
               'artifact': {'file': 'morphed.glb', 'sha256': hashlib.sha256(output).hexdigest(), 'bytes': len(output)},
               'morph': recipe, 'pivot_world': pivot, 'axis_extent': extent, 'geometry': geometry,
               'world_bounds_before': {'min': low, 'max': high},
               'world_bounds_after': {'min': [min(p[i] for p in final_world) for i in range(3)],
                                      'max': [max(p[i] for p in final_world) for i in range(3)]},
               'preservation': {'original_bin_prefix_unchanged': bytes(result_binary[:len(binary)]) == binary,
                                'original_bin_sha256': hashlib.sha256(binary).hexdigest(),
                                'indices_uvs_images_materials_preserved': True,
                                'node_hierarchy_transforms_names_preserved': target.get('nodes') == doc.get('nodes'),
                                'normal_and_tangent_fields_transformed': True, 'source_overwritten': False},
               'neural_model_used': False, 'provider_spend_usd': 0,
               'independently_blender_verified': False, 'owner_art_accepted': False,
               'limitations': ['static self-contained uncompressed GLB only; skins/animations/shape targets refuse',
                               'one scene; differently transformed instances and unsupported geometry extensions refuse',
                               'global authored six-control deformation, not semantic face/body fitting or learned reconstruction',
                               'topology/UV/image bytes retained; severe deformation can stretch authored textures',
                               'structural and triangle preservation is not target-engine or artistic acceptance']}
    return output, receipt


def morph_glb_bytes(blob, morph=None, *, expected_sha256=None):
    """Public byte contract: malformed structures refuse as validation errors."""
    try:
        return _morph_glb_bytes(blob, morph, expected_sha256=expected_sha256)
    except (KeyError, IndexError, TypeError, AttributeError, OverflowError, struct.error) as error:
        raise ValueError('malformed or unsupported static GLB morph input') from error


def validate_imported_glb(blob, morph=None, *, expected_sha256=None):
    """Run the identical pure byte/geometry path before allocating a native job."""
    return morph_glb_bytes(blob, morph, expected_sha256=expected_sha256)[1]


def static_glb_world_positions(blob):
    """Read original world-space vertices under the same bounded static contract.

    This is an observation of source geometry, never a revision or acceptance of
    authored collider metadata. Identity validation shares every unsupported-input
    refusal with the morph writer; hierarchy/accessor decoding is not duplicated.
    """
    validate_imported_glb(blob)
    doc, _ = parse_character_glb(blob)
    json_size = struct.unpack_from('<I', blob, 12)[0]
    binary = blob[28 + json_size:]
    transforms = _mesh_transforms(doc)
    return tuple(_point(transforms[mi], point)
                 for mi, mesh in enumerate(doc['meshes'])
                 for primitive in mesh['primitives']
                 for point in _accessor(doc, binary, primitive['attributes']['POSITION']))


def morph_imported_glb(source, output, morph=None, *, expected_sha256=None):
    """Write a NEW source-preserving revision; never alter an existing asset."""
    path, destination = Path(source), Path(output)
    if not path.is_file() or path.is_symlink() or path.suffix.lower() != '.glb':
        raise ValueError('ordinary source GLB required for a static morph revision')
    if destination.exists():
        raise FileExistsError('preserve prior morph revisions; choose a new output directory')
    if not 28 <= path.stat().st_size <= MAX_BYTES:
        raise ValueError('source GLB outside static morph byte budget')
    original = path.read_bytes()
    derived, receipt = morph_glb_bytes(original, morph, expected_sha256=expected_sha256)
    destination.mkdir(parents=True, exist_ok=False)
    (destination/'original.glb').write_bytes(original)
    (destination/'morphed.glb').write_bytes(derived)
    (destination/'morph-receipt.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n', encoding='utf8')
    return receipt
