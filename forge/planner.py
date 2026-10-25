"""Bounded natural-language-to-world planner; offline deterministic rules, not an LLM."""

import re
from dataclasses import dataclass

from .spec import WorldSpec


@dataclass(frozen=True)
class Plan:
    method: str
    reason: str
    external_cost_usd: float
    spec: WorldSpec

    def as_dict(self):
        return {"schema": "mgr.forge.plan.v1", "method": self.method,
                "reason": self.reason, "external_cost_usd": self.external_cost_usd,
                "spec": self.spec.as_dict()}


def plan_neighborhood(prompt: str, *, seed=8964) -> Plan:
    """Extract a building count from a limited phrase; never pretend broad understanding."""
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4096:
        raise ValueError("prompt must be 1-4096 characters")
    match = re.search(r"\b(\d{1,4})\s+(?:buildings?|houses?)\b", prompt, re.I)
    count = int(match.group(1)) if match else 10
    if count > 1000:
        raise ValueError("CPU baseline limits generated buildings to 1000")
    columns = max(1, int(count ** 0.5 + 0.999999))
    rows = max(1, (count + columns - 1) // columns)
    if max(rows, columns) > 100:
        raise ValueError("requested scene exceeds region limit")
    spec = WorldSpec(seed=seed, columns=columns, rows=rows, buildings=count,
                     name=prompt.strip()[:120])
    return Plan(method="cpu-procedural", reason="Structured building/road layout needs no neural model",
                external_cost_usd=0.0, spec=spec)
