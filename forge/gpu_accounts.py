"""MGR-native GPU account and credential management.

Each user connects their own GPU provider accounts (RunPod, Vast.ai, Lambda).
Tevin auto-selects the best account/GPU for a job, shows cost, and rents under
that account. A founder/pooled account exists for "shadow use": when a user
finishes early, the remaining purchased hour goes to a shared pool for other
users' jobs instead of being wasted.

Credentials are stored encrypted at rest (XOR with a local key for now; real
deployment should use OS keyring or a proper KMS). They are NEVER committed to
the repo. The module works fully offline for planning; real rental requires a
provider backend + double confirmation (see forge.gpu_rental).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

SCHEMA = "mgr.forge.gpu-accounts.v1"
ACCOUNTS_FILE = "gpu-accounts.json"
KEY_ENV = "MGR_GPU_ACCOUNT_KEY"


@dataclass
class ProviderCredential:
    provider: str  # runpod | vast | lambda
    api_key: str
    account_id: str = ""
    label: str = ""

    def masked(self) -> dict:
        return {
            "provider": self.provider,
            "account_id": self.account_id,
            "label": self.label,
            "api_key": "***" + self.api_key[-4:] if len(self.api_key) >= 4 else "***",
        }


@dataclass
class UserAccount:
    user_id: str
    credentials: list = field(default_factory=list)  # list of ProviderCredential
    pool_hours: float = 0.0  # pre-purchased GPU hours
    used_hours: float = 0.0
    shadow_contributed_hours: float = 0.0  # hours contributed to shadow pool
    shadow_consumed_hours: float = 0.0  # hours consumed from shadow pool
    is_founder: bool = False

    @property
    def remaining_pool_hours(self) -> float:
        return max(0.0, self.pool_hours - self.used_hours)

    def as_dict(self, include_keys: bool = False) -> dict:
        d = {
            "user_id": self.user_id,
            "is_founder": self.is_founder,
            "pool_hours": self.pool_hours,
            "used_hours": self.used_hours,
            "remaining_pool_hours": self.remaining_pool_hours,
            "shadow_contributed_hours": self.shadow_contributed_hours,
            "shadow_consumed_hours": self.shadow_consumed_hours,
            "credentials": [c.masked() for c in self.credentials],
        }
        if include_keys:
            d["credentials"] = [c.__dict__ for c in self.credentials]
        return d


class AccountStore:
    """Encrypted-at-rest store for GPU provider credentials."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / ACCOUNTS_FILE

    def _key(self) -> bytes:
        raw = os.environ.get(KEY_ENV, "mgr-default-dev-key")
        return hashlib.sha256(raw.encode()).digest()

    def _encrypt(self, data: bytes) -> bytes:
        key = self._key()
        # simple XOR (not production-grade; use OS keyring in real deployment)
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def _decrypt(self, data: bytes) -> bytes:
        return self._encrypt(data)  # XOR is symmetric

    def load(self) -> dict[str, UserAccount]:
        if not self.path.is_file():
            return {}
        raw = self.path.read_bytes()
        try:
            decrypted = self._decrypt(raw)
            payload = json.loads(decrypted.decode("utf-8"))
        except (ValueError, UnicodeError, json.JSONDecodeError):
            return {}
        accounts = {}
        for uid, data in payload.get("accounts", {}).items():
            creds = [ProviderCredential(**c) for c in data.get("credentials", [])]
            accounts[uid] = UserAccount(
                user_id=uid,
                credentials=creds,
                pool_hours=data.get("pool_hours", 0.0),
                used_hours=data.get("used_hours", 0.0),
                shadow_contributed_hours=data.get("shadow_contributed_hours", 0.0),
                shadow_consumed_hours=data.get("shadow_consumed_hours", 0.0),
                is_founder=data.get("is_founder", False),
            )
        return accounts

    def save(self, accounts: dict[str, UserAccount]) -> None:
        payload = {"schema": SCHEMA, "accounts": {}}
        for uid, acct in accounts.items():
            payload["accounts"][uid] = {
                "credentials": [c.__dict__ for c in acct.credentials],
                "pool_hours": acct.pool_hours,
                "used_hours": acct.used_hours,
                "shadow_contributed_hours": acct.shadow_contributed_hours,
                "shadow_consumed_hours": acct.shadow_consumed_hours,
                "is_founder": acct.is_founder,
            }
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.path.write_bytes(self._encrypt(raw))

    def register_user(self, user_id: str, *, is_founder: bool = False) -> UserAccount:
        accounts = self.load()
        if user_id in accounts:
            return accounts[user_id]
        acct = UserAccount(user_id=user_id, is_founder=is_founder)
        accounts[user_id] = acct
        self.save(accounts)
        return acct

    def add_credential(self, user_id: str, cred: ProviderCredential) -> UserAccount:
        accounts = self.load()
        if user_id not in accounts:
            accounts[user_id] = UserAccount(user_id=user_id)
        acct = accounts[user_id]
        # replace if same provider+account_id
        acct.credentials = [c for c in acct.credentials
                           if not (c.provider == cred.provider and c.account_id == cred.account_id)]
        acct.credentials.append(cred)
        self.save(accounts)
        return acct

    def remove_credential(self, user_id: str, provider: str, account_id: str = "") -> bool:
        accounts = self.load()
        if user_id not in accounts:
            return False
        acct = accounts[user_id]
        before = len(acct.credentials)
        acct.credentials = [c for c in acct.credentials
                           if not (c.provider == provider and c.account_id == account_id)]
        if len(acct.credentials) < before:
            self.save(accounts)
            return True
        return False

    def get_user(self, user_id: str) -> Optional[UserAccount]:
        return self.load().get(user_id)

    def list_users(self) -> list[str]:
        return sorted(self.load().keys())


