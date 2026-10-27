"""Durable local job queue with file-based checkpointing.

Upgrades the Studio's process-local workers to a file-based queue that survives
process restarts. Jobs are enqueued as JSON files in a queue directory; a
worker process (or thread) claims them by renaming to a "running" suffix and
writes progress to a checkpoint file. On restart, any "running" job is marked
interrupted and can be retried.

This is single-machine, single-writer coordination via filesystem rename
(atomic on most platforms). It is NOT a distributed queue.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Callable

SCHEMA = "mgr.forge.durable-job-queue.v1"


@dataclass
class JobSpec:
    job_id: str
    kind: str
    payload: dict = field(default_factory=dict)
    max_attempts: int = 3
    created_at: float = field(default_factory=time.time)


@dataclass
class JobState:
    job_id: str
    kind: str
    status: str = "queued"  # queued | running | done | failed | interrupted
    attempt: int = 0
    created_at: float = 0.0
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    progress: float = 0.0


class DurableJobQueue:
    """File-based durable job queue."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.queued_dir = self.root / "queued"
        self.running_dir = self.root / "running"
        self.done_dir = self.root / "done"
        self.failed_dir = self.root / "failed"
        for d in (self.queued_dir, self.running_dir, self.done_dir, self.failed_dir):
            d.mkdir(exist_ok=True)

    def _job_path(self, directory: Path, job_id: str) -> Path:
        return directory / f"{job_id}.json"

    def enqueue(self, spec: JobSpec) -> JobState:
        state = JobState(job_id=spec.job_id, kind=spec.kind,
                         created_at=spec.created_at)
        state.status = "queued"
        path = self._job_path(self.queued_dir, spec.job_id)
        if path.exists():
            raise ValueError(f"job already queued: {spec.job_id}")
        # store spec alongside state
        data = {"spec": asdict(spec), "state": asdict(state)}
        path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
        return state

    def _read(self, path: Path) -> dict:
        if not path.is_file() or path.stat().st_size > 1_000_000:
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError):
            return None

    def claim_next(self) -> Optional[tuple[JobSpec, JobState]]:
        """Atomically claim the next queued job. Returns (spec, state) or None."""
        queued = sorted(self.queued_dir.glob("*.json"))
        for path in queued:
            data = self._read(path)
            if data is None:
                continue
            job_id = data["state"]["job_id"]
            running_path = self._job_path(self.running_dir, job_id)
            try:
                path.rename(running_path)  # atomic claim
            except OSError:
                continue  # another worker claimed it
            # update state
            data["state"]["status"] = "running"
            data["state"]["started_at"] = time.time()
            data["state"]["attempt"] = data["state"].get("attempt", 0) + 1
            running_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
            spec = JobSpec(**data["spec"])
            state = JobState(**data["state"])
            return spec, state
        return None

    def update_progress(self, job_id: str, progress: float, **extra) -> None:
        path = self._job_path(self.running_dir, job_id)
        data = self._read(path)
        if data is None:
            return
        data["state"]["progress"] = max(0.0, min(1.0, progress))
        data["state"].update(extra)
        path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")

    def complete(self, job_id: str, result: dict) -> JobState:
        path = self._job_path(self.running_dir, job_id)
        data = self._read(path)
        if data is None:
            raise ValueError(f"running job not found: {job_id}")
        data["state"]["status"] = "done"
        data["state"]["finished_at"] = time.time()
        data["state"]["result"] = result
        data["state"]["progress"] = 1.0
        done_path = self._job_path(self.done_dir, job_id)
        path.rename(done_path)
        done_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
        return JobState(**data["state"])

    def fail(self, job_id: str, error: str) -> JobState:
        path = self._job_path(self.running_dir, job_id)
        data = self._read(path)
        if data is None:
            raise ValueError(f"running job not found: {job_id}")
        spec = JobSpec(**data["spec"])
        attempt = data["state"].get("attempt", 1)
        if attempt < spec.max_attempts:
            # re-queue
            data["state"]["status"] = "queued"
            data["state"]["error"] = error
            data["state"]["started_at"] = None
            queued_path = self._job_path(self.queued_dir, job_id)
            path.rename(queued_path)
            queued_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
            return JobState(**data["state"])
        else:
            data["state"]["status"] = "failed"
            data["state"]["finished_at"] = time.time()
            data["state"]["error"] = error
            failed_path = self._job_path(self.failed_dir, job_id)
            path.rename(failed_path)
            failed_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
            return JobState(**data["state"])

    def recover_interrupted(self) -> list[str]:
        """On startup, mark running jobs as interrupted and re-queue if possible."""
        recovered = []
        for path in self.running_dir.glob("*.json"):
            data = self._read(path)
            if data is None:
                continue
            job_id = data["state"]["job_id"]
            spec = JobSpec(**data["spec"])
            attempt = data["state"].get("attempt", 1)
            if attempt < spec.max_attempts:
                data["state"]["status"] = "queued"
                data["state"]["error"] = "interrupted by restart"
                queued_path = self._job_path(self.queued_dir, job_id)
                path.rename(queued_path)
                queued_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
            else:
                data["state"]["status"] = "interrupted"
                data["state"]["finished_at"] = time.time()
                data["state"]["error"] = "interrupted by restart (max attempts reached)"
                failed_path = self._job_path(self.failed_dir, job_id)
                path.rename(failed_path)
                failed_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
            recovered.append(job_id)
        return recovered

    def status(self, job_id: str) -> Optional[JobState]:
        for d in (self.queued_dir, self.running_dir, self.done_dir, self.failed_dir):
            path = self._job_path(d, job_id)
            if path.is_file():
                data = self._read(path)
                if data:
                    return JobState(**data["state"])
        return None

    def counts(self) -> dict:
        return {
            "queued": len(list(self.queued_dir.glob("*.json"))),
            "running": len(list(self.running_dir.glob("*.json"))),
            "done": len(list(self.done_dir.glob("*.json"))),
            "failed": len(list(self.failed_dir.glob("*.json"))),
        }
