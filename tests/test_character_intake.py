"""Candidate admission does not confuse geometry with a rig or human identity."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge.character import build_mannequin
from forge.character_intake import admit_candidate, create_character_blend, inspect_candidate, verify_character_blend
from forge.cli import main


class CharacterIntakeTests(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.root = Path(holder.name)
        build_mannequin(self.root / "source")
        self.source = self.root / "source" / "mannequin.glb"

    def test_actual_source_mesh_inspected(self):
        result = inspect_candidate(self.source)
        self.assertGreater(result["geometry"]["triangles"], 0)
        self.assertEqual(result["source_sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_no_phony_likeness_or_rig_claim(self):
        result = inspect_candidate(self.source)
        self.assertFalse(result["identity_verified"])
        self.assertFalse(result["anatomy_verified"])
        self.assertFalse(result["deformation_verified"])
        self.assertEqual(result["skin_count"], 0)
        self.assertIn("No skin/armature", result["warnings"][0])

    def test_bounds_are_finite(self):
        result = inspect_candidate(self.source)
        self.assertIsNotNone(result["bounds_min"])
        self.assertTrue(all(low <= high for low, high in zip(result["bounds_min"], result["bounds_max"])))

    def test_admission_preserves_binary(self):
        result = admit_candidate(self.source, self.root / "intake")
        self.assertEqual((self.root / "intake" / "candidate.glb").read_bytes(), self.source.read_bytes())
        self.assertEqual(json.loads((self.root / "intake" / "candidate.json").read_text())["source_sha256"],
                         result["source_sha256"])

    def test_admission_cannot_overwrite(self):
        admit_candidate(self.source, self.root / "intake")
        with self.assertRaises(FileExistsError):
            admit_candidate(self.source, self.root / "intake")

    def test_wrong_extension_refused(self):
        with self.assertRaises(ValueError):
            inspect_candidate(self.root / "source" / "character.json")

    def test_missing_source_refused(self):
        with self.assertRaises(ValueError):
            inspect_candidate(self.root / "notfound.glb")

    def test_corrupt_glb_refused(self):
        corrupted = self.root / "corrupt.glb"
        corrupted.write_bytes(self.source.read_bytes()[:-11])
        with self.assertRaises(ValueError):
            inspect_candidate(corrupted)

    def test_large_input_refused_before_read(self):
        from forge.character_intake import MAX_CHARACTER_BYTES
        with patch("forge.character_intake.MAX_CHARACTER_BYTES", 20):
            with self.assertRaisesRegex(ValueError, "size"):
                inspect_candidate(self.source)
        self.assertGreater(MAX_CHARACTER_BYTES, 1000)

    def test_modified_admitted_glb_refused_for_blender(self):
        admit_candidate(self.source, self.root / "intake")
        (self.root / "intake" / "candidate.glb").write_bytes(self.source.read_bytes()[:-4])
        with self.assertRaises(ValueError):
            create_character_blend(self.root / "intake", self.root / "scene.blend",
                                   self.root / "report.json", binary="definitely-no-blender")

    def test_blender_unavailable_cannot_fake_project(self):
        admit_candidate(self.source, self.root / "intake")
        with self.assertRaises(RuntimeError):
            create_character_blend(self.root / "intake", self.root / "scene.blend",
                                   self.root / "report.json", binary="definitely-no-blender")

    def test_invalid_output_suffix_refused(self):
        admit_candidate(self.source, self.root / "intake")
        with self.assertRaises(ValueError):
            create_character_blend(self.root / "intake", self.root / "scene.obj",
                                   self.root / "report.json")

    def test_cli_admission(self):
        self.assertEqual(main(["character-intake", "--source", str(self.source),
                               "--out", str(self.root / "intake")]), 0)
        self.assertTrue((self.root / "intake" / "candidate.glb").exists())

    def test_reopen_requires_existing_blend(self):
        with self.assertRaises(ValueError):
            verify_character_blend(self.root / "missing.blend", "a" * 64,
                                   self.root / "reopened.json")

    def test_reopen_rejects_invalid_fingerprint(self):
        file = self.root / "scene.blend"
        file.write_bytes(b"synthetic fixture")
        with self.assertRaises(ValueError):
            verify_character_blend(file, "unknown", self.root / "reopened.json")

    def test_reopen_requires_new_receipt(self):
        file = self.root / "scene.blend"
        file.write_bytes(b"synthetic fixture")
        report = self.root / "reopened.json"
        report.write_text("{}")
        with self.assertRaises(ValueError):
            verify_character_blend(file, "a" * 64, report)

    def test_reopen_requires_native_blender_binary(self):
        file = self.root / "scene.blend"
        file.write_bytes(b"synthetic fixture")
        with self.assertRaises(RuntimeError):
            verify_character_blend(file, "a" * 64, self.root / "reopened.json",
                                   binary="definitely-no-blender")


if __name__ == "__main__":
    unittest.main()
