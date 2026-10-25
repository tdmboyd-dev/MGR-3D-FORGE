"""Native Godot source export, exact asset identity and engine-proof separation."""

import json
from pathlib import Path
import tempfile
import unittest

from forge.cli import build, main
from forge.engine_handoff import export_godot_project
from forge.spec import WorldSpec


class EngineHandoffTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.world = self.root / "world"
        build(WorldSpec(seed=15, columns=2, rows=2, buildings=3), self.world)

    def pack(self):
        return export_godot_project(self.world, self.root / "godot")

    def test_source_project_materialized(self):
        report = self.pack()
        self.assertEqual(report["status"], "MATERIALIZED")
        self.assertEqual(report["engine"], "Godot 4")
        self.assertFalse(report["engine_import_verified"])
        for name in report["files"]:
            self.assertTrue((self.root / "godot" / name).is_file())

    def test_binary_asset_preserved_exactly(self):
        self.pack()
        self.assertEqual((self.world / "world.glb").read_bytes(),
                         (self.root / "godot/assets/world.glb").read_bytes())

    def test_manifest_hash_preserved(self):
        result = self.pack()
        manifest = json.loads((self.world / "manifest.json").read_text())
        self.assertEqual(result["source_glb_sha256"], manifest["artifact"]["sha256"])

    def test_collider_count_matches_buildings(self):
        result = self.pack()
        scene = (self.root / "godot/world.tscn").read_text()
        self.assertEqual(scene.count('type="StaticBody3D"'), result["building_colliders"] + 1)
        self.assertEqual(scene.count('type="CollisionShape3D"'), result["building_colliders"] + 1)

    def test_independent_scene_entry_and_light(self):
        self.pack()
        scene = (self.root / "godot/world.tscn").read_text()
        project = (self.root / "godot/project.godot").read_text()
        self.assertIn('run/main_scene="res://world.tscn"', project)
        self.assertIn('res://assets/world.glb', scene)
        self.assertIn('type="Camera3D"', scene)
        self.assertIn('type="DirectionalLight3D"', scene)

    def test_refuse_overwrite(self):
        self.pack()
        with self.assertRaises(FileExistsError):
            self.pack()

    def test_tampered_asset_refused(self):
        path = self.world / "world.glb"
        path.write_bytes(path.read_bytes() + b"garbage")
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.pack()
        self.assertFalse((self.root / "godot").exists())

    def test_bad_source_manifest_refused(self):
        (self.world / "manifest.json").write_text("{}")
        with self.assertRaises(ValueError):
            self.pack()

    def test_duplicate_building_identity_refused(self):
        path = self.world / "manifest.json"
        metadata = json.loads(path.read_text())
        metadata["buildings"].append(dict(metadata["buildings"][0]))
        path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.pack()

    def test_infinite_collision_value_refused(self):
        path = self.world / "manifest.json"
        metadata = json.loads(path.read_text())
        metadata["buildings"][0]["size"][0] = float("inf")
        path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, "bounds"):
            self.pack()

    def test_cli_writes_project(self):
        result = main(["godot-handoff", "--world", str(self.world), "--out", str(self.root / "godot")])
        self.assertEqual(result, 0)
        self.assertTrue((self.root / "godot/world.tscn").exists())


if __name__ == "__main__":
    unittest.main()
