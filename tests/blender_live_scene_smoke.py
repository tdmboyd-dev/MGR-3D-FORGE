"""Run a complete browser-format edit → GLB → independently editable Blender .blend test."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from forge.cli import build
from forge.live_blender import create_live_blender_scene
from forge.spec import WorldSpec
from forge.world_editor import apply_world_edits


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
    print(json.dumps({"status": "PASS", "real_blender": True, "editable_buildings": 5,
                      "output_folder": str(root), "receipt": receipt}, indent=2))


if __name__ == "__main__":
    main()
