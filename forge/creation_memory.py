"""MGR Creation Memory — approved identity locks and reproducible revisions.

Single-writer JSON storage prototype; production needs transactional database,
multi-user permissions and signed owner approval integration.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class CreationMemory:
    def __init__(self, root):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def _file(self, identity):
        if not isinstance(identity,str) or not identity or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in identity):
            raise ValueError("invalid creation identity")
        return self.root / f"{identity}.json"

    def read(self, identity):
        record=json.loads(self._file(identity).read_text(encoding="utf-8"))
        history=record["history"]
        previous="0"*64
        for revision in history:
            if revision["previous_sha256"]!=previous:
                raise ValueError("broken memory chain")
            body={k:v for k,v in revision.items() if k!="sha256"}
            digest=sha256(_canonical(body).encode()).hexdigest()
            if digest!=revision["sha256"]:
                raise ValueError("memory integrity failure")
            previous=digest
        if not history or record["head"]!=previous:
            raise ValueError("invalid memory head")
        if (_canonical(record["properties"])!=_canonical(history[-1]["properties"])
                or record["locked_keys"]!=history[-1]["locked_keys"]
                or record["identity"]!=identity):
            raise ValueError("memory snapshot mismatch")
        return record

    def record(self, identity, *, properties, locked_keys=(), author, expected_head=None):
        if not isinstance(properties,dict) or not isinstance(author,str) or not author.strip():
            raise ValueError("properties and author required")
        if not all(isinstance(key,str) and key in properties for key in locked_keys):
            raise ValueError("locks must reference properties")
        target=self._file(identity)
        current=self.read(identity) if target.exists() else None
        if (current["head"] if current else None)!=expected_head:
            raise ValueError("stale memory head")
        locks=set(current["locked_keys"]) if current else set()
        for key in locks:
            if key not in properties or _canonical(properties[key])!=_canonical(current["properties"][key]):
                raise PermissionError(f"owner-approved property locked: {key}")
        locks.update(locked_keys)
        revision={"number":len(current["history"])+1 if current else 1,
                  "author":author,"properties":properties,
                  "locked_keys":sorted(locks),
                  "previous_sha256":current["head"] if current else "0"*64}
        revision["sha256"]=sha256(_canonical(revision).encode()).hexdigest()
        history=[*current["history"],revision] if current else [revision]
        result={"schema":"mgr.forge.creation-memory.v1", "identity":identity,
                "head":revision["sha256"], "properties":properties,
                "locked_keys":sorted(locks),"history":history}
        encoded=(_canonical(result)+"\n").encode()
        fd,name=tempfile.mkstemp(prefix=".memory-",dir=self.root)
        try:
            with os.fdopen(fd,"wb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name,target)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        return result
