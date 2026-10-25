"""Reconcile a real Blender edit back to MGR's original world geometry contract."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from .geometry import create_neighborhood
from .spec import WorldSpec
from .world_editor import _load_json, _validate_edits


SCRIPT = Path(__file__).resolve().parent.parent / "bridge" / "blender_roundtrip_export.py"


def roundtrip_command(binary, blend, edits, receipt):
    if not Path(blend).is_file() or Path(blend).suffix.lower() != ".blend":
        raise ValueError("existing Blender project required")
    if Path(edits).suffix.lower() != ".json" or Path(receipt).suffix.lower() != ".json":
        raise ValueError("roundtrip needs JSON outputs")
    if Path(edits).exists() or Path(receipt).exists():
        raise FileExistsError("roundtrip refuses to overwrite any output")
    return [str(binary), "--background", "--factory-startup", str(Path(blend).resolve()),
            "--python", str(SCRIPT), "--", str(Path(edits).resolve()), str(Path(receipt).resolve())]


def export_blender_edits(binary, blend, original_world, output, receipt, *, timeout=180):
    output, receipt = Path(output), Path(receipt)
    if output.exists() or receipt.exists():
        raise FileExistsError("roundtrip output must be new")
    original_world = Path(original_world)
    manifest = _load_json(original_world / "manifest.json", max_bytes=10_000_000)
    blob = (original_world / "world.glb").read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    if manifest.get("artifact", {}).get("sha256") != digest:
        raise ValueError("original world GLB fingerprint mismatch")
    _, authored = create_neighborhood(WorldSpec(**manifest["spec"]))
    if authored["buildings"] != manifest["buildings"]:
        raise ValueError("source authored building identity mismatch")
    if not shutil.which(str(binary)):
        raise RuntimeError("Blender binary not installed")
    with tempfile.TemporaryDirectory(prefix="mgr-roundtrip-") as temp:
        staging = Path(temp)
        command = roundtrip_command(binary, blend, staging / "edits.json", staging / "receipt.json")
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        if result.returncode or not (staging / "edits.json").is_file() or not (staging / "receipt.json").is_file():
            raise RuntimeError(f"Blender roundtrip did not finish: {(result.stdout + result.stderr)[-1200:]}")
        document = _load_json(staging / "edits.json")
        _validate_edits(document, authored["buildings"], digest, authored["grounds"])
        proof = _load_json(staging / "receipt.json")
        if (proof.get("status") != "EXPORTED" or proof.get("editable_buildings") != len(document["buildings"])
                or proof.get("source_sha256") != digest):
            raise ValueError("Blender roundtrip verification receipt mismatch")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(document, sort_keys=True, indent=2) + "\n")
        with receipt.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(proof, sort_keys=True, indent=2) + "\n")
        return proof
