"""Honest, deterministic experiments for ten MGR-native production concepts."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from forge.geometry import Mesh
from forge.cli import main
from forge.blender_bridge import blender_studio_witness_command
from forge.studio_quality import (
    material_reality_witness, adaptive_light_orchestra,
    flesh_translucence_witness, surface_anatomy_guardian,
    living_hair_director, layered_world_dna, horizon_truth_streaming,
    visual_surface_reconciler, cross_view_reality_judge,
    atmosphere_memory,
)


class StudioQualityTests(unittest.TestCase):
    def test_real_blender_studio_command_requires_new_typed_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)
            command=blender_studio_witness_command("blender",base/"scene.blend",base/"render.png",base/"receipt.json")
            self.assertIn("blender_studio_witness.py",command[4])
            self.assertEqual(command[0],"blender")
            with self.assertRaises(ValueError):
                blender_studio_witness_command("blender",base/"scene.glb",base/"render.png",base/"receipt.json")
            (base/"receipt.json").write_text("not overwritten")
            with self.assertRaises(FileExistsError):
                blender_studio_witness_command("blender",base/"scene.blend",base/"render.png",base/"receipt.json")

    def test_studio_cli_materializes_all_ten_evidence_receipts(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/"studio.json"
            self.assertEqual(main(["studio-proof","--out",str(output)]),0)
            proof=json.loads(output.read_text())
            self.assertEqual(proof["status"],"PASS")
            self.assertEqual(proof["count"],10)
            self.assertEqual(len(proof["checks"]),10)
            with self.assertRaises(FileExistsError):
                main(["studio-proof","--out",str(output)])

    def test_material_witness_catches_bad_roughness(self):
        material={"base_color":[0.3,0.2,0.1],"metallic":0.1,"roughness":0.4}
        self.assertEqual(material_reality_witness([material])["status"],"PASS")
        self.assertEqual(material_reality_witness([{**material,"roughness":1.7}])["status"],"FAIL")

    def test_light_orchestra_is_ranked_and_bounded(self):
        lights=[{"id":"far","position":[20,0,0],"energy":10},
                {"id":"near","position":[1,0,0],"energy":10}]
        receipt=adaptive_light_orchestra(lights,(0,0,0),max_active=1)
        self.assertEqual(receipt["active"],["near"])
        self.assertEqual(receipt["deferred"],["far"])
        with self.assertRaises(ValueError):
            adaptive_light_orchestra(lights+[lights[0]],(0,0,0))

    def test_translucence_decreases_with_thickness_and_rejects_bad_input(self):
        result=flesh_translucence_witness([0,0.1,1],10)
        a,b,c=result["transmission"]
        self.assertAlmostEqual(a,1)
        self.assertGreater(b,c)
        with self.assertRaises(ValueError):
            flesh_translucence_witness([-1],2)

    def test_surface_guardian_uses_real_mesh_edge_audit(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,2,2)
        self.assertEqual(surface_anatomy_guardian(mesh)["status"],"PASS")
        mesh.indices=mesh.indices[:-3]
        self.assertEqual(surface_anatomy_guardian(mesh)["status"],"FAIL")

    def test_living_hair_tracks_root_and_strand_stretch(self):
        good=[[[0,0,0],[0,1,0],[0,2,0]],[[0.05,0,0],[0.05,1,0],[0.05,2,0]]]
        self.assertEqual(living_hair_director(good)["status"],"PASS")
        jump=copy.deepcopy(good)
        jump[1][0]=[1,0,0]
        self.assertEqual(living_hair_director(jump)["status"],"FAIL")
        stretched=copy.deepcopy(good)
        stretched[1][2]=[0.05,5,0]
        self.assertEqual(living_hair_director(stretched)["status"],"FAIL")

    def test_layered_world_preserves_source_and_stable_hash(self):
        base={"hero":{"coat":"black","owner":"MGR"},"door":{"open":False}}
        patches=[{"id":"hero","operation":"set","properties":{"coat":"silver"}}]
        old=copy.deepcopy(base)
        a=layered_world_dna(base,patches)
        b=layered_world_dna(base,patches)
        self.assertEqual(a["scene_sha256"],b["scene_sha256"])
        self.assertEqual(a["objects"]["hero"]["coat"],"silver")
        self.assertEqual(base,old)
        with self.assertRaises(ValueError):
            layered_world_dna(base,[{"id":"ghost","operation":"set","properties":{"coat":"red"}}])
        with self.assertRaises(ValueError):
            layered_world_dna(base,[{"id":"hero","operation":"set","properties":{"owner":"stolen"}}])

    def test_horizon_truth_does_not_claim_actual_streaming(self):
        chunks={"chunks":[{"id":"near","world_origin":[0,0,0]},
                          {"id":"far","world_origin":[1000,0,0]}]}
        plan=horizon_truth_streaming(chunks,(0,0,0),active_radius_m=10,prefetch_radius_m=15)
        self.assertEqual(plan["status"],"PLAN_ONLY")
        self.assertEqual(plan["residency"]["active"],["near"])
        self.assertNotIn("far",plan["residency"]["active"])

    def test_surface_reconciler_rejects_large_landmark_drift(self):
        fixed={"left_eye":(1,1),"right_eye":(3,1)}
        self.assertEqual(visual_surface_reconciler(fixed,fixed)["status"],"PASS")
        self.assertEqual(visual_surface_reconciler(fixed,{"left_eye":(1,1),"right_eye":(30,1)})["status"],"FAIL")
        with self.assertRaises(ValueError):
            visual_surface_reconciler(fixed,{"left_eye":(1,1)})

    def test_cross_view_judge_checks_anatomy_under_camera_rotation(self):
        world={"head":(0,2,4),"left_hand":(-1,1,4),"right_hand":(1,1,4)}
        identity=((1,0,0),(0,1,0),(0,0,1))
        yaw=((0,0,1),(0,1,0),(-1,0,0))
        a={"position":(0,0,0),"camera_to_world":identity,"focal_px":400,
           "observed":{"head":(0,200),"left_hand":(-100,100),"right_hand":(100,100)}}
        # Camera at (-4,0,4), rotated to look along world +X.
        b={"position":(-4,0,4),"camera_to_world":yaw,"focal_px":400,
           "observed":{"head":(0,200),"left_hand":(0,400/3),"right_hand":(0,80)}}
        passed=cross_view_reality_judge(world,[a,b])
        self.assertEqual(passed["status"],"PASS")
        missing=copy.deepcopy(b)
        del missing["observed"]["right_hand"]
        self.assertEqual(cross_view_reality_judge(world,[a,missing])["status"],"FAIL")
        wrong=copy.deepcopy(b)
        wrong["observed"]["left_hand"]=(60,100)
        self.assertEqual(cross_view_reality_judge(world,[a,wrong])["status"],"FAIL")

    def test_atmosphere_memory_detects_unexpected_flash(self):
        self.assertEqual(atmosphere_memory([[0.1,0.2],[0.12,0.19]])["status"],"PASS")
        self.assertEqual(atmosphere_memory([[0.1,0.2],[0.9,0.19]])["status"],"FAIL")
        with self.assertRaises(ValueError):
            atmosphere_memory([[0.1,0.2],[0.3]])


if __name__=="__main__":
    unittest.main()
