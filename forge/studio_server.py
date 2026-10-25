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
import subprocess
import threading
from urllib.parse import urlparse
from zipfile import ZipFile, ZIP_DEFLATED

from .image_relief import export_image_relief
from .character_intake import admit_candidate
from .engine_handoff import export_godot_project
from .live_blender import create_live_blender_scene
from .web_runtime import make_world_flight
from .world_editor import apply_world_edits


MAX_REQUEST = 1_800_000
JOB_ID = re.compile(r"[a-f0-9]{24}\Z")
FILES = {"relief.glb": "model/gltf-binary", "relief.obj": "text/plain",
         "relief.mtl": "text/plain", "manifest.json": "application/json",
         "world.glb": "model/gltf-binary", "world.obj": "text/plain",
         "world.mtl": "text/plain", "world-editor.html": "text/html",
         "scene.blend": "application/octet-stream", "scene-report.json": "application/json",
         "godot-project.zip": "application/zip", "candidate.glb": "model/gltf-binary",
         "candidate.json": "application/json"}


class ForgeWorkstation:
    def __init__(self, world, workspace, *, blender="blender"):
        self.world = Path(world).resolve(strict=True)
        self.workspace = Path(workspace).resolve()
        self.blender = blender
        self.blender_jobs = {}
        self.blender_lock = threading.Lock()
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

    @staticmethod
    def _write_job_state(job, state):
        """Persist atomic, bounded job receipts across a local Studio restart."""
        temporary = job / "blender-state.tmp"
        final = job / "blender-state.json"
        temporary.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
        temporary.replace(final)

    @staticmethod
    def _read_job_state(job):
        path = job / "blender-state.json"
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
            return None
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError):
            return None
        if not isinstance(state, dict) or state.get("status") not in ("RUNNING", "PASS", "FAILED"):
            return None
        return state

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
        if route == "/api/character":
            if set(payload) != {"glb_base64"} or type(payload["glb_base64"]) is not str:
                raise ValueError("expect only GLB base64")
            try:
                raw = base64.b64decode(payload["glb_base64"], validate=True)
            except (ValueError, binascii.Error) as error:
                raise ValueError("invalid model base64") from error
            from .character_intake import inspect_candidate
            # Validate the payload first to avoid allocating a persistent job for junk.
            # File-backed validation is required by the canonical candidate contract.
            from tempfile import TemporaryDirectory
            with TemporaryDirectory(dir=self.workspace) as scratch:
                staging = Path(scratch) / "upload.glb"
                staging.write_bytes(raw)
                inspected = inspect_candidate(staging)
                job_id, folder = self.create_job()
                admitted = admit_candidate(staging, folder / "candidate")
            return {"status": "INSPECTED", "job_id": job_id,
                    "glb_url": f"/files/{job_id}/candidate/candidate.glb",
                    "report_url": f"/files/{job_id}/candidate/candidate.json",
                    "triangles": inspected["geometry"]["triangles"],
                    "mesh_containers": inspected["geometry"]["meshes"],
                    "skins": admitted["skin_count"], "warnings": inspected["warnings"]}
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
        if route == "/api/godot":
            if set(payload) != {"job_id"}:
                raise ValueError("expect only authored job identifier")
            job_id = payload["job_id"]
            job = self.valid_job(job_id)
            if not (job / "edited" / "manifest.json").is_file():
                raise ValueError("job does not have an edited MGR world")
            archive = job / "godot-project.zip"
            if not archive.exists():
                project = job / "godot"
                result = export_godot_project(job / "edited", project)
                with ZipFile(archive, "x", compression=ZIP_DEFLATED) as package:
                    for name in [*result["files"], "handoff.json"]:
                        package.write(project / name, arcname=name)
            return {"status": "MATERIALIZED", "engine_import_verified": False,
                    "archive_url": f"/files/{job_id}/godot-project.zip"}
        if route in ("/api/blender", "/api/blender-status"):
            if set(payload) != {"job_id"}:
                raise ValueError("expect only authored job identifier")
            job = self.valid_job(payload["job_id"])
            if not (job / "edited" / "manifest.json").is_file():
                raise ValueError("job does not have an edited MGR world")
            job_id = payload["job_id"]
            with self.blender_lock:
                state = self.blender_jobs.get(job_id)
                if (job / "scene-report.json").is_file() and (job / "scene.blend").is_file():
                    proof = json.loads((job / "scene-report.json").read_text(encoding="utf-8"))
                    if proof.get("status") == "PASS":
                        return {"status": "PASS", "job_id": job_id,
                                "blend_url": f"/files/{job_id}/scene.blend",
                                "editable_buildings": proof["editable_buildings"]}
                if state is None:
                    state = self._read_job_state(job)
                    if state and state["status"] == "RUNNING":
                        # Process-local workers cannot survive a Studio restart.
                        state = {"status": "FAILED", "job_id": job_id,
                                 "error": "Previous Blender job was interrupted; start a new edited-world job"}
                        self._write_job_state(job, state)
                    if state:
                        self.blender_jobs[job_id] = state
                if route == "/api/blender" and state is None:
                    state = {"status": "RUNNING", "job_id": job_id}
                    self._write_job_state(job, state)
                    self.blender_jobs[job_id] = state
                    thread = threading.Thread(target=self._build_blender_job, args=(job_id, job), daemon=True)
                    thread.start()
                return state or {"status": "NOT_STARTED", "job_id": job_id}
        raise ValueError("unknown studio command")

    def _build_blender_job(self, job_id, job):
        try:
            proof = create_live_blender_scene(job / "edited", job / "scene.blend",
                                              job / "scene-report.json", binary=self.blender)
            result = {"status": "PASS", "job_id": job_id,
                      "blend_url": f"/files/{job_id}/scene.blend",
                      "editable_buildings": proof["editable_buildings"]}
        except (ValueError, RuntimeError, FileExistsError, OSError, subprocess.TimeoutExpired) as error:
            result = {"status": "FAILED", "job_id": job_id, "error": str(error)[:500]}
        with self.blender_lock:
            self._write_job_state(job, result)
            self.blender_jobs[job_id] = result


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
            match = re.fullmatch(r"/files/([a-f0-9]{24})/(relief|edited|candidate)?/?([a-z-]+\.(?:glb|obj|mtl|json|html|zip)|scene\.blend)", path)
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
            if self.path not in ("/api/relief", "/api/character", "/api/world", "/api/godot", "/api/blender", "/api/blender-status"):
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
