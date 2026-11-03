"""Bounded read-only navigation over original creation journals.

Journal state is an observation, not artifact acceptance. Reopening delegates
to each original status reader; this module never starts or retries a job.
"""
import hashlib
import json
import re

from .world_jobs import _index, _ID, world_job_status
from .creature_jobs import creature_job_status
from .biome_jobs import biome_job_status
from .human_jobs import human_lipsync_job_status
from .world_composition_jobs import world_composition_status
from .creation_asset_jobs import asset_job_status

SOURCES = {
    "world": ("world-requests.json", world_job_status),
    "creature": ("creature-requests.json", creature_job_status),
    "biome": ("biome-requests.json", biome_job_status),
    "human": ("human-lipsync-requests.json", human_lipsync_job_status),
    "composed": ("world-composition-requests.json", world_composition_status),
    "reconstruction": ("reconstruction-requests.json", lambda studio, rid: asset_job_status(studio, 'reconstruction', rid)),
    "morph": ("morph-requests.json", lambda studio, rid: asset_job_status(studio, 'morph', rid)),
    "uv": ("uv-requests.json", lambda studio, rid: asset_job_status(studio, 'uv', rid)),
}
STATES = {"STARTED", "RUNNING", "MATERIALIZED", "FAILED", "NEEDS_RECONCILIATION"}


def list_saved_jobs(studio, payload):
    if not isinstance(payload, dict) or set(payload) - {"kind", "limit", "cursor"}:
        raise ValueError("saved jobs accepts only kind, limit and cursor")
    kind, limit, cursor = payload.get("kind", "all"), payload.get("limit", 20), payload.get("cursor", "")
    if not isinstance(kind, str) or kind not in ("all", *SOURCES):
        raise ValueError("unknown saved creation kind")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("saved creation page size must be 1..20")
    if not isinstance(cursor, str) or (cursor and not re.fullmatch(r"[a-f0-9]{64}:[0-9]{1,4}", cursor)):
        raise ValueError("invalid saved creation cursor")
    items, unavailable = [], []
    with studio.world_job_lock:
        for name, (ledger, _) in SOURCES.items():
            if kind != "all" and kind != name:
                continue
            try:
                rows, _ = _index(studio, ledger)
                selected = []
                for rid, row in rows.items():
                    if (not isinstance(rid, str) or not _ID.fullmatch(rid) or
                            not isinstance(row, dict) or not isinstance(row.get("status"), str) or
                            row["status"] not in STATES or
                            not isinstance(row.get("job_id"), str) or
                            not re.fullmatch(r"[a-f0-9]{24}", row["job_id"])):
                        raise ValueError("invalid saved journal row")
                    state = row["status"]
                    if state == "STARTED" or (state == "RUNNING" and rid not in getattr(
                            studio, "human_active_jobs" if name == "human" else "composed_active_jobs", set())):
                        state = "NEEDS_RECONCILIATION"
                    selected.append({"kind": name, "request_id": rid, "job_id": row["job_id"],
                                     "status": state, "artifact_verified": False})
                items.extend(selected)
            except (ValueError, OSError, UnicodeError):
                # Keep unaffected journals usable without leaking local paths/data.
                unavailable.append(name)
    items.sort(key=lambda row: (row["kind"], row["request_id"]))
    revision = hashlib.sha256(json.dumps([kind, items, unavailable], sort_keys=True).encode()).hexdigest()
    offset = 0
    if cursor:
        previous, raw_offset = cursor.split(":")
        offset = int(raw_offset)
        if previous != revision:
            raise ValueError("saved creations changed; refresh the list")
        if not 0 < offset < len(items):
            raise ValueError("saved creation cursor outside results")
    stop = offset + limit
    return {"schema": "mgr.forge.saved-jobs.v1", "status": "JOURNAL_OBSERVATION",
            "items": items[offset:stop], "total": len(items), "unavailable_kinds": unavailable,
            "next_cursor": f"{revision}:{stop}" if stop < len(items) else None,
            "order": "kind_then_request_id", "creates_jobs": False}


def reopen_saved_job(studio, payload):
    if not isinstance(payload, dict) or set(payload) != {"kind", "request_id"}:
        raise ValueError("reopen requires kind and request_id only")
    kind = payload["kind"]
    if not isinstance(kind, str) or kind not in SOURCES:
        raise ValueError("unknown saved creation kind")
    # Original readers validate the request, running-worker state and artifact.
    return SOURCES[kind][1](studio, payload["request_id"])
