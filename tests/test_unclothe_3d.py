"""Unclothe 3D must never extract or fabricate assets before owner approval."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

from forge.unclothe_3d import extract_approved_parts, inspect_unclothe, materialize_unclothe_proxies


class UnclotheTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        Image.new("RGB", (128, 128), (120, 50, 40)).save(self.root / "source.png")
        mask = Image.new("L", (128, 128), 0)
        for x in range(20, 90):
            for y in range(15, 110):
                mask.putpixel((x, y), 255)
        mask.save(self.root / "mask.png")
        self.spec = self.root / "proposal.json"
        self.part = {"id": "hair_1", "kind": "hair", "mask": "mask.png", "decision": "approved"}

    def write(self, parts=None, source="source.png", schema="mgr.forge.unclothe.v1"):
        self.spec.write_text(json.dumps({"schema": schema, "source": source,
                                         "parts": [self.part] if parts is None else parts}))

    def test_review_and_real_extraction(self):
        self.write()
        self.assertTrue(inspect_unclothe(self.spec)["ready_to_extract"])
        result = extract_approved_parts(self.spec, self.root / "output")
        self.assertEqual(result["part_count"], 1)
        self.assertFalse(result["image_to_3d_ran"])
        self.assertEqual(result["parts"][0]["visible_pixel_bbox_xyxy"], [20, 15, 90, 110])
        with Image.open(self.root / "output" / "hair_1.png") as image:
            self.assertEqual(image.size, (70, 95))
            self.assertEqual(image.mode, "RGBA")

    def test_pending_blocks_everything(self):
        self.write([{**self.part, "decision": "pending"}])
        with self.assertRaisesRegex(ValueError, "every part"):
            extract_approved_parts(self.spec, self.root / "output")
        self.assertFalse((self.root / "output").exists())

    def test_rejected_only_blocks(self):
        self.write([{**self.part, "decision": "rejected"}])
        with self.assertRaises(ValueError):
            extract_approved_parts(self.spec, self.root / "output")

    def test_rejected_part_excluded(self):
        self.write([self.part, {"id": "boot_1", "kind": "boots", "mask": "mask.png",
                                "decision": "rejected"}])
        result = extract_approved_parts(self.spec, self.root / "output")
        self.assertEqual(result["part_count"], 1)
        self.assertFalse((self.root / "output" / "boot_1.png").exists())

    def test_duplicate_part_blocked(self):
        self.write([self.part, self.part])
        with self.assertRaisesRegex(ValueError, "repeated"):
            inspect_unclothe(self.spec)

    def test_traversal_blocked(self):
        self.write(source="../source.png")
        with self.assertRaisesRegex(ValueError, "basename"):
            inspect_unclothe(self.spec)

    def test_no_overwrite(self):
        self.write()
        extract_approved_parts(self.spec, self.root / "output")
        with self.assertRaises(FileExistsError):
            extract_approved_parts(self.spec, self.root / "output")

    def test_size_mismatch_blocks_without_output(self):
        Image.new("L", (64, 64), 255).save(self.root / "mask.png")
        self.write()
        with self.assertRaisesRegex(ValueError, "mask must match"):
            extract_approved_parts(self.spec, self.root / "output")
        self.assertFalse((self.root / "output").exists())

    def test_empty_mask_blocks(self):
        Image.new("L", (128, 128), 0).save(self.root / "mask.png")
        self.write()
        with self.assertRaisesRegex(ValueError, "no foreground"):
            extract_approved_parts(self.spec, self.root / "output")

    def test_invalid_kind(self):
        self.write([{**self.part, "kind": "mystery"}])
        with self.assertRaisesRegex(ValueError, "semantic"):
            inspect_unclothe(self.spec)

    def test_invalid_schema(self):
        self.write(schema="other")
        with self.assertRaisesRegex(ValueError, "schema"):
            inspect_unclothe(self.spec)

    def test_separate_real_glb_proxy_after_approval(self):
        self.write()
        extract_approved_parts(self.spec, self.root / "output")
        report = materialize_unclothe_proxies(self.root / "output", self.root / "proxies")
        self.assertEqual(len(report["parts"]), 1)
        self.assertGreater(report["parts"][0]["geometry"]["triangles"], 0)
        self.assertTrue(report["independent_glb_parsing_passed"])
        self.assertFalse(report["photorealistic_3d_reconstruction"])
        self.assertTrue((self.root / "proxies" / "hair_1.glb").is_file())

    def test_proxy_rejects_second_write(self):
        self.write()
        extract_approved_parts(self.spec, self.root / "output")
        materialize_unclothe_proxies(self.root / "output", self.root / "proxies")
        with self.assertRaises(FileExistsError):
            materialize_unclothe_proxies(self.root / "output", self.root / "proxies")

    def test_proxy_rejects_tampered_bounds(self):
        self.write()
        extract_approved_parts(self.spec, self.root / "output")
        manifest = self.root / "output" / "manifest.json"
        payload = json.loads(manifest.read_text())
        payload["parts"][0]["visible_pixel_bbox_xyxy"] = [0, 0, 128, 128]
        manifest.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, "bounds differ"):
            materialize_unclothe_proxies(self.root / "output", self.root / "proxies")

    def test_proxy_invalid_grid(self):
        self.write()
        extract_approved_parts(self.spec, self.root / "output")
        with self.assertRaisesRegex(ValueError, "grid"):
            materialize_unclothe_proxies(self.root / "output", self.root / "proxies", grid=200)

    def test_cli_three_stage_real_files(self):
        self.write()
        root = Path(__file__).resolve().parent.parent
        steps = [
            ["unclothe-review", "--spec", str(self.spec)],
            ["unclothe-extract", "--spec", str(self.spec), "--out", str(self.root / "output")],
            ["unclothe-proxy", "--parts", str(self.root / "output"),
             "--out", str(self.root / "proxies")],
        ]
        for command in steps:
            result = subprocess.run([sys.executable, "-m", "forge.cli", *command],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "proxies" / "hair_1.glb").is_file())


if __name__ == "__main__":
    unittest.main()
