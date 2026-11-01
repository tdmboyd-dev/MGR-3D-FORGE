"""Reproducible geometry morph operations, limits and preservation."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from forge.imagination import create_original_creature,genome_candidates,creature_meshes
from forge.morph_engine import morph_mesh,normalize_morph
from forge.meshqa import analyze_mesh


class MorphTests(unittest.TestCase):
    def test_existing_mesh_stays_unchanged_morph_rebuilds_normals(self):
        g=genome_candidates("invent a crystalline armored dragon",33,1)[0]
        original=creature_meshes(g)[0]
        positions=list(original.positions)
        out,receipt=morph_mesh(original,{"length":1.5,"height":0.7,
                                         "width":1.2,"twist_degrees":17})
        self.assertEqual(original.positions,positions)
        self.assertNotEqual(out.positions,positions)
        self.assertEqual(original.indices,out.indices)
        self.assertEqual(len(out.normals),len(out.positions))
        self.assertTrue(analyze_mesh(out)["passed"])
        self.assertTrue(receipt["indices_preserved"])

    def test_bend_taper_is_shared_by_all_meshes_and_rig_joints(self):
        from forge.morph_engine import morph_point
        from forge.creature_rig_recipe import creature_bones
        genome=genome_candidates("invent a flying armored serpent with horns",91,1)[0]
        settings={"bend_degrees":18.0,"taper":1.27,"twist_degrees":7}
        rig=creature_bones(genome,morph=settings,axis_extent=5.4)
        root=next(b for b in rig["skeleton"] if b["name"]=="root")
        expected=morph_point((0,genome["standing_height"],0),settings,axis_extent=5.4)
        self.assertEqual(tuple(root["tail"]),expected)
        curved=morph_point((0,3,0),settings,axis_extent=5.4)
        original=morph_point((0,3,0),None,axis_extent=5.4)
        self.assertGreater(curved[0],original[0])
        self.assertNotEqual(morph_point((1,3,1),settings,axis_extent=5.4),
                            morph_point((1,3,1),{"bend_degrees":18},axis_extent=5.4))
        mesh=creature_meshes(genome)[0]
        output,audit=morph_mesh(mesh,settings,axis_extent=5.4)
        self.assertTrue(audit["indices_preserved"])
        self.assertTrue(analyze_mesh(output)["passed"])

    def test_bend_taper_reject_unbounded_or_non_numeric_values(self):
        for recipe in ({"bend_degrees":100},{"bend_degrees":True},
                       {"taper":0},{"taper":float("inf")},{"taper":"wide"}):
            with self.subTest(recipe=recipe),self.assertRaises(ValueError):
                normalize_morph(recipe)

    def test_rejected_morphs_do_not_invent_geometry(self):
        bad=({"length":0.01},{"height":99},{"twist_degrees":360},
             {"width":float("nan")},{"foo":3},{"length":"huge"})
        for params in bad:
            with self.subTest(params=params),self.assertRaises(ValueError):
                normalize_morph(params)
        self.assertEqual(normalize_morph(None)["width"],1)

    def test_morphed_creature_variants_produce_independent_file_hashes(self):
        with TemporaryDirectory() as root:
            a=create_original_creature("invent a colossal winged steel creature",
                Path(root)/"a",seed=4,variants=4)
            b=create_original_creature("invent a colossal winged steel creature",
                Path(root)/"b",seed=4,variants=4,morph={
                    "length":1.25,"height":0.82,"width":1.3,"twist_degrees":11})
            self.assertNotEqual(a["artifact"]["sha256"],b["artifact"]["sha256"])
            self.assertEqual(b["applied_morph"]["twist_degrees"],11)
            self.assertFalse(b["rigged"])
            self.assertFalse(b["model_inference_used"])
