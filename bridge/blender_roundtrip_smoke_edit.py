"""Deterministic QA-only edit of a Blender-created MGR building; never run prompts."""

from pathlib import Path
import sys
import bpy


source_out = Path(sys.argv[sys.argv.index("--") + 1])
if source_out.exists() or source_out.suffix.lower() != ".blend":
    raise ValueError("QA destination must be a fresh .blend")
obj = bpy.data.objects.get("mgr-created-0001")
if obj is None or obj.get("mgr_id") != "mgr-created-0001":
    raise ValueError("expected MGR-created building missing")
obj.location.x += 1.25
obj.dimensions.z += 3.0
obj.location.z += 1.5
print("MGR_BPY_EDIT", obj.name, tuple(round(v, 5) for v in obj.location), tuple(round(v, 5) for v in obj.dimensions))
bpy.ops.wm.save_as_mainfile(filepath=str(source_out.resolve()))
