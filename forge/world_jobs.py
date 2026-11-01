"""Recoverable, exactly-one-owner idempotency ledger for local 3D world edits.

An interrupted request is NOT retried blindly. Its intermediate folder/receipt
is kept for reconciliation. A repeated completed request hashes the same output.
"""
import hashlib
import json
from pathlib import Path
import re

from .world_editor import apply_world_edits

_ID = re.compile(r"[A-Za-z0-9_-]{12,100}\Z")
MAX_EDIT_BYTES = 1_000_000
MAX_LEDGER_BYTES = 1_000_000


def _atomic_json(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def _index(studio, ledger="world-requests.json"):
    if ledger not in ("world-requests.json", "creature-requests.json", "biome-requests.json", "human-lipsync-requests.json", "world-composition-requests.json"):
        raise ValueError("unsupported creation job ledger")
    path = studio.workspace / ledger
    if not path.exists():
        return {}, path
    if path.is_symlink() or path.stat().st_size > MAX_LEDGER_BYTES:
        raise ValueError("world request ledger integrity failure")
    contents = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(contents, dict) or len(contents) > 1000:
        raise ValueError("invalid world request ledger")
    return contents, path


def _read_materialized(studio, record, request_id, *, replay):
    if record.get("status") != "MATERIALIZED":
        return {"status": "NEEDS_RECONCILIATION", "request_id": request_id,
                "job_id": record.get("job_id"), "replayed": replay}
    folder = studio.valid_job(record.get("job_id"))
    target = folder / "edited" / "world.glb"
    if target.is_symlink() or not target.is_file():
        raise RuntimeError("world artifact missing; reconciliation required")
    raw = target.read_bytes()
    if hashlib.sha256(raw).hexdigest() != record.get("world_sha256") or raw[:4] != b"glTF":
        raise RuntimeError("world artifact checksum mismatch; reconciliation required")
    return {"status": "MATERIALIZED", "request_id": request_id, "job_id": record["job_id"],
            "world_sha256": record["world_sha256"], "world_bytes": len(raw),
            "glb_url": f"/files/{record['job_id']}/edited/world.glb",
            "buildings": record["buildings"], "replayed": replay,
            "provider_cost_usd": 0, "independent_blender_verified": False}


def world_job_status(studio, request_id):
    if not isinstance(request_id, str) or not _ID.fullmatch(request_id):
        raise ValueError("invalid stable world request id")
    with studio.world_job_lock:
        entries, _ = _index(studio)
        if request_id not in entries:
            return {"status": "NOT_FOUND", "request_id": request_id}
        return _read_materialized(studio, entries[request_id], request_id, replay=True)


def _binding(studio, request_id, edits):
    if not isinstance(request_id, str) or not _ID.fullmatch(request_id):
        raise ValueError("invalid stable world request id")
    if not isinstance(edits, dict):
        raise ValueError("world edits must be a JSON object")
    encoded = json.dumps(edits, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(encoded) > MAX_EDIT_BYTES:
        raise ValueError("world edits outside byte budget")
    base = hashlib.sha256((studio.world/"world.glb").read_bytes()).hexdigest()
    input_hash = hashlib.sha256(base.encode("ascii") + b":" + encoded).hexdigest()
    return encoded, base, input_hash


def create_world_job(studio, request_id, edits):
    encoded, base, input_hash = _binding(studio, request_id, edits)
    with studio.world_job_lock:
        entries, path = _index(studio)
        previous = entries.get(request_id)
        if previous is not None:
            if previous.get("input_hash") != input_hash or previous.get("base_hash") != base:
                raise ValueError("request id reused with different input/world")
            return _read_materialized(studio, previous, request_id, replay=True)
        job_id, folder = studio.create_job()
        entries[request_id] = {"status": "STARTED", "job_id": job_id,
                               "input_hash": input_hash, "base_hash": base}
        _atomic_json(path, entries)
        try:
            (folder/"edits.json").write_bytes(encoded)
            result = apply_world_edits(studio.world, folder/"edits.json", folder/"edited")
            target = folder/"edited"/"world.glb"
            raw = target.read_bytes()
            if not raw.startswith(b"glTF") or len(raw) < 28:
                raise RuntimeError("world generator produced invalid GLB")
            entries[request_id].update({"status": "MATERIALIZED",
                                        "world_sha256": hashlib.sha256(raw).hexdigest(),
                                        "buildings": result["buildings"]})
            _atomic_json(path, entries)
        except Exception:
            # Do not silently repeat a side effect whose outcome may be unknown.
            entries[request_id]["status"] = "NEEDS_RECONCILIATION"
            _atomic_json(path, entries)
            raise
        return _read_materialized(studio, entries[request_id], request_id, replay=False)
