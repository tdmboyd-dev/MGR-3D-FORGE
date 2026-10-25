"""Execute with Blender: blender -b --python bridge/blender_probe.py -- input.glb report.json.

Requires actual Blender and bpy. This file is intentionally not imported by
Forge's no-dependency Python test runtime.
"""

import json
from pathlib import Path
import sys

import bpy


def main():
    arguments=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if len(arguments)!=2:
        raise SystemExit("usage: blender -b --python bridge/blender_probe.py -- FILE.glb REPORT.json")
    source,report=map(Path,arguments)
    if not source.is_file() or source.suffix.lower()!=".glb":
        raise ValueError("missing GLB source")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    meshes=[object for object in bpy.data.objects if object.type=="MESH"]
    triangles=0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles+=len(obj.data.loop_triangles)
    receipt={"blender_version":bpy.app.version_string,
             "source":source.name,"imported_mesh_objects":len(meshes),
             "triangles":triangles,"status":"PASS" if meshes and triangles else "FAIL"}
    report.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if receipt["status"]!="PASS":
        raise RuntimeError("Blender import contained no triangle meshes")
    print("MGR_FORGE_BLENDER_REPORT="+json.dumps(receipt,sort_keys=True))


if __name__=="__main__":
    main()
