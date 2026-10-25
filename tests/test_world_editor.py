"""End-to-end proofs for persistent, materialized editable world creation."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from forge.cli import build, main
from forge.glb import inspect_glb
from forge.receipt import verify_bundle
from forge.spec import WorldSpec
from forge.world_editor import apply_world_edits


class WorldEditorRoundtripTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.world = self.root / "original"
        build(WorldSpec(seed=8964, columns=3, rows=3, buildings=4), self.world)
        self.manifest = json.loads((self.world / "manifest.json").read_text())
        self.original_hash = hashlib.sha256((self.world / "world.glb").read_bytes()).hexdigest()
        self.edits = {"schema": "mgr.forge.world-edit.v1", "asset_sha256": self.original_hash,
                      "buildings": [{k: copy.deepcopy(b[k]) for k in ("id", "center", "size", "material")}
                                    for b in self.manifest["buildings"]]}
        self.edits["buildings"][0]["center"][0] += 1.25
        self.edits["buildings"][0]["size"][1] = 31.5
        self.edits["buildings"][0]["material"] = "building-emerald"
        self.edits["buildings"][1]["material"] = "building-gold"
        self.edits_path = self.root / "edits.json"
        self.write_edits()

    def write_edits(self):
        self.edits_path.write_text(json.dumps(self.edits), encoding="utf-8")

    def test_browser_edits_materialize_into_real_exported_assets(self):
        output = self.root / "edited"
        report = apply_world_edits(self.world, self.edits_path, output)
        self.assertEqual(report["status"], "MATERIALIZED")
        self.assertEqual(report["changed_buildings"], 2)
        self.assertEqual(verify_bundle(output)["files"], 4)
        self.assertTrue((output / "world-editor.html").exists())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["buildings"][0]["size"][1], 31.5)
        self.assertEqual(manifest["buildings"][0]["material"], "building-emerald")
        self.assertIn("newmtl building-gold", (output / "world.mtl").read_text())
        self.assertIn("#32846b", (output / "preview.svg").read_text())
        self.assertEqual(manifest["triangle_count"], inspect_glb((output / "world.glb").read_bytes())["triangles"])
        self.assertEqual(self.original_hash, hashlib.sha256((self.world / "world.glb").read_bytes()).hexdigest())

    def test_cli_and_deterministic_repeated_exports(self):
        a, b = self.root / "edited-a", self.root / "edited-b"
        self.assertEqual(main(["apply-world-edits", "--world", str(self.world), "--edits", str(self.edits_path), "--out", str(a)]), 0)
        apply_world_edits(self.world, self.edits_path, b)
        self.assertEqual((a / "world.glb").read_bytes(), (b / "world.glb").read_bytes())
        with self.assertRaises(FileExistsError):
            apply_world_edits(self.world, self.edits_path, a)

    def test_bad_sha_rejected_before_output_created(self):
        self.edits["asset_sha256"] = "0" * 64
        self.write_edits()
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            apply_world_edits(self.world, self.edits_path, self.root / "bad")
        self.assertFalse((self.root / "bad").exists())

    def test_bad_identity_rejected(self):
        self.edits["buildings"][0]["id"] = "imposter"
        self.write_edits()
        with self.assertRaises(ValueError):
            apply_world_edits(self.world, self.edits_path, self.root / "bad")

    def test_invalid_height_rejected(self):
        self.edits["buildings"][0]["size"][1] = -10
        self.write_edits()
        with self.assertRaises(ValueError):
            apply_world_edits(self.world, self.edits_path, self.root / "bad")

    def test_tampered_source_glb_rejected(self):
        with (self.world / "world.glb").open("ab") as handle:
            handle.write(b"tampered")
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            apply_world_edits(self.world, self.edits_path, self.root / "bad")

    def test_oversized_json_rejected(self):
        self.edits_path.write_text(" " * 1_000_001, encoding="utf-8")
        with self.assertRaises(ValueError):
            apply_world_edits(self.world, self.edits_path, self.root / "bad")

    def test_native_created_building_exports_true_new_geometry(self):
        self.edits["buildings"].append({"id": "mgr-created-0001", "center": [0, 0, 0],
                                         "size": [8, 16, 8], "material": "building-gold"})
        self.write_edits()
        report = apply_world_edits(self.world, self.edits_path, self.root / "created")
        self.assertEqual(report["buildings"], 5)
        self.assertEqual(report["changed_buildings"], 3)
        self.assertEqual(report["triangles"], 228)
        self.assertEqual(verify_bundle(self.root / "created")["passed"], True)

    def test_native_deleted_building_updates_true_geometry(self):
        self.edits["buildings"] = self.edits["buildings"][1:]
        self.write_edits()
        report = apply_world_edits(self.world, self.edits_path, self.root / "removed")
        self.assertEqual(report["buildings"], 3)
        self.assertEqual(report["changed_buildings"], 2)
        self.assertEqual(report["triangles"], 180)

    def test_native_resized_building_materializes_true_dimensions(self):
        self.edits["buildings"][0]["size"][0] = 19
        self.edits["buildings"][0]["size"][2] = 17
        self.write_edits()
        output = self.root / "resized"
        apply_world_edits(self.world, self.edits_path, output)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["buildings"][0]["size"], [19, 31.5, 17])

    def test_duplicate_or_unauthorized_created_identity_fails(self):
        self.edits["buildings"].append(copy.deepcopy(self.edits["buildings"][0]))
        self.write_edits()
        with self.assertRaises(ValueError):
            apply_world_edits(self.world, self.edits_path, self.root / "bad-duplicate")
        self.edits["buildings"][-1]["id"] = "unsafe@name"
        self.write_edits()
        with self.assertRaises(ValueError):
            apply_world_edits(self.world, self.edits_path, self.root / "bad-id")


if __name__ == "__main__":
    unittest.main()
