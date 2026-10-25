"""Whole-character image batches must preserve every asset and report missing views."""

import json
from pathlib import Path
import struct
import tempfile
import unittest

from forge.reference_pack import prepare_reference_pack


class ReferencePackTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.reference = self.root / "body.png"
        self.reference.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR"
                                   + struct.pack(">II", 512, 768) + b"\x08\x06\0\0\0" + b"\0\0\0\0")
        self.spec = self.root / "set.json"

    def pack(self, images, approval="pending"):
        self.spec.write_text(json.dumps({"schema": "mgr.forge.reference-input.v1",
                                         "character": "Private test", "owner_approval": approval,
                                         "images": images}))
        return prepare_reference_pack(self.spec, self.root / "out.json")

    def test_one_view_is_not_full_character(self):
        report = self.pack([{"file": "body.png", "asset": "body", "view": "front"}])
        self.assertEqual(report["asset_jobs"][0]["status"], "NEEDS_MORE_VIEWS")
        self.assertFalse(report["model_generation_performed"])

    def test_sha_and_dimensions_recorded(self):
        image = self.pack([{"file": "body.png", "asset": "body", "view": "front"}])["asset_jobs"][0]["reference_images"][0]
        self.assertEqual(image["width"], 512)
        self.assertEqual(len(image["sha256"]), 64)

    def test_sheet_is_not_four_verified_views(self):
        report = self.pack([{"file": "body.png", "asset": "hair", "view": "sheet"}])
        self.assertEqual(report["asset_jobs"][0]["status"], "NEEDS_VIEW_EXTRACTION")

    def test_duplicate_view_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.pack([{"file": "body.png", "asset": "body", "view": "front"}] * 2)

    def test_parent_escape_refused(self):
        with self.assertRaisesRegex(ValueError, "basename"):
            self.pack([{"file": "../body.png", "asset": "body", "view": "front"}])

    def test_no_overwrite(self):
        entries = [{"file": "body.png", "asset": "body", "view": "front"}]
        self.pack(entries)
        with self.assertRaises(ValueError):
            self.pack(entries)

    def test_unknown_asset_refused(self):
        with self.assertRaises(ValueError):
            self.pack([{"file": "body.png", "asset": "unknown", "view": "front"}])

    def test_owner_approval_is_distinct_from_technical_verification(self):
        report = self.pack([{"file": "body.png", "asset": "face", "view": "sheet"}], "owner_approved")
        self.assertEqual(report["owner_approval"], "owner_approved")
        self.assertFalse(report["global_identity_consistency_verified"])
        self.assertFalse(report["model_generation_performed"])
        self.assertEqual(report["asset_jobs"][0]["status"], "NEEDS_VIEW_EXTRACTION")

    def test_unrecognized_approval_refused(self):
        with self.assertRaisesRegex(ValueError, "owner approval"):
            self.pack([{"file": "body.png", "asset": "feet", "view": "sheet"}], "verified")


if __name__ == "__main__":
    unittest.main()
