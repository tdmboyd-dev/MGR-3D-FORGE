import json
import math
from pathlib import Path
import struct
import tempfile
import unittest

from forge.fx import create_magic_effect,export_effect_glb
from forge.glb import inspect_glb
from forge.cli import main
from forge.blender_bridge import blender_fx_render_command


class FantasyForgeTests(unittest.TestCase):
    def test_three_effects_are_actual_3d_glb(self):
        for kind in ("portal","spell-orbit","aura"):
            with self.subTest(kind=kind):
                meshes,receipt=create_magic_effect(kind=kind,particles=16)
                payload=export_effect_glb(meshes)
                self.assertGreater(inspect_glb(payload)["triangles"],100)
                self.assertEqual(receipt["execution"]["external_api_calls"],0)

    def test_effect_determinism_and_motion(self):
        first,baseline=create_magic_effect(kind="portal",phase=0.0,seed=4,particles=16)
        repeat,_=create_magic_effect(kind="portal",phase=0.0,seed=4,particles=16)
        changed,other=create_magic_effect(kind="portal",phase=.5,seed=4,particles=16)
        self.assertEqual(export_effect_glb(first),export_effect_glb(repeat))
        self.assertNotEqual(export_effect_glb(first),export_effect_glb(changed))
        self.assertNotEqual(baseline["sample_positions"],other["sample_positions"])

    def test_emission_in_real_gltf_materials(self):
        meshes,_=create_magic_effect(particles=16)
        binary=export_effect_glb(meshes)
        size=struct.unpack_from("<I",binary,12)[0]
        doc=json.loads(binary[20:20+size])
        self.assertEqual(len(doc["materials"]),3)
        self.assertTrue(all("emissiveFactor" in item for item in doc["materials"]))

    def test_invalid_budget_and_unsupported_effect_rejected(self):
        for kwargs in ({"phase":math.nan},{"particles":4},{"radius":-2},
                       {"kind":"copyrighted-magic"},{"seed":1.1}):
            with self.assertRaises(ValueError):
                create_magic_effect(**kwargs)

    def test_cli_writes_inspectable_effect_and_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/"portal"
            self.assertEqual(main(["fantasy-effect","--kind","portal","--particles","16",
                                   "--out",str(out)]),0)
            self.assertTrue((out/"effect.glb").exists())
            self.assertEqual(json.loads((out/"effect.json").read_text())["kind"],"portal")
            with self.assertRaises(FileExistsError):
                main(["fantasy-effect","--out",str(out)])

    def test_blender_fx_bridge_rejects_absent_glb(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                blender_fx_render_command("blender",Path(directory)/"missing.glb",
                                          Path(directory)/"image.png",Path(directory)/"report.json")

    def test_blender_fx_scene_has_real_light_and_optical_glow_contract(self):
        # Blender itself validates version-specific node APIs on Windows.
        import ast
        source=(Path(__file__).resolve().parents[1]/"bridge"/"blender_fx_render.py").read_text()
        ast.parse(source)
        self.assertIn('"POINT"',source)
        self.assertIn('"Fog Glow"',source)
        self.assertIn('"MGR_FX_Light_Witness"',source)


if __name__=="__main__":
    unittest.main()
