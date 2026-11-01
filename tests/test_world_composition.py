"""World Forge one actual city+biome editable scene composer contract."""
import hashlib,json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from forge.cli import build
from forge.spec import WorldSpec
from forge.environment import write_biome_shell
from forge.world_composition import compose_world

class WorldComposerTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.city=self.root/"city"
        self.biome=self.root/"biome"
        build(WorldSpec(seed=15,columns=2,rows=2,buildings=2),self.city)
        write_biome_shell(self.city,self.biome,biome="tundra",seed=72,resolution=20)

    def test_missing_blender_does_not_touch_originals(self):
        before=hashlib.sha256((self.city/"world.glb").read_bytes()).hexdigest()
        with patch("forge.world_composition.shutil.which",return_value=None):
            with self.assertRaisesRegex(RuntimeError,"Blender"):
                compose_world(self.city,self.biome,self.root/"composed",blender="not-installed")
        self.assertFalse((self.root/"composed").exists())
        self.assertEqual(hashlib.sha256((self.city/"world.glb").read_bytes()).hexdigest(),before)

    def test_disallows_cross_world_biome_and_duplicate_output(self):
        other=self.root/"other"
        build(WorldSpec(seed=99,columns=2,rows=2,buildings=3),other)
        with patch("forge.world_composition.shutil.which",return_value="blender"):
            with self.assertRaisesRegex(ValueError,"SHA"):
                compose_world(other,self.biome,self.root/"composed")
        occupied=self.root/"existing"
        occupied.mkdir()
        with self.assertRaises(FileExistsError):
            compose_world(self.city,self.biome,occupied)

    def test_failed_blender_preserves_partial_failure_proof_not_false_success(self):
        with patch("forge.world_composition.shutil.which",return_value="blender"),patch(
              "forge.world_composition._run",side_effect=RuntimeError("mock Blender failed")):
            with self.assertRaisesRegex(RuntimeError,"mock Blender"):
                compose_world(self.city,self.biome,self.root/"partial")
        self.assertFalse((self.root/"partial"/"composition-receipt.json").exists())
