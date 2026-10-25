"""Run a complete browser-format edit → GLB → independently editable Blender .blend test."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forge.cli import build
from forge.live_blender import create_live_blender_scene
from forge.spec import WorldSpec
from forge.world_editor import apply_world_edits
from forge.blender_roundtrip import export_blender_edits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blender", required=True)
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="mgr-blender-scene-proof-"))
    source = root / "original"
    build(WorldSpec(seed=8964, columns=3, rows=3, buildings=4), source)
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    edits = {"schema": "mgr.forge.world-edit.v1",
             "asset_sha256": hashlib.sha256((source / "world.glb").read_bytes()).hexdigest(),
             "buildings": [{k: b[k] for k in ("id", "center", "size", "material")}
                           for b in manifest["buildings"]]}
    edits["buildings"].append({"id": "mgr-created-0001", "center": [0, 0, 0],
                               "size": [8, 16, 8], "material": "building-gold"})
    edit_path = root / "edits.json"
    edit_path.write_text(json.dumps(edits), encoding="utf-8")
    edited = root / "edited"
    apply_world_edits(source, edit_path, edited)
    receipt = create_live_blender_scene(edited, root / "mgr-scene.blend", root / "blender-proof.json",
                                        binary=args.blender, timeout=240)
    assert receipt["editable_buildings"] == 5
    assert "mgr-created-0001" in receipt["object_names"]
    altered_blend = root / "modified-scene.blend"
    script = Path(__file__).resolve().parent.parent / "bridge" / "blender_roundtrip_smoke_edit.py"
    mutation = subprocess.run([args.blender, "--background", "--factory-startup", str(root / "mgr-scene.blend"),
                               "--python", str(script), "--", str(altered_blend)],
                              capture_output=True, text=True, timeout=120, check=False)
    if mutation.returncode or not altered_blend.is_file():
        raise RuntimeError("real Blender editing failed: " + (mutation.stdout + mutation.stderr)[-900:])
    back = export_blender_edits(args.blender, altered_blend, source, root / "blender-edits.json",
                                root / "roundtrip-proof.json")
    assert back["editable_buildings"] == 5
    returned = json.loads((root / "blender-edits.json").read_text(encoding="utf-8"))
    changed = next(b for b in returned["buildings"] if b["id"] == "mgr-created-0001")
    assert changed["center"][0] == 1.25
    assert changed["size"][1] == 19.0
    second = apply_world_edits(source, root / "blender-edits.json", root / "roundtrip-world")
    assert second["buildings"] == 5
    print(json.dumps({"status": "PASS", "real_blender": True, "editable_buildings": 5,
                      "roundtrip_into_new_glb": "PASS", "modified_building_x": 1.25,
                      "modified_building_height": 19.0,
                      "output_folder": str(root), "receipt": receipt}, indent=2))


if __name__ == "__main__":
    main()
