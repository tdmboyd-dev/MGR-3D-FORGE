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
            source: str = "MGR-native-generated", extra: dict | None = None):
        if not owner.strip() or not license_id.strip() or not source.strip():
            raise ValueError("asset provenance fields are required")
        if extra is not None and (not isinstance(extra, dict) or
                                  any(key not in {"title", "category", "provider_id", "source_slug",
                                                  "rights_reviewed", "geometry_status"} for key in extra)):
            raise ValueError("unsupported asset provenance extension")
        digest = hashlib.sha256(asset).hexdigest()
        blob = self.root / "objects" / digest[:2] / digest
        entries = json.loads(self.index.read_text()) if self.index.exists() else {}
        metadata = {"sha256": digest, "bytes": len(asset), "owner": owner,
                    "license": license_id, "source": source,
                    "relative_path": str(blob.relative_to(self.root))}
        if extra:
            metadata.update(extra)
        if digest in entries and entries[digest] != metadata:
            raise ValueError("content hash reused with conflicting provenance")
        # Validate provenance before touching the object store. If a previous
        # object was tampered with, never let this add silently bless it.
        if blob.exists():
            if hashlib.sha256(blob.read_bytes()).hexdigest() != digest:
                raise ValueError("existing asset hash mismatch")
        else:
            blob.parent.mkdir(parents=True, exist_ok=True)
            with blob.open("xb") as stream:
                stream.write(asset)
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
