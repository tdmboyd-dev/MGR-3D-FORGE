"""Independent Blender process imports animated GLB and checks animation + skin."""

import hashlib
import json
from pathlib import Path
import sys

import bpy


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 3:
        raise ValueError("animated.glb original-sha256 new-report.json required")
    source, expected, report = Path(args[0]), args[1], Path(args[2])
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise ValueError("export modified since receipt")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    skinned = [o for o in bpy.data.objects if o.type == "MESH"
               and any(m.type == "ARMATURE" for m in o.modifiers)]
    clips = list(bpy.data.actions)
    if not armatures or not skinned or not clips:
        raise RuntimeError("GLB receiving import lost skin, skeleton or animation")
    result = {"schema": "mgr.forge.animation-reimport.v1", "status": "PASS",
              "sha256": expected, "blender_version": bpy.app.version_string,
              "armatures": len(armatures), "skinned_mesh_objects": len(skinned),
              "animation_actions": len(clips),
              "action_names": sorted(action.name for action in clips),
              "game_engine_import_verified": False}
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
