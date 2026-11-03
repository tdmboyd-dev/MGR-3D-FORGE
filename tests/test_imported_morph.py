"""Imported static assets must morph without losing parts, images, UVs or source."""
import base64
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zlib

from forge.geometry import Mesh
from forge.glb import export_glb
from forge.character_glb import parse_character_glb
from forge.imported_morph import (morph_glb_bytes, morph_imported_glb, validate_imported_glb,
                                static_glb_world_positions)
from forge.morph_engine import morph_point


def unpack(blob):
    size = struct.unpack_from('<I', blob, 12)[0]
    return json.loads(blob[20:20+size]), blob[28+size:]


def pack(doc, binary):
    data = json.dumps(doc, separators=(',', ':')).encode()
    data += b' ' * (-len(data) % 4)
    binary += b'\0' * (-len(binary) % 4)
    return (struct.pack('<4sII', b'glTF', 2, 28+len(data)+len(binary)) +
            struct.pack('<I4s', len(data), b'JSON') + data + struct.pack('<I4s', len(binary), b'BIN\0') + binary)


def values(doc, binary, index):
    acc = doc['accessors'][index]
    view = doc['bufferViews'][acc['bufferView']]
    width = {'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[acc['type']]
    offset = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    return [struct.unpack_from('<'+'f'*width, binary, offset+i*view.get('byteStride', width*4))
            for i in range(acc['count'])]


def fixture():
    meshes = [Mesh(), Mesh()]
    for mesh in meshes:mesh.box(0, 0, 0, 1, 2, 1)
    blob = export_glb(meshes, materials=[('outer shell', [.6, .2, .1, 1]), ('owned accessory', [.1, .3, .6, 1])])
    doc, binary = unpack(blob)
    primitives = doc['meshes'][0]['primitives']
    doc['meshes'] = [{'name': 'outer shell', 'primitives': [primitives[0]]},
                     {'name': 'owned accessory', 'primitives': [primitives[1]]}]
    doc['nodes'] = [{'name': 'original root', 'translation': [10, 0, 0], 'children': [1, 2]},
                    {'name': 'shell part', 'mesh': 0, 'translation': [-3, 0, 0]},
                    {'name': 'accessory part', 'mesh': 1, 'translation': [3, 0, 0]}]
    # An original embedded 2x2 PNG and authored UV attributes, not a network asset.
    def chunk(kind, content):
        return struct.pack('>I', len(content))+kind+content+struct.pack('>I', zlib.crc32(kind+content))
    image = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 2, 8, 2, 0, 0, 0)) +
             chunk(b'IDAT', zlib.compress(bytes([0, 230, 50, 20, 20, 180, 70, 0, 20, 50, 230, 245, 220, 40]))) + chunk(b'IEND', b''))
    for primitive in primitives:
        count = doc['accessors'][primitive['attributes']['POSITION']]['count']
        raw = b''.join(struct.pack('<2f', i % 2, (i//2) % 2) for i in range(count))
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(raw), 'target': 34962})
        binary += raw
        doc['accessors'].append({'bufferView': len(doc['bufferViews'])-1, 'componentType': 5126, 'count': count, 'type': 'VEC2'})
        primitive['attributes']['TEXCOORD_0'] = len(doc['accessors'])-1
    doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(image)})
    binary += image
    binary += b'\0' * (-len(binary) % 4)
    doc['images'] = [{'name': 'original color patch', 'mimeType': 'image/png', 'bufferView': len(doc['bufferViews'])-1}]
    doc['samplers'] = [{'magFilter': 9729, 'minFilter': 9729, 'wrapS': 10497, 'wrapT': 10497}]
    doc['textures'] = [{'source': 0, 'sampler': 0}]
    doc['materials'][0]['pbrMetallicRoughness']['baseColorTexture'] = {'index': 0}
    doc['extras'] = {'original_project_id': 'owned-fixture-0001'}
    doc['buffers'][0]['byteLength'] = len(binary)
    return pack(doc, binary)


