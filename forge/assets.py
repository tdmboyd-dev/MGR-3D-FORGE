"""Content-addressed asset indexing with explicit rights and provenance metadata."""

import hashlib
import json
from pathlib import Path


class AssetRegistry:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index = self.root / "index.json"

    def add(self, asset: bytes, *, owner: str, license_id: str,
            source: str = "MGR-native-generated"):
        if not owner.strip() or not license_id.strip() or not source.strip():
            raise ValueError("asset provenance fields are required")
        digest = hashlib.sha256(asset).hexdigest()
        blob = self.root / "objects" / digest[:2] / digest
        blob.parent.mkdir(parents=True, exist_ok=True)
        if not blob.exists():
            blob.write_bytes(asset)
        entries = json.loads(self.index.read_text()) if self.index.exists() else {}
        metadata = {"sha256": digest, "bytes": len(asset), "owner": owner,
                    "license": license_id, "source": source,
                    "relative_path": str(blob.relative_to(self.root))}
        if digest in entries and entries[digest] != metadata:
            raise ValueError("content hash reused with conflicting provenance")
        entries[digest] = metadata
        temporary = self.index.with_suffix(".tmp")
        temporary.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n")
        temporary.replace(self.index)
        return metadata

    def get(self, digest):
        if not isinstance(digest, str) or not re_sha256(digest):
            raise ValueError("invalid sha256")
        entries = json.loads(self.index.read_text())
        record = entries[digest]
        asset = self.root / "objects" / digest[:2] / digest
        contents = asset.read_bytes()
        if hashlib.sha256(contents).hexdigest() != digest:
            raise ValueError("asset hash mismatch")
        return contents, record


def re_sha256(value):
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
