import json
import math
from pathlib import Path
import struct
import tempfile
import unittest

from forge.blender_bridge import blender_cinematic_command
from forge.character import build_mannequin
from forge.cli import build
from forge.geometry import Mesh
from forge.glb import export_glb, inspect_glb
from forge.materials import MGR_MATERIAL_PRESETS, make_material, validate_pbr_recipe
from forge.material_guardian import validate_imported_materials
from forge.shot_design import lighting_recipe, validate_shot_reel
from forge.spec import WorldSpec
from forge.wardrobe import wardrobe_inventory


class MaterialsAndCinematicTests(unittest.TestCase):
    def test_all_native_pbr_presets(self):
        for name, values in MGR_MATERIAL_PRESETS.items():
            with self.subTest(name=name):
                self.assertEqual(len(validate_pbr_recipe(values)["baseColorFactor"]),4)
                self.assertEqual(make_material(name,name)["name"],name)

    def test_pbr_nonfinite_and_out_of_range_fail(self):
        for key,value in (("roughness",math.nan),("metallic",1.1)):
            recipe=dict(MGR_MATERIAL_PRESETS["gold"])
            recipe[key]=value
            with self.assertRaises(ValueError):
                validate_pbr_recipe(recipe)

    def test_pbr_wrong_channels_fail(self):
        with self.assertRaises(ValueError):
            validate_pbr_recipe({"base_color":[1,1,1],"metallic":0,"roughness":.4})

    def test_glb_keeps_actual_pbr_params(self):
        mesh=Mesh()
        mesh.box(0,0,0,1,1,1)
        payload=export_glb([mesh],materials=[("metal",[1,1,1,1])],
                          pbr_overrides={0:MGR_MATERIAL_PRESETS["gold"]})
        self.assertTrue(inspect_glb(payload)["valid"])
        size=struct.unpack_from("<I",payload,12)[0]
        gltf=json.loads(payload[20:20+size])
        metal=gltf["materials"][0]["pbrMetallicRoughness"]
        self.assertEqual(metal["metallicFactor"],.95)
        self.assertEqual(metal["roughnessFactor"],.22)

    def test_override_index_validated(self):
        with self.assertRaises(ValueError):
            export_glb([Mesh()],materials=[("base",[1,1,1,1])],pbr_overrides={3:MGR_MATERIAL_PRESETS["gold"]})

    def test_material_guardian_rejects_missing_and_invalid(self):
        self.assertEqual(validate_imported_materials({"materials":[]})["status"],"FAIL")
        bad={"materials":[{"name":"metal","metallic":math.nan,"roughness":.4,
                            "base_color":[1,1,1,1]}]}
        self.assertEqual(validate_imported_materials(bad)["status"],"FAIL")
        bad["materials"][0]["metallic"] = .4
        self.assertEqual(validate_imported_materials(bad)["status"],"PASS")

    def test_lighting_moods_are_distinct_and_valid(self):
        first=lighting_recipe(mood="daylight")
        golden=lighting_recipe(mood="golden-hour")
        dark=lighting_recipe(mood="moonlit")
        self.assertGreater(first["sun_strength"],dark["sun_strength"])
        self.assertNotEqual(first["sun_color"],golden["sun_color"])
        with self.assertRaises(ValueError):
            lighting_recipe(mood="invisible")

    def test_shot_validation_rejects_bad_camera_and_duplicate(self):
        shot={"id":"one","camera":[1,3,1],"look_at":[0,0,0],"hold_seconds":2}
        self.assertEqual(validate_shot_reel({"shots":[shot]})["status"],"PASS")
        for broken in ({"shots":[]},{"shots":[shot,shot]},
                       {"shots":[{**shot,"camera":[0,0,0]}]},
                       {"shots":[{**shot,"hold_seconds":0}]}):
            with self.assertRaises(ValueError):
                validate_shot_reel(broken)

    def test_character_has_independently_editable_trousers(self):
        with tempfile.TemporaryDirectory() as directory:
            data=build_mannequin(Path(directory))
            self.assertIn("left_pant_leg",data["editable_parts"])
            self.assertIn("right_pant_leg",data["editable_parts"])
            wardrobe=json.loads((Path(directory)/"wardrobe.json").read_text())
            self.assertEqual(wardrobe["status"],"PASS")
            self.assertTrue((Path(directory)/"parts"/"left_pant_leg.glb").is_file())
            self.assertEqual(len(data["editable_parts"]),20)

    def test_wardrobe_missing_piece_and_bad_rig_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            data=build_mannequin(Path(directory))
            incomplete={**data,"editable_parts":[p for p in data["editable_parts"] if p!="shirt"]}
            self.assertEqual(wardrobe_inventory(incomplete)["status"],"FAIL")
            self.assertEqual(wardrobe_inventory(data,{"attachments":{"shirt":"head"}})["status"],"FAIL")

    def test_world_emits_cinematic_and_material_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            result=build(WorldSpec(buildings=2),Path(directory))
            self.assertEqual(result["cinematic_reel_quality"]["shots"],2)
            self.assertEqual(lighting_recipe(),json.loads((Path(directory)/"lighting.json").read_text()))
            self.assertIn("lighting",result["additional_artifacts"])
            command=blender_cinematic_command("blender",Path(directory)/"world.glb",
                    Path(directory)/"camera_tour.json","daylight",
                    Path(directory)/"scene.blend",Path(directory)/"scene.png",Path(directory)/"scene.json")
            self.assertIn("blender_cinematic.py"," ".join(command))


if __name__=="__main__":
    unittest.main()
