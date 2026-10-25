"""Independent fresh-process Blender check of saved candidate handoff .blend."""

import json
from pathlib import Path
import sys

import bpy


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 3:
        raise ValueError("source.blend new-proof.json expected-source-sha required")
    source, report, expected = args
    bpy.ops.wm.open_mainfile(filepath=str(Path(source).resolve()))
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    actual = bpy.context.scene.get("mgr_character_source_sha256")
    for obj in meshes:
        if obj.get("mgr_character_source_sha256") != expected:
            raise RuntimeError("editable source fingerprint lost on mesh")
    triangles = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    if actual != expected or not meshes or triangles < 1:
        raise RuntimeError("reopened Blender candidate did not preserve geometry and fingerprint")
    result = {"schema": "mgr.forge.character-reopen.v1", "status": "PASS",
              "source_sha256": expected, "mesh_objects": len(meshes),
              "triangles": triangles, "blender_version": bpy.app.version_string}
    Path(report).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
