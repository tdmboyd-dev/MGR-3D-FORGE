"""Headless Blender 5.x prototype: fit a DNA rig to a generated MGR creature.

Does not claim learned auto-rigging or production-quality skinning.
blender --background --factory-startup --python THIS -- CREATURE_DIR OUTPUT_DIR
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def point(p):
    # glTF/FORGE Y-up -> Blender Z-up.
    return Vector((p[0],-p[2],p[1]))


def distance_to_segment(q,a,b):
    ab=b-a
    denom=ab.length_squared
    if denom<1e-12:
        return (q-a).length
    t=max(0.0,min(1.0,(q-a).dot(ab)/denom))
    return (q-(a+t*ab)).length


def deform_coords(mesh_obj,frame):
    scene=bpy.context.scene
    scene.frame_set(frame)
    graph=bpy.context.evaluated_depsgraph_get()
    evaluated=mesh_obj.evaluated_get(graph)
    m=evaluated.to_mesh()
    try:
        return [evaluated.matrix_world@v.co for v in m.vertices]
    finally:
        evaluated.to_mesh_clear()


def main():
    if "--" not in sys.argv:
        raise ValueError("source creature and output dir required")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=2:
        raise ValueError("expected CREATURE_DIR and OUTPUT_DIR")
    source,target=map(Path,args)
    recipe=json.loads((source/"rig-blueprint.json").read_text(encoding="utf-8"))
    manifest=json.loads((source/"creature.json").read_text(encoding="utf-8"))
    if recipe["schema"]!="mgr.forge.creature-rig-blueprint.v1" or (
            recipe["mesh_sha256"]!=manifest["artifact"]["sha256"]):
        raise ValueError("rig recipe not bound to the creature mesh")
    raw=(source/"creature.glb").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=recipe["mesh_sha256"]:
        raise ValueError("creature mesh changed since rig plan")
    if target.exists():
        raise FileExistsError("refuse to overwrite existing rig output")
    target.mkdir(parents=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str((source/"creature.glb").resolve()))
    meshes=[o for o in bpy.data.objects if o.type=="MESH"]
    if len(meshes)!=1 or len(meshes[0].data.vertices)<20:
        raise ValueError("expected one valid procedural mesh")
    obj=meshes[0]
    original_vertices=len(obj.data.vertices)
    arm=bpy.data.armatures.new("MGR_Creature_Armature")
    rig=bpy.data.objects.new("MGR_Creature_Rig",arm)
    bpy.context.scene.collection.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode="EDIT")
    entries=recipe["skeleton"]
    for item in entries:
        b=arm.edit_bones.new(item["name"])
        b.head,b.tail=point(item["head"]),point(item["tail"])
    for item in entries:
        if item["parent"] is not None:
            arm.edit_bones[item["name"]].parent=arm.edit_bones[item["parent"]]
    bpy.ops.object.mode_set(mode="OBJECT")
    groups={item["name"]:obj.vertex_groups.new(name=item["name"]) for item in entries}
    # Conservative, general proximity weights; unlike semantic per-face skinning,
    # this may create undesirable bends at body/limb intersections.
    segments=[(item["name"],point(item["head"]),point(item["tail"]))
              for item in entries if item["role"]!="root"]
    for vertex in obj.data.vertices:
        position=obj.matrix_world@vertex.co
        ranked=sorted(((distance_to_segment(position,a,b),name)
                      for name,a,b in segments),key=lambda x:(x[0],x[1]))[:3]
        # Inverse-square weights respect nearby anatomy; weights normalize to 1.
        raw_weights=[(name,1/(max(dist,0.08)**2)) for dist,name in ranked]
        total=sum(weight for _,weight in raw_weights)
        for name,weight in raw_weights:
            groups[name].add([vertex.index],weight/total,"REPLACE")
    modifier=obj.modifiers.new("MGR_Armature_Deform","ARMATURE")
    modifier.object=rig
    obj.parent=rig
    obj.matrix_parent_inverse=rig.matrix_world.inverted()
    bpy.context.view_layer.update()
    scene=bpy.context.scene
    scene.frame_start=1
    scene.frame_end=16
    chosen=[b for b in recipe.get("preview_animation_bones",
                               ["tail_01","tail_02","left_wing_01","right_wing_01"])
            if b in rig.pose.bones]
    if not chosen:
        raise ValueError("no supported articulated appendage")
    for bone_name in chosen:
        bone=rig.pose.bones[bone_name]
        bone.rotation_mode="XYZ"
        bone.rotation_euler=(0,0,0)
        bone.keyframe_insert(data_path="rotation_euler",frame=1)
        sign=-1 if "right_wing" in bone_name or bone_name=="leg_02_upper" else 1
        bone.rotation_euler[2]=math.radians(24*sign)
        bone.keyframe_insert(data_path="rotation_euler",frame=16)
    first=deform_coords(obj,1)
    moved=deform_coords(obj,16)
    if len(first)!=len(moved) or not first:
        raise RuntimeError("deformed mesh evaluation failed")
    max_displacement=max((a-b).length for a,b in zip(first,moved))
    if max_displacement<0.01:
        raise RuntimeError("skin weights and animation failed to move the mesh")
    scene.frame_set(1)
    blend=target/"creature-rigged.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    output=target/"creature-rigged.glb"
    bpy.ops.export_scene.gltf(filepath=str(output.resolve()), export_format="GLB",
                             export_animations=True,export_skins=True,
                             use_selection=True)
    if not output.is_file() or output.stat().st_size<10000:
        raise RuntimeError("Blender did not export rigged GLB")
    report={
      "schema":"mgr.forge.creature-skin-smoke.v1","status":"LOCAL_SKIN_ANIMATION_PROTOTYPE",
      "mesh_source_sha256":recipe["mesh_sha256"],
      "rigged_glb_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
      "rigged_glb_bytes":output.stat().st_size,
      "blender_version":bpy.app.version_string,
      "mesh_objects":len(meshes),"vertices":original_vertices,
      "bones":len(rig.data.bones),"animation_bones":chosen,
      "weighted_vertices":original_vertices,
      "max_evaluated_vertex_motion_m":round(max_displacement,5),
      "reopened_in_second_process":False,
      "production_rig_accepted":False,
      "quality_limitations":["nearest-segment weights only; no joint-aware anatomical skin",
                             "no locomotion, cloth, facial controls or game-performance acceptance",
                             "fixed skeleton family derived from generated creature DNA"]
    }
    (target/"skin-proof.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",
                                         encoding="utf-8")
    print("MGR_CREATURE_SKIN="+json.dumps(report))


if __name__=="__main__":
    main()
