"""Bake caller-mapped source rotation deltas onto the original target skeleton."""
import json
from pathlib import Path
import sys
import bpy
from mathutils import Matrix,Quaternion

sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_motion_retarget_common import load,source_samples,parents,rest_rotations,rigid_rotation,angle,sha


def bake(out):
    spec=json.loads((out/'motion-map.json').read_text())
    samples,source_parents=source_samples(out/'source-original.glb',spec)
    scene,rig,meshes=load(out/'target-original.glb',spec['fps'])
    if bpy.data.actions or rig.animation_data and rig.animation_data.action:
        raise ValueError('target previously animated; original action would be replaced')
    for bone in rig.pose.bones:
        basis=bone.matrix_basis
        if (basis.translation.length>1e-5 or max(abs(value-1) for value in basis.to_scale())>1e-5 or
                angle(basis.to_quaternion(),Quaternion())>.003):
            raise ValueError('target must be in original neutral bind pose before creating a new motion revision')
    target_parents=parents(rig);target_rest=rest_rotations(rig)
    mapping=spec['bone_map'];inverse_map={target:source for source,target in mapping.items()}
    if set(inverse_map)-set(target_rest):raise ValueError('target receiving rig lost mapped joints')
    for source,target in mapping.items():
        sp,tp=source_parents[source],target_parents[target]
        if (sp is None)!=(tp is None) or (sp in mapping and mapping[sp]!=tp) or (tp in inverse_map and inverse_map[tp]!=sp):
            raise ValueError('explicit mapped parent relations disagree between original rigs')
    ordered=[]
    def visit(bone):
        ordered.append(bone)
        for child in bone.children:visit(child)
    for bone in rig.pose.bones:
        if bone.parent is None:visit(bone)
    target_world=rigid_rotation(rig.matrix_world)
    scene.frame_start=1;scene.frame_end=len(samples)
    previous={};max_error=0.
    for frame,sample in enumerate(samples,1):
        scene.frame_set(frame)
        converted={};expected={}
        for bone in ordered:
            parent=bone.parent;rest=bone.bone.matrix_local
            parent_pose=converted[parent.name] if parent else None
            kwargs={'parent_matrix':parent_pose,'parent_matrix_local':parent.bone.matrix_local} if parent else {}
            if bone.name in inverse_map:
                desired=(Quaternion(sample[inverse_map[bone.name]])@target_rest[bone.name]).normalized()
                expected[bone.name]=desired
                pose=(target_world.conjugated()@desired).to_matrix().to_4x4()
                pose.translation=(parent_pose@parent.bone.matrix_local.inverted()@rest).translation if parent else rest.translation
                basis=bone.bone.convert_local_to_pose(pose,rest,invert=True,**kwargs)
                if basis.translation.length>1e-5 or max(abs(v-1) for v in basis.to_scale())>1e-5:
                    raise RuntimeError('mapped target solve would change original bone translation/scale')
                rotation=basis.to_quaternion().normalized()
                if bone.name in previous and previous[bone.name].dot(rotation)<0:rotation.negate()
                previous[bone.name]=rotation.copy()
                bone.rotation_mode='QUATERNION';bone.location=(0,0,0);bone.scale=(1,1,1)
                bone.rotation_quaternion=rotation
                bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=bone.name)
            else:bone.matrix_basis=Matrix.Identity(4)
            converted[bone.name]=bone.bone.convert_local_to_pose(bone.matrix_basis,rest,**kwargs)
        bpy.context.view_layer.update()
        for name,desired in expected.items():
            max_error=max(max_error,angle(rigid_rotation(rig.matrix_world@rig.pose.bones[name].matrix),desired))
    if max_error>.003:raise RuntimeError('actual creator target orientations differ from mapped source deltas')
    rig.animation_data.action.name='MGR original mapped motion'
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'retargeted.blend'))
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
    for obj in meshes:obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    result=bpy.ops.export_scene.gltf(filepath=str(out/'retargeted.glb'),export_format='GLB',use_selection=True,
        export_skins=True,export_animations=True,export_rest_position_armature=True,
        export_current_frame=False,export_all_influences=True,export_frame_range=True,export_force_sampling=True)
    if result!={'FINISHED'} or not (out/'retargeted.glb').is_file():raise RuntimeError('Blender did not export actual retargeted GLB')
    report={'schema':'mgr.forge.motion-retarget-creator.v1','status':'LOCAL_BAKED_TARGET_RECEIVER_PENDING',
            'source_sha256':sha(out/'source-original.glb'),'target_sha256':sha(out/'target-original.glb'),
            'artifact_sha256':sha(out/'retargeted.glb'),'editable_blend_sha256':sha(out/'retargeted.blend'),
            'creator_max_target_rotation_error_rad':max_error,'frames':len(samples),
            'mapped_bones':len(mapping),'blender_version':bpy.app.version_string}
    (out/'retarget-creator.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print('MGR_RETARGET_BAKED='+json.dumps(report))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('one motion retarget revision folder required')
    bake(Path(args[0]).resolve())
