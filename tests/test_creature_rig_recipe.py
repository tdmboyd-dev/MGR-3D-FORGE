from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from forge.imagination import create_original_creature,genome_candidates
from forge.creature_rig_recipe import creature_bones,save_creature_rig_recipe
from forge.morph_engine import morph_point


class RigRecipeTests(unittest.TestCase):
    def test_winged_spider_hybrid_creates_parents_legs_wings_and_tail(self):
        genome=genome_candidates("invent a winged spider with massive tail",42,1)[0]
        rig=creature_bones(genome,morph={"length":1.2,"height":0.85,"twist_degrees":11},
                           axis_extent=5)
        self.assertEqual(rig["status"],"BLUEPRINT_NOT_SKINNED")
        names={b["name"] for b in rig["skeleton"]}
        self.assertEqual(rig["bones"],7+16+4)
        self.assertIn("right_wing_02",names)
        self.assertIn("leg_08_lower",names)
        self.assertFalse(rig["deforming_skin_verified"])
        for bone in rig["skeleton"]:
            if bone["parent"]:
                self.assertIn(bone["parent"],names)

    def test_rig_matches_exact_morph_field_for_corresponding_original_joint(self):
        genome=genome_candidates("invent a winged aquatic dragon",3,1)[0]
        morph={"width":1.25,"twist_degrees":10}
        rig=creature_bones(genome,morph=morph,axis_extent=5)
        root=next(b for b in rig["skeleton"] if b["name"]=="root")
        self.assertEqual(tuple(root["tail"]),morph_point((0,genome["standing_height"],0),
                                                         morph,axis_extent=5))

    def test_manifest_to_recoverable_recipe_and_no_overwrite(self):
        with TemporaryDirectory() as temp:
            folder=Path(temp)/"creature"
            manifest=create_original_creature("invent a wild fantasy wyvern with horns",
                                              folder,seed=5,variants=3)
            dest=folder/"rig-blueprint.json"
            rig=save_creature_rig_recipe(folder/"creature.json",dest)
            self.assertEqual(rig["mesh_sha256"],manifest["artifact"]["sha256"])
            self.assertTrue(dest.is_file())
            with self.assertRaises(FileExistsError):
                save_creature_rig_recipe(folder/"creature.json",dest)

    def test_disallowed_or_invalid_rig_shape_fails(self):
        genome=genome_candidates("invent a flying elephant monster",3,1)[0]
        with self.assertRaises(ValueError):
            creature_bones({**genome,"legs":3})
        with self.assertRaises(ValueError):
            creature_bones(genome,morph={"twist_degrees":999})
