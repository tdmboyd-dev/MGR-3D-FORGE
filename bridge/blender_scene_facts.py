"""Actual Blender object inventory after importing a Forge GLB.

Usage: blender --background --factory-startup --python THIS -- input.glb output.json
"""

import json
import sys
from pathlib import Path

import bpy


def main():
    if "--" not in sys.argv:
        raise ValueError("expected -- <input.glb> <report.json>")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=2:
        raise ValueError("expected input and report")
    source,destination=map(Path,args)
    if source.suffix.lower()!=".glb" or not source.is_file():
        raise ValueError("GLB input required")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    objects=[]
    for obj in sorted(bpy.context.scene.objects,key=lambda value:value.name):
        if obj.type not in ("MESH","ARMATURE","EMPTY","CAMERA","LIGHT"):
            continue
        world=obj.matrix_world
        object_fact={
            "name":obj.name,"kind":obj.type,
            "location_m":[round(float(value),6) for value in world.translation],
            "dimensions_m":[round(float(value),6) for value in obj.dimensions],
            "parent":obj.parent.name if obj.parent else None,
            "evidence":"direct-Blender-object-data"
        }
        if obj.type=="MESH":
            mesh=obj.data
            object_fact["vertices"]=len(mesh.vertices)
            object_fact["polygons"]=len(mesh.polygons)
            object_fact["materials"]=[slot.material.name if slot.material else None for slot in obj.material_slots]
            object_fact["has_uv"]=len(mesh.uv_layers)>0
            object_fact["armature_modifiers"]=[m.object.name if m.object else None for m in obj.modifiers if m.type=="ARMATURE"]
        if obj.type=="ARMATURE":
            object_fact["bones"]=sorted(bone.name for bone in obj.data.bones)
        objects.append(object_fact)
    receipt={"schema":"mgr.forge.blender-scene-facts.v1",
             "blender_version":bpy.app.version_string,
             "status":"PASS" if any(obj["kind"]=="MESH" for obj in objects) else "FAIL",
             "objects":objects,
             "limitations":["GLB mesh objects may combine multiple semantic world objects",
                            "data is from imported GLB, not scene understanding from pixels"]}
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if receipt["status"]!="PASS":
        raise RuntimeError("no imported mesh")
    print("MGR_BLENDER_SCENE_FACTS_PASS "+str(destination.resolve()))


if __name__=="__main__":
    main()
