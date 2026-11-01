"""Additive original World Forge biomes with immutable city input."""
import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from forge.cli import build
from forge.spec import WorldSpec
from forge.environment import generate_biome_shell,write_biome_shell
from forge.glb import inspect_glb

class BiomeTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.world=self.root/"world"
        build(WorldSpec(seed=14,columns=2,rows=2,buildings=2),self.world)

    def test_biome_generates_real_asset_outside_unchanged_original_city(self):
        source=self.world/"world.glb"
        sha=hashlib.sha256(source.read_bytes()).hexdigest()
        for biome in ("forest","desert","tundra","volcanic","alien"):
            with self.subTest(biome=biome):
                folder=self.root/biome
                receipt=write_biome_shell(self.world,folder,biome=biome,seed=28,resolution=18)
                self.assertEqual(receipt["biome"],biome)
                self.assertTrue(receipt["city_unchanged"])
                self.assertTrue(receipt["world_original_untouched"])
                self.assertGreater(receipt["tiles"],20)
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),sha)
                raw=(folder/"biome.glb").read_bytes()
                self.assertGreater(inspect_glb(raw)["triangles"],60)
                self.assertEqual(hashlib.sha256(raw).hexdigest(),receipt["artifact"]["sha256"])
                self.assertFalse(receipt["collision_navigation_built"])
                with self.assertRaises(FileExistsError):
                    write_biome_shell(self.world,folder,biome=biome,seed=28,resolution=18)

    def test_biome_is_reproducible_without_paid_model(self):
        first=write_biome_shell(self.world,self.root/"a",biome="alien",seed=17)
        second=write_biome_shell(self.world,self.root/"b",biome="alien",seed=17)
        other=write_biome_shell(self.world,self.root/"c",biome="alien",seed=18)
        self.assertEqual(first["artifact"]["sha256"],second["artifact"]["sha256"])
        self.assertNotEqual(first["artifact"]["sha256"],other["artifact"]["sha256"])

    def test_rejects_incorrect_biome_resolution_and_tampered_world(self):
        doc=json.loads((self.world/"manifest.json").read_text())
        for params in ({"biome":"impossible"},{"seed":-4},{"resolution":128}):
            with self.subTest(params=params),self.assertRaises(ValueError):
                generate_biome_shell(doc,**params)
        (self.world/"world.glb").write_bytes(b"altered")
        with self.assertRaises(ValueError):
            write_biome_shell(self.world,self.root/"invalid")
