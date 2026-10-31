import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from forge.security.rambler import create_roster,verify_roster,save_roster

class RamblerTests(unittest.TestCase):
    def test_bytes_match_tamper_fail_and_no_fake_signing(self):
        with TemporaryDirectory() as t:
            root=Path(t)/"public";root.mkdir()
            (root/"meshes").mkdir()
            (root/"meshes"/"a.glb").write_bytes(b"glTFtest")
            (root/"manifest.json").write_text('{"ready":true}')
            listed=["manifest.json","meshes/a.glb"]
            a=create_roster(root,listed)
            self.assertEqual(verify_roster(root,a)["status"],"BYTE_INTEGRITY_VERIFIED_NOT_SIGNED")
            self.assertFalse(a["publisher_authenticated"])
            self.assertFalse(a["reverse_engineering_impossible"])
            (root/"meshes"/"a.glb").write_bytes(b"glTFchanged")
            with self.assertRaisesRegex(ValueError,"integrity mismatch"):
                verify_roster(root,a)
    def test_hidden_secrets_unlisted_files_paths_and_overwrite_blocked(self):
        with TemporaryDirectory() as t:
            root=Path(t)/"release";root.mkdir()
            (root/"a.txt").write_text("A")
            for path in ["../escape.txt",".env","private/key.pem","C:/private/data.txt","foo//bar"]:
                with self.subTest(path=path),self.assertRaises(ValueError):
                    create_roster(root,[path])
            manifest=create_roster(root,["a.txt"])
            (root/"other.txt").write_text("UNLISTED")
            with self.assertRaisesRegex(ValueError,"unlisted"):
                verify_roster(root,manifest)
            (root/"other.txt").unlink()
            out=Path(t)/"rambler-roster.json"
            save_roster(root,["a.txt"],out)
            self.assertEqual(verify_roster(root,out)["files"],1)
            with self.assertRaises(FileExistsError):
                save_roster(root,["a.txt"],out)
    def test_cannot_forge_publisher_signature_claim(self):
        with TemporaryDirectory() as t:
            root=Path(t)/"release";root.mkdir()
            (root/"app.txt").write_text("owned code")
            a=create_roster(root,["app.txt"])
            a["publisher_signature"]="FAKE"
            with self.assertRaisesRegex(ValueError,"signature"):
                verify_roster(root,a)
            a["publisher_signature"]=None
            a["publisher_authenticated"]=True
            with self.assertRaisesRegex(ValueError,"signature"):
                verify_roster(root,a)
