"""Local workstation contract, authorization, endpoints, job scope and file safety."""

import base64
import hashlib
import http.client
import json
import struct
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import zlib
from io import BytesIO
from zipfile import ZipFile
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from forge.cli import build
from forge.character import build_mannequin
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation, start_server


def gray_png():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", 4, 1, 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(b"\x00\x00\x55\xaa\xff")) + chunk(b"IEND", b""))


class StudioServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.world = self.root / "world"
        build(WorldSpec(seed=42, columns=2, rows=2, buildings=2), self.world)
        try:
            self.server, self.studio = start_server(self.world, self.root / "workspace")
        except PermissionError:
            self.skipTest("runner forbids localhost sockets; run HTTP acceptance on Windows")
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.root_url = f"http://127.0.0.1:{self.server.server_port}"

    def fetch(self, path, payload=None, *, token=True, origin=None, content_type="application/json"):
        headers = {}
        if token:
            headers["X-MGR-Forge-Token"] = self.studio.token
        if origin:
            headers["Origin"] = origin
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = content_type
        request = Request(self.root_url + path, data=data, headers=headers)
        try:
            with urlopen(request, timeout=4) as response:
                return response.status, response.read(), response.headers
        except HTTPError as error:
            with error:
                return error.code, error.read(), error.headers

    def test_studio_binds_only_localhost(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_public_home_contains_no_bearer_or_private_world(self):
        status, body, headers = self.fetch("/", token=False)
        self.assertEqual(status, 200)
        self.assertFalse(self.studio.token.encode() in body, "public home exposed the actual private Studio bearer")
        self.assertNotIn(b"MGR_WORLD_BASE64", body)
        self.assertNotIn(b"MGR CREATION DIRECTOR", body)
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_private_editor_never_accepts_missing_query_or_cookie_tokens(self):
        self.assertEqual(self.fetch("/studio", token=False)[0], 403)
        self.assertEqual(self.fetch("/studio?token=" + self.studio.token, token=False)[0], 403)
        request = Request(self.root_url + "/studio", headers={"Cookie": "forge=" + self.studio.token})
        with self.assertRaises(HTTPError) as failed:
            urlopen(request, timeout=4)
        with failed.exception as response:
            self.assertEqual(response.code, 403)
        status, owner_page, _ = self.fetch("/studio")
        self.assertEqual(status, 200)
        self.assertIn(b"MGR CREATION DIRECTOR", owner_page)

    def test_duplicate_studio_authorization_headers_cannot_select_the_first_token(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        self.addCleanup(connection.close)
        connection.putrequest("POST", "/api/asset-sources")
        connection.putheader("X-MGR-Forge-Token", self.studio.token)
        connection.putheader("X-MGR-Forge-Token", "owned-invalid-second-token")
        connection.putheader("Content-Type", "application/json")
        connection.putheader("Content-Length", "2")
        connection.endheaders(b"{}")
        response = connection.getresponse()
        self.assertEqual(response.status, 403)
        response.read()

    def test_owner_launcher_link_keeps_the_token_in_fragment_and_out_of_http_query(self):
        from urllib.parse import parse_qs, urlsplit
        link = urlsplit(getattr(self.server, "owner_url", ""))
        self.assertEqual(link.scheme, "http")
        self.assertEqual(link.hostname, "127.0.0.1")
        self.assertEqual(link.port, self.server.server_port)
        self.assertEqual(link.query, "")
        self.assertEqual(parse_qs(link.fragment).get("mgr-token"), [self.studio.token])

    def test_studio_renders_actual_3d_editor(self):
        code, data, _ = self.fetch("/")
        self.assertEqual(code, 200)
        self.assertIn(b"MGR CREATION DIRECTOR", data)
        self.assertIn(b"MGR_FORGE_STUDIO_TOKEN", data)
        self.assertIn(b"director-generate-relief", data)
        self.assertIn(b"director-asset-search", data)
        self.assertIn(b"director-creature-create", data)
        self.assertIn(b"director-creature-status", data)
        self.assertIn(b"/api/creature-create", data)
        self.assertIn(b"Download verified 3D creature", data)

    def test_source_atlas_search_authenticated_over_local_http(self):
        code, raw, _ = self.fetch("/api/asset-sources", {"query": "quaternius"})
        self.assertEqual(code, 200)
        found = json.loads(raw)
        self.assertEqual(found["count"], 1)
        self.assertIn("NO_STANDALONE_REDISTRIBUTION", found["sources"][0]["rights"])
        self.assertEqual(self.fetch("/api/asset-sources", {"query": "skin"}, token=False)[0], 403)

    def test_source_atlas_rejects_unbounded_live_search(self):
        code, _, _ = self.fetch("/api/asset-search", {"query": "x" * 121, "live": True})
        self.assertEqual(code, 400)

    def test_source_atlas_cached_search_no_external_network(self):
        code, raw, _ = self.fetch("/api/asset-search", {"query": "dragon", "live": False})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["listings"], [])

    def test_source_atlas_polyhaven_routed_to_matching_read_adapter(self):
        expected = {"status": "CACHED_SOURCE_METADATA", "provider": "polyhaven", "listings": []}
        with patch("forge.studio_server.MGRAssetCatalog.search_live_polyhaven", return_value=expected) as vendor:
            code, raw, _ = self.fetch("/api/asset-search", {
                "query": "rock", "live": True, "provider": "polyhaven", "kind": "models", "limit": 3})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw), expected)
        vendor.assert_called_once_with("rock", kind="models", limit=3)

    def test_http_original_creature_produces_real_token_protected_glb_and_replay(self):
        payload={"request_id":"owner-creator-actor-01",
                 "prompt":"invent a winged forest creature with horns",
                 "seed":44,"variants":3,"morph":{"length":1.1}}
        status,body,_=self.fetch("/api/creature-create",payload)
        self.assertEqual(status,200)
        result=json.loads(body)
        self.assertEqual(result["status"],"MATERIALIZED")
        self.assertGreater(result["triangles"],300)
        self.assertFalse(result["owner_art_accepted"])
        self.assertFalse(result["model_inference_used"])
        self.assertEqual(self.fetch("/api/creature-create",payload,token=False)[0],403)
        replay=json.loads(self.fetch("/api/creature-create",payload)[1])
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["creature_sha256"],result["creature_sha256"])
        self.assertEqual(self.fetch(result["glb_url"],token=False)[0],403)
        request=Request(self.root_url+result["glb_url"],
                        headers={"X-MGR-Forge-Token":self.studio.token})
        with urlopen(request,timeout=4) as response:
            blob=response.read()
        self.assertEqual(hashlib.sha256(blob).hexdigest(),result["creature_sha256"])
        self.assertEqual(blob[:4],b"glTF")
        self.assertEqual(self.fetch("/api/creature-create",{**payload,"prompt":"something else"})[0],400)

    def test_http_biome_creation_real_glb_token_status_and_replay(self):
        initial=hashlib.sha256((self.world/"world.glb").read_bytes()).hexdigest()
        payload={"request_id":"owner-biome-world-00001","biome":"tundra","seed":19,"resolution":21}
        self.assertEqual(self.fetch("/api/biome-create",payload,token=False)[0],403)
        status,raw,_=self.fetch("/api/biome-create",payload)
        self.assertEqual(status,200)
        data=json.loads(raw)
        self.assertEqual(data["status"],"MATERIALIZED")
        self.assertEqual(data["source_world_sha256"],initial)
        self.assertTrue(data["editor_world_unchanged"])
        self.assertGreater(data["biome_bytes"],400)
        self.assertEqual(self.fetch(data["glb_url"],token=False)[0],403)
        res,file,_=self.fetch(data["glb_url"],token=True)
        self.assertEqual(res,200)
        self.assertEqual(file[:4],b"glTF")
        self.assertEqual(hashlib.sha256(file).hexdigest(),data["biome_sha256"])
        reread=json.loads(self.fetch("/api/biome-status",{"request_id":payload["request_id"]})[1])
        self.assertEqual(reread["biome_sha256"],data["biome_sha256"])
        replay=json.loads(self.fetch("/api/biome-create",payload)[1])
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["biome_sha256"],data["biome_sha256"])
        self.assertEqual(self.fetch("/api/biome-create",{**payload,"seed":20})[0],400)
        self.assertEqual(hashlib.sha256((self.world/"world.glb").read_bytes()).hexdigest(),initial)

    def test_creation_chat_has_morph_and_world_biome_controls(self):
        status,html,_=self.fetch("/")
        self.assertEqual(status,200)
        for element in (b"director-morph-bend",b"director-morph-taper",b"director-biome-create",
                        b"director-biome-status",b"/api/biome-create",b"/api/biome-status",
                        b"Download verified"):
            self.assertIn(element,html)

    def test_no_public_tokenless_post(self):
        code, _, _ = self.fetch("/api/world", {"edits": {}}, token=False)
        self.assertEqual(code, 403)

    def test_foreign_origin_cannot_post(self):
        code, _, _ = self.fetch("/api/world", {"edits": {}}, origin="https://evil.example")
        self.assertEqual(code, 403)

    def test_path_traversal_not_exposed(self):
        code, _, _ = self.fetch("/files/../../world/manifest.json")
        self.assertEqual(code, 404)

    def test_unknown_command_404(self):
        code, _, _ = self.fetch("/api/execute", {"shell": "echo hi"})
        self.assertEqual(code, 404)

    def test_non_json_refused(self):
        code, _, _ = self.fetch("/api/world", {"edits": {}}, content_type="text/plain")
        self.assertEqual(code, 415)

    def test_no_arbitrary_python(self):
        code, _, _ = self.fetch("/api/world", {"script": "import os"})
        self.assertEqual(code, 400)

    def test_downloads_require_token_for_relief_world_and_candidate(self):
        relief=self.fetch("/api/relief",{"png_base64":base64.b64encode(gray_png()).decode()})
        self.assertEqual(relief[0],200)
        relief_url=json.loads(relief[1])["glb_url"]
        self.assertEqual(self.fetch(relief_url,token=False)[0],403)
        self.assertEqual(self.fetch(relief_url,token=True)[0],200)
        manifest=json.loads((self.world/"manifest.json").read_text())
        edits={"schema":"mgr.forge.world-edit.v1",
               "asset_sha256":hashlib.sha256((self.world/"world.glb").read_bytes()).hexdigest(),
               "buildings":[{k:b[k] for k in ("id","center","size","material")} for b in manifest["buildings"]]}
        result=json.loads(self.fetch("/api/world",{"edits":edits})[1])
        for name in ("glb_url","html_url"):
            self.assertEqual(self.fetch(result[name],token=False)[0],403)
            self.assertEqual(self.fetch(result[name],token=True)[0],200)
        build_mannequin(self.root/"secure-character")
        raw=(self.root/"secure-character"/"mannequin.glb").read_bytes()
        obj=json.loads(self.fetch("/api/character",{"glb_base64":base64.b64encode(raw).decode()})[1])
        for name in ("glb_url","report_url"):
            self.assertEqual(self.fetch(obj[name],token=False)[0],403)
            self.assertEqual(self.fetch(obj[name],token=True)[0],200)
        godot=json.loads(self.fetch("/api/godot",{"job_id":result["job_id"]})[1])
        self.assertEqual(self.fetch(godot["archive_url"],token=False)[0],403)
        self.assertEqual(self.fetch(godot["archive_url"],token=True)[0],200)

    def test_foreign_host_and_origin_cannot_read_local_studio(self):
        request=Request(self.root_url+"/studio",headers={"Host":"evil.example"})
        with self.assertRaises(HTTPError) as failure:
            urlopen(request,timeout=4)
        with failure.exception as response:
            self.assertEqual(response.code,403)
        self.assertEqual(self.fetch("/",token=False,origin="https://evil.example")[0],403)

    def test_existing_creation_chat_links_fetch_private_artifacts_with_token(self):
        status,html,_=self.fetch("/")
        self.assertEqual(status,200)
        self.assertIn(b"Preparing authenticated Forge artifact",html)
        self.assertIn(b'headers:{"X-MGR-Forge-Token":forgeToken}',html)
        self.assertIn(b"URL.createObjectURL(file)",html)
        self.assertIn(b'viewerLink.rel="noopener noreferrer"',html)
        self.assertIn(b"viewerLink.target=",html)
        self.assertIn(b"if(url.endsWith",html)

    def test_png_to_real_downloadable_glb(self):
        code, body, _ = self.fetch("/api/relief", {"png_base64": base64.b64encode(gray_png()).decode()})
        self.assertEqual(code, 200)
        result = json.loads(body)
        self.assertEqual(result["triangles"], 48)
        status, payload, headers = self.fetch(result["glb_url"])
        self.assertEqual(status, 200)
        self.assertEqual(payload[:4], b"glTF")
        self.assertEqual(headers["Content-Type"], "model/gltf-binary")

    def test_invalid_image_refused_before_job_allocation(self):
        before = list(self.studio.jobs.iterdir())
        code, _, _ = self.fetch("/api/relief", {"png_base64": "!!!!"})
        self.assertEqual(code, 400)
        self.assertEqual(before, list(self.studio.jobs.iterdir()))

    def test_uploaded_real_glb_is_preserved_and_inspected(self):
        build_mannequin(self.root / "generic-character")
        original = (self.root / "generic-character" / "mannequin.glb").read_bytes()
        code, data, _ = self.fetch("/api/character", {"glb_base64": base64.b64encode(original).decode()})
        self.assertEqual(code, 200)
        result = json.loads(data)
        self.assertEqual(result["status"], "INSPECTED")
        self.assertGreater(result["triangles"], 0)
        self.assertEqual(result["skins"], 0)
        self.assertEqual(self.fetch(result["glb_url"])[1], original)
        report = json.loads(self.fetch(result["report_url"])[1])
        self.assertFalse(report["identity_verified"])

    def test_character_upload_refuses_invalid_base64(self):
        prior = list(self.studio.jobs.iterdir())
        code, _, _ = self.fetch("/api/character", {"glb_base64": "!!!!"})
        self.assertEqual(code, 400)
        self.assertEqual(prior, list(self.studio.jobs.iterdir()))

    def test_character_upload_refuses_other_keys(self):
        code, _, _ = self.fetch("/api/character", {"python": "print('unsafe')"})
        self.assertEqual(code, 400)

    def test_character_upload_token_required(self):
        code, _, _ = self.fetch("/api/character", {"glb_base64": "bad"}, token=False)
        self.assertEqual(code, 403)

    def test_world_json_materialization_and_download(self):
        manifest = json.loads((self.world / "manifest.json").read_text())
        edits = {"schema": "mgr.forge.world-edit.v1",
                 "asset_sha256": hashlib.sha256((self.world / "world.glb").read_bytes()).hexdigest(),
                 "buildings": [{k: b[k] for k in ("id", "center", "size", "material")}
                               for b in manifest["buildings"]]}
        edits["buildings"].append({"id": "mgr-created-0001", "center": [0, 0, 0],
                                   "size": [6, 11, 7], "material": "building-gold"})
        code, body, _ = self.fetch("/api/world", {"edits": edits})
        self.assertEqual(code, 200)
        result = json.loads(body)
        self.assertEqual(result["buildings"], 3)
        self.assertEqual(self.fetch(result["glb_url"])[1][:4], b"glTF")
        self.assertIn(b"MGR WORLD", self.fetch(result["html_url"])[1].upper())

    def test_world_rejects_untrusted_sha(self):
        code, _, _ = self.fetch("/api/world", {"edits": {"schema": "mgr.forge.world-edit.v1",
                                                    "asset_sha256": "bad", "buildings": []}})
        self.assertEqual(code, 400)

    def test_bad_blender_job_refused(self):
        code, _, _ = self.fetch("/api/blender", {"job_id": "../../outside"})
        self.assertEqual(code, 400)

    def test_studio_token_unique_per_session(self):
        second = ForgeWorkstation(self.world, self.root / "other")
        self.assertNotEqual(second.token, self.studio.token)

    def test_safety_headers(self):
        status, _, headers = self.fetch("/")
        self.assertEqual(status, 200)
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def _edited_job(self):
        manifest = json.loads((self.world / "manifest.json").read_text())
        edits = {"schema": "mgr.forge.world-edit.v1",
                 "asset_sha256": hashlib.sha256((self.world / "world.glb").read_bytes()).hexdigest(),
                 "buildings": [{k: b[k] for k in ("id", "center", "size", "material")}
                               for b in manifest["buildings"]]}
        code, raw, _ = self.fetch("/api/world", {"edits": edits})
        self.assertEqual(code, 200)
        return json.loads(raw)["job_id"]

    def test_blender_poll_before_start_is_not_started(self):
        job = self._edited_job()
        code, raw, _ = self.fetch("/api/blender-status", {"job_id": job})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["status"], "NOT_STARTED")

    def test_blender_runs_once_even_with_duplicate_clicks(self):
        job = self._edited_job()
        started, release = threading.Event(), threading.Event()
        calls = []
        def create(*args, **kwargs):
            calls.append(args)
            started.set()
            release.wait(4)
            return {"editable_buildings": 2}
        with patch("forge.studio_server.create_live_blender_scene", side_effect=create):
            first = json.loads(self.fetch("/api/blender", {"job_id": job})[1])
            self.assertEqual(first["status"], "RUNNING")
            self.assertTrue(started.wait(2))
            again = json.loads(self.fetch("/api/blender", {"job_id": job})[1])
            self.assertEqual(again["status"], "RUNNING")
            self.assertEqual(len(calls), 1)
            release.set()
            for _ in range(100):
                state = json.loads(self.fetch("/api/blender-status", {"job_id": job})[1])
                if state["status"] == "PASS":
                    break
                time.sleep(.01)
            self.assertEqual(state["status"], "PASS")
            self.assertEqual(state["editable_buildings"], 2)
            self.assertEqual(state["blend_url"], f"/files/{job}/scene.blend")

    def test_blender_background_failure_is_reported(self):
        job = self._edited_job()
        with patch("forge.studio_server.create_live_blender_scene", side_effect=RuntimeError("no Blender found")):
            self.fetch("/api/blender", {"job_id": job})
            for _ in range(100):
                state = json.loads(self.fetch("/api/blender-status", {"job_id": job})[1])
                if state["status"] == "FAILED":
                    break
                time.sleep(.01)
            self.assertEqual(state["status"], "FAILED")
            self.assertIn("no Blender found", state["error"])

    def test_blender_status_requires_correct_token(self):
        job = self._edited_job()
        code, _, _ = self.fetch("/api/blender-status", {"job_id": job}, token=False)
        self.assertEqual(code, 403)

    def test_godot_package_from_live_edited_world(self):
        job = self._edited_job()
        code, raw, _ = self.fetch("/api/godot", {"job_id": job})
        self.assertEqual(code, 200)
        response = json.loads(raw)
        self.assertFalse(response["engine_import_verified"])
        archive_status, payload, _ = self.fetch(response["archive_url"])
        self.assertEqual(archive_status, 200)
        with ZipFile(BytesIO(payload)) as zipfile:
            self.assertEqual(set(zipfile.namelist()),
                             {"project.godot", "world.tscn", "assets/world.glb", "handoff.json"})
            self.assertEqual(zipfile.read("assets/world.glb")[:4], b"glTF")

    def test_engine_endpoint_refuses_invalid_job(self):
        code, _, _ = self.fetch("/api/godot", {"job_id": "../escape"})
        self.assertEqual(code, 400)

    def test_engine_endpoint_requires_token(self):
        code, _, _ = self.fetch("/api/godot", {"job_id": "a" * 24}, token=False)
        self.assertEqual(code, 403)

    def test_blender_job_receipt_persists_between_sessions(self):
        job = self._edited_job()
        folder = self.studio.valid_job(job)
        result = {"status": "FAILED", "job_id": job, "error": "Blender binary missing"}
        self.studio._write_job_state(folder, result)
        recovered = ForgeWorkstation(self.world, self.studio.workspace)
        self.assertEqual(recovered.command("/api/blender-status", {"job_id": job}), result)

    def test_interrupted_blender_job_is_recovered_as_failure(self):
        job = self._edited_job()
        folder = self.studio.valid_job(job)
        self.studio._write_job_state(folder, {"status": "RUNNING", "job_id": job})
        recovered = ForgeWorkstation(self.world, self.studio.workspace)
        result = recovered.command("/api/blender-status", {"job_id": job})
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("interrupted", result["error"])
        self.assertEqual(recovered._read_job_state(folder), result)

    def test_invalid_receipt_does_not_crash_recovery(self):
        job = self._edited_job()
        folder = self.studio.valid_job(job)
        (folder / "blender-state.json").write_text("{broken", encoding="utf-8")
        recovered = ForgeWorkstation(self.world, self.studio.workspace)
        self.assertEqual(recovered.command("/api/blender-status", {"job_id": job})["status"],
                         "NOT_STARTED")

    def test_job_state_replaces_file_without_extra_files(self):
        job = self._edited_job()
        folder = self.studio.valid_job(job)
        self.studio._write_job_state(folder, {"status": "RUNNING", "job_id": job})
        self.studio._write_job_state(folder, {"status": "FAILED", "job_id": job, "error": "stopped"})
        self.assertEqual(self.studio._read_job_state(folder)["status"], "FAILED")
        self.assertFalse((folder / "blender-state.tmp").exists())


if __name__ == "__main__":
    unittest.main()
