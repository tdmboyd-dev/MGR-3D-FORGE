import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from forge.imagination import create_original_creature
from forge.creature_rig import rig_creature


class CreatureRigLocalTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/"dna-creature"
        create_original_creature("invent a winged dragon with a flexible tail",
                                 self.source,seed=11,variants=3)
        self.destination=self.root/"rigged"

    def test_missing_blender_fails_without_partial_output(self):
        with self.assertRaisesRegex(RuntimeError,"Blender"):
            rig_creature(self.source,self.destination,blender="nonexistent-blender-executable")
        self.assertFalse(self.destination.exists())

    def test_wrong_input_fails_before_side_effects(self):
        with self.assertRaises(ValueError):
            rig_creature(self.root/"missing",self.destination)
        self.assertFalse(self.destination.exists())

    def test_existing_output_protected(self):
        self.destination.mkdir()
        with self.assertRaises(FileExistsError):
            rig_creature(self.source,self.destination)
        self.assertTrue(self.destination.is_dir())

    def test_zero_exit_with_error_output_fails_closed(self):
        class Proc:
            returncode=0
            stdout="Traceback (most recent call last)"
            stderr=""
        with patch("forge.creature_rig.shutil.which",return_value="blender"),patch(
                "forge.creature_rig.subprocess.run",return_value=Proc()):
            with self.assertRaisesRegex(RuntimeError,"reported an error"):
                rig_creature(self.source,self.destination)
