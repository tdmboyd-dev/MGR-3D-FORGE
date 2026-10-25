"""Roundtrip safety: no forged provenance, no unchecked Blender output writes."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge.blender_roundtrip import roundtrip_command, export_blender_edits
from forge.cli import build
from forge.spec import WorldSpec


class BlenderRoundtripSafetyTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.world = self.root / "world"
        build(WorldSpec(seed=14, columns=2, rows=2, buildings=2), self.world)
        self.blend = self.root / "source.blend"
        self.blend.write_bytes(b"BLENDER MOCK - only path checks are tested here")

    def test_command_is_static_and_has_explicit_paths(self):
        args = roundtrip_command("blender", self.blend, self.root / "returned.json", self.root / "proof.json")
        self.assertEqual(args[1:3], ["--background", "--factory-startup"])
        self.assertEqual(args[-3], "--")
        self.assertTrue(args[5].endswith("blender_roundtrip_export.py"))

    def test_existing_output_refused(self):
        output = self.root / "returned.json"
        output.touch()
        with self.assertRaises(FileExistsError):
            roundtrip_command("blender", self.blend, output, self.root / "proof.json")

    def test_missing_blend_refused(self):
        with self.assertRaises(ValueError):
            roundtrip_command("blender", self.root / "none.blend", self.root / "out.json", self.root / "proof.json")

    def test_original_glb_mutation_fails_closed(self):
        with (self.world / "world.glb").open("ab") as file:
            file.write(b"TAMPER")
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            export_blender_edits("blender", self.blend, self.world, self.root / "out.json", self.root / "proof.json")

    def test_missing_blender_binary_is_not_a_fake_success(self):
        with patch("forge.blender_roundtrip.shutil.which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "not installed"):
                export_blender_edits("notinstalled", self.blend, self.world,
                                     self.root / "out.json", self.root / "proof.json")

    def test_blender_false_success_is_not_exported(self):
        class FakeResult:
            returncode = 0
            stdout = "Blender quit"
            stderr = ""

        with patch("forge.blender_roundtrip.shutil.which", return_value="blender"), \
             patch("forge.blender_roundtrip.subprocess.run", return_value=FakeResult()):
            with self.assertRaisesRegex(RuntimeError, "did not finish"):
                export_blender_edits("blender", self.blend, self.world,
                                     self.root / "out.json", self.root / "proof.json")
        self.assertFalse((self.root / "out.json").exists())


if __name__ == "__main__":
    unittest.main()
