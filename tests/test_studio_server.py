"""Local workstation contract, authorization, endpoints, job scope and file safety."""

import base64
import hashlib
import json
import struct
from pathlib import Path
import tempfile
import threading
import unittest
import zlib
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from forge.cli import build
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
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = content_type
            if token:
                headers["X-MGR-Forge-Token"] = self.studio.token
            if origin:
                headers["Origin"] = origin
        request = Request(self.root_url + path, data=data, headers=headers)
        try:
            with urlopen(request, timeout=4) as response:
                return response.status, response.read(), response.headers
        except HTTPError as error:
            with error:
                return error.code, error.read(), error.headers

    def test_studio_binds_only_localhost(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_studio_renders_actual_3d_editor(self):
        code, data, _ = self.fetch("/")
        self.assertEqual(code, 200)
        self.assertIn(b"MGR CREATION DIRECTOR", data)
        self.assertIn(b"MGR_FORGE_STUDIO_TOKEN", data)
        self.assertIn(b"director-generate-relief", data)

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


if __name__ == "__main__":
    unittest.main()
