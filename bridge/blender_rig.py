"""MGR modular mannequin armature assembly in actual Blender.

Command: blender --background --factory-startup --python THIS --
         character_folder output.blend report.json

Default uses rigid mesh/bone parenting. Optional SKIN mode creates actual
armature modifiers and vertex groups with rigid 1.0 weights, and measures
evaluated-mesh motion over animation keyframes. Smooth multi-bone deformation
and production animation remain open.
"""

import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Quaternion, Vector


RIG_BONES = {
    "root": ((0,0.92,0),(0,1.15,0),None),
    "torso": ((0,1.15,0),(0,1.49,0),"root"),
    "head": ((0,1.49,0),(0,1.84,0),"torso"),
    "left_upper_arm": ((-0.28,1.47,0),(-0.61,1.47,0),"torso"),
    "left_forearm": ((-0.61,1.47,0),(-0.87,1.47,0),"left_upper_arm"),
    "left_hand": ((-0.87,1.47,0),(-0.99,1.47,0),"left_forearm"),
    "right_upper_arm": ((0.28,1.47,0),(0.61,1.47,0),"torso"),
    "right_forearm": ((0.61,1.47,0),(0.87,1.47,0),"right_upper_arm"),
    "right_hand": ((0.87,1.47,0),(0.99,1.47,0),"right_forearm"),
    "left_leg": ((-0.15,0.92,0),(-0.15,0.12,0),"root"),
    "right_leg": ((0.15,0.92,0),(0.15,0.12,0),"root"),
}


def bone_for_part(name):
    if name in RIG_BONES:
        return name
    if name in ("torso","shirt","coat","chain"):
        return "torso"
    if name in ("hair",):
        return "head"
    if name=="left_boot":
        return "left_leg"
    if name=="right_boot":
        return "right_leg"
    if name=="left_pant_leg":
        return "left_leg"
    if name=="right_pant_leg":
        return "right_leg"
    if name=="left_elbow_sleeve":
        return "left_upper_arm"
    if name=="right_elbow_sleeve":
        return "right_upper_arm"
    raise ValueError(f"unmapped part: {name}")


def to_blender_axes(point):
    """Convert Forge/glTF Y-up landmarks into Blender Z-up bone coordinates."""
    x,y,z=point
    return (x,-z,y)


def main():
    if "--" not in sys.argv:
        raise ValueError("missing arguments")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args) not in (3,4) or (len(args)==4 and args[3]!="SKIN"):
        raise ValueError("expected character folder, .blend, JSON report, optional SKIN")
    source,destination,report=map(Path,args[:3])
    skin=len(args)==4
    manifest=json.loads((source/"character.json").read_text(encoding="utf-8"))
    if manifest["pose"]!="T":
        raise ValueError("neutral T mannequin required for initial armature assembly")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    assembled=[]
    for part in manifest["editable_parts"]:
        glb=source/"parts"/f"{part}.glb"
        if not glb.is_file():
            raise FileNotFoundError(glb)
        previous=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(glb.resolve()))
        meshes=[obj for obj in set(bpy.data.objects)-previous if obj.type=="MESH"]
        if len(meshes)!=1:
            raise ValueError(f"expected one imported mesh for {part}, got {len(meshes)}")
        obj=meshes[0]
        obj.name=f"MGR_{part}"
        assembled.append((part,obj))
    armature=bpy.data.armatures.new("MGR_Neutral_Armature")
    rig=bpy.data.objects.new("MGR_Character_Rig",armature)
    bpy.context.scene.collection.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name,(head,tail,_) in RIG_BONES.items():
        bone=armature.edit_bones.new(name)
        bone.head=to_blender_axes(head)
        bone.tail=to_blender_axes(tail)
    for name,(_,_,parent) in RIG_BONES.items():
        if parent:
            armature.edit_bones[name].parent=armature.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    assignments={}
    mixed_weight_vertices=0
    for part,obj in assembled:
        target=bone_for_part(part)
        if skin:
            if part.endswith("_elbow_sleeve"):
                side=part.split("_")[0]
                upper=obj.vertex_groups.new(name=f"{side}_upper_arm")
                lower=obj.vertex_groups.new(name=f"{side}_forearm")
                for vertex in obj.data.vertices:
                    # All imported meshes are in Blender Z-up. Sleeve is
                    # positioned around |x| = 0.61m at neutral T pose.
                    x=abs((obj.matrix_world @ vertex.co).x)
                    t=max(.05,min(.95,(x-.52)/.18))
                    upper.add([vertex.index],1-t,"REPLACE")
                    lower.add([vertex.index],t,"REPLACE")
                    mixed_weight_vertices+=1
            else:
                group=obj.vertex_groups.new(name=target)
                group.add(list(range(len(obj.data.vertices))),1.0,"REPLACE")
            modifier=obj.modifiers.new("MGR_Deform_Armature","ARMATURE")
            modifier.object=rig
        else:
            matrix=obj.matrix_world.copy()
            obj.parent=rig
            obj.parent_type="BONE"
            obj.parent_bone=target
            obj.matrix_world=matrix
        assignments[part]=target
    movement_m=None
    if skin:
        scene=bpy.context.scene
        scene.frame_start=1
        scene.frame_end=12
        for name in ("left_upper_arm","right_upper_arm"):
            bone=rig.pose.bones[name]
            bone.rotation_mode="QUATERNION"
            bone.rotation_quaternion=Quaternion((1,0,0,0))
            bone.keyframe_insert(data_path="rotation_quaternion",frame=1)
            bone.rotation_quaternion=Quaternion((0,0,1),math.radians(35 if name.startswith("left") else -35))
            bone.keyframe_insert(data_path="rotation_quaternion",frame=12)
        def positions_at(frame):
            scene.frame_set(frame)
            depsgraph=bpy.context.evaluated_depsgraph_get()
            obj=next(mesh for part,mesh in assembled if part=="left_hand")
            evaluated=obj.evaluated_get(depsgraph)
            mesh=evaluated.to_mesh()
            try:
                return [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            finally:
                evaluated.to_mesh_clear()
        start=positions_at(1)
        end=positions_at(12)
        if len(start)!=len(end) or not start:
            raise RuntimeError("invalid evaluated hand mesh")
        movement_m=max((a-b).length for a,b in zip(start,end))
        if movement_m<0.01:
            raise RuntimeError("pose keyframes did not visibly deform evaluated hand geometry")
        scene.frame_set(1)
    destination.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination.resolve()))
    result={"schema":"mgr.forge.modular-armature.v1","blender_version":bpy.app.version_string,
            "status":"PASS" if len(assembled)==len(manifest["editable_parts"]) else "FAIL",
            "mesh_parts":len(assembled),"bones":sorted(RIG_BONES),
            "attachments":assignments,"blend_file":destination.name,"rig_mode":"skin" if skin else "rigid",
            "dual_bone_weight_vertices":mixed_weight_vertices,
            "animation_motion_m":round(movement_m,6) if skin else None,
            "limitations":["two-bone elbow sleeve interpolation only; rest of mesh remains rigid single-bone weights" if skin else "rigid bone parenting, no deforming vertex weights",
                           "only hand-motion smoke test, no full pose deformation acceptance" if skin else "no animation curves or full pose deformation acceptance",
                           "generic mannequin only, not approved Tevin likeness"]}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("MGR_MODULAR_ARMATURE_"+result["status"])
    if result["status"]!="PASS":
        raise RuntimeError("incomplete rig")


if __name__=="__main__":
    main()