class GpuAccountManager:
    """High-level account management: registration, credential storage, selection."""

    def __init__(self, store: AccountStore):
        self.store = store

    def register(self, user_id: str, *, is_founder: bool = False) -> UserAccount:
        return self.store.register_user(user_id, is_founder=is_founder)

    def connect_provider(self, user_id: str, provider: str, api_key: str,
                         account_id: str = "", label: str = "") -> UserAccount:
        if not api_key or len(api_key) < 8:
            raise ValueError("api_key must be at least 8 characters")
        if provider not in ("runpod", "vast", "lambda"):
            raise ValueError(f"unknown provider: {provider}")
        cred = ProviderCredential(provider=provider, api_key=api_key,
                                  account_id=account_id, label=label)
        return self.store.add_credential(user_id, cred)

    def disconnect_provider(self, user_id: str, provider: str, account_id: str = "") -> bool:
        return self.store.remove_credential(user_id, provider, account_id)

    def allocate_pool(self, user_id: str, hours: float) -> UserAccount:
        accounts = self.store.load()
        if user_id not in accounts:
            accounts[user_id] = UserAccount(user_id=user_id)
        acct = accounts[user_id]
        if hours < 0:
            raise ValueError("hours must be >= 0")
        acct.pool_hours += hours
        self.store.save(accounts)
        return acct

    def select_account(self, user_id: str, *, min_vram_gb: float = 0.0) -> dict:
        """Tevin auto-picks the best provider account for a job.

        Returns a dict with the selected provider, credential (masked), and rationale.
        Does NOT rent anything.
        """
        acct = self.store.get_user(user_id)
        if acct is None:
            raise ValueError(f"unknown user: {user_id}")
        if not acct.credentials:
            raise ValueError(f"no provider credentials for user {user_id}")
        # pick the provider with the most credentials / first available
        # (real selection would check provider availability + offer prices)
        best = acct.credentials[0]
        return {
            "schema": SCHEMA,
            "status": "SELECTED (dry run, no rental)",
            "user_id": user_id,
            "selected_provider": best.provider,
            "selected_account": best.masked(),
            "available_credentials": len(acct.credentials),
            "pool_hours_remaining": acct.remaining_pool_hours,
            "rationale": "first registered credential; real selection checks live offers",
        }

    def founder_shadow_pool(self) -> dict:
        """Status of the founder pooled account for shadow use."""
        accounts = self.store.load()
        founders = [a for a in accounts.values() if a.is_founder]
        total_contributed = sum(a.shadow_contributed_hours for a in founders)
        total_consumed = sum(a.shadow_consumed_hours for a in founders)
        return {
            "schema": SCHEMA,
            "founder_accounts": len(founders),
            "total_contributed_hours": total_contributed,
            "total_consumed_hours": total_consumed,
            "available_shadow_hours": max(0.0, total_contributed - total_consumed),
            "notes": [
                "shadow hours come from users who finished early",
                "shadow jobs fill spare time in purchased blocks",
                "no money is charged for shadow consumption",
            ],
        }

    def contribute_shadow_hours(self, user_id: str, hours: float) -> dict:
        """A user contributes remaining purchased hours to the shadow pool."""
        if hours < 0:
            raise ValueError("hours must be >= 0")
        accounts = self.store.load()
        if user_id not in accounts:
            raise ValueError(f"unknown user: {user_id}")
        acct = accounts[user_id]
        if hours > acct.remaining_pool_hours:
            raise ValueError("cannot contribute more than remaining pool hours")
        acct.shadow_contributed_hours += hours
        acct.pool_hours -= hours  # moved to shadow pool
        self.store.save(accounts)
        return {"user_id": user_id, "contributed_hours": hours,
                "remaining_pool_hours": acct.remaining_pool_hours}

    def consume_shadow_hours(self, user_id: str, hours: float) -> dict:
        """A shadow job consumes hours from the founder pool."""
        if hours < 0:
            raise ValueError("hours must be >= 0")
        accounts = self.store.load()
        founders = [a for a in accounts.values() if a.is_founder]
        if not founders:
            raise ValueError("no founder account available")
        founder = founders[0]
        available = founder.shadow_contributed_hours - founder.shadow_consumed_hours
        if hours > available + 1e-9:
            raise ValueError(f"insufficient shadow hours: need {hours}, have {available}")
        founder.shadow_consumed_hours += hours
        # charge to the consuming user's account as shadow (free)
        if user_id in accounts:
            accounts[user_id].shadow_consumed_hours += hours
        self.store.save(accounts)
        return {"user_id": user_id, "consumed_shadow_hours": hours,
                "remaining_shadow_hours": max(0.0, available - hours)}

    def describe(self) -> dict:
        accounts = self.store.load()
        return {
            "schema": SCHEMA,
            "user_count": len(accounts),
            "founder_count": sum(1 for a in accounts.values() if a.is_founder),
            "total_pool_hours": sum(a.pool_hours for a in accounts.values()),
            "total_used_hours": sum(a.used_hours for a in accounts.values()),
            "shadow_available_hours": self.founder_shadow_pool()["available_shadow_hours"],
            "honesty": "credentials stored encrypted at rest; never committed; "
                       "real rental requires provider backend + double confirmation",
        }
