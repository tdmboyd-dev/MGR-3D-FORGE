"""Separate Blender receiver: unchanged triangles/materials and real padded UVs."""
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector


def imported(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects=[obj for obj in bpy.data.objects if obj.type=='MESH']
    triangles=[];uvs=[];names=[]
    for obj in objects:
        names.append(obj.name)
        obj.data.calc_loop_triangles()
        layer=obj.data.uv_layers.active
        for triangle in obj.data.loop_triangles:
            points=[obj.matrix_world@obj.data.vertices[index].co for index in triangle.vertices]
            coords=tuple(sorted(tuple(round(float(v),5) for v in point) for point in points))
            material=obj.material_slots[triangle.material_index].material.name
            triangles.append((coords,material))
            if layer:
                uvs.append([tuple(layer.data[index].uv) for index in triangle.loops])
    return objects,sorted(names),sorted(triangles),uvs


def main():
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=3:raise ValueError('expected original.glb revision_directory NEW_output_directory')
    original,revision,out=map(lambda p:Path(p).resolve(),args)
    out.mkdir(parents=True,exist_ok=False)
    receipt=json.loads((revision/'uv-receipt.json').read_text())
    artifact=revision/'uv-mapped.glb'
    if hashlib.sha256(original.read_bytes()).hexdigest()!=receipt['source_sha256'] or hashlib.sha256(artifact.read_bytes()).hexdigest()!=receipt['artifact_sha256']:
        raise ValueError('UV source/artifact changed before receiving import')
    _,source_names,source_triangles,_=imported(original)
    objects,names,triangles,uvs=imported(artifact)
    if names!=source_names or triangles!=source_triangles:
        raise RuntimeError('UV revision changed receiving original world triangles/materials/names')
    if len(uvs)!=receipt['chart_count']:raise RuntimeError('receiving UV chart count differs from original triangles')
    boxes=[]
    for points in uvs:
        if not all(0<v<1 for p in points for v in p):raise RuntimeError('received UV escaped atlas range')
        a,b,c=points
        area=abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2
        if area<=1e-12:raise RuntimeError('received UV triangle collapsed')
        low=[min(p[i] for p in points) for i in range(2)]
        high=[max(p[i] for p in points) for i in range(2)]
        boxes.append((low,high))
    for i,(low,high) in enumerate(boxes):
        for other_low,other_high in boxes[i+1:]:
            if not any(high[axis]<other_low[axis] or other_high[axis]<low[axis] for axis in range(2)):
                raise RuntimeError('received triangle islands overlap in UV space')
    # Checker is applied only in the independent diagnostic scene, preserving
    # original material definitions in the delivered GLB.
    image=bpy.data.images.load(str(revision/'diagnostic-checker.png'),check_existing=True)
    material=bpy.data.materials.new('MGR diagnostic UV checker only')
    material.use_nodes=True
    nodes=material.node_tree.nodes
    texture=nodes.new('ShaderNodeTexImage');texture.image=image;texture.interpolation='Closest'
    shader=nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value=.7
    material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
    for obj in objects:
        obj.data.materials.clear();obj.data.materials.append(material)
        for polygon in obj.data.polygons:polygon.material_index=0
    points=[obj.matrix_world@Vector(corner) for obj in objects for corner in obj.bound_box]
    center=sum(points,Vector((0,0,0)))/len(points)
    radius=max(max(p[i] for p in points)-min(p[i] for p in points) for i in range(3))
    camera_data=bpy.data.cameras.new('MGR UV diagnostic camera')
    camera=bpy.data.objects.new('MGR UV diagnostic camera',camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location=center+Vector((radius*1.1,-radius*1.8,radius*.9))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.type='ORTHO';camera_data.ortho_scale=radius*1.4
    scene=bpy.context.scene;scene.camera=camera
    for x,y,z,power in [(1,-1,2,1000),(-1,1,1,700)]:
        light_data=bpy.data.lights.new('MGR UV diagnostic light','AREA');light_data.energy=power;light_data.shape='DISK';light_data.size=radius
        light=bpy.data.objects.new('MGR UV diagnostic light',light_data);bpy.context.collection.objects.link(light)
        light.location=center+Vector((x*radius,y*radius,z*radius))
        light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    scene.world=bpy.data.worlds.new('MGR UV diagnostic world')
    scene.world.color=(.1,.1,.1)
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
    scene.render.resolution_x=700;scene.render.resolution_y=500;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'uv-checker-preview.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'uv-diagnostic.blend'))
    bpy.ops.render.render(write_still=True)
    png=(out/'uv-checker-preview.png').read_bytes()
    proof={'schema':'mgr.forge.uv-atlas-blender-witness.v1','status':'INDEPENDENT_UV_ATLAS_IMPORT_CHECKER_RENDER_PASS',
           'source_sha256':receipt['source_sha256'],'artifact_sha256':receipt['artifact_sha256'],
           'blender_version':bpy.app.version_string,'renderer':'CYCLES_CPU','triangles':len(triangles),
           'chart_count':len(uvs),'part_names':names,'same_original_world_triangles_materials_and_part_names':True,
           'all_uv_islands_nonzero_inside_unit_range_and_nonoverlapping':True,
           'checker_render_is_diagnostic_only':True,'preview_sha256':hashlib.sha256(png).hexdigest(),
           'owner_art_accepted':False,'generated_texture_art':False}
    (out/'blender-proof.json').write_text(json.dumps(proof,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print('MGR_UV_ATLAS_RECEIVER='+json.dumps(proof))


if __name__=='__main__':main()
