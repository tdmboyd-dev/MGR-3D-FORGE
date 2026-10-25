"""MGR Code Architect: inspectable, recoverable workspace-file jobs.

This starter deliberately does NOT execute generated commands or claim to
provide an operating-system sandbox. A future isolated runner is needed for
arbitrary code execution and untrusted subprocesses.
"""

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import tempfile


@dataclass(frozen=True)
class FileChange:
    path: str
    content: str
    expected_sha256: str | None = None


def _safe_relative(name):
    if not isinstance(name, str) or not name or "\\" in name or "\0" in name:
        raise ValueError("unsafe file path")
    rel = PurePosixPath(name)
    if rel.is_absolute() or any(part in ("..", ".") for part in name.split("/")):
        raise ValueError("path escapes job root")
    if str(rel) != name or ":" in name:
        raise ValueError("noncanonical file path")
    return rel


def _checked_destination(root, rel):
    path = root.joinpath(*rel.parts)
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise PermissionError("symlink target blocked")
    if not path.resolve().is_relative_to(root.resolve()):
        raise PermissionError("path outside workspace")
    return path


class WorkspaceFileJob:
    """Atomic writes with preconditions and an on-disk rollback manifest.

    The workspace must be a dedicated job directory. Never point this at a
    shared home folder or repository root containing unrelated files.
    """

    def __init__(self, root, *, max_files=30, max_bytes=2_000_000):
        supplied=Path(root)
        if supplied.is_symlink():
            raise ValueError("symlink workspaces prohibited")
        self.root = supplied.resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("workspace must be an existing real directory")
        self.max_files, self.max_bytes = max_files, max_bytes

    def preview(self, changes):
        items = list(changes)
        if not items or len(items) > self.max_files:
            raise ValueError("file-count limit")
        total = 0
        prepared = []
        seen = set()
        for change in items:
            rel = _safe_relative(change.path)
            if str(rel) in seen or str(rel).startswith(".mgr-job/"):
                raise ValueError("duplicate or reserved path")
            seen.add(str(rel))
            if not isinstance(change.content, str):
                raise ValueError("text-only file job")
            data = change.content.encode("utf-8")
            total += len(data)
            if total > self.max_bytes:
                raise ValueError("byte limit")
            dest = _checked_destination(self.root, rel)
            old = dest.read_bytes() if dest.is_file() else None
            old_hash = sha256(old).hexdigest() if old is not None else None
            if change.expected_sha256 != old_hash:
                raise ValueError(f"stale or missing file precondition: {rel}")
            prepared.append({"path": str(rel), "old_sha256": old_hash,
                             "new_sha256": sha256(data).hexdigest(), "bytes": len(data)})
        return prepared

    def apply(self, job_id, changes):
        if not job_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in job_id):
            raise ValueError("invalid job ID")
        changes = list(changes)
        receipt = self.preview(changes)
        job_root = self.root / ".mgr-job"
        if job_root.is_symlink():
            raise PermissionError("job receipt directory is a symlink")
        job_root.mkdir(exist_ok=True)
        backup_dir = job_root / job_id
        backup_dir.mkdir(exist_ok=False)
        written = []
        try:
            for index, change in enumerate(changes):
                rel = _safe_relative(change.path)
                dest = _checked_destination(self.root, rel)
                dest.parent.mkdir(parents=True, exist_ok=True)
                old = dest.read_bytes() if dest.is_file() else None
                actual_hash=sha256(old).hexdigest() if old is not None else None
                if actual_hash != receipt[index]["old_sha256"]:
                    raise ValueError("file changed after job preview")
                if old is not None:
                    (backup_dir / f"{index}.bak").write_bytes(old)
                fd, tmp = tempfile.mkstemp(prefix=".mgr-write-", dir=dest.parent)
                try:
                    with os.fdopen(fd, "wb") as handle:
                        handle.write(change.content.encode("utf-8"))
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.replace(tmp, dest)
                finally:
                    if os.path.exists(tmp):
                        os.unlink(tmp)
                written.append((dest, old))
            result = {"job_id": job_id, "status": "applied", "changes": receipt,
                      "rollback_dir": str(backup_dir.relative_to(self.root)),
                      "execution": "typed-file-edits-only; no shell or network"}
            (backup_dir / "receipt.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            return result
        except BaseException:
            for dest, old in reversed(written):
                if old is None:
                    dest.unlink(missing_ok=True)
                else:
                    dest.write_bytes(old)
            raise

    def rollback(self, job_id):
        if not job_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in job_id):
            raise ValueError("invalid job ID")
        folder = self.root / ".mgr-job" / job_id
        if folder.is_symlink():
            raise PermissionError("symlink receipt blocked")
        receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8"))
        if receipt["status"] != "applied":
            raise ValueError("job not applied")
        targets = []
        for idx, entry in enumerate(receipt["changes"]):
            dest = _checked_destination(self.root, _safe_relative(entry["path"]))
            if not dest.is_file() or sha256(dest.read_bytes()).hexdigest() != entry["new_sha256"]:
                raise ValueError("refuse rollback over subsequent changes")
            backup = folder / f"{idx}.bak"
            data = backup.read_bytes() if entry["old_sha256"] is not None else None
            if data is not None and sha256(data).hexdigest() != entry["old_sha256"]:
                raise ValueError("corrupt rollback backup")
            targets.append((dest, data))
        for dest, data in reversed(targets):
            if data is None:
                dest.unlink()
            else:
                dest.write_bytes(data)
        receipt["status"] = "rolled-back"
        (folder / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt
