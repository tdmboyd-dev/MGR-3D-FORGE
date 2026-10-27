"""GPU instance lifecycle and per-user billing ledger.

Pure CPU bookkeeping. No real provider calls, no money. Real lifecycle
management happens behind a GpuProvider (see forge.gpu_rental); this module
tracks what happened and who owes what, for auditing and billing receipts.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

SCHEMA_INSTANCE = "mgr.forge.gpu-instance.v1"
SCHEMA_LEDGER = "mgr.forge.gpu-billing-ledger.v1"


@dataclass
class InstanceRecord:
    instance_id: str
    provider: str
    gpu_type: str
    cost_per_hour: float
    started_at: float
    terminated_at: Optional[float] = None
    jobs: list = field(default_factory=list)
    status: str = "running"  # running | terminated

    @property
    def runtime_seconds(self) -> float:
        end = self.terminated_at if self.terminated_at is not None else time.time()
        return max(0.0, end - self.started_at)

    @property
    def billed_hours(self) -> float:
        # bill in whole-hour increments, minimum 1 hour
        import math
        hours = self.runtime_seconds / 3600.0
        return max(1.0, math.ceil(hours * 1000) / 1000.0)

    @property
    def cost(self) -> float:
        return round(self.billed_hours * self.cost_per_hour, 6)


@dataclass
class UserAccount:
    user_id: str
    pool_hours: float = 0.0  # pre-purchased GPU hours
    used_hours: float = 0.0
    instances: list = field(default_factory=list)

    @property
    def remaining_pool_hours(self) -> float:
        return max(0.0, self.pool_hours - self.used_hours)


class InstanceManager:
    """Tracks GPU instances and their lifecycle."""

    def __init__(self):
        self._instances: dict[str, InstanceRecord] = {}

    def register(self, record: InstanceRecord) -> None:
        if record.instance_id in self._instances:
            raise ValueError(f"duplicate instance id: {record.instance_id}")
        self._instances[record.instance_id] = record

    def get(self, instance_id: str) -> InstanceRecord:
        if instance_id not in self._instances:
            raise KeyError(f"unknown instance: {instance_id}")
        return self._instances[instance_id]

    def terminate(self, instance_id: str, *, at: Optional[float] = None) -> InstanceRecord:
        rec = self.get(instance_id)
        if rec.status == "terminated":
            raise ValueError(f"instance already terminated: {instance_id}")
        rec.terminated_at = at if at is not None else time.time()
        rec.status = "terminated"
        return rec

    def running(self) -> list[InstanceRecord]:
        return [r for r in self._instances.values() if r.status == "running"]

    def all_instances(self) -> list[InstanceRecord]:
        return list(self._instances.values())

    def total_cost(self) -> float:
        return round(sum(r.cost for r in self._instances.values()), 6)

    def shadow_available_seconds(self, instance_id: str) -> float:
        """Spare seconds in the current billing hour for shadow jobs."""
        rec = self.get(instance_id)
        if rec.status != "running":
            return 0.0
        # remaining in the current hour
        elapsed_in_hour = rec.runtime_seconds % 3600.0
        return max(0.0, 3600.0 - elapsed_in_hour)


class BillingLedger:
    """Per-user GPU hour accounting and billing receipts."""

    def __init__(self):
        self._accounts: dict[str, UserAccount] = {}
        self._receipts: list[dict] = []

    def get_or_create_account(self, user_id: str) -> UserAccount:
        if user_id not in self._accounts:
            self._accounts[user_id] = UserAccount(user_id=user_id)
        return self._accounts[user_id]

    def allocate_pool(self, user_id: str, hours: float) -> UserAccount:
        if hours < 0:
            raise ValueError("hours must be >= 0")
        acct = self.get_or_create_account(user_id)
        acct.pool_hours += hours
        return acct

    def charge(self, user_id: str, instance: InstanceRecord) -> dict:
        acct = self.get_or_create_account(user_id)
        hours = instance.billed_hours
        if acct.remaining_pool_hours < hours:
            raise ValueError(
                f"insufficient pool hours: need {hours}, have {acct.remaining_pool_hours}")
        acct.used_hours += hours
        instance.jobs.append(user_id)
        receipt = {
            "schema": SCHEMA_LEDGER,
            "user_id": user_id,
            "instance_id": instance.instance_id,
            "gpu_type": instance.gpu_type,
            "billed_hours": hours,
            "cost": instance.cost,
            "remaining_pool_hours": acct.remaining_pool_hours,
        }
        self._receipts.append(receipt)
        return receipt

    def receipts(self, user_id: Optional[str] = None) -> list[dict]:
        if user_id is None:
            return list(self._receipts)
        return [r for r in self._receipts if r["user_id"] == user_id]

    def total_billed(self, user_id: Optional[str] = None) -> float:
        rs = self.receipts(user_id)
        return round(sum(r["cost"] for r in rs), 6)

    def pool_status(self, user_id: str) -> dict:
        acct = self.get_or_create_account(user_id)
        return {
            "user_id": user_id,
            "pool_hours": acct.pool_hours,
            "used_hours": acct.used_hours,
            "remaining_pool_hours": acct.remaining_pool_hours,
        }
