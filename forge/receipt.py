"""Cryptographic artifact receipts and tamper checks for generated bundles."""

import hashlib
import json
from pathlib import Path


def file_receipt(path):
    data=Path(path).read_bytes()
    return {"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}


def verify_bundle(directory):
    root=Path(directory).resolve()
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    inventory=manifest.get("artifact_inventory",{})
    if not inventory:
        raise ValueError("artifact inventory missing")
    for name,expected in inventory.items():
        if not isinstance(name,str) or Path(name).name!=name or name.startswith("."):
            raise ValueError("unsafe artifact name")
        file=root/name
        if not file.is_file() or file.resolve().parent!=root:
            raise ValueError(f"missing or redirected artifact: {name}")
        actual=file_receipt(file)
        if actual!=expected:
            raise ValueError(f"artifact integrity mismatch: {name}")
    return {"passed":True,"files":len(inventory),
            "verified_bytes":sum(item["bytes"] for item in inventory.values())}
