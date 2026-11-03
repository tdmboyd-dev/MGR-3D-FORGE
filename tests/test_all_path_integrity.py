"""Cross-path integrity regressions found through actual offline CLI qualification."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from forge.cli import main, build
from forge.glb import inspect_glb
from forge.spec import WorldSpec
from forge.engine_handoff import export_godot_project
from forge.security.rambler import save_roster, verify_roster
from forge.receipt import file_receipt, verify_bundle


class AllPathIntegrityTests(unittest.TestCase):
    def test_approved_small_crops_become_real_proxies_without_weakening_sources(self):
        from PIL import Image,ImageDraw
        from forge.unclothe_3d import extract_approved_parts,materialize_unclothe_proxies
        from forge.reference_pack import prepare_reference_pack
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            Image.new("RGBA",(128,128),(80,120,180,255)).save(root/"source.png")
            for size in (16,32):
                mask=Image.new("L",(128,128),0)
                ImageDraw.Draw(mask).rectangle((32,32,31+size,31+size),fill=255)
                mask.save(root/"mask.png")
                spec={"schema":"mgr.forge.unclothe.v1","source":"source.png","parts":[{"id":"coat","kind":"coat","decision":"approved","mask":"mask.png"}]}
                (root/"parts.json").write_text(json.dumps(spec),encoding="utf8")
                extracted=root/f"parts-{size}"
                extract_approved_parts(root/"parts.json",extracted)
                with Image.open(extracted/"coat.png") as crop:
                    self.assertEqual(crop.size,(size,size))
                proxies=root/f"proxy-{size}"
                materialize_unclothe_proxies(extracted,proxies,grid=8)
                outputs=list(proxies.glob("*.glb"))
                self.assertTrue(outputs)
                self.assertGreater(inspect_glb(outputs[0].read_bytes())["triangles"],0)
            Image.new("RGBA",(32,32),(80,120,180,255)).save(root/"too-small.png")
            reference={"schema":"mgr.forge.reference-input.v1","images":[{"asset":"body","view":"front","file":"too-small.png"}]}
            (root/"reference.json").write_text(json.dumps(reference),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"dimensions"):
                prepare_reference_pack(root/"reference.json",root/"admitted.json")
            self.assertFalse((root/"admitted.json").exists())

    def test_rectify_cli_materializes_pixels_from_real_png(self):
        from PIL import Image,ImageDraw
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            image=Image.new("L",(16,16),0)
            ImageDraw.Draw(image).rectangle((4,4,11,11),fill=255)
            image.save(root/"mask.png")
            (root/"quad.json").write_text(json.dumps([[0,0],[15,0],[15,15],[0,15]]),encoding="utf8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["rectify-mask","--image",str(root/"mask.png"),"--src-quad",str(root/"quad.json"),
                                       "--dst-quad",str(root/"quad.json"),"--size","16","16","--out",str(root/"rectified.png")]),0)
            with Image.open(root/"rectified.png") as actual:
                self.assertEqual(actual.size,image.size)
                self.assertEqual(actual.tobytes(),image.tobytes())

    def test_compare_render_cli_uses_original_comparator(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            Image.new("RGB",(8,8),(20,40,60)).save(root/"image.png")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["compare-renders",str(root/"image.png"),str(root/"image.png")]),0)

    def test_rectify_identity_preserves_border_foreground(self):
        from forge.rectify import rectify_mask
        rows=[[255,0,0,255],[0,255,255,0],[0,255,255,0],[255,0,0,255]]
        quad=[[0,0],[3,0],[3,3],[0,3]]
        self.assertEqual(rectify_mask(rows,(4,4),(4,4),quad,quad),rows)

    def test_godot_rejects_valid_glb_with_shifted_manifest_collider(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            world=root/"world"
            document=build(WorldSpec(columns=2,rows=2,buildings=2),world)
            original_hash=document["artifact"]["sha256"]
            document["buildings"][0]["center"][0]+=1.25
            (world/"manifest.json").write_text(json.dumps(document),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"visual corners"):
                export_godot_project(world,root/"godot")
            self.assertFalse((root/"godot").exists())
            self.assertEqual(file_receipt(world/"world.glb")["sha256"],original_hash)

    def test_godot_rejects_changed_ground_footprint_and_accepts_zero_world(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            world=root/"world"
            document=build(WorldSpec(buildings=0),world)
            result=export_godot_project(world,root/"valid")
            self.assertEqual(result["collision_visual_witness"]["corners"],4)
            document["grounds"]["width"]+=2
            (world/"manifest.json").write_text(json.dumps(document),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"footprint"):
                export_godot_project(world,root/"bad")
            self.assertFalse((root/"bad").exists())

    def test_zero_building_world_retains_real_ground_camera_and_valid_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"world"
            document=build(WorldSpec(buildings=0),root)
            self.assertEqual(document["buildings"],[])
            self.assertEqual(document["cinematic_reel_quality"]["status"],"PASS")
            self.assertEqual(document["omitted_empty_layers"],["interiors","lod1"])
            self.assertIsNone(document["lod1_quality"])
            self.assertFalse((root/"interiors.glb").exists())
            self.assertFalse((root/"world_lod1.glb").exists())
            self.assertTrue(verify_bundle(root)["passed"])
            self.assertGreater(inspect_glb((root/"world.glb").read_bytes())["triangles"],0)
            self.assertGreater(inspect_glb((root/"parks.glb").read_bytes())["triangles"],0)

    def test_fully_occupied_world_does_not_emit_invalid_empty_park_glb(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"world"
            document=build(WorldSpec(columns=2,rows=2,buildings=4),root)
            self.assertEqual(document["omitted_empty_layers"],["parks"])
            self.assertFalse((root/"parks.glb").exists())
            self.assertNotIn("parks",document["additional_artifacts"])
            self.assertTrue(verify_bundle(root)["passed"])

    def test_valid_hash_subset_cannot_qualify_missing_declared_primary(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"side.txt").write_text("valid bytes",encoding="utf8")
            inventory={"side.txt":file_receipt(root/"side.txt")}
            document={"artifact":{"path":"missing.glb","sha256":"0"*64,"bytes":20},
                      "artifact_inventory":inventory}
            (root/"manifest.json").write_text(json.dumps(document),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"primary artifact"):
                verify_bundle(root)

    def test_primary_lineage_and_declared_sidecars_are_inventory_bound(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"world.glb").write_bytes(b"source bytes")
            receipt=file_receipt(root/"world.glb")
            document={"artifact":{"path":"world.glb",**receipt},"artifact_inventory":{"world.glb":receipt}}
            manifest=root/"manifest.json"
            manifest.write_text(json.dumps(document),encoding="utf8")
            self.assertTrue(verify_bundle(root)["passed"])
            document["additional_artifacts"]={"preview":"missing.svg"}
            manifest.write_text(json.dumps(document),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"sidecar"):
                verify_bundle(root)
            del document["additional_artifacts"]
            document["artifact"]["sha256"]="0"*64
            manifest.write_text(json.dumps(document),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"primary artifact"):
                verify_bundle(root)

    def test_receipt_types_do_not_accept_boolean_byte_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"tiny.txt").write_bytes(b"a")
            receipt=file_receipt(root/"tiny.txt")
            receipt["bytes"]=True
            (root/"manifest.json").write_text(json.dumps({"artifact_inventory":{"tiny.txt":receipt}}),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"receipt"):
                verify_bundle(root)

    def test_release_roster_inside_root_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"release"
            root.mkdir()
            (root/"app.txt").write_text("original",encoding="utf8")
            for target in (root/"roster.json",root/"subdir"/"roster.json"):
                with self.subTest(target=target),self.assertRaisesRegex(ValueError,"outside"):
                    save_roster(root,["app.txt"],target)
                self.assertFalse(target.exists())
            self.assertFalse((root/"subdir").exists())

    def test_real_cli_seal_external_roster_then_verify(self):
        with tempfile.TemporaryDirectory() as temp:
            parent=Path(temp)
            root=parent/"release"
            root.mkdir()
            (root/"app.txt").write_text("original",encoding="utf8")
            files=parent/"files.json"
            files.write_text(json.dumps(["app.txt"]),encoding="utf8")
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError,"outside"):
                    main(["rambler-seal","--root",str(root),"--files-json",str(files),"--out",str(root/"roster.json")])
                self.assertEqual(main(["rambler-seal","--root",str(root),"--files-json",str(files),"--out",str(parent/"roster.json")]),0)
            self.assertEqual(verify_roster(root,parent/"roster.json")["files"],1)


if __name__=="__main__":
    unittest.main()
