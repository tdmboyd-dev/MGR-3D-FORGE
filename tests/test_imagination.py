"""Native imagination acceptance: real geometry, mutations, prompts, hard gates."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from forge.imagination import genome_candidates,creature_meshes,create_original_creature
from forge.meshqa import analyze_mesh
from forge.glb import inspect_glb


class ImaginationTests(unittest.TestCase):
    def test_prompt_creates_original_mesh_without_preset_or_provider(self):
        with TemporaryDirectory() as t:
            root=Path(t)/"first"
            result=create_original_creature(
                "invent a huge armored winged dragon with eight eyes", root,seed=42,variants=6)
            mesh=root/"creature.glb"
            self.assertTrue(mesh.is_file())
            self.assertGreater(len(mesh.read_bytes()),10000)
            self.assertEqual(result["artifact"]["sha256"],hashlib.sha256(mesh.read_bytes()).hexdigest())
            self.assertGreater(inspect_glb(mesh.read_bytes())["triangles"],300)
            self.assertFalse(result["external_model_used"])
            self.assertFalse(result["rigged"])
            self.assertFalse(result["novelty_worldwide_verified"])
            self.assertEqual(len(result["candidates"]),6)

    def test_deterministic_same_seed_same_glb_different_seed_variants_change_geometry(self):
        with TemporaryDirectory() as t:
            base=Path(t)
            a=create_original_creature("a novel crystal sea creature with wings",base/"a",seed=9)
            b=create_original_creature("a novel crystal sea creature with wings",base/"b",seed=9)
            c=create_original_creature("a novel crystal sea creature with wings",base/"c",seed=10)
            self.assertEqual(a["artifact"]["sha256"],b["artifact"]["sha256"])
            self.assertNotEqual(a["artifact"]["sha256"],c["artifact"]["sha256"])

    def test_prompt_constraints_change_body_features(self):
        spider=genome_candidates("invent a wingless spider creature",22,1)[0]
        serpent=genome_candidates("invent a huge serpent creature",22,1)[0]
        bird=genome_candidates("invent a tall feathered bird creature",22,1)[0]
        self.assertEqual(spider["legs"],8)
        self.assertEqual(serpent["legs"],0)
        self.assertEqual(bird["legs"],2)
        self.assertEqual(bird["wing_pairs"],1)
        self.assertGreater(spider["legs"],serpent["legs"])

    def test_all_candidate_geometry_passes_real_triangle_validation(self):
        for prompt in ("invent a small forest creature without wings",
                       "invent a spider beast with horns",
                       "invent an underwater serpent with a strong tail"):
            with self.subTest(prompt=prompt):
                candidates=genome_candidates(prompt,55,5)
                for g in candidates:
                    checks=[analyze_mesh(m) for m in creature_meshes(g) if m.indices]
                    self.assertTrue(all(x["passed"] for x in checks))

    def test_invalid_budget_prompt_output_overwrite_refused(self):
        with TemporaryDirectory() as t:
            root=Path(t)/"new"
            for kwargs in ({"seed":-1},{"variants":0},{"variants":13},{"variants":True}):
                with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                    create_original_creature("invent a fantasy creature",root,**kwargs)
            with self.assertRaises(ValueError):
                create_original_creature("bad",root)
            create_original_creature("invent a fantasy creature",root,variants=1)
            with self.assertRaises(FileExistsError):
                create_original_creature("invent a fantasy creature",root)
