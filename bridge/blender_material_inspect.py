"""Open GLB with Blender and inspect actual Principled BSDF material sockets."""

import json
from pathlib import Path
import sys

import bpy


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=2:
        raise ValueError("expected source.glb report.json")
    source,report=map(Path,args)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    materials={}
    for obj in bpy.data.objects:
        if obj.type!="MESH":
            continue
        for slot in obj.material_slots:
            material=slot.material
            if material is None or material.name in materials:
                continue
            node=next((node for node in material.node_tree.nodes
                       if node.type=="BSDF_PRINCIPLED"),None) if material.use_nodes else None
            if node is None:
                raise RuntimeError(f"no Principled material for {material.name}")
            materials[material.name]={"name":material.name,
                "base_color":list(node.inputs["Base Color"].default_value),
                "metallic":float(node.inputs["Metallic"].default_value),
                "roughness":float(node.inputs["Roughness"].default_value)}
    if not materials:
        raise RuntimeError("imported GLB has no material")
    result={"schema":"mgr.forge.blender-material-observation.v1",
            "blender_version":bpy.app.version_string,
            "source":source.name,"materials":list(sorted(materials.values(),key=lambda x:x["name"]))}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("MGR_MATERIAL_OBSERVATION_PASS")


if __name__=="__main__":
    main()
