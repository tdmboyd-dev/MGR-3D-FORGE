"""Multi-view silhouette carving: real measured geometry, honest limits, CLI gate."""

import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

from forge.glb import inspect_glb
from forge.multiview import (EVIDENCE_LEVEL, LIMITATIONS, MAX_FACES, MAX_GRID,
                             SCORE_EVIDENCE, SCORE_SCHEMA, SCHEMA,
                             export_reconstruction, reconstruct, score_against_solid)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def mask_png(rows):
    """Encode a 0/255 grayscale silhouette mask from boolean rows."""
    height, width = len(rows), len(rows[0])
    packed = bytearray()
    for row in rows:
        packed.append(0)
        packed.extend(255 if value else 0 for value in row)
    return (PNG_MAGIC + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(bytes(packed))) + _chunk(b"IEND", b""))


def square_grid(size, low, high):
    """Boolean square mask covering [low, high) on both axes of a size x size grid."""
    return [[low <= x < high and low <= y < high for x in range(size)] for y in range(size)]


def rect_grid(size, left, right, top, bottom):
    """Boolean rectangle mask covering [left, right) x [top, bottom) of the grid."""
    return [[left <= x < right and top <= y < bottom for x in range(size)] for y in range(size)]


def cross_grid(size, torso, arms):
    torso_low, torso_high = torso
    arm_low, arm_high = arms
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            inside = torso_low <= x < torso_high and torso_low <= y < size - torso_low
            if arm_low <= y < arm_high and torso_low - 4 <= x < torso_high + 4:
                inside = True
            row.append(inside)
        rows.append(row)
    return rows


class MultiViewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.size = 16
        self.cube_views = ["front", "back", "left", "right"]
        for axis in self.cube_views:
            (self.root / f"{axis}.png").write_bytes(mask_png(square_grid(self.size, 4, 12)))

    def spec(self, axes=None, bounds=(2.0, 2.0, 2.0), grid=16, **overrides):
        payload = {
            "base_dir": str(self.root),
            "bounds": {"width": bounds[0], "height": bounds[1], "depth": bounds[2]},
            "grid": grid,
            "views": [{"axis": axis, "mask": f"{axis}.png"} for axis in (axes or self.cube_views)],
        }
        payload.update(overrides)
        return payload

    def write_spec(self, name, payload):
        path = self.root / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_cube_phantom_recovers_measured_bounds_and_volume(self):
        mesh, manifest = reconstruct(self.spec())
        self.assertEqual(manifest["status"], "MATERIALIZED")
        self.assertEqual(manifest["evidence_level"], EVIDENCE_LEVEL)
        self.assertEqual(manifest["schema"], SCHEMA)
        self.assertEqual(manifest["bbox_min_m"], [-0.5, 0.5, -0.5])
        self.assertEqual(manifest["bbox_max_m"], [0.5, 1.5, 0.5])
        self.assertAlmostEqual(manifest["volume_m3"], 1.0, places=6)
        self.assertEqual(manifest["occupied_voxels"], 8 * 8 * 8)
        self.assertGreater(len(mesh.indices) // 3, 0)
        self.assertEqual(manifest["triangles"], len(mesh.indices) // 3)

    def test_every_supplied_silhouette_is_reproduced(self):
        _mesh, manifest = reconstruct(self.spec())
        self.assertEqual(manifest["fit"]["status"], "PASS")
        for view in manifest["views"]:
            self.assertEqual(view["hull_shadow_iou"], 1.0, view["axis"])
            self.assertGreater(view["mask_coverage"], 0.0)

    def test_humanoid_phantom_uses_depth_view_to_limit_thickness(self):
        size = 16
        (self.root / "front.png").write_bytes(mask_png(cross_grid(size, (6, 10), (7, 10))))
        (self.root / "left.png").write_bytes(mask_png(square_grid(size, 6, 10)))
        _mesh, manifest = reconstruct(self.spec(axes=["front", "left"]))
        width = manifest["bbox_max_m"][0] - manifest["bbox_min_m"][0]
        depth = manifest["bbox_max_m"][2] - manifest["bbox_min_m"][2]
        height = manifest["bbox_max_m"][1] - manifest["bbox_min_m"][1]
        self.assertGreater(width, depth)
        self.assertAlmostEqual(depth, 0.5, places=6)
        self.assertAlmostEqual(width, 12 * (2.0 / size), places=6)
        self.assertGreater(height, 0.4)
        self.assertEqual(manifest["view_axes"], ["front", "left"])

    def test_carving_removes_volume_the_second_view_forbids(self):
        """A wide front silhouette plus a thin side silhouette must stay thin."""
        wide_rows = [[4 <= y < 12 for _x in range(16)] for y in range(16)]
        (self.root / "front_wide.png").write_bytes(mask_png(wide_rows))
        (self.root / "left_thin.png").write_bytes(mask_png(rect_grid(16, 6, 10, 4, 12)))
        (self.root / "left_wide.png").write_bytes(
            mask_png([[4 <= y < 12 for _x in range(16)] for y in range(16)]))
        wide = self.spec(axes=["front", "left"])
        wide["views"][0]["mask"] = "front_wide.png"
        wide["views"][1]["mask"] = "left_wide.png"
        _mesh, full = reconstruct(wide)
        thin = self.spec(axes=["front", "left"])
        thin["views"][0]["mask"] = "front_wide.png"
        thin["views"][1]["mask"] = "left_thin.png"
        _mesh, carved = reconstruct(thin)
        self.assertAlmostEqual(full["volume_m3"], 4.0, places=6)
        self.assertAlmostEqual(carved["volume_m3"], 1.0, places=6)
        self.assertLess(carved["volume_m3"], full["volume_m3"] / 3)

    def test_back_and_right_masks_are_mirrored_before_carving(self):
        """A back camera sees the mirrored image, so an offset bump survives carving."""
        rows = [[False] * 16 for _ in range(16)]
        for y in range(4, 12):
            for x in range(4, 12):
                rows[y][x] = True
            rows[y][2] = rows[y][3] = True  # world -X bump
        (self.root / "front.png").write_bytes(mask_png(rows))
        (self.root / "back.png").write_bytes(
            mask_png([list(reversed(row)) for row in rows]))
        (self.root / "left.png").write_bytes(mask_png(square_grid(16, 4, 12)))
        payload = self.spec(axes=["front", "back", "left"])
        _mesh, manifest = reconstruct(payload)
        width = manifest["bbox_max_m"][0] - manifest["bbox_min_m"][0]
        self.assertAlmostEqual(width, 10 * (2.0 / 16), places=6)
        self.assertEqual([view["hull_shadow_iou"] for view in manifest["views"]],
                         [1.0, 1.0, 1.0])
        self.assertEqual(manifest["mirrored_axes"], ["back", "right"])
        wrong = self.spec(axes=["front", "back", "left"])
        (self.root / "back.png").write_bytes(mask_png(rows))
        with self.assertRaisesRegex(ValueError, "does not reproduce the measured silhouettes"):
            reconstruct(wrong)

    def test_hull_never_invents_unseen_detail(self):
        _mesh, manifest = reconstruct(self.spec())
        self.assertFalse(manifest["hidden_surface_inference"])
        self.assertFalse(manifest["identity_verified"])
        self.assertEqual(manifest["external_api_calls"], 0)
        self.assertEqual(manifest["method"], "orthographic-silhouette-space-carving")
        self.assertTrue(manifest["limitations"])
        self.assertEqual(list(manifest["limitations"]), list(LIMITATIONS))
        self.assertTrue(any("concave" in item for item in manifest["limitations"]))

    def test_identical_silhouettes_give_identical_hull(self):
        """Two different subjects with the same silhouette set are indistinguishable."""
        first = reconstruct(self.spec())[1]
        second = reconstruct(self.spec())[1]
        self.assertEqual(first["volume_m3"], second["volume_m3"])
        self.assertEqual(first["triangles"], second["triangles"])
        self.assertEqual([v["hull_shadow_iou"] for v in first["views"]],
                         [v["hull_shadow_iou"] for v in second["views"]])

    def test_two_view_minimum_is_enforced(self):
        with self.assertRaisesRegex(ValueError, "front or back silhouette required"):
            reconstruct(self.spec(axes=["left", "right"]))
        with self.assertRaisesRegex(ValueError, "left or right silhouette required"):
            reconstruct(self.spec(axes=["front", "back"]))

    def test_duplicate_and_unknown_axes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate silhouette axis"):
            reconstruct(self.spec(axes=["front", "front"]))
        payload = self.spec()
        payload["views"][0]["axis"] = "diagonal"
        with self.assertRaisesRegex(ValueError, "unknown silhouette axis"):
            reconstruct(payload)

    def test_grid_and_bounds_are_bounded(self):
        for grid in (4, MAX_GRID + 1, "48", 48.0, None):
            with self.assertRaisesRegex(ValueError, "grid must be an integer"):
                reconstruct(self.spec(grid=grid))
        with self.assertRaisesRegex(ValueError, "invalid bounds.width"):
            reconstruct(self.spec(bounds=(0.0, 2.0, 2.0)))
        with self.assertRaisesRegex(ValueError, "bounds object required"):
            reconstruct({"grid": 16, "views": self.spec()["views"]})
        payload = self.spec()
        payload["bounds"]["depth"] = float("inf")
        with self.assertRaisesRegex(ValueError, "invalid bounds.depth"):
            reconstruct(payload)

    def test_opposing_views_must_agree_on_scale(self):
        (self.root / "back_big.png").write_bytes(mask_png(square_grid(16, 0, 16)))
        payload = self.spec()
        payload["views"][1]["mask"] = "back_big.png"
        with self.assertRaisesRegex(ValueError, "disagree on subject scale"):
            reconstruct(payload)

    def test_views_must_agree_on_image_size_and_height(self):
        (self.root / "back_wide.png").write_bytes(mask_png(square_grid(8, 2, 6)))
        payload = self.spec()
        payload["views"][1]["mask"] = "back_wide.png"
        with self.assertRaisesRegex(ValueError, "disagree on image size"):
            reconstruct(payload)
        (self.root / "left_tall.png").write_bytes(
            mask_png([[True] * 16 for _ in range(32)]))
        tall = self.spec(axes=["front", "left"])
        tall["views"][1]["mask"] = "left_tall.png"
        with self.assertRaisesRegex(ValueError, "disagree on subject height"):
            reconstruct(tall)

    def test_empty_and_missing_masks_are_rejected(self):
        (self.root / "blank.png").write_bytes(mask_png(square_grid(16, 0, 0)))
        payload = self.spec()
        payload["views"][2]["mask"] = "blank.png"
        with self.assertRaisesRegex(ValueError, "silhouette mask is empty"):
            reconstruct(payload)
        missing = self.spec()
        missing["views"][2]["mask"] = "absent.png"
        with self.assertRaisesRegex(ValueError, "missing silhouette mask"):
            reconstruct(missing)

    def test_invalid_threshold_and_oversized_spec_are_rejected(self):
        payload = self.spec()
        payload["views"][0]["threshold"] = 0
        with self.assertRaisesRegex(ValueError, "mask threshold must be an integer"):
            reconstruct(payload)
        payload = self.spec()
        payload["views"][0]["threshold"] = True
        with self.assertRaisesRegex(ValueError, "mask threshold must be an integer"):
            reconstruct(payload)

    def test_face_budget_cannot_be_hit_by_a_legal_solid_grid(self):
        """A solid at maximum legal grid stays well under the face cap."""
        self.assertGreater(MAX_FACES, 6 * MAX_GRID * MAX_GRID)

    def test_export_writes_verifiable_glb_obj_and_manifest(self):
        spec_path = self.write_spec("spec.json", self.spec())
        result = export_reconstruction(spec_path, self.root / "hull")
        self.assertTrue((self.root / "hull" / "hull.glb").is_file())
        self.assertTrue((self.root / "hull" / "hull.obj").is_file())
        self.assertTrue((self.root / "hull" / "hull.mtl").is_file())
        glb = (self.root / "hull" / "hull.glb").read_bytes()
        self.assertTrue(inspect_glb(glb)["valid"])
        self.assertEqual(result["manifest"]["glb"]["sha256"], hashlib.sha256(glb).hexdigest())
        self.assertEqual(result["manifest"]["glb"]["bytes"], len(glb))
        self.assertTrue(result["manifest"]["internally_consistent"])
        written = json.loads((self.root / "hull" / "reconstruction.json").read_text(encoding="utf-8"))
        self.assertEqual(written["schema"], SCHEMA)
        self.assertEqual(written["triangles"], result["manifest"]["triangles"])
        with self.assertRaises(FileExistsError):
            export_reconstruction(spec_path, self.root / "hull")

    def test_export_is_byte_deterministic(self):
        spec_path = self.write_spec("spec.json", self.spec())
        first = export_reconstruction(spec_path, self.root / "a")
        second = export_reconstruction(spec_path, self.root / "b")
        self.assertEqual(first["glb_path"].read_bytes(), second["glb_path"].read_bytes())
        self.assertEqual(first["manifest_path"].read_text(encoding="utf-8"),
                         second["manifest_path"].read_text(encoding="utf-8"))

    def test_spec_paths_are_relative_to_the_spec_directory(self):
        nested = self.root / "reference"
        nested.mkdir()
        (nested / "front.png").write_bytes(mask_png(square_grid(16, 4, 12)))
        (nested / "left.png").write_bytes(mask_png(square_grid(16, 4, 12)))
        spec_path = nested / "spec.json"
        relative = self.spec(axes=["front", "left"])
        relative.pop("base_dir")
        spec_path.write_text(json.dumps(relative), encoding="utf-8")
        result = export_reconstruction(spec_path, self.root / "nested_hull")
        self.assertEqual(result["manifest"]["fit"]["status"], "PASS")
        self.assertEqual([view["mask"] for view in result["manifest"]["views"]],
                         ["front.png", "left.png"])

    def test_missing_spec_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing reconstruction spec"):
            export_reconstruction(self.root / "absent.json", self.root / "out")

    def test_score_against_matching_solid_is_exact(self):
        score = score_against_solid(self.spec(), [{"min": [-0.5, 0.5, -0.5],
                                                   "max": [0.5, 1.5, 0.5]}])
        self.assertEqual(score["schema"], SCORE_SCHEMA)
        self.assertEqual(score["evidence_level"], SCORE_EVIDENCE)
        self.assertAlmostEqual(score["hull_vs_solid_iou"], 1.0, places=6)
        self.assertAlmostEqual(score["solid_volume_m3"], 1.0, places=9)
        self.assertAlmostEqual(score["hull_volume_m3"], 1.0, places=9)
        self.assertEqual(score["overfill_voxels"], 0)
        self.assertEqual(score["missed_voxels"], 0)
        self.assertFalse(score["silhouettes_prove_identity"])

    def test_score_exposes_overfill_where_two_views_cannot_disagree(self):
        """Half the row is thick, half is thin: no silhouette can separate them."""
        (self.root / "front.png").write_bytes(mask_png(rect_grid(16, 0, 16, 4, 12)))
        (self.root / "left.png").write_bytes(mask_png(rect_grid(16, 4, 12, 4, 12)))
        boxes = [{"min": [-1.0, 0.5, -0.5], "max": [0.0, 1.5, 0.5]},
                 {"min": [0.0, 0.5, -0.125], "max": [1.0, 1.5, 0.125]}]
        score = score_against_solid(self.spec(axes=["front", "left"]), boxes)
        self.assertAlmostEqual(score["solid_volume_m3"], 1.25, places=9)
        self.assertAlmostEqual(score["hull_volume_m3"], 2.0, places=9)
        self.assertAlmostEqual(score["overfill_volume_m3"], 0.75, places=9)
        self.assertEqual(score["missed_voxels"], 0)
        self.assertAlmostEqual(score["hull_vs_solid_iou"], 0.625, places=6)

    def test_score_rejects_unusable_solids(self):
        spec = self.spec()
        with self.assertRaisesRegex(ValueError, "invalid solid box list"):
            score_against_solid(spec, [])
        with self.assertRaisesRegex(ValueError, "min must be below max"):
            score_against_solid(spec, [{"min": [0.0, 0.5, 0.0], "max": [0.0, 1.5, 0.5]}])
        with self.assertRaisesRegex(ValueError, "outside the reconstruction bounds"):
            score_against_solid(spec, [{"min": [-2.0, 0.5, -0.5], "max": [0.0, 1.5, 0.5]}])
        with self.assertRaisesRegex(ValueError, "3-axis min/max"):
            score_against_solid(spec, [{"min": [-0.5, 0.5], "max": [0.5, 1.5, 0.5]}])
        with self.assertRaisesRegex(ValueError, "coordinate must be finite"):
            score_against_solid(spec, [{"min": [float("nan"), 0.5, -0.5],
                                        "max": [0.5, 1.5, 0.5]}])

    def test_smooth_normals_preserves_triangles_and_dedups_vertices(self):
        from forge.smooth import smooth_normals
        mesh, _manifest = reconstruct(self.spec())
        original_vertices = len(mesh.positions) // 3
        original_triangles = len(mesh.indices) // 3
        smoothed = smooth_normals(mesh)
        self.assertEqual(len(smoothed.indices) // 3, original_triangles)
        self.assertLessEqual(len(smoothed.positions) // 3, original_vertices)
        self.assertEqual(len(smoothed.normals) // 3, len(smoothed.positions) // 3)
        # averaged normals are unit length
        for i in range(0, len(smoothed.normals), 3):
            nx, ny, nz = smoothed.normals[i:i + 3]
            self.assertAlmostEqual((nx * nx + ny * ny + nz * nz) ** 0.5, 1.0, places=6)

    def test_cli_smooth_flag_produces_smoothed_manifest(self):
        spec_path = self.write_spec("spec.json", self.spec())
        out = self.root / "smooth_hull"
        root = Path(__file__).resolve().parent.parent
        result = subprocess.run([sys.executable, "-m", "forge.cli", "reconstruct-silhouette",
                                 "--spec", str(spec_path), "--out", str(out), "--smooth"],
                                cwd=root, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((out / "reconstruction.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["smoothing"], "taubin-averaged-normals")
        self.assertTrue((out / "hull.glb").is_file())

    def test_cli_reconstructs_real_files_end_to_end(self):
        spec_path = self.write_spec("spec.json", self.spec())
        root = Path(__file__).resolve().parent.parent
        out = self.root / "cli_hull"
        result = subprocess.run([sys.executable, "-m", "forge.cli", "reconstruct-silhouette",
                                 "--spec", str(spec_path), "--out", str(out)],
                                cwd=root, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema"], SCHEMA)
        self.assertTrue((out / "hull.glb").is_file())
        self.assertTrue(inspect_glb((out / "hull.glb").read_bytes())["valid"])

    def test_cli_scores_hull_against_truth_file(self):
        spec_path = self.write_spec("spec.json", self.spec())
        truth = self.root / "truth.json"
        truth.write_text(json.dumps({"boxes": [{"min": [-0.5, 0.5, -0.5],
                                                "max": [0.5, 1.5, 0.5]}]}), encoding="utf-8")
        root = Path(__file__).resolve().parent.parent
        out = self.root / "accuracy.json"
        result = subprocess.run([sys.executable, "-m", "forge.cli", "reconstruct-score",
                                 "--spec", str(spec_path), "--truth", str(truth),
                                 "--out", str(out)],
                                cwd=root, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], SCORE_SCHEMA)
        self.assertAlmostEqual(payload["hull_vs_solid_iou"], 1.0, places=6)

    def test_cli_score_refuses_to_overwrite_a_receipt(self):
        spec_path = self.write_spec("spec.json", self.spec())
        truth = self.root / "truth.json"
        truth.write_text(json.dumps({"boxes": [{"min": [-0.5, 0.5, -0.5],
                                                "max": [0.5, 1.5, 0.5]}]}), encoding="utf-8")
        out = self.root / "accuracy.json"
        out.write_text("{}", encoding="utf-8")
        root = Path(__file__).resolve().parent.parent
        result = subprocess.run([sys.executable, "-m", "forge.cli", "reconstruct-score",
                                 "--spec", str(spec_path), "--truth", str(truth),
                                 "--out", str(out)],
                                cwd=root, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)


if __name__ == "__main__":
    unittest.main()
