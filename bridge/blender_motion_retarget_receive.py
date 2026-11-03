"""Separate Blender import: compare original rotations and target skin deformation."""
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Quaternion,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_motion_retarget_common import (angle,evaluated_vertices,load,parents,rest_rotations,
                                            rigid_rotation,sha,signature,source_samples)


def receive(out):
    spec=json.loads((out/'motion-map.json').read_text())
    creator=json.loads((out/'retarget-creator.json').read_text())
    for key,name in [('source_sha256','source-original.glb'),('target_sha256','target-original.glb'),
                     ('artifact_sha256','retargeted.glb'),('editable_blend_sha256','retargeted.blend')]:
        if creator.get(key)!=sha(out/name):raise ValueError('retarget source/export changed before receiving import')
    samples,_=source_samples(out/'source-original.glb',spec)
    _,original,original_meshes=load(out/'target-original.glb',spec['fps'])
    before=signature(original_meshes);rest=rest_rotations(original);original_parents=parents(original)
    heads={bone.name:tuple(original.matrix_world@bone.head_local) for bone in original.data.bones}
    lengths={bone.name:((original.matrix_world@bone.head_local)-(original.matrix_world@bone.tail_local)).length
             for bone in original.data.bones}
    scene,rig,meshes=load(out/'retargeted.glb',spec['fps'])
    after=signature(meshes)
    if any(before[k]!=after[k] for k in before if k!='weighted_vertices'):
        raise RuntimeError('receiving target rest triangles/skin/UV/materials differ from the original target')
    if parents(rig)!=original_parents:raise RuntimeError('receiving target skeleton names/hierarchy changed')
    max_rest_error=0.;max_length_error=0.
    for bone in rig.data.bones:
        head=rig.matrix_world@bone.head_local;tail=rig.matrix_world@bone.tail_local
        max_rest_error=max(max_rest_error,(head-Vector(heads[bone.name])).length,
                           angle(rigid_rotation(rig.matrix_world@bone.matrix_local),rest[bone.name]))
        max_length_error=max(max_length_error,abs((head-tail).length-lengths[bone.name]))
    if max_rest_error>.003 or max_length_error>1e-4:
        raise RuntimeError('receiving original target bind bone positions/orientations/lengths changed')
    action=rig.animation_data.action if rig.animation_data else None
    if action is None or len(bpy.data.actions)!=1:raise RuntimeError('receiving target lost unique baked skeletal clip')
    start,end=action.frame_range
    if abs(start-1)>.001 or abs(end-len(samples))>.001:
        raise RuntimeError(f'receiving target clip frame range changed: {start:g}..{end:g}')
    maximum=0.;max_orientation_error=0.;peak=1;first=None;peak_points=None;moving=0
    for frame,sample in enumerate(samples,1):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for source,target in spec['bone_map'].items():
            actual=(rigid_rotation(rig.matrix_world@rig.pose.bones[target].matrix)@rest[target].conjugated()).normalized()
            max_orientation_error=max(max_orientation_error,angle(actual,Quaternion(sample[source])))
        points=evaluated_vertices(meshes)
        if first is None:first=points
        if not points or len(first)!=len(points):raise RuntimeError('receiving target evaluation lost vertex correspondence')
        displacement=[(a-b).length for a,b in zip(first,points)]
        if any(not math.isfinite(v) for v in displacement):raise RuntimeError('nonfinite received target motion')
        if max(displacement)>maximum:
            maximum=max(displacement);peak=frame;peak_points=points
            moving=sum(d>1e-6 for d in displacement)
    if max_orientation_error>.003:raise RuntimeError('received target rotations do not follow original mapped source clip')
    if maximum<=1e-5 or peak==1 or not moving:raise RuntimeError('received target skin does not actually deform')
    bounds=first+peak_points
    center=Vector([(min(p[i] for p in bounds)+max(p[i] for p in bounds))/2 for i in range(3)])
    radius=max(max(p[i] for p in bounds)-min(p[i] for p in bounds) for i in range(3))
    data=bpy.data.cameras.new('MGR retarget witness camera');camera=bpy.data.objects.new(data.name,data)
    bpy.context.collection.objects.link(camera);scene.camera=camera
    camera.location=center+Vector((radius*.8,-radius*2,radius*.8))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=radius*1.4
    for x,y,z,power in [(1,-1,2,500),(-1,1,1,400)]:
        lamp=bpy.data.lights.new('MGR retarget witness light','AREA');lamp.energy=power;lamp.size=radius
        obj=bpy.data.objects.new(lamp.name,lamp);bpy.context.collection.objects.link(obj)
        obj.location=center+Vector((x*radius,y*radius,z*radius));obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
    scene.world=bpy.data.worlds.new('MGR retarget witness world');scene.world.color=(.12,.12,.12)
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=10
    scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    previews={}
    for name,frame in [('retarget-before.png',1),('retarget-after.png',peak)]:
        scene.frame_set(frame);scene.render.filepath=str(out/name)
        bpy.ops.render.render(write_still=True)
        previews[name]={'frame':frame,'sha256':sha(out/name)}
    if previews['retarget-before.png']['sha256']==previews['retarget-after.png']['sha256']:
        raise RuntimeError('receiving deformation produced identical witness images')
    proof={'schema':'mgr.forge.motion-retarget-blender-witness.v1','status':'INDEPENDENT_RETARGET_GLTF_DEFORMATION_PASS',
           **{key:creator[key] for key in ('source_sha256','target_sha256','artifact_sha256','editable_blend_sha256')},
           'blender_version':bpy.app.version_string,'frames':len(samples),'fps':spec['fps'],
           'mapped_bones':len(spec['bone_map']),'target_bones':len(rest),
           'target_rest_skin_uv_materials_preserved':True,'original_target_inventory':before,'received_target_inventory':after,
           'max_mapped_orientation_error_radians':max_orientation_error,'max_bind_position_or_angle_error':max_rest_error,
           'max_bone_length_error_m':max_length_error,'received_max_vertex_motion_m':maximum,
           'received_moving_vertices_at_peak':moving,'received_evaluated_vertices':len(first),
           'witness_previews':previews,'owner_art_accepted':False,'root_motion_transferred':False}
    (out/'retarget-blender-proof.json').write_text(json.dumps(proof,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print('MGR_RETARGET_RECEIVED='+json.dumps(proof))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('one motion retarget revision folder required')
    receive(Path(args[0]).resolve())