class ImportedMorphTests(unittest.TestCase):
    def test_read_only_world_positions_share_affine_matrix_and_static_refusals(self):
        original = fixture()
        doc, binary = unpack(original)
        # Column-major affine shear + translation; hierarchy root is retained.
        doc['nodes'][1].pop('translation')
        doc['nodes'][1]['matrix'] = [1, 0, 0, 0, .5, 1, 0, 0, 0, 0, 1, 0, -3, 0, 0, 1]
        source = pack(doc, binary)
        points = static_glb_world_positions(source)
        self.assertEqual(len(points), 48)
        self.assertEqual(min(p[0] for p in points), 6.5)
        self.assertEqual(max(p[0] for p in points), 13.5)
        self.assertIn((8.5, 2., -.5), points)  # 10 - 3 + .5 + .5*2
        self.assertEqual(source, pack(doc, binary))
        doc['animations'] = [{'channels': []}]
        with self.assertRaisesRegex(ValueError, 'skins, animations'):
            static_glb_world_positions(pack(doc, binary))

    def test_real_asset_preserves_original_texture_uv_indices_parts_and_scene(self):
        original = fixture()
        before, source_bin = unpack(original)
        derived, receipt = morph_glb_bytes(original, {'height': 1.25, 'width': .8, 'bend_degrees': 14, 'twist_degrees': 17})
        after, output_bin = unpack(derived)
        self.assertEqual(output_bin[:len(source_bin)], source_bin)
        for field in ('materials', 'images', 'textures', 'samplers', 'nodes', 'scenes', 'scene', 'extras'):
            self.assertEqual(after[field], before[field])
        self.assertEqual(parse_character_glb(original)[1], parse_character_glb(derived)[1])
        self.assertEqual(receipt['source_sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(receipt['artifact_sha256'], hashlib.sha256(derived).hexdigest())
        self.assertTrue(receipt['preservation']['original_bin_prefix_unchanged'])
        self.assertFalse(receipt['independently_blender_verified'])
        for first, last in zip(before['meshes'], after['meshes']):
            self.assertEqual(first['name'], last['name'])
            p, q = first['primitives'][0], last['primitives'][0]
            self.assertEqual(p['indices'], q['indices'])
            self.assertEqual(p['attributes']['TEXCOORD_0'], q['attributes']['TEXCOORD_0'])
            self.assertEqual(p['material'], q['material'])
            self.assertNotEqual(p['attributes']['POSITION'], q['attributes']['POSITION'])

    def test_all_parts_follow_one_world_field_without_rewriting_node_transforms(self):
        original = fixture()
        derived, receipt = morph_glb_bytes(original, {'length': 2, 'height': 1.5})
        after, binary = unpack(derived)
        self.assertEqual(receipt['pivot_world'], [10., 0., 0.])
        self.assertEqual(receipt['world_bounds_before'], {'min': [6.5, 0., -.5], 'max': [13.5, 2., .5]})
        self.assertEqual(receipt['world_bounds_after'], {'min': [3., 0., -.5], 'max': [17., 3., .5]})
        expected = ((-4., -2.), (2., 4.))
        for mesh, (low, high) in zip(after['meshes'], expected):
            points = values(after, binary, mesh['primitives'][0]['attributes']['POSITION'])
            self.assertEqual(min(p[0] for p in points), low)
            self.assertEqual(max(p[0] for p in points), high)
            self.assertEqual(max(p[1] for p in points), 3)

    def test_source_hash_gate_new_revision_and_collision_do_not_overwrite(self):
        original = fixture()
        sha = hashlib.sha256(original).hexdigest()
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination = root/'owned.glb', root/'revision'
            source.write_bytes(original)
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                morph_imported_glb(source, destination, {'length': 1.4}, expected_sha256='0'*64)
            self.assertFalse(destination.exists())
            receipt = morph_imported_glb(source, destination, {'length': 1.4}, expected_sha256=sha)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual((destination/'original.glb').read_bytes(), original)
            saved = (destination/'morphed.glb').read_bytes()
            self.assertEqual(hashlib.sha256(saved).hexdigest(), receipt['artifact']['sha256'])
            with self.assertRaises(FileExistsError):morph_imported_glb(source, destination, {'length': .8})
            self.assertEqual((destination/'morphed.glb').read_bytes(), saved)

    def test_validation_and_creation_use_same_deterministic_byte_contract(self):
        original, settings = fixture(), {'height': .8, 'bend_degrees': -15, 'taper': 1.3}
        expected, receipt = morph_glb_bytes(original, settings)
        self.assertEqual(validate_imported_glb(original, settings), receipt)
        self.assertEqual(morph_glb_bytes(original, settings)[0], expected)

    def test_skinned_animated_targeted_compressed_or_external_assets_refuse_without_outputs(self):
        original, binary = unpack(fixture())
        mutations = [lambda d: d.update(skins=[{'joints': [0]}]),
                     lambda d: d.update(animations=[{'channels': []}]),
                     lambda d: d['meshes'][0]['primitives'][0].update(targets=[]),
                     lambda d: d.update(extensionsUsed=['KHR_draco_mesh_compression']),
                     lambda d: d['bufferViews'][0].update(extensions={'EXT_meshopt_compression': {}}),
                     lambda d: d['nodes'][1].update(skin=0),
                     lambda d: d['images'][0].update(uri='https://example.invalid/private.png'),
                     lambda d: d['buffers'][0].update(uri='file:///private.bin')]
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            for i, mutate in enumerate(mutations):
                doc = copy.deepcopy(original)
                mutate(doc)
                source, output = root/f'input-{i}.glb', root/f'output-{i}'
                source.write_bytes(pack(doc, binary))
                with self.subTest(i=i), self.assertRaises(ValueError):morph_imported_glb(source, output, {'height': 1.2})
                self.assertFalse(output.exists())

    def test_bad_hierarchy_instances_and_transform_values_refuse(self):
        original, binary = unpack(fixture())
        mutations = [lambda d: d['nodes'][1].update(children=[0]),
                     lambda d: d['nodes'][0].update(children=[1, 1, 2]),
                     lambda d: d['nodes'][1].update(scale=[1, 0, 1]),
                     lambda d: d['nodes'][1].update(rotation=[0, 0, 0, 2]),
                     lambda d: d['nodes'][2].update(mesh=0),
                     lambda d: d['scenes'].append({'nodes': [0]}),
                     lambda d: d['scenes'][0].update(nodes=[[]]),
                     lambda d: d['nodes'][1].update(matrix=[1]*16)]
        for i, mutate in enumerate(mutations):
            doc = copy.deepcopy(original)
            mutate(doc)
            with self.subTest(i=i), self.assertRaises(ValueError):validate_imported_glb(pack(doc, binary))

    def test_budget_bad_morph_and_malformed_optional_attributes_are_validation_errors(self):
        original = fixture()
        for settings in ({'length': 20}, {'width': True}, {'bend_degrees': float('nan')}, {'unknown': 1}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):validate_imported_glb(original, settings)
        with patch('forge.imported_morph.MAX_VERTICES', 3), self.assertRaisesRegex(ValueError, 'budget'):
            validate_imported_glb(original)
        source, binary = unpack(original)
        for mutation in (lambda d: d['images'][0].update(uri=42),
                         lambda d: d['meshes'][0]['primitives'][0]['attributes'].update(NORMAL=-1),
                         lambda d: d['meshes'][0]['primitives'][0]['attributes'].update(JOINTS_0=0),
                         lambda d: d['meshes'][0]['primitives'][0]['attributes'].update(TEXCOORD_bad=0)):
            doc = copy.deepcopy(source)
            mutation(doc)
            with self.assertRaises(ValueError):validate_imported_glb(pack(doc, binary))

    def test_transformed_normals_match_scaled_triangle_winding_and_remain_unit(self):
        source, binary = unpack(fixture())
        # Ninety-degree Y rotation and nonuniform node scale, preserved as source transforms.
        source['nodes'][1]['rotation'] = [0, math.sqrt(.5), 0, math.sqrt(.5)]
        source['nodes'][1]['scale'] = [1.2, .8, .6]
        derived, _ = morph_glb_bytes(pack(source, binary), {'length': 1.7, 'width': .7, 'height': 1.3})
        doc, data = unpack(derived)
        for mesh in doc['meshes']:
            p = mesh['primitives'][0]
            points = values(doc, data, p['attributes']['POSITION'])
            normals = values(doc, data, p['attributes']['NORMAL'])
            index = doc['accessors'][p['indices']]
            view = doc['bufferViews'][index['bufferView']]
            indices = struct.unpack_from('<'+'I'*index['count'], data, view['byteOffset'])
            for j in range(0, len(indices), 3):
                a, b, c = (points[k] for k in indices[j:j+3])
                u, v = [b[k]-a[k] for k in range(3)], [c[k]-a[k] for k in range(3)]
                face = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
                mag = math.sqrt(sum(k*k for k in face))
                n = normals[indices[j]]
                self.assertAlmostEqual(sum(n[k]*face[k]/mag for k in range(3)), 1, places=5)
            for n in normals:self.assertAlmostEqual(math.sqrt(sum(v*v for v in n)), 1, places=6)

    def test_nonlinear_normals_and_tangents_match_independent_surface_differentials(self):
        mesh = Mesh(positions=[-.3, .2, 0, .7, .8, 0, -.2, 1.2, 0],
                    normals=[0, 0, 1]*3, indices=[0, 1, 2])
        doc, binary = unpack(export_glb([mesh], materials=[('owned plane', [.5, .3, .1, 1])]))
        tangent = struct.pack('<12f', *([1, 0, 0, 1]*3))
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(tangent), 'target': 34962})
        binary += tangent
        doc['buffers'][0]['byteLength'] = len(binary)
        doc['accessors'].append({'bufferView': len(doc['bufferViews'])-1, 'componentType': 5126, 'type': 'VEC4', 'count': 3})
        doc['meshes'][0]['primitives'][0]['attributes']['TANGENT'] = len(doc['accessors'])-1
        settings = {'length': 1.4, 'width': .7, 'height': 1.2, 'twist_degrees': 33, 'bend_degrees': 20, 'taper': 1.3}
        output, receipt = morph_glb_bytes(pack(doc, binary), settings)
        after, data = unpack(output)
        attrs = after['meshes'][0]['primitives'][0]['attributes']
        normal = values(after, data, attrs['NORMAL'])[1]
        received_tangent = values(after, data, attrs['TANGENT'])[1]
        pivot, extent = receipt['pivot_world'], receipt['axis_extent']
        point = values(doc, binary, doc['meshes'][0]['primitives'][0]['attributes']['POSITION'])[1]
        def transform(p):
            value = morph_point((p[0]-pivot[0], p[1], p[2]-pivot[2]), settings, pivot_y=pivot[1], axis_extent=extent)
            return value[0]+pivot[0], value[1], value[2]+pivot[2]
        derivatives = []
        for axis in (0, 1):
            a, b = list(point), list(point)
            a[axis] -= 1e-5
            b[axis] += 1e-5
            aa, bb = transform(a), transform(b)
            vector = [bb[i]-aa[i] for i in range(3)]
            length = math.sqrt(sum(v*v for v in vector))
            vector = [v/length for v in vector]
            self.assertAlmostEqual(sum(normal[i]*vector[i] for i in range(3)), 0, places=6)
            derivatives.append(vector)
        self.assertAlmostEqual(sum(received_tangent[i]*derivatives[0][i] for i in range(3)), 1, places=6)
        self.assertEqual(received_tangent[3], 1)

    def test_interleaved_geometry_retains_original_uv_stride_bytes(self):
        mesh = Mesh(positions=[0, 0, 0, 1, 0, 0, 0, 1, 0], normals=[0, 0, 1]*3, indices=[0, 1, 2])
        doc, binary = unpack(export_glb([mesh], materials=[('owned triangle', [.2, .6, .8, 1])]))
        attrs = doc['meshes'][0]['primitives'][0]['attributes']
        positions = values(doc, binary, attrs['POSITION'])
        normal = values(doc, binary, attrs['NORMAL'])
        uv = [(0., 0.), (1., 0.), (0., 1.)]
        raw = b''.join(struct.pack('<8f', *p, *n, *t) for p, n, t in zip(positions, normal, uv))
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(raw), 'byteStride': 32})
        binary += raw
        vi = len(doc['bufferViews'])-1
        doc['accessors'][attrs['POSITION']].update(bufferView=vi, byteOffset=0)
        doc['accessors'][attrs['NORMAL']].update(bufferView=vi, byteOffset=12)
        doc['accessors'].append({'bufferView': vi, 'byteOffset': 24, 'componentType': 5126, 'type': 'VEC2', 'count': 3})
        attrs['TEXCOORD_0'] = len(doc['accessors'])-1
        doc['buffers'][0]['byteLength'] = len(binary)
        original = pack(doc, binary)
        output, _ = morph_glb_bytes(original, {'length': 1.5, 'height': 1.3, 'taper': .8})
        after, data = unpack(output)
        self.assertEqual(data[:len(binary)], binary)
        self.assertEqual(values(after, data, attrs['TEXCOORD_0']), uv)
        self.assertEqual(after['bufferViews'][vi], doc['bufferViews'][vi])


if __name__ == '__main__':unittest.main()
