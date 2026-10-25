"""Blender-backed export and independent receiving-import proof for deforming rigs."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def _run(script, inputs, binary, timeout):
    if not shutil.which(str(binary)):
        raise RuntimeError("Blender executable unavailable")
    command = [str(binary), "--background", "--factory-startup", "--python",
               str(Path(__file__).resolve().parent.parent / "bridge" / script), "--"]
    try:
        result = subprocess.run(command + [str(x) for x in inputs], capture_output=True,
                                text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Blender motion operation timed out") from exc
    if result.returncode:
        raise RuntimeError("Blender motion operation failed: " + (result.stderr + result.stdout)[-500:])


def export_character_motion(blend, output, report, *, binary="blender", timeout=180):
    original, target, receipt = Path(blend), Path(output), Path(report)
    if not original.is_file() or original.suffix.lower() != ".blend":
        raise ValueError("existing character rig .blend required")
    if target.suffix.lower() != ".glb" or receipt.suffix.lower() != ".json":
        raise ValueError("new GLB and JSON report required")
    if target.exists() or receipt.exists():
        raise FileExistsError("refusing to overwrite motion outputs")
    _run("blender_motion_export.py", [original.resolve(), target.resolve(), receipt.resolve()], binary, timeout)
    if not target.is_file() or not receipt.is_file():
        raise RuntimeError("Blender did not materialize output and report")
    result = json.loads(receipt.read_text())
    if result.get("output_sha256") != hashlib.sha256(target.read_bytes()).hexdigest() or result.get("observed_motion_m", 0) <= .01:
        raise RuntimeError("animated GLB report verification failed")
    return result


def reimport_character_motion(glb, sha256, report, *, binary="blender", timeout=180):
    original, receipt = Path(glb), Path(report)
    if not original.is_file() or original.suffix.lower() != ".glb":
        raise ValueError("existing animated GLB required")
    if receipt.suffix.lower() != ".json" or receipt.exists():
        raise ValueError("new JSON report required")
    if not isinstance(sha256, str) or len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
        raise ValueError("lowercase expected SHA-256 required")
    if hashlib.sha256(original.read_bytes()).hexdigest() != sha256:
        raise ValueError("animated GLB fingerprint mismatch")
    _run("blender_motion_reimport.py", [original.resolve(), sha256, receipt.resolve()], binary, timeout)
    if not receipt.is_file():
        raise RuntimeError("Blender receiving import did not produce report")
    result = json.loads(receipt.read_text())
    if result.get("status") != "PASS" or result.get("sha256") != sha256:
        raise RuntimeError("animated GLB receiving import verification failed")
    return result
