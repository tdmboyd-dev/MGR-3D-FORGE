"""Safe new-output material splitting contract; live Blender proof is separate."""

from pathlib import Path
import tempfile
import unittest

from forge.character_intake import separate_character_materials


class CharacterSeparationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.original = self.root / "original.blend"
        self.original.write_bytes(b"Source stays unchanged")

    def test_missing_original_rejected(self):
        with self.assertRaises(ValueError):
            separate_character_materials(self.root / "none.blend", self.root / "new.blend",
                                         self.root / "new.json")

    def test_in_place_overwrite_refused(self):
        with self.assertRaises(FileExistsError):
            separate_character_materials(self.original, self.original, self.root / "proof.json")

    def test_existing_destination_refused(self):
        (self.root / "new.blend").write_bytes(b"existing project")
        with self.assertRaises(FileExistsError):
            separate_character_materials(self.original, self.root / "new.blend",
                                         self.root / "proof.json")

    def test_blender_unavailable_is_not_success(self):
        with self.assertRaises(RuntimeError):
            separate_character_materials(self.original, self.root / "new.blend",
                                         self.root / "proof.json", binary="missing-binary")
        self.assertEqual(self.original.read_bytes(), b"Source stays unchanged")

    def test_invalid_suffix_rejected(self):
        with self.assertRaises(ValueError):
            separate_character_materials(self.original, self.root / "new.glb", self.root / "proof.json")


if __name__ == "__main__":
    unittest.main()
