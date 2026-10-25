"""Admission of user-owned GLB character candidates without inventing likeness/rigs."""

import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

from .character_glb import parse_character_glb


MAX_CHARACTER_BYTES = 80_000_000


def inspect_candidate(source):
    path = Path(source)
    if not path.is_file() or path.is_symlink() or path.suffix.lower() != ".glb":
        raise ValueError("existing ordinary .glb character candidate required")
    if not 28 <= path.stat().st_size <= MAX_CHARACTER_BYTES:
        raise ValueError("character candidate size outside safe bounds")
    blob = path.read_bytes()
    doc, geometry = parse_character_glb(blob)
    if geometry["triangles"] < 1 or geometry["triangles"] > 4_000_000:
        raise ValueError("character needs bounded triangle geometry")
    if len(doc.get("nodes", [])) > 10000 or len(doc.get("skins", [])) > 128:
        raise ValueError("character hierarchy exceeds inspection bounds")
    bounds = []
    for mesh in doc["meshes"]:
        for primitive in mesh["primitives"]:
            accessor = doc["accessors"][primitive["attributes"]["POSITION"]]
            low, high = accessor.get("min"), accessor.get("max")
            if low is None or high is None:
                continue
            if (not isinstance(low, list) or not isinstance(high, list) or len(low) != 3
                    or len(high) != 3 or any(type(v) not in (float, int) or not math.isfinite(v)
                                                    for v in low + high)
                    or any(a > b for a, b in zip(low, high))):
                raise ValueError("invalid mesh bounds")
            bounds.append((low, high))
    minimum = [min(b[0][i] for b in bounds) for i in range(3)] if bounds else None
    maximum = [max(b[1][i] for b in bounds) for i in range(3)] if bounds else None
    skins, animations = doc.get("skins", []), doc.get("animations", [])
    joints = sum(len(s.get("joints", [])) for s in skins)
    morphs = sum(len(p.get("targets", [])) for mesh in doc["meshes"] for p in mesh["primitives"])
    warnings = []
    if not skins:
        warnings.append("No skin/armature in source; not animation-ready")
    if not animations:
        warnings.append("No embedded animation clips")
    if len(doc["meshes"]) == 1:
        warnings.append("One mesh container; clothing/hair separation not demonstrated")
    if minimum is None:
        warnings.append("Bounds missing; size and proportions unverified")
    return {"schema": "mgr.forge.character-candidate.v1", "status": "INSPECTED",
            "source_sha256": hashlib.sha256(blob).hexdigest(), "source_bytes": len(blob),
            "geometry": geometry, "nodes": len(doc.get("nodes", [])),
            "skin_count": len(skins), "joint_references": joints,
            "animation_clips": len(animations), "morph_target_groups": morphs,
            "bounds_min": minimum, "bounds_max": maximum, "warnings": warnings,
            "identity_verified": False, "anatomy_verified": False,
            "deformation_verified": False, "image_reconstruction_performed": False}


def admit_candidate(source, output):
    result = inspect_candidate(source)
    destination = Path(output)
    if destination.exists():
        raise FileExistsError("refusing to overwrite character admission")
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(source, destination / "candidate.glb")
    (destination / "candidate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def create_character_blend(admitted, blend, report, *, binary="blender", timeout=180):
    source = Path(admitted) / "candidate.glb"
    meta = Path(admitted) / "candidate.json"
    if not meta.is_file() or not source.is_file():
        raise ValueError("admitted character directory required")
    data = json.loads(meta.read_text(encoding="utf-8"))
    actual = inspect_candidate(source)
    if data.get("source_sha256") != actual["source_sha256"]:
        raise ValueError("candidate file was modified after admission")
    output, receipt = Path(blend), Path(report)
    if output.suffix.lower() != ".blend" or receipt.suffix.lower() != ".json":
        raise ValueError("expected new .blend and JSON output paths")
    if output.exists() or receipt.exists():
        raise FileExistsError("refusing to overwrite character project")
    if not shutil.which(str(binary)):
        raise RuntimeError("Blender binary unavailable")
    script = Path(__file__).resolve().parent.parent / "bridge" / "blender_character_intake.py"
    command = [str(binary), "--background", "--factory-startup", "--python", str(script),
               "--", str(source.resolve()), str(output.resolve()), str(receipt.resolve()),
               actual["source_sha256"]]
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Blender character import timed out") from error
    if process.returncode != 0 or not receipt.is_file():
        raise RuntimeError("Blender character import failed or did not produce receipt: " +
                           (process.stderr + process.stdout)[-500:])
    result = json.loads(receipt.read_text(encoding="utf-8"))
    if (result.get("status") != "PASS" or result.get("source_sha256") != actual["source_sha256"]
            or result.get("mesh_objects", 0) < 1 or not output.is_file()
            or output.stat().st_size < 1000):
        raise RuntimeError("Blender character project validation failed")
    return result


def verify_character_blend(blend, expected_sha256, report, *, binary="blender", timeout=180):
    """Reopen a saved project in an independent Blender process, not the creator."""
    source, target = Path(blend), Path(report)
    if not source.is_file() or source.suffix.lower() != ".blend":
        raise ValueError("existing Blender character project required")
    if target.exists() or target.suffix.lower() != ".json":
        raise ValueError("new JSON reopen receipt required")
    if (type(expected_sha256) is not str or len(expected_sha256) != 64
            or any(c not in "0123456789abcdef" for c in expected_sha256)):
        raise ValueError("expected real lowercase SHA-256 fingerprint")
    if not shutil.which(str(binary)):
        raise RuntimeError("Blender executable unavailable")
    script = Path(__file__).resolve().parent.parent / "bridge" / "blender_character_reopen.py"
    try:
        process = subprocess.run([str(binary), "--background", "--factory-startup", "--python",
                                  str(script), "--", str(source.resolve()), str(target.resolve()),
                                  expected_sha256], timeout=timeout, capture_output=True, text=True)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Blender character reopen timed out") from error
    if process.returncode or not target.is_file():
        raise RuntimeError("Independent character reopen failed: " +
                           (process.stderr + process.stdout)[-500:])
    result = json.loads(target.read_text(encoding="utf-8"))
    if result.get("status") != "PASS" or result.get("source_sha256") != expected_sha256:
        raise RuntimeError("Character reopen proof mismatch")
    return result
