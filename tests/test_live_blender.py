"""Adversarial contract checks before entering Blender's Python interpreter."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge.live_blender import live_blender_command, validate_live_bundle, create_live_blender_scene
from forge.world_editor import apply_world_edits
from forge.cli import build
from forge.spec import WorldSpec


class BlenderLiveSceneTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        source = self.root / "source"
        build(WorldSpec(seed=52, columns=2, rows=2, buildings=2), source)
        manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
        document = {"schema": "mgr.forge.world-edit.v1",
                    "asset_sha256": hashlib.sha256((source / "world.glb").read_bytes()).hexdigest(),
                    "buildings": [{k: b[k] for k in ("id", "center", "size", "material")}
                                  for b in manifest["buildings"]]}
        document["buildings"].append({"id": "mgr-created-0001", "center": [0, 0, 0],
                                      "size": [8, 12, 7], "material": "building-gold"})
        edits = self.root / "edits.json"
        edits.write_text(json.dumps(document), encoding="utf-8")
        self.world = self.root / "edited"
        apply_world_edits(source, edits, self.world)

    def test_validated_real_geometry_is_accepted(self):
        result = validate_live_bundle(self.world)
        self.assertEqual(len(result["buildings"]), 3)
        self.assertIn("mgr-created-0001", [b["id"] for b in result["buildings"]])
        cmd = live_blender_command("blender", self.world, self.root / "out.blend", self.root / "proof.json")
        self.assertEqual(cmd[1:3], ["--background", "--factory-startup"])
        self.assertIn("blender_live_scene.py", cmd[4])
        self.assertNotIn("eval", " ".join(cmd))

    def test_tampered_glb_rejected(self):
        with (self.world / "world.glb").open("ab") as f:
            f.write(b"tamper")
        with self.assertRaisesRegex(ValueError, "hash"):
            validate_live_bundle(self.world)

    def test_non_editor_input_rejected(self):
        manifest = json.loads((self.world / "manifest.json").read_text(encoding="utf-8"))
        manifest.pop("edit_provenance")
        (self.world / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "editable source"):
            validate_live_bundle(self.world)

    def test_blend_and_report_cannot_be_overwritten(self):
        blend = self.root / "out.blend"
        blend.touch()
        with self.assertRaises(FileExistsError):
            live_blender_command("blender", self.world, blend, self.root / "out.json")

    def test_missing_blender_is_not_falsely_verified(self):
        with patch("forge.live_blender.shutil.which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "unavailable"):
                create_live_blender_scene(self.world, self.root / "out.blend", self.root / "out.json")

    def test_blender_false_zero_exit_without_receipt_is_rejected(self):
        class FakeResult:
            returncode = 0
            stdout = "Python: Traceback..."
            stderr = ""

        with patch("forge.live_blender.shutil.which", return_value="blender"), \
             patch("forge.live_blender.subprocess.run", return_value=FakeResult()):
            with self.assertRaisesRegex(RuntimeError, "without a proof receipt"):
                create_live_blender_scene(self.world, self.root / "out.blend", self.root / "out.json")


if __name__ == "__main__":
    unittest.main()
