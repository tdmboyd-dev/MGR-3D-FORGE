"""Animated export/reimport must fail closed without native rig and honest proofs."""

import hashlib
from pathlib import Path
import tempfile
import unittest

from forge.character_motion import export_character_motion, reimport_character_motion


class CharacterMotionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.blend = self.root / "source.blend"
        self.blend.write_bytes(b"fixture")
        self.glb = self.root / "source.glb"
        self.glb.write_bytes(b"fixture GLB")

    def test_missing_rig_refused(self):
        with self.assertRaises(ValueError):
            export_character_motion(self.root / "missing.blend", self.root / "out.glb", self.root / "out.json")

    def test_missing_blender_not_faked(self):
        with self.assertRaises(RuntimeError):
            export_character_motion(self.blend, self.root / "out.glb", self.root / "out.json", binary="missing-blender")

    def test_no_overwrite_export(self):
        (self.root / "out.glb").write_bytes(b"safe")
        with self.assertRaises(FileExistsError):
            export_character_motion(self.blend, self.root / "out.glb", self.root / "out.json")

    def test_no_overwrite_import(self):
        (self.root / "receipt.json").write_text("{}")
        with self.assertRaises(ValueError):
            reimport_character_motion(self.glb, hashlib.sha256(self.glb.read_bytes()).hexdigest(), self.root / "receipt.json")

    def test_source_fingerprint_required(self):
        with self.assertRaises(ValueError):
            reimport_character_motion(self.glb, "a" * 64, self.root / "receipt.json")

    def test_unavailable_receiving_blender_fails(self):
        with self.assertRaises(RuntimeError):
            reimport_character_motion(self.glb, hashlib.sha256(self.glb.read_bytes()).hexdigest(),
                                      self.root / "receipt.json", binary="missing-blender")

    def test_invalid_export_suffix_refused(self):
        with self.assertRaises(ValueError):
            export_character_motion(self.blend, self.root / "wrong.obj", self.root / "receipt.json")


if __name__ == "__main__":
    unittest.main()
