"""Independent Blender import/material/UV/render witness for a static morph.

Blender --background --factory-startup --python THIS -- ORIGINAL MORPHED RECEIPT NEW_OUT.
The original native Python creator does not execute inside this receiver.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def facts(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
    meshes = sorted((obj for obj in bpy.data.objects if obj.type == 'MESH'), key=lambda obj: obj.name)
    if not meshes:raise RuntimeError('independent static morph import contains no mesh')
    bound = [obj.matrix_world @ vertex.co for obj in meshes for vertex in obj.data.vertices]
    objects = []
    for obj in meshes:
        uv = []
        for layer in obj.data.uv_layers:
            raw = b''.join(struct.pack('<2f', *loop.uv) for loop in layer.data)
            uv.append({'name': layer.name, 'sha256': hashlib.sha256(raw).hexdigest(), 'loops': len(layer.data)})
        objects.append({'name': obj.name, 'vertices': len(obj.data.vertices),
                        'triangles': sum(len(face.vertices)-2 for face in obj.data.polygons),
                        'materials': [slot.material.name if slot.material else None for slot in obj.material_slots],
                        'uv_layers': uv})
    images = []
    for image in bpy.data.images:
        if image.name in ('Render Result', 'Viewer Node'):continue
        if len(image.pixels) > 4_000_000:raise RuntimeError('receiver texture pixel budget exceeded')
        raw = b''.join(struct.pack('<f', value) for value in image.pixels)
        images.append({'size': list(image.size), 'channels': image.channels,
                       'linear_pixels_sha256': hashlib.sha256(raw).hexdigest()})
    images.sort(key=lambda item: item['linear_pixels_sha256'])
    return {'objects': objects, 'images': images,
            'bounds': {'min': [min(p[i] for p in bound) for i in range(3)],
                       'max': [max(p[i] for p in bound) for i in range(3)]}}, bound


def main():
    arguments = sys.argv[sys.argv.index('--')+1:]
    if len(arguments) != 4:raise ValueError('ORIGINAL MORPHED RECEIPT NEW_OUT required')
    original, morphed, receipt_file, out = (Path(value).resolve() for value in arguments)
    if out.exists():raise FileExistsError('preserve prior independent morph witness')
    native = json.loads(receipt_file.read_text(encoding='utf8'))
    if sha(original) != native['source_sha256'] or sha(morphed) != native['artifact_sha256']:
        raise RuntimeError('source/derived model changed from original native receipt')
    before, p = facts(original)
    after, q = facts(morphed)
    if before['objects'] != after['objects'] or before['images'] != after['images']:
        raise RuntimeError('independent import changed original parts, topology, UVs, materials or texture pixels')
    if before['bounds'] == after['bounds']:raise RuntimeError('static morph witness did not change geometry bounds')
    # Independent glTF Y-up -> Blender Z-up coordinate witness.
    low, high = native['world_bounds_after']['min'], native['world_bounds_after']['max']
    expected = {'min': [low[0], -high[2], low[1]], 'max': [high[0], -low[2], high[1]]}
    for side in ('min', 'max'):
        if any(abs(a-b) > max(1e-5, abs(b)*1e-6) for a, b in zip(after['bounds'][side], expected[side])):
            raise RuntimeError('independent imported bounds differ from native world-space morph')
    points = p + q
    low = Vector([min(value[i] for value in points) for i in range(3)])
    high = Vector([max(value[i] for value in points) for i in range(3)])
    center, extent = (low+high)/2, max(high-low)
    out.mkdir(parents=True)
    images = []
    for label, source in (('before', original), ('after', morphed)):
        found, _ = facts(source)
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = 12
        scene.render.resolution_x = 700
        scene.render.resolution_y = 500
        scene.render.resolution_percentage = 100
        scene.world = bpy.data.worlds.new('MGR_Static_Morph_World')
        scene.world.use_nodes = True
        scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.12, .15, .21, 1)
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
        camera_data = bpy.data.cameras.new('MGR_Original_Morph_Witness')
        camera = bpy.data.objects.new(camera_data.name, camera_data)
        scene.collection.objects.link(camera)
        camera.location = center+Vector((extent*.65, -extent*1.4, extent*.8))
        camera.rotation_euler = (center-camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = extent*1.35
        scene.camera = camera
        for name, delta, power in (('Key', (.4, -.6, .9), 1700), ('Fill', (-.5, .3, .5), 1000)):
            light = bpy.data.lights.new('MGR_Morph_'+name, 'AREA')
            light.energy = power
            light.shape = 'DISK'
            light.size = extent*.65
            obj = bpy.data.objects.new(light.name, light)
            scene.collection.objects.link(obj)
            obj.location = center+Vector(delta)*extent
            obj.rotation_euler = (center-obj.location).to_track_quat('-Z', 'Y').to_euler()
        image, blend = out/(label+'.png'), out/(label+'.blend')
        scene.render.filepath = str(image)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.render.render(write_still=True)
        if not image.is_file() or image.stat().st_size < 1000:raise RuntimeError('actual CPU render absent')
        images.append({'name': label, 'png_sha256': sha(image), 'blend_sha256': sha(blend), 'import': found})
    if images[0]['png_sha256'] == images[1]['png_sha256']:raise RuntimeError('render did not change')
    report = {'schema': 'mgr.forge.imported-morph-blender-witness.v1',
              'status': 'INDEPENDENT_BLENDER_STATIC_MORPH_IMPORT_RENDER_PASS',
              'blender_version': bpy.app.version_string, 'renderer': 'CYCLES_CPU',
              'source_sha256': native['source_sha256'], 'artifact_sha256': native['artifact_sha256'],
              'same_source_parts_topology_uv_materials_and_image_pixels': True,
              'imported_world_bounds_match_native_receipt': True,
              'same_camera_and_lights': True, 'renders': images,
              'owner_art_accepted': False, 'rig_deformation_verified': False,
              'limits': ['original static geometry only, not skinned/animated/shape-target input',
                         'measured GLB/import/material preservation, not semantic likeness or arbitrary topology editing']}
    (out/'blender-proof.json').write_text(json.dumps(report, sort_keys=True, indent=2)+'\n', encoding='utf8')
    print('MGR_IMPORTED_MORPH_BLENDER_PROOF='+json.dumps(report))


if __name__ == '__main__':main()
