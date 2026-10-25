"""MGR modular mannequin armature assembly in actual Blender.

Command: blender --background --factory-startup --python THIS --
         character_folder output.blend report.json

Uses rigid separate mesh parts attached to armature bones. This is an
early articulated assembly, NOT deformation skinning or animation acceptance.
"""

import json
from pathlib import Path
import sys

import bpy


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
    raise ValueError(f"unmapped part: {name}")


def to_blender_axes(point):
    """Convert Forge/glTF Y-up landmarks into Blender Z-up bone coordinates."""
    x,y,z=point
    return (x,-z,y)


def main():
    if "--" not in sys.argv:
        raise ValueError("missing arguments")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=3:
        raise ValueError("expected character folder, .blend, JSON report")
    source,destination,report=map(Path,args)
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
    for part,obj in assembled:
        target=bone_for_part(part)
        matrix=obj.matrix_world.copy()
        obj.parent=rig
        obj.parent_type="BONE"
        obj.parent_bone=target
        obj.matrix_world=matrix
        assignments[part]=target
    destination.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination.resolve()))
    result={"schema":"mgr.forge.modular-armature.v1","blender_version":bpy.app.version_string,
            "status":"PASS" if len(assembled)==len(manifest["editable_parts"]) else "FAIL",
            "mesh_parts":len(assembled),"bones":sorted(RIG_BONES),
            "attachments":assignments,"blend_file":destination.name,
            "limitations":["rigid bone parenting, no deforming vertex weights",
                           "no animation curves or full pose deformation acceptance",
                           "generic mannequin only, not approved Tevin likeness"]}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("MGR_MODULAR_ARMATURE_"+result["status"])
    if result["status"]!="PASS":
        raise RuntimeError("incomplete rig")


if __name__=="__main__":
    main()
