"""Translate a verified MGR edited-world bundle into an editable Blender scene."""

import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

from .glb import inspect_glb
from .world_editor import BUILDING_MATERIALS


def validate_live_bundle(folder):
    """Verify geometry fingerprint and independently editable building metadata."""
    folder = Path(folder)
    manifest_path, glb_path = folder / "manifest.json", folder / "world.glb"
    if not manifest_path.is_file() or not glb_path.is_file():
        raise ValueError("existing MGR world manifest and GLB required")
    if manifest_path.stat().st_size > 10_000_000 or glb_path.stat().st_size > 100_000_000:
        raise ValueError("scene bundle exceeds validated size limits")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("edit_provenance", {}).get("schema") != "mgr.forge.edited-world.v1":
        raise ValueError("editable source must come from apply-world-edits")
    blob = glb_path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != manifest.get("artifact", {}).get("sha256"):
        raise ValueError("GLB hash does not match edited manifest")
    inspect_glb(blob)
    buildings = manifest.get("buildings")
    if not isinstance(buildings, list) or len(buildings) > 128:
        raise ValueError("invalid authored building inventory")
    names = set()
    for item in buildings:
        if not isinstance(item, dict) or type(item.get("id")) is not str or item["id"] in names:
            raise ValueError("invalid building identity")
        names.add(item["id"])
        if item.get("material") not in BUILDING_MATERIALS:
            raise ValueError("unsupported building material")
        center, size = item.get("center"), item.get("size")
        if not isinstance(center, list) or not isinstance(size, list) or len(center) != 3 or len(size) != 3:
            raise ValueError("building transform malformed")
        if any(type(n) not in (float, int) or not math.isfinite(n) for n in center + size):
            raise ValueError("building transform must be finite")
        if center[1] != 0 or min(size) < 2 or max(size) > 100:
            raise ValueError("building dimensions invalid")
    return {"schema": "mgr.forge.blender-live-scene-input.v1", "buildings": buildings,
            "source_glb_sha256": manifest["artifact"]["sha256"]}


def live_blender_command(blender_binary, folder, blend_path, report_path):
    """Generate a fixed-script command; never compile untrusted prompts as Python."""
    validate_live_bundle(folder)
    blend_path, report_path = Path(blend_path), Path(report_path)
    if blend_path.suffix.lower() != ".blend" or report_path.suffix.lower() != ".json":
        raise ValueError("Blender output must be .blend and receipt .json")
    if blend_path.exists() or report_path.exists():
        raise FileExistsError("refusing to overwrite an existing Blender output")
    script = Path(__file__).resolve().parent.parent / "bridge" / "blender_live_scene.py"
    if not script.is_file():
        raise FileNotFoundError("MGR native Blender bridge missing")
    return [str(blender_binary), "--background", "--factory-startup", "--python", str(script),
            "--", str(Path(folder).resolve()), str(blend_path.resolve()), str(report_path.resolve())]


def create_live_blender_scene(folder, blend_path, report_path, *, binary="blender", timeout=180):
    command = live_blender_command(binary, folder, blend_path, report_path)
    if not shutil.which(str(binary)):
        raise RuntimeError("Blender binary unavailable; scene was not produced")
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"Blender scene build failed ({result.returncode}): {result.stderr[-800:]}")
    if not Path(report_path).is_file():
        raise RuntimeError(f"Blender exited without a proof receipt: {(result.stdout + result.stderr)[-1200:]}")
    receipt = json.loads(Path(report_path).read_text(encoding="utf-8"))
    original = validate_live_bundle(folder)
    if (receipt.get("status") != "PASS" or receipt.get("editable_buildings") != len(original["buildings"])
            or receipt.get("source_glb_sha256") != original["source_glb_sha256"]
            or not Path(blend_path).is_file() or Path(blend_path).stat().st_size < 1000):
        raise RuntimeError("Blender produced invalid or mismatched editable-scene proof")
    return receipt
