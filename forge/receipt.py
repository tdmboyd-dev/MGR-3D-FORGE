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
    if not isinstance(manifest,dict):
        raise ValueError("bundle manifest object required")
    inventory=manifest.get("artifact_inventory",{})
    if not isinstance(inventory,dict) or not inventory:
        raise ValueError("artifact inventory missing")
    # A valid subset of hashes must not qualify a different/missing main asset
    # or omit a sidecar that the same manifest advertises as part of the bundle.
    if "artifact" in manifest:
        artifact=manifest["artifact"]
        if not isinstance(artifact,dict) or not isinstance(artifact.get("path"),str):
            raise ValueError("invalid primary artifact declaration")
        expected={key:artifact.get(key) for key in ("sha256","bytes")}
        if inventory.get(artifact["path"])!=expected:
            raise ValueError("primary artifact is not bound to artifact inventory")
    if "additional_artifacts" in manifest:
        additional=manifest["additional_artifacts"]
        if not isinstance(additional,dict) or any(not isinstance(name,str) or name not in inventory
                                                 for name in additional.values()):
            raise ValueError("declared sidecar missing from artifact inventory")
    for name,expected in inventory.items():
        if not isinstance(name,str) or Path(name).name!=name or name.startswith("."):
            raise ValueError("unsafe artifact name")
        if (not isinstance(expected,dict) or set(expected)!={"sha256","bytes"}
                or type(expected["bytes"]) is not int or expected["bytes"]<0
                or not isinstance(expected["sha256"],str) or len(expected["sha256"])!=64
                or any(char not in "0123456789abcdef" for char in expected["sha256"])):
            raise ValueError("invalid artifact receipt")
        file=root/name
        if not file.is_file() or file.resolve().parent!=root:
            raise ValueError(f"missing or redirected artifact: {name}")
        actual=file_receipt(file)
        if actual!=expected:
            raise ValueError(f"artifact integrity mismatch: {name}")
    return {"passed":True,"files":len(inventory),
            "verified_bytes":sum(item["bytes"] for item in inventory.values())}
