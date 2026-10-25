"""Local-only MGR Forge creation workstation: browser to verified files.

No public bind, no arbitrary shell/Blender scripts, no direct personal-file reads.
"""

import base64
import binascii
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import threading
from urllib.parse import unquote, urlparse

from .image_relief import export_image_relief
from .live_blender import create_live_blender_scene
from .web_runtime import make_world_flight
from .world_editor import apply_world_edits


MAX_REQUEST = 1_800_000
JOB_ID = re.compile(r"[a-f0-9]{24}\Z")
FILES = {"relief.glb": "model/gltf-binary", "relief.obj": "text/plain",
         "relief.mtl": "text/plain", "manifest.json": "application/json",
         "world.glb": "model/gltf-binary", "world.obj": "text/plain",
         "world.mtl": "text/plain", "world-editor.html": "text/html",
         "scene.blend": "application/octet-stream", "scene-report.json": "application/json"}


class ForgeWorkstation:
    def __init__(self, world, workspace, *, blender="blender"):
        self.world = Path(world).resolve(strict=True)
        self.workspace = Path(workspace).resolve()
        self.blender = blender
        self.token = secrets.token_urlsafe(32)
        if not (self.world / "world.glb").is_file():
            raise ValueError("original generated world required")
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.jobs = self.workspace / "jobs"
        self.jobs.mkdir(exist_ok=True)
        # A new unique offline HTML keeps previously generated scenes recoverable.
        output = self.workspace / f"studio-{secrets.token_hex(8)}.html"
        make_world_flight(self.world, output)
        self.page = output.read_text(encoding="utf-8").replace(
            "<body>", f'<body><script>window.MGR_FORGE_STUDIO_TOKEN={json.dumps(self.token)};</script>', 1)

    def create_job(self):
        while True:
            job_id = secrets.token_hex(12)
            try:
                folder = self.jobs / job_id
                folder.mkdir(exist_ok=False)
                return job_id, folder
            except FileExistsError:
                continue

    def valid_job(self, identifier):
        if type(identifier) is not str or not JOB_ID.fullmatch(identifier):
            raise ValueError("invalid job identifier")
        folder = self.jobs / identifier
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError("unknown job")
        return folder

    def command(self, route, payload):
        if not isinstance(payload, dict):
            raise ValueError("JSON object required")
        if route == "/api/relief":
            if set(payload) != {"png_base64"} or type(payload["png_base64"]) is not str:
                raise ValueError("expect only PNG base64")
            try:
                raw = base64.b64decode(payload["png_base64"], validate=True)
            except (ValueError, binascii.Error) as error:
                raise ValueError("invalid image base64") from error
            from .image_relief import decode_png
            decode_png(raw)
            job_id, folder = self.create_job()
            (folder / "source.png").write_bytes(raw)
            report = export_image_relief(folder / "source.png", folder / "relief")
            return {"status": "MATERIALIZED", "job_id": job_id,
                    "glb_url": f"/files/{job_id}/relief/relief.glb",
                    "triangles": report["triangles"], "kind": "2.5D image relief"}
        if route == "/api/world":
            if set(payload) != {"edits"} or not isinstance(payload["edits"], dict):
                raise ValueError("expect only world edits document")
            if len(json.dumps(payload["edits"])) > 1_000_000:
                raise ValueError("world edits too large")
            job_id, folder = self.create_job()
            edits = folder / "edits.json"
            edits.write_text(json.dumps(payload["edits"]), encoding="utf-8")
            result = apply_world_edits(self.world, edits, folder / "edited")
            return {"status": "MATERIALIZED", "job_id": job_id,
                    "glb_url": f"/files/{job_id}/edited/world.glb",
                    "html_url": f"/files/{job_id}/edited/world-editor.html",
                    "buildings": result["buildings"]}
        if route == "/api/blender":
            if set(payload) != {"job_id"}:
                raise ValueError("expect only authored job identifier")
            job = self.valid_job(payload["job_id"])
            if not (job / "edited" / "manifest.json").is_file():
                raise ValueError("job does not have an edited MGR world")
            proof = create_live_blender_scene(job / "edited", job / "scene.blend",
                                              job / "scene-report.json", binary=self.blender)
            return {"status": proof["status"], "job_id": payload["job_id"],
                    "blend_url": f"/files/{payload['job_id']}/scene.blend",
                    "editable_buildings": proof["editable_buildings"]}
        raise ValueError("unknown studio command")


def make_handler(studio):
    class StudioHandler(BaseHTTPRequestHandler):
        server_version = "MGR-Forge-Local/1"

        def send_bytes(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self' blob: data: 'unsafe-inline'; connect-src 'self'; img-src 'self' blob: data:")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/", "/studio"):
                return self.send_bytes(200, studio.page.encode("utf-8"), "text/html; charset=utf-8")
            match = re.fullmatch(r"/files/([a-f0-9]{24})/(relief|edited)?/?([a-z-]+\.(?:glb|obj|mtl|json|html)|scene\.blend)", path)
            if match:
                jid, subfolder, name = match.groups()
                if name not in FILES:
                    return self.send_bytes(404, b"not found", "text/plain")
                try:
                    folder = studio.valid_job(jid)
                except ValueError:
                    return self.send_bytes(404, b"not found", "text/plain")
                target = folder / subfolder / name if subfolder else folder / name
                if target.is_symlink() or not target.is_file():
                    return self.send_bytes(404, b"not found", "text/plain")
                return self.send_bytes(200, target.read_bytes(), FILES[name])
            return self.send_bytes(404, b"not found", "text/plain")

        def do_POST(self):
            if self.path not in ("/api/relief", "/api/world", "/api/blender"):
                return self.send_bytes(404, b"not found", "text/plain")
            if self.headers.get("X-MGR-Forge-Token") != studio.token:
                return self.send_bytes(403, b"forbidden", "text/plain")
            origin = self.headers.get("Origin")
            if origin is not None and origin != f"http://127.0.0.1:{self.server.server_port}":
                return self.send_bytes(403, b"forbidden", "text/plain")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.send_bytes(415, b"JSON required", "text/plain")
            try:
                size = int(self.headers.get("Content-Length", "-1"))
                if not 0 < size <= MAX_REQUEST:
                    raise ValueError("request body outside limit")
                payload = json.loads(self.rfile.read(size))
                result = studio.command(self.path, payload)
                return self.send_bytes(200, json.dumps(result).encode("utf-8"), "application/json")
            except (ValueError, json.JSONDecodeError, UnicodeError) as error:
                return self.send_bytes(400, json.dumps({"error": str(error)}).encode("utf-8"), "application/json")
            except (RuntimeError, FileExistsError) as error:
                return self.send_bytes(409, json.dumps({"error": str(error)}).encode("utf-8"), "application/json")

        def log_message(self, _format, *_args):
            return

    return StudioHandler


def start_server(world, workspace, *, port=0, blender="blender"):
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("invalid local port")
    studio = ForgeWorkstation(world, workspace, blender=blender)
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(studio))
    server.daemon_threads = True
    return server, studio
