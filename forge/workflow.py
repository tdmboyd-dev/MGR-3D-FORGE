"""Dependency-aware creation plan, spend gate and durable local job state.

No provider is executed by this module. Explicit owner approval is mandatory
for external network jobs and any projected paid model use.
"""

from dataclasses import dataclass, asdict
import json
import math
import os
from pathlib import Path
import tempfile


@dataclass(frozen=True)
class Step:
    id: str
    kind: str
    depends_on: tuple[str, ...] = ()
    estimated_usd: float = 0.0
    network_access: bool = False
    license_id: str = "MGR-native"

    def __post_init__(self):
        if (not self.id or not self.kind or not isinstance(self.estimated_usd,(float,int))
                or not math.isfinite(self.estimated_usd) or self.estimated_usd < 0):
            raise ValueError("invalid job step")
        if not self.license_id:
            raise ValueError("license metadata required")
        if not all(isinstance(value, str) for value in self.depends_on):
            raise ValueError("dependencies must be step IDs")


def resolve_plan(steps):
    """Stable topological order; rejects duplicates, missing dependencies, cycles."""
    index = {step.id: step for step in steps}
    if len(index) != len(steps):
        raise ValueError("duplicate IDs")
    ordered, visiting, visited = [], set(), set()

    def visit(node):
        if node in visiting:
            raise ValueError("dependency cycle")
        if node in visited:
            return
        if node not in index:
            raise ValueError(f"missing dependency {node}")
        visiting.add(node)
        for dep in sorted(index[node].depends_on):
            visit(dep)
        visiting.remove(node)
        visited.add(node)
        ordered.append(index[node])

    for step_id in sorted(index):
        visit(step_id)
    return ordered


def approve_plan(steps, *, budget_usd=0.0, approved_step_ids=(),
                 permitted_licenses=("MGR-native",)):
    """Fail closed: paid, online or non-whitelisted-license steps need approval.

    Explicit approval is never implied by a high budget.
    """
    if not isinstance(budget_usd,(int,float)) or not math.isfinite(budget_usd) or budget_usd < 0:
        raise ValueError("negative budget")
    ordered = resolve_plan(steps)
    cost = sum(step.estimated_usd for step in ordered)
    if cost > budget_usd + 1e-9:
        raise PermissionError(f"estimated ${cost:.4f} exceeds approved ${budget_usd:.4f}")
    approvals = set(approved_step_ids)
    licenses = set(permitted_licenses)
    for step in ordered:
        needs_approval = (step.estimated_usd > 0 or step.network_access
                          or step.license_id not in licenses)
        if needs_approval and step.id not in approvals:
            raise PermissionError(f"step {step.id}: explicit approval needed")
    return {"allowed": True, "estimated_usd": round(cost, 6),
            "ordered_ids": [step.id for step in ordered]}


class LocalJobStore:
    """Single-worker durable JSON checkpoint store; not a concurrent job queue."""

    _STATES = {"pending", "running", "failed", "complete"}

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _file(self, job_id):
        if not job_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in job_id):
            raise ValueError("invalid job ID")
        return self.root / f"{job_id}.json"

    def create(self, job_id, steps):
        ordered = resolve_plan(steps)
        record = {"job_id": job_id, "state": "pending", "completed_ids": [],
                  "steps": [asdict(step) for step in ordered]}
        target = self._file(job_id)
        with target.open("x", encoding="utf-8") as handle:
            json.dump(record, handle, sort_keys=True)
        return record

    def read(self, job_id):
        return json.loads(self._file(job_id).read_text(encoding="utf-8"))

    def checkpoint(self, job_id, *, completed_id=None, state="running"):
        if state not in self._STATES:
            raise ValueError("unknown job state")
        record = self.read(job_id)
        if record["state"] == "complete":
            raise ValueError("completed job cannot resume")
        completed = record["completed_ids"]
        if completed_id is not None:
            step = next((s for s in record["steps"] if s["id"] == completed_id), None)
            if step is None:
                raise ValueError("unknown step")
            if not set(step["depends_on"]).issubset(completed):
                raise ValueError("dependencies incomplete")
            if completed_id not in completed:
                completed.append(completed_id)
        if state == "complete" and len(completed) != len(record["steps"]):
            raise ValueError("unfinished steps")
        record["state"] = state
        target = self._file(job_id)
        fd, temp_name = tempfile.mkstemp(prefix=f".{job_id}.", dir=self.root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(record, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return record
