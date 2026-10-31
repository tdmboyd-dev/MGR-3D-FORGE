"""Source Atlas tests: provenance, bounded public API, quarantine and CLI."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest

from forge.asset_atlas import (
    MGRSourceAtlas, MGRAssetCatalog, inspect_import_glb, MAX_CATALOG_BYTES,
)
from forge.assets import AssetRegistry
from forge.cli import main
from forge.geometry import Mesh
from forge.glb import export_glb


class FakeResponse:
    def __init__(self, payload, url, headers=None):
        self.payload = payload
        self.url = url
        self.headers = headers or {"Content-Length": str(len(payload))}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def geturl(self):
        return self.url

    def read(self, count):
        return self.payload[:count]


def asset_model():
    geometry = Mesh()
    geometry.box(0, 0, 0, 1, 2, 1)
    return export_glb([geometry], materials=[("fixture", [0.5, 0.6, 0.4, 1])])


def source_row(payload, **overrides):
    data = {
        "id": "42", "slug": "fantasy-dragon-42", "title": "Fantasy dragon",
        "status": "published", "url": "https://3dassets.dev/assets/fantasy-dragon-42",
        "cdnUrl": "https://cdn.3dassets.dev/assets/42/v1/model.glb",
        "license": {"slug": "cc0-1.0", "url": "https://creativecommons.org/publicdomain/zero/1.0/"},
        "category": {"slug": "characters"}, "tags": [{"slug": "fantasy"}],
        "contributor": {"name": "Creator"},
        "stats": {"fileSize": len(payload), "triangles": 12}, "aiGenerated": True,
    }
    data.update(overrides)
    return data


class TestAssetAtlas(unittest.TestCase):
    def setUp(self):
        self.testroot = TemporaryDirectory()
        self.addCleanup(self.testroot.cleanup)
        self.root = Path(self.testroot.name)
        self.catalog = MGRAssetCatalog(self.root / "catalog")
        self.payload = asset_model()

    def stub_search(self, rows, *, returned_url="https://3dassets.dev/api/v1/assets"):
        raw = json.dumps({"data": rows}).encode()
        return lambda *_a, **_k: FakeResponse(raw, returned_url)

    def discover_fixture(self):
        return self.catalog.search_live_3dassets("dragon", opener=self.stub_search([source_row(self.payload)]))

    def test_source_directory_spans_requested_creation_domains(self):
        atlas = MGRSourceAtlas()
        self.assertGreaterEqual(len(atlas.sources), 15)
        for category in ("faces", "skin-materials", "animals", "fantasy-creatures",
                         "vehicles", "worlds", "materials", "game-kits", "animation", "ai-shape"):
            self.assertTrue(atlas.find(category=category), category)

    def test_restricted_pack_is_not_mislabeled_cc0(self):
        source = MGRSourceAtlas().find(text="quaternius")[0]
        self.assertIn("NO_STANDALONE_REDISTRIBUTION", source["rights"])
        self.assertEqual(source["access"], "DIRECTORY_ONLY")

    def test_search_directory_by_creator_kind(self):
        self.assertEqual(MGRSourceAtlas().find(kind="character-generator")[0]["id"], "mpfb")

    def test_live_search_is_metadata_only_and_persistent(self):
        found = self.discover_fixture()
        self.assertEqual(found["returned"], 1)
        self.assertEqual(found["assets_downloaded"], 0)
        self.assertEqual(found["listings"][0]["rights_status"], "SOURCE_CC0_CLAIM_REVIEW_PENDING")
        reopened = MGRAssetCatalog(self.root / "catalog").search(text="dragon")
        self.assertEqual(len(reopened), 1)
        self.assertEqual(reopened[0]["source_url"], "https://3dassets.dev/assets/fantasy-dragon-42")

    def test_wrong_license_is_not_promoted(self):
        wrong = source_row(self.payload, license={"slug": "cc-by-nc"})
        found = self.catalog.search_live_3dassets("dragon", opener=self.stub_search([wrong]))
        self.assertEqual(found["returned"], 0)
        self.assertEqual(found["skipped_unadmittable"], 1)

    def test_polyhaven_search_caches_models_with_api_credit_obligation(self):
        def vendor(request, **_options):
            url = request.full_url
            if "/search?" in url:
                return FakeResponse(json.dumps({"results": [{"slug": "rock_face_02", "score": 0.65}]}).encode(), url)
            return FakeResponse(json.dumps({"name": "Rock Face 02", "type": 2,
                "authors": {"Dario": "All"}, "tags": ["geology"], "polycount": 29566}).encode(), url)
        found = self.catalog.search_live_polyhaven("rock", kind="models", limit=1, opener=vendor)
        self.assertEqual(found["returned"], 1)
        self.assertEqual(found["api_credit"], "Powered by Poly Haven")
        item = self.catalog.search(provider="polyhaven")[0]
        self.assertEqual(item["rights_status"], "PROVIDER_CC0_CLAIM_API_CREDIT_REQUIRED")
        self.assertIsNone(item["bytes_claimed"])
        self.assertEqual(item["source_url"], "https://polyhaven.com/a/rock_face_02")

    def test_polyhaven_type_filter_and_remote_host_validation(self):
        with self.assertRaises(ValueError):
            self.catalog.search_live_polyhaven("skin", kind="unknown")
        with self.assertRaises(ValueError):
            self.catalog.search_live_polyhaven("skin", limit=11)
        rogue = lambda request, **_kw: FakeResponse(b'{"results":[]}', "https://evil.example/")
        with self.assertRaisesRegex(ValueError, "redirected"):
            self.catalog.search_live_polyhaven("skin", opener=rogue)

    def test_unexpected_download_host_is_rejected_before_caching(self):
        wrong = source_row(self.payload, cdnUrl="https://some-other-host.example/dragon.glb")
        found = self.catalog.search_live_3dassets("dragon", opener=self.stub_search([wrong]))
        self.assertEqual(found["returned"], 0)

    def test_api_redirect_outside_allowlist_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "redirected"):
            self.catalog.search_live_3dassets("dragon", opener=self.stub_search([], returned_url="https://evil.example/index"))

    def test_live_search_bounds(self):
        for query, limit in (("", 20), ("x" * 121, 20), ("dragon", 101)):
            with self.assertRaises(ValueError):
                self.catalog.search_live_3dassets(query, limit=limit)

    def test_upstream_payload_budget(self):
        response = lambda *_a, **_k: FakeResponse(b"x" * (MAX_CATALOG_BYTES + 1),
                                                   "https://3dassets.dev/api/v1/assets")
        with self.assertRaisesRegex(ValueError, "byte budget"):
            self.catalog.search_live_3dassets("dragon", opener=response)

    def test_license_or_cdn_changes_do_not_silently_replace_existing_entry(self):
        self.discover_fixture()
        second = source_row(self.payload, cdnUrl="https://cdn.3dassets.dev/assets/42/v2/model.glb")
        with self.assertRaisesRegex(ValueError, "changed"):
            self.catalog.search_live_3dassets("dragon", opener=self.stub_search([second]))
        self.assertIn("/v1/", self.catalog.search()[0]["cdn_url"])

    def test_acquire_real_glb_bytes_into_existing_hash_vault_but_quarantine(self):
        self.discover_fixture()
        getter = lambda *_a, **_k: FakeResponse(self.payload, "https://cdn.3dassets.dev/assets/42/v1/model.glb")
        record = self.catalog.acquire_3dassets("fantasy-dragon-42", self.root / "vault", opener=getter)
        self.assertEqual(record["status"], "QUARANTINED_RIGHTS_AND_QUALITY")
        self.assertEqual(record["container_inspection"]["status"], "STRUCTURE_INSPECTED")
        stored, meta = AssetRegistry(self.root / "vault").get(record["asset"]["sha256"])
        self.assertEqual(stored, self.payload)
        self.assertFalse(meta["rights_reviewed"])
        self.assertEqual(meta["source_slug"], "fantasy-dragon-42")
        self.assertEqual(self.catalog.acquire_3dassets("fantasy-dragon-42", self.root / "vault", opener=getter)["asset"], meta)

    def test_acquire_missing_listing_refused(self):
        with self.assertRaisesRegex(ValueError, "discovered"):
            self.catalog.acquire_3dassets("not-cached", self.root / "vault")

    def test_acquire_rejects_source_byte_mismatch_without_vault_write(self):
        self.discover_fixture()
        getter = lambda *_a, **_k: FakeResponse(self.payload[:-4], "https://cdn.3dassets.dev/assets/42/v1/model.glb")
        with self.assertRaisesRegex(ValueError, "length differs"):
            self.catalog.acquire_3dassets("fantasy-dragon-42", self.root / "vault", opener=getter)
        self.assertFalse((self.root / "vault" / "index.json").exists())

    def test_acquire_rejects_cdn_redirect(self):
        self.discover_fixture()
        getter = lambda *_a, **_k: FakeResponse(self.payload, "https://evil.example/fake.glb")
        with self.assertRaisesRegex(ValueError, "redirected"):
            self.catalog.acquire_3dassets("fantasy-dragon-42", self.root / "vault", opener=getter)

    def test_glb_rejects_external_asset_uri(self):
        self.assertEqual(inspect_import_glb(self.payload)["meshes"], 1)
        with self.assertRaisesRegex(ValueError, "header"):
            inspect_import_glb(b"MALICIOUS" + self.payload[9:])

    def test_glb_rejects_negative_declared_buffer_length(self):
        document = {"asset": {"version": "2.0"}, "meshes": [{}],
                    "buffers": [{"byteLength": -1}]}
        manifest = json.dumps(document).encode("utf-8")
        manifest += b" " * (-len(manifest) % 4)
        binary = b"\0" * 4
        total = 12 + 8 + len(manifest) + 8 + len(binary)
        fixture = (struct.pack("<4sII", b"glTF", 2, total) +
                   struct.pack("<I4s", len(manifest), b"JSON") + manifest +
                   struct.pack("<I4s", len(binary), b"BIN\0") + binary)
        with self.assertRaisesRegex(ValueError, "buffer or mesh"):
            inspect_import_glb(fixture)

    def test_asset_registry_prevents_conflicting_provenance(self):
        vault = AssetRegistry(self.root / "vault")
        first = vault.add(b"same content", owner="owner-a", license_id="CC0")
        with self.assertRaisesRegex(ValueError, "conflicting provenance"):
            vault.add(b"same content", owner="owner-b", license_id="CC0")
        self.assertEqual(vault.get(first["sha256"])[1]["owner"], "owner-a")

    def test_cli_owner_can_find_source_families_without_network(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["asset-sources", "--category", "fantasy-creatures"]), 0)
        self.assertGreaterEqual(json.loads(out.getvalue())["count"], 3)

    def test_cli_reopens_cached_model_search(self):
        self.discover_fixture()
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["asset-search", "--catalog", str(self.root / "catalog"),
                                   "--query", "dragon"]), 0)
        self.assertEqual(json.loads(out.getvalue())["count"], 1)


if __name__ == "__main__":
    unittest.main()
