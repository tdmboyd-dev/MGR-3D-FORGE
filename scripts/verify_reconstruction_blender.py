"""Independent Blender import, bounds, volume, edge and render witness.

Blender --background --factory-startup --python THIS -- HULL_DIRECTORY NEW_OUTPUT
Only owner-authored PNG fixture reconstructions are used in the saved evidence.
This verifies usable mesh transport, not learned reconstruction or likeness.
"""
import hashlib
import json
from pathlib import Path
import sys
import bmesh
import bpy
from mathutils import Vector


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=2:
        raise ValueError('HULL_DIRECTORY NEW_OUTPUT required')
    source,out=map(Path,args)
    if out.exists():
        raise FileExistsError('new proof destination required')
    manifest=json.loads((source/'reconstruction.json').read_text(encoding='utf-8'))
    glb=source/'hull.glb'
    if digest(glb)!=manifest['glb']['sha256']:
        raise ValueError('original reconstruction receipt mismatch')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb.resolve()))
    meshes=[obj for obj in bpy.data.objects if obj.type=='MESH']
    if len(meshes)!=1:
        raise RuntimeError('expected one editable hull mesh')
    obj=meshes[0]
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    boundary=sum(edge.is_boundary for edge in bm.edges)
    nonmanifold=sum(not edge.is_manifold for edge in bm.edges)
    volume=bm.calc_volume(signed=True)
    bm.free()
    points=[obj.matrix_world@vertex.co for vertex in obj.data.vertices]
    native=[(point.x,point.z,-point.y) for point in points]
    low=[min(point[axis] for point in native) for axis in range(3)]
    high=[max(point[axis] for point in native) for axis in range(3)]
    max_error=max(abs(observed-expected) for actual,recorded in
                  ((low,manifest['mesh_bbox_min_m']),(high,manifest['mesh_bbox_max_m']))
                  for observed,expected in zip(actual,recorded))
    triangles=sum(len(poly.vertices)-2 for poly in obj.data.polygons)
    if boundary or nonmanifold or volume<=0 or triangles!=manifest['triangles'] or max_error>1e-5:
        raise RuntimeError('independent geometry witness failed')
    world_low=Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    world_high=Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    center=(world_low+world_high)/2
    extent=max(world_high-world_low)
    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('MGR_Reconstruction_Witness_World')
    scene.world.color=(.04,.05,.07)
    camera=bpy.data.objects.new('MGR_Orthographic_Witness',bpy.data.cameras.new('MGR_Camera'))
    scene.collection.objects.link(camera)
    camera.location=center+Vector((extent*.8,-extent*1.5,extent*.7))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'
    camera.data.ortho_scale=extent*1.9
    scene.camera=camera
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_cavity=True
    scene.display.shading.show_shadows=True
    scene.display.shading.background_type='WORLD'
    scene.render.resolution_x=900
    scene.render.resolution_y=650
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    out.mkdir(parents=True)
    image=out/'mesh.png'
    scene.render.filepath=str(image.resolve())
    bpy.ops.render.render(write_still=True)
    if not image.is_file() or image.stat().st_size<2000:
        raise RuntimeError('independent render missing')
    report={'schema':'mgr.forge.reconstruction-blender-witness.v1',
            'status':'REAL_BLENDER_IMPORT_GEOMETRY_RENDER_PASS',
            'blender_version':bpy.app.version_string,'input_glb_sha256':digest(glb),
            'vertices':len(obj.data.vertices),'triangles':triangles,
            'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,
            'signed_mesh_volume_m3':volume,'native_bbox_min_m':low,'native_bbox_max_m':high,
            'max_native_bounds_error_m':max_error,'render_sha256':digest(image),
            'fixture_kind':'owner-authored synthetic calibrated PNG masks',
            'hidden_geometry_measured':False,'production_or_likeness_accepted':False,
            'limitations':['visual hull cannot recover occluded concavities',
                           'positive volume and manifold edges do not prove self-intersection freedom',
                           'surface nets rounds voxel corners; compare mesh and occupancy volume separately']}
    (out/'blender-witness.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('MGR_RECONSTRUCTION_WITNESS='+json.dumps(report))


if __name__=='__main__':
    main()
