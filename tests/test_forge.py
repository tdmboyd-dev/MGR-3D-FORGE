import json
import struct
import tempfile
import unittest
from pathlib import Path

from forge.cli import build
from forge.geometry import create_neighborhood
from forge.geometry import Mesh
from forge.glb import export_glb, inspect_glb
from forge.quality import validate_character_landmarks, validate_neighborhood
from forge.spec import WorldSpec
from forge.planner import plan_neighborhood
from forge.assets import AssetRegistry
from forge.quality import compare_character_identity


class ForgeTests(unittest.TestCase):
    def test_spec_rejects_excess_count(self):
        with self.assertRaises(ValueError):
            WorldSpec(rows=2, columns=2, buildings=5)

    def test_spec_rejects_extra_json_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text('{"rows": 4, "evil": true}')
            with self.assertRaises(ValueError):
                WorldSpec.from_json(path)

    def test_seed_deterministic(self):
        spec = WorldSpec()
        meshes1, world1 = create_neighborhood(spec)
        meshes2, world2 = create_neighborhood(spec)
        self.assertEqual(world1, world2)
        self.assertEqual(export_glb(meshes1), export_glb(meshes2))

    def test_new_seed_changes_geometry(self):
        first = create_neighborhood(WorldSpec(seed=8964))[1]
        second = create_neighborhood(WorldSpec(seed=8965))[1]
        self.assertNotEqual(first["buildings"], second["buildings"])

    def test_world_qa(self):
        _, scene = create_neighborhood(WorldSpec())
        self.assertTrue(validate_neighborhood(scene)["passed"])
        self.assertEqual(len(scene["buildings"]), 10)

    def test_large_world_no_missing_lots(self):
        _, scene = create_neighborhood(WorldSpec(columns=40, rows=25, buildings=1000))
        self.assertTrue(validate_neighborhood(scene)["passed"])
        self.assertEqual(len({tuple(b["lot"]) for b in scene["buildings"]}), 1000)

    def test_glb_export_roundtrip(self):
        meshes, scene = create_neighborhood(WorldSpec())
        result = inspect_glb(export_glb(meshes))
        self.assertTrue(result["valid"])
        self.assertEqual(result["triangles"], scene["triangle_count"])
        self.assertEqual(result["vertices"], scene["vertex_count"])

    def test_glb_rejects_corrupt_index(self):
        meshes, _ = create_neighborhood(WorldSpec())
        data = bytearray(export_glb(meshes))
        data[0:4] = b"BADD"
        with self.assertRaises(ValueError):
            inspect_glb(data)

    def test_glb_rejects_short_chunk(self):
        meshes, _ = create_neighborhood(WorldSpec())
        data = export_glb(meshes)[:-4]
        with self.assertRaises(ValueError):
            inspect_glb(data)

    def test_box_face_normals_point_outward(self):
        mesh = Mesh()
        mesh.box(0, 0, 0, 2, 3, 4)
        centers = []
        for index in range(0, len(mesh.positions), 12):
            x = sum(mesh.positions[index + j] for j in (0,3,6,9)) / 4
            y = sum(mesh.positions[index + j] for j in (1,4,7,10)) / 4
            z = sum(mesh.positions[index + j] for j in (2,5,8,11)) / 4
            centers.append((x, y - 1.5, z))
        for i, vector in enumerate(centers):
            normal = mesh.normals[i * 12:i * 12 + 3]
            self.assertGreater(sum(a * b for a, b in zip(normal, vector)), 0)

    def test_build_manifest_and_file(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = build(WorldSpec(), Path(temp))
            self.assertTrue((Path(temp) / "world.glb").is_file())
            self.assertEqual(manifest["execution"]["external_api_calls"], 0)
            self.assertFalse(manifest["execution"]["blender_verified"])
            saved = json.loads((Path(temp) / "manifest.json").read_text())
            self.assertEqual(saved["artifact"], manifest["artifact"])

    def test_character_missing_hand(self):
        landmarks = {name: [0, i, 0] for i, name in enumerate((
            "head", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hand", "right_hand", "left_hip",
            "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"))}
        del landmarks["right_hand"]
        result = validate_character_landmarks(landmarks)
        self.assertFalse(result["passed"])
        self.assertIn("missing or invalid right_hand", result["errors"])

    def test_bounded_prompt_planner(self):
        plan = plan_neighborhood("Build 37 houses in a futuristic neighborhood")
        self.assertEqual(plan.spec.buildings, 37)
        self.assertEqual(plan.external_cost_usd, 0)
        self.assertEqual(plan.method, "cpu-procedural")

    def test_planner_refuses_unbounded_request(self):
        with self.assertRaises(ValueError):
            plan_neighborhood("1001 buildings")

    def test_asset_registry_deduplicates_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            store = AssetRegistry(Path(temp))
            first = store.add(b"mesh-contents", owner="MGR", license_id="MGR-native")
            second = store.add(b"mesh-contents", owner="MGR", license_id="MGR-native")
            self.assertEqual(first, second)
            contents, _ = store.get(first["sha256"])
            self.assertEqual(contents, b"mesh-contents")
            (Path(temp) / first["relative_path"]).write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                store.get(first["sha256"])

    def test_asset_provenance_required(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                AssetRegistry(Path(temp)).add(b"asset", owner="", license_id="MIT")

    def test_character_identity_proportion_drift(self):
        points = {
            "head": [0, 2.1, 0],
            "left_shoulder": [-0.5, 1.8, 0], "right_shoulder": [0.5, 1.8, 0],
            "left_elbow": [-0.9, 1.35, 0], "right_elbow": [0.9, 1.35, 0],
            "left_wrist": [-1.1, 0.9, 0], "right_wrist": [1.1, 0.9, 0],
            "left_hand": [-1.2, 0.8, 0], "right_hand": [1.2, 0.8, 0],
            "left_hip": [-0.3, 1.0, 0], "right_hip": [0.3, 1.0, 0],
            "left_knee": [-0.3, 0.55, 0], "right_knee": [0.3, 0.55, 0],
            "left_ankle": [-0.3, 0.1, 0], "right_ankle": [0.3, 0.1, 0],
        }
        self.assertTrue(compare_character_identity(points, points)["passed"])
        changed = {k: list(v) for k, v in points.items()}
        changed["left_wrist"][0] += 3
        self.assertFalse(compare_character_identity(points, changed)["passed"])


if __name__ == "__main__":
    unittest.main()
