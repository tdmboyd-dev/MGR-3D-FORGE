"""Readiness gates distinguish existing mesh data from semantic/pose proof."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge.character import build_mannequin
from forge.character_readiness import inventory_character, write_character_readiness
from forge.cli import main


class CharacterReadinessTests(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.root = Path(holder.name)
        build_mannequin(self.root / "asset")
        self.source = self.root / "asset" / "mannequin.glb"

    def test_real_model_is_not_claimed_rigged(self):
        info = inventory_character(self.source)
        self.assertEqual(info["rig_structure"], "NOT_READY")
        self.assertEqual(info["skins"], 0)
        self.assertFalse(info["owner_approved_identity"])
        self.assertFalse(info["hands_anatomically_verified"])

    def test_mesh_parts_are_measured(self):
        info = inventory_character(self.source)
        self.assertEqual(len(info["parts"]), info["geometry"]["meshes"])
        self.assertGreater(sum(p["vertices"] for part in info["parts"] for p in part["primitives"]), 0)

    def test_cli_writes_new_receipt(self):
        target = self.root / "report.json"
        self.assertEqual(main(["character-readiness", "--source", str(self.source), "--out", str(target)]), 0)
        self.assertEqual(json.loads(target.read_text())["rig_structure"], "NOT_READY")
        with self.assertRaises(ValueError):
            write_character_readiness(self.source, target)

    def test_invalid_source_refused(self):
        with self.assertRaises(ValueError):
            inventory_character(self.root / "missing.glb")

    def test_nonglb_refused(self):
        with self.assertRaises(ValueError):
            inventory_character(self.root / "thing.json")

    def test_invalid_output_type_refused(self):
        with self.assertRaises(ValueError):
            write_character_readiness(self.source, self.root / "bad.txt")

    def test_skin_must_be_bound(self):
        from forge.character_glb import parse_character_glb
        doc, geo = parse_character_glb(self.source.read_bytes())
        doc["skins"] = [{"joints": [0]}]
        with patch("forge.character_readiness.parse_character_glb", return_value=(doc, geo)):
            info = inventory_character(self.source)
        self.assertTrue(any("not bound" in s for s in info["rig_issues"]))

    def test_mismatched_skin_accessor_not_ready(self):
        from forge.character_glb import parse_character_glb
        doc, geo = parse_character_glb(self.source.read_bytes())
        doc["skins"] = [{"joints": [0], "inverseBindMatrices": 0}]
        doc.setdefault("nodes", []).append({"mesh": 0, "skin": 0})
        with patch("forge.character_readiness.parse_character_glb", return_value=(doc, geo)):
            info = inventory_character(self.source)
        self.assertIn("inverse-bind matrices mismatch", " ".join(info["rig_issues"]))

    def test_semantic_labels_never_auto_approved(self):
        info = inventory_character(self.source)
        self.assertFalse(info["garments_semantically_verified"])
        self.assertFalse(info["hair_semantically_verified"])
        self.assertFalse(info["pose_deformation_verified"])


if __name__ == "__main__":
    unittest.main()
