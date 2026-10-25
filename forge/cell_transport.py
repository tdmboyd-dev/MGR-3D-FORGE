"""Bounded, integrity-checked local 3D cell transport with deterministic LRU.

Real disk reads and memory residency, no rendering/network/thread promises.
"""

from collections import OrderedDict
import hashlib
import json
from pathlib import Path
import re


_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}\Z")


class MGRCellTransport:
    def __init__(self, root, manifest, *, memory_budget_bytes=8_000_000):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise ValueError("existing warehouse directory required")
        if type(memory_budget_bytes) is not int or not 1 <= memory_budget_bytes <= 512_000_000:
            raise ValueError("finite bounded memory budget required")
        if not isinstance(manifest, dict) or not 1 <= len(manifest) <= 10_000:
            raise ValueError("nonempty bounded manifest required")
        for key, info in manifest.items():
            if not isinstance(key, str) or not _ID.fullmatch(key):
                raise ValueError("unsafe cell identifier")
            if (not isinstance(info, dict) or set(info) != {"sha256", "bytes"}
                    or not isinstance(info["sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", info["sha256"])
                    or type(info["bytes"]) is not int or not 0 < info["bytes"] <= 512_000_000):
                raise ValueError("invalid size/hash cell receipt")
        self.manifest = manifest
        self.budget = memory_budget_bytes
        self.cache = OrderedDict()
        self.bytes = 0
        self.reads = 0

    def _path(self, cell_id):
        if not isinstance(cell_id, str) or not _ID.fullmatch(cell_id):
            raise ValueError("unsafe cell name")
        target = self.root / (cell_id + ".glb")
        if target.is_symlink() or target.resolve().parent != self.root:
            raise ValueError("cell path must stay inside warehouse")
        return target

    def get(self, cell_id):
        if cell_id not in self.manifest:
            raise KeyError(cell_id)
        if cell_id in self.cache:
            self.cache.move_to_end(cell_id)
            return self.cache[cell_id]
        record = self.manifest[cell_id]
        if record["bytes"] > self.budget:
            raise ValueError("cell larger than memory budget")
        path = self._path(cell_id)
        if not path.is_file() or path.stat().st_size != record["bytes"]:
            raise ValueError("cell missing or size mismatched")
        payload = path.read_bytes()
        self.reads += 1
        if hashlib.sha256(payload).hexdigest() != record["sha256"]:
            raise ValueError("cell content integrity mismatch")
        while self.bytes + len(payload) > self.budget:
            _, previous = self.cache.popitem(last=False)
            self.bytes -= len(previous)
        self.cache[cell_id] = payload
        self.bytes += len(payload)
        return payload

    def apply_plan(self, plan):
        """Read prioritized active cells and optional prefetch; return actual results."""
        if (not isinstance(plan, dict) or plan.get("status") != "PLAN_ONLY"
                or not isinstance(plan.get("active"), list)
                or not isinstance(plan.get("prefetch"), list)
                or not isinstance(plan.get("evict"), list)):
            raise ValueError("validated residency plan required")
        requested = plan["active"] + plan["prefetch"]
        if len(requested) > 10_000 or len(set(requested)) != len(requested):
            raise ValueError("invalid requested residency set")
        for name in plan["evict"]:
            if name in self.cache:
                self.bytes -= len(self.cache.pop(name))
        loaded, skipped, faults = [], [], {}
        protected = set()
        for name in requested:
            if name not in self.manifest:
                faults[name] = "UNKNOWN_CELL"
                continue
            if self.manifest[name]["bytes"] > self.budget:
                skipped.append(name)
                continue
            required = 0 if name in self.cache else self.manifest[name]["bytes"]
            # Unload old/stale cells before touching a requested active cell.
            # Never silently evict an active cell loaded earlier this tick.
            while self.bytes + required > self.budget:
                candidate = next((key for key in self.cache if key not in protected), None)
                if candidate is None:
                    skipped.append(name)
                    break
                self.bytes -= len(self.cache.pop(candidate))
            if name in skipped:
                continue
            try:
                self.get(name)
                loaded.append(name)
                if name in plan["active"]:
                    protected.add(name)
            except (ValueError, OSError) as exc:
                faults[name] = str(exc)
        return {"schema": "mgr.forge.cell-transport.v1",
                "status": "PASS" if not faults else "PARTIAL_FAILURE",
                "resident": list(self.cache), "loaded": loaded, "skipped": skipped,
                "faults": faults, "disk_reads": self.reads,
                "resident_bytes": self.bytes, "memory_budget_bytes": self.budget,
                "limitations": ["local synchronous GLB transport only, no renderer/GPU residency",
                                "no async load, FPS, network or collision-continuity proof"]}
