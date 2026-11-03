"""Exact Blender 5.2 observation helpers for native mapped motion transfer."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Quaternion


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rigid_rotation(matrix):
    axes=[matrix.to_3x3().col[i] for i in range(3)]
    lengths=[v.length for v in axes]
    if (not all(math.isfinite(v) and 1e-5<v<1e3 for v in lengths) or
        max(lengths)-min(lengths)>max(lengths)*1e-5 or matrix.to_3x3().determinant()<=0 or
        any(abs(axes[i].normalized().dot(axes[j].normalized()))>1e-5 for i in range(3) for j in range(i+1,3))):
        raise ValueError('motion retarget requires positive rigid/uniform transforms, not scale/shear/reflection')
    return matrix.to_quaternion().normalized()


def angle(a,b):return 2*math.acos(max(0.,min(1.,abs(a.normalized().dot(b.normalized())))))


def load(path,fps):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.fps=fps;scene.render.fps_base=1
    if bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()),disable_bone_shape=True,
                                merge_vertices=False,import_merge_material_slots=False)!={'FINISHED'}:
        raise RuntimeError('Blender did not import original rigged GLB')
    rigs=[obj for obj in bpy.data.objects if obj.type=='ARMATURE']
    meshes=[obj for obj in bpy.data.objects if obj.type=='MESH']
    if len(rigs)!=1 or not 1<=len(meshes)<=32 or not 1<=len(rigs[0].data.bones)<=128:
        raise ValueError('one bounded armature and 1..32 original skinned parts required')
    rig=rigs[0]
    for obj in meshes:
        if len(obj.modifiers)!=1 or obj.modifiers[0].type!='ARMATURE' or obj.modifiers[0].object is not rig:
            raise ValueError('all receiving parts must retain the unique original armature binding')
        if obj.data.shape_keys:raise ValueError('existing shape key animation is outside the retarget contract')
    if rig.constraints or any(b.constraints for b in rig.pose.bones):
        raise ValueError('retarget refuses unsupported rig constraints')
    bpy.context.view_layer.update()
    rigid_rotation(rig.matrix_world)
    return scene,rig,sorted(meshes,key=lambda obj:obj.name)


def rest_rotations(rig):
    return {bone.name:rigid_rotation(rig.matrix_world@bone.matrix_local) for bone in rig.data.bones}


def parents(rig):return {bone.name:bone.parent.name if bone.parent else None for bone in rig.data.bones}


def source_samples(path,spec):
    scene,rig,_=load(path,spec['fps'])
    action=rig.animation_data.action if rig.animation_data else None
    if action is None or len(bpy.data.actions)!=1:
        raise ValueError('source must reopen one active skeletal clip in Blender')
    first,last=spec['start_frame'],spec['end_frame']
    start,end=action.frame_range
    if first<start-.001 or last>end+.001:
        raise ValueError(f'original source clip contains frames {start:g}..{end:g}, requested range outside')
    rest=rest_rotations(rig);hierarchy=parents(rig)
    wanted=spec['bone_map']
    if set(wanted)-set(rest):raise ValueError('source import renamed or lost mapped joints')
    samples=[]
    for frame in range(first,last+1):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for bone in rig.pose.bones:
            basis=bone.matrix_basis
            if basis.translation.length>1e-5 or max(abs(v-1) for v in basis.to_scale())>1e-5:
                raise ValueError('in-place rotation transfer refuses source bone translation or scale motion')
        samples.append({name:tuple((rigid_rotation(rig.matrix_world@rig.pose.bones[name].matrix)@
                                    rest[name].conjugated()).normalized()) for name in wanted})
    if max(angle(Quaternion(sample[name]),Quaternion(samples[0][name])) for sample in samples for name in wanted)<.002:
        raise ValueError('mapped source bones do not contain meaningful sampled rotation motion')
    return samples,hierarchy


def signature(meshes):
    """Triangle-corner identity survives harmless glTF vertex splits/reordering."""
    entries=[];materials={};images={};weights_checked=0
    def f(values):return tuple(round(float(v),5)+0. for v in values)
    for obj in meshes:
        data=obj.data;data.calc_loop_triangles()
        uv_layers=list(data.uv_layers)
        if len(uv_layers)>4:raise ValueError('retarget UV layer budget exceeded')
        groups={group.index:group.name for group in obj.vertex_groups}
        weight_rows=[]
        for vertex in data.vertices:
            row=tuple(sorted((groups[item.group],round(float(item.weight),5)) for item in vertex.groups if item.weight>1e-6))
            if not 1<=len(row)<=8 or abs(sum(weight for _,weight in row)-1)>1e-4:
                raise ValueError('retarget requires normalized original skin weights and at most eight influences')
            weight_rows.append(row);weights_checked+=1
        for slot in obj.material_slots:
            mat=slot.material
            if mat is None:continue
            if mat.name in materials:continue
            node=next((node for node in mat.node_tree.nodes if node.type=='BSDF_PRINCIPLED'),None) if mat.node_tree else None
            if node is None:raise ValueError('retarget supports original Principled material round-trip')
            materials[mat.name]=[f(node.inputs['Base Color'].default_value),
                f((node.inputs['Metallic'].default_value,node.inputs['Roughness'].default_value)),
                [node.inputs[name].is_linked for name in ('Base Color','Metallic','Roughness','Normal')]]
            for node in mat.node_tree.nodes:
                if node.type!='TEX_IMAGE' or not node.image:continue
                image=node.image
                if image.as_pointer() in images:continue
                count=image.size[0]*image.size[1]*image.channels
                if not 1<=count<=16_777_216:raise ValueError('retarget imported texture exceeds pixel budget')
                pixels=array('f',[0.])*count;image.pixels.foreach_get(pixels)
                images[image.as_pointer()]=[list(image.size),image.channels,hashlib.sha256(pixels.tobytes()).hexdigest()]
        for triangle in data.loop_triangles:
            corners=[]
            for vertex,loop in zip(triangle.vertices,triangle.loops):
                point=f(obj.matrix_world@data.vertices[vertex].co)
                uv=tuple(f(layer.data[loop].uv) for layer in uv_layers)
                corners.append((point,uv,weight_rows[vertex]))
            oriented=min(tuple(corners[i:]+corners[:i]) for i in range(3))
            material=(obj.material_slots[triangle.material_index].material.name
                      if obj.material_slots and obj.material_slots[triangle.material_index].material else None)
            entries.append(hashlib.sha256(json.dumps([obj.name,material,oriented],separators=(',',':')).encode()).digest())
    return {'triangle_skin_uv_material_sha256':hashlib.sha256(b''.join(sorted(entries))).hexdigest(),
            'triangles':len(entries),'parts':[obj.name for obj in meshes],'materials':materials,
            'embedded_images':sorted(images.values()),'weighted_vertices':weights_checked}


def evaluated_vertices(meshes):
    graph=bpy.context.evaluated_depsgraph_get();points=[]
    for obj in meshes:
        evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
        try:points.extend(evaluated.matrix_world@vertex.co for vertex in data.vertices)
        finally:evaluated.to_mesh_clear()
    return points
