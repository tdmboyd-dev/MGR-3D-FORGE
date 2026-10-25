"""Compile a fully offline, self-contained playable WebGL2 world from Forge output."""

import base64
import hashlib
import json
from pathlib import Path

from .glb import inspect_glb


VIEWER_DIR = Path(__file__).resolve().parent.parent / "viewer"


def make_world_flight(world_dir, output):
    """Create a self-contained HTML+embedded GLB world; no CDN or web server."""
    root = Path(world_dir).resolve()
    output = Path(output)
    if output.exists():
        raise FileExistsError("live world output exists; no automatic overwrite")
    manifest_file = root / "manifest.json"
    glb_file = root / "world.glb"
    if not manifest_file.is_file() or not glb_file.is_file() or glb_file.is_symlink():
        raise ValueError("valid generated Forge world directory required")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    asset = glb_file.read_bytes()
    if len(asset) > 40_000_000:
        raise ValueError("offline web world exceeds 40MB bound")
    if hashlib.sha256(asset).hexdigest() != manifest.get("artifact", {}).get("sha256"):
        raise ValueError("world GLB receipt mismatch")
    geometry = inspect_glb(asset)
    if not geometry["valid"] or not isinstance(manifest.get("buildings"), list):
        raise ValueError("invalid authored world")
    world = {key: manifest[key] for key in ("spec", "grounds", "buildings", "axis", "unit")}
    json_data = json.dumps(world, separators=(",", ":"), sort_keys=True).replace("<", "\\u003c")
    script = (VIEWER_DIR / "runtime.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    html = (VIEWER_DIR / "template.html").read_text(encoding="utf-8")
    html = html.replace("__MGR_MANIFEST__", json_data)
    html = html.replace("__MGR_GLB_BASE64__", base64.b64encode(asset).decode("ascii"))
    html = html.replace("__MGR_RUNTIME_JS__", script)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(html)
    return {"schema":"mgr.forge.world-flight.v1", "status":"MATERIALIZED",
            "html":str(output.resolve()), "bytes":output.stat().st_size,
            "glb_sha256":hashlib.sha256(asset).hexdigest(),
            "triangles":geometry["triangles"], "buildings":len(world["buildings"]),
            "runtime":"offline-browser-WebGL2",
            "limitations":["browser GPU/WebGL2 capability required", "static generated city geometry",
                           "bounds-based building collision, no navmesh or full physics",
                           "browser performance and visual QA require actual browser execution"]}
