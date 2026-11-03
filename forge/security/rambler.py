"""MGR Rambler v0: safe release byte-integrity manifest, not secrecy.

A release on another person's computer can be analyzed. This validates exact
files and bounded hashes but is NOT authenticated code signing. Trustworthy
signatures must be checked with separately governed public keys later.
"""
import hashlib, json, os
from pathlib import Path, PurePosixPath

SCHEMA="mgr.rambler.release-roster.v1"
MAX_FILES=5000
MAX_FILE=200_000_000
MAX_ALL=1_000_000_000
SENSITIVE={".env",".pem",".key",".p12",".pfx",".safetensors",".pth",".ckpt"}
PRIVATE_NAMES={"id_ed25519","id_rsa","auth.json","secrets.json"}

def _relative(value):
    if not isinstance(value,str) or not 1<=len(value)<=240 or "\\" in value or ":" in value:
        raise ValueError("release path must be a bounded forward-slash relative path")
    parts=value.split("/")
    if value.startswith("/") or any(s in ("",".","..") for s in parts):
        raise ValueError("unsafe relative release path")
    pure=PurePosixPath(value)
    if pure.suffix.lower() in SENSITIVE or pure.name.lower() in PRIVATE_NAMES or any(
       s.startswith(".") for s in parts):
        raise ValueError("secret, hidden or private file excluded from release")
    return value

def _file(root,name):
    here=root
    for part in PurePosixPath(_relative(name)).parts:
        here=here/part
        if here.is_symlink():raise ValueError("release link not permitted")
    file=here.resolve(strict=True)
    if os.path.commonpath((str(root),str(file)))!=str(root):
        raise ValueError("path escaped release root")
    if not file.is_file() or file.stat().st_size>MAX_FILE:
        raise ValueError("release file missing or oversized")
    return file

def _entries(root,names):
    if not isinstance(names,list) or not 1<=len(names)<=MAX_FILES or not all(
       isinstance(x,str) for x in names) or len(names)!=len(set(names)):
        raise ValueError("invalid release file list")
    result=[];total=0
    for name in sorted(names):
        data=_file(root,name).read_bytes()
        total+=len(data)
        if total>MAX_ALL:raise ValueError("release expanded size exceeded")
        result.append({"path":name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
    return result

def _digest(entries):
    return hashlib.sha256(json.dumps(entries,sort_keys=True,separators=(",",":")).encode("utf8")).hexdigest()

def create_roster(root,paths):
    source=Path(root).resolve(strict=True)
    if not source.is_dir() or source.is_symlink():
        raise ValueError("release root must be a normal directory")
    entries=_entries(source,paths)
    return {
      "schema":SCHEMA,"status":"UNSIGNED_INTEGRITY_ONLY",
      "files":entries,"file_count":len(entries),"release_bytes":sum(x["bytes"] for x in entries),
      "roster_sha256":_digest(entries),
      "publisher_signature":None,"publisher_authenticated":False,
      "license_reviewed":False,"reverse_engineering_impossible":False,
      "limits":["SHA hashes detect changed bytes only when the roster is trusted externally",
                "Signed distribution and trust anchor not yet implemented",
                "No secrets or proprietary model weights should be shipped to untrusted clients"]
    }

def verify_roster(root,roster):
    if isinstance(roster,(str,Path)):
        source=Path(roster)
        if source.is_symlink() or not source.is_file() or source.stat().st_size>2_000_000:
            raise ValueError("invalid roster file")
        roster=json.loads(source.read_text(encoding="utf8"))
    if not isinstance(roster,dict) or roster.get("schema")!=SCHEMA or (
         roster.get("publisher_signature") is not None or roster.get("publisher_authenticated") is not False):
        raise ValueError("unrecognized scheme or unverified signature claim")
    claimed=roster.get("files")
    if not isinstance(claimed,list) or not 1<=len(claimed)<=MAX_FILES or any(
         not isinstance(x,dict) or set(x)!={"path","bytes","sha256"} for x in claimed):
        raise ValueError("invalid manifest entries")
    root=Path(root).resolve(strict=True)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("invalid release root")
    correct=_entries(root,[x["path"] for x in claimed])
    if correct!=claimed or _digest(correct)!=roster.get("roster_sha256"):
        raise ValueError("MGR Rambler release integrity mismatch")
    all_files=[]
    for p in root.rglob("*"):
        if p.is_symlink():raise ValueError("unknown symlink in release")
        if p.is_file():all_files.append(p.relative_to(root).as_posix())
    if sorted(all_files)!=sorted(x["path"] for x in claimed):
        raise ValueError("release has unlisted files")
    return {"status":"BYTE_INTEGRITY_VERIFIED_NOT_SIGNED",
            "files":len(correct),"sha256":_digest(correct),
            "publisher_authenticated":False,"code_hidden":False}

def save_roster(root,paths,target):
    path=Path(target)
    if path.exists():raise FileExistsError("refusing to overwrite release manifest")
    source=Path(root).resolve(strict=True)
    resolved_target=path.resolve()
    if resolved_target==source or source in resolved_target.parents:
        raise ValueError("release manifest must be outside the release root")
    entry=create_roster(root,paths)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf8") as f:
        json.dump(entry,f,sort_keys=True,indent=2);f.write("\n")
    return entry
