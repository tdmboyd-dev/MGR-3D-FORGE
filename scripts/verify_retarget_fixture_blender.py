"""Authored different-rest skin rigs used only to verify mapped motion transfer."""
import math
from pathlib import Path
import sys
import bpy
from mathutils import Quaternion,Vector


def material(name,color,out,texture=False):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*color,1)
    shader.inputs['Roughness'].default_value=.63;shader.inputs['Metallic'].default_value=.14
    if texture:
        image=bpy.data.images.new('Owned MGR original pattern',width=8,height=8,alpha=True)
        pixels=[]
        for y in range(8):
            for x in range(8):pixels.extend((.76,.18,.05,1) if (x//2+y//2)%2 else (.025,.34,.66,1))
        image.pixels.foreach_set(pixels)
        image.file_format='PNG';image.filepath_raw=str(out/'original-texture.png');image.save();image.pack()
        node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;node.interpolation='Closest'
        mat.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
    return mat


def fixture(out,target=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=16
    name='Target original rig' if target else 'Source original rig'
    data=bpy.data.armatures.new(name);rig=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    a=data.edit_bones.new('target_base' if target else 'source_root');a.head=(0,0,0);a.tail=(0,0,1.5 if target else 1)
    b=data.edit_bones.new('target_tip' if target else 'source_arm');b.head=a.tail;b.tail=(1.55,0,2.1) if target else (1.2,0,1);b.parent=a
    b.roll=.4 if target else -.2
    if target:
        c=data.edit_bones.new('target_counterweight');c.head=a.tail;c.tail=(-.75,0,1.3);c.parent=a;c.roll=-.3
    bpy.ops.object.mode_set(mode='OBJECT')
    originals=[]
    colors=[(.14,.45,.7),(.8,.26,.11),(.4,.18,.6)]
    for index,bone in enumerate(rig.data.bones):
        head,tail=bone.head_local.copy(),bone.tail_local.copy();center=(head+tail)/2
        bpy.ops.mesh.primitive_cube_add(size=2,location=center)
        obj=bpy.context.object;obj.name='MGR original part '+bone.name
        obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector((0,0,1)).rotation_difference((tail-head).normalized())
        obj.scale=(.14,.14,bone.length*.51)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        obj.data.materials.append(material('MGR material '+bone.name,colors[index],out,texture=target and index==1))
        group=obj.vertex_groups.new(name=bone.name)
        group.add(list(range(len(obj.data.vertices))),.75 if bone.parent else 1.,'REPLACE')
        if bone.parent:obj.vertex_groups.new(name=bone.parent.name).add(list(range(len(obj.data.vertices))),.25,'REPLACE')
        modifier=obj.modifiers.new('MGR original skin','ARMATURE');modifier.object=rig
        obj.parent=rig;obj.matrix_parent_inverse=rig.matrix_world.inverted()
        originals.append(obj)
    if not target:
        for name,axis,degrees in [('source_root',(0,0,1),17),('source_arm',(0,1,0),45)]:
            bone=rig.pose.bones[name];bone.rotation_mode='QUATERNION'
            for frame,amount in [(1,0.),(8,.35),(16,1.)]:
                bone.rotation_quaternion=Quaternion(axis,math.radians(degrees*amount))
                bone.keyframe_insert('rotation_quaternion',frame=frame)
        rig.animation_data.action.name='Owned original source clip'
    scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
    for obj in originals:obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    path=out/('target-original.glb' if target else 'source-original.glb')
    result=bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
        export_animations=not target,export_skins=True,export_rest_position_armature=True,
        export_current_frame=False,export_all_influences=True,export_frame_range=True,export_force_sampling=True)
    if result!={'FINISHED'} or not path.is_file():raise RuntimeError('original fixture export failed')


if __name__=='__main__':
    out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=False)
    fixture(out);fixture(out,True)
