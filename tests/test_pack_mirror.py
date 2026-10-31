import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from forge.pack_mirror import mirror_kaykit_pack, license_claim_scope

REPO = "KayKit-Prototype-Bits-1.0"
COMMIT = "a" * 40


def zip_bytes(*, license_text="License: Creative Commons Zero CC0 1.0", path="pack/model.glb"):
    memory = io.BytesIO()
    with ZipFile(memory, "w", ZIP_DEFLATED) as z:
        z.writestr("pack/LICENSE.txt", license_text)
        z.writestr(path, b"synthetic fixture; not real 3D")
    return memory.getvalue()


class FakeResponse:
    headers = {}
    def __init__(self, payload, address="https://codeload.github.com/KayKit-Game-Assets/x/zip/y"):
        self.payload, self.address = payload, address
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def geturl(self): return self.address
    def read(self, limit): return self.payload[:limit]


class PackMirrorTests(unittest.TestCase):
    def test_directory_licenses_do_not_bleed_into_sibling_code(self):
        folder="repo-abcdef/addons/assets/Assets"
        self.assertTrue(license_claim_scope(folder+"/gltf/a.gltf", folder))
        self.assertFalse(license_claim_scope("repo-abcdef/addons/runtime/plugin.py", folder))
        self.assertFalse(license_claim_scope(folder+"/../runtime/plugin.py",folder))
        self.assertFalse(license_claim_scope("repo-abcdef/addons/assets/AssetSomething/raw.bin",folder))

    def test_saved_receipt_marks_each_asset_folder_scope_without_licensing_siblings(self):
        payload = io.BytesIO()
        with ZipFile(payload,"w",ZIP_DEFLATED) as archive:
            archive.writestr("repo/Assets/LICENSE.txt","Creative Commons Zero CC0")
            archive.writestr("repo/Assets/model.glb",b"glTF-fixture")
            archive.writestr("repo/code/plugin.py",b"proprietary-style unreviewed fixture")
        with TemporaryDirectory() as root:
            result=mirror_kaykit_pack(REPO,COMMIT,root,opener=lambda *_a,**_k:
                                       FakeResponse(payload.getvalue()))
            receipt=json.loads(Path(result["receipt"]).read_text())
            self.assertEqual(receipt["schema"],"mgr.forge.pack-preservation.v2")
            self.assertEqual(receipt["cc0_folder_claim_count"],2)
            self.assertEqual(receipt["outside_license_scope_count"],1)
            states={record["path"]:record["source_license_scope_claimed"]
                    for record in receipt["files"]}
            self.assertTrue(states["repo/Assets/model.glb"])
            self.assertFalse(states["repo/code/plugin.py"])
            self.assertFalse(receipt["safe_to_redistribute"])

    def test_official_pinned_archive_has_durable_file_and_license_receipt(self):
        blob = zip_bytes()
        with TemporaryDirectory() as root:
            result = mirror_kaykit_pack(REPO, COMMIT, root, expected_sha256=hashlib.sha256(blob).hexdigest(),
                                        opener=lambda *_args, **_kwargs: FakeResponse(blob))
            self.assertEqual(result["status"], "PRESERVED_QUARANTINED_RIGHTS_AND_QUALITY")
            receipt = json.loads(Path(result["receipt"]).read_text())
            self.assertEqual(receipt["file_count"], 2)
            self.assertIn("CC0", receipt["license_notice"]["text"])
            self.assertFalse(receipt["safe_to_redistribute"])
            saved = Path(root) / receipt["content_object"]
            self.assertEqual(saved.read_bytes(), blob)
            self.assertEqual(result["archive_sha256"], hashlib.sha256(blob).hexdigest())
            retry = mirror_kaykit_pack(REPO, COMMIT, root, opener=lambda *_args, **_kwargs: FakeResponse(blob))
            self.assertEqual(retry["archive_sha256"], result["archive_sha256"])

    def test_wrong_repo_commit_license_and_traversal_rejected(self):
        blob = zip_bytes()
        with TemporaryDirectory() as root:
            def attempt(archive=blob, repo=REPO, commit=COMMIT, address=None):
                return mirror_kaykit_pack(repo, commit, root, opener=lambda *_a, **_kw: FakeResponse(
                    archive, address=address) if address else FakeResponse(archive))
            with self.assertRaises(ValueError): attempt(repo="Random-Paid-Pack")
            with self.assertRaises(ValueError): attempt(commit="latest")
            with self.assertRaises(ValueError): attempt(archive=zip_bytes(license_text="All rights reserved"))
            with self.assertRaises(ValueError): attempt(archive=zip_bytes(path="../escape.glb"))
            with self.assertRaises(ValueError): attempt(address="https://evil.example/zip")
            with self.assertRaises(ValueError):
                mirror_kaykit_pack(REPO, COMMIT, root, expected_sha256="b"*64,
                                   opener=lambda *_a, **_kw: FakeResponse(blob))
            self.assertFalse((Path(root)/"index.json").exists())
