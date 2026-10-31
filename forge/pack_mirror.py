"""Pin and preserve explicitly chosen official CC0 kits; never auto-promote assets.

This module stores the original ZIP unchanged, a per-file digest inventory and
the license notice. It never extracts executable content or registers a kit as
approved for redistribution, animation or live creation use.
"""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from zipfile import ZipFile, BadZipFile

from .assets import AssetRegistry

KAYKIT_REPOS = frozenset({
    "KayKit-Prototype-Bits-1.0",
    "KayKit-Character-Pack-Adventures-1.0",
    "KayKit-Character-Pack-Skeletons-1.0",
    "KayKit-Dungeon-Remastered-1.0",
    "KayKit-City-Builder-Bits-1.0",
    "KayKit-Halloween-Bits-1.0",
    "KayKit-Medieval-Hexagon-Pack-1.0",
    "KayKit-Space-Base-Bits-1.0",
})
MAX_ARCHIVE_BYTES = 75_000_000
MAX_TOTAL_EXPANDED = 350_000_000
MAX_ENTRIES = 12_000


def license_claim_scope(file_path, license_folder):
    """Only paths within the exact license folder inherit a source claim.

    Even an in-scope CC0 *claim* is not enough to authorize redistribution.
    """
    if not isinstance(file_path,str) or not isinstance(license_folder,str):
        return False
    if (file_path.startswith("/") or license_folder.startswith("/") or
            "\\" in file_path or "\\" in license_folder or
            ".." in PurePosixPath(file_path).parts or
            ".." in PurePosixPath(license_folder).parts):
        return False
    return file_path.startswith(license_folder.rstrip("/") + "/")


def _scan_archive(blob):
    if not 100 <= len(blob) <= MAX_ARCHIVE_BYTES:
        raise ValueError("pack archive outside bounded download budget")
    try:
        with ZipFile(io.BytesIO(blob)) as package:
            names = set()
            inventory = []
            licenses = []
            expanded = 0
            for info in package.infolist():
                if len(inventory) >= MAX_ENTRIES:
                    raise ValueError("archive has too many entries")
                name = info.filename
                pure = PurePosixPath(name)
                if (name.startswith("/") or "\\" in name or
                        any(part in ("", "..", ".") for part in pure.parts) or
                        name in names or ":" in name):
                    raise ValueError("unsafe or duplicated archive path")
                names.add(name)
                mode = info.external_attr >> 16
                if stat.S_IFMT(mode) == stat.S_IFLNK:
                    raise ValueError("archive contains link")
                if info.is_dir():
                    continue
                if info.file_size < 0 or info.file_size > MAX_ARCHIVE_BYTES:
                    raise ValueError("archive entry exceeds size limit")
                expanded += info.file_size
                if expanded > MAX_TOTAL_EXPANDED:
                    raise ValueError("archive expands beyond safety budget")
                if info.file_size > 1_000_000 and info.compress_size * 250 < info.file_size:
                    raise ValueError("archive entry suspicious compression ratio")
                payload = package.read(info)
                sha = hashlib.sha256(payload).hexdigest()
                inventory.append({"path": name, "bytes": len(payload), "sha256": sha})
                if pure.name.lower() in ("license.txt", "license.md", "license"):
                    if 2 <= len(pure.parts) <= 8 and len(payload) <= 100_000:
                        decoded = payload.decode("utf-8", errors="replace")
                        if "cc0" in decoded.lower() or "creative commons zero" in decoded.lower():
                            licenses.append({"path": name, "sha256": sha, "text": decoded[:20_000],
                                             "scope": str(pure.parent),
                                             "scope_note": "Only files under the license folder are CC0-claimed; other folders need review"})
    except (BadZipFile, EOFError, OSError) as error:
        raise ValueError("invalid pack archive") from error
    if not licenses or not inventory:
        raise ValueError("official package must contain a verifiable scoped CC0 notice and files")
    if len(licenses)!=1:
        raise ValueError("multiple license scopes require individual human review")
    scope=licenses[0]["scope"]
    annotated=[{**file,"source_license_scope_claimed":license_claim_scope(file["path"],scope)}
               for file in inventory]
    return {"file_count": len(inventory), "expanded_bytes": expanded,
            "files": sorted(annotated, key=lambda x: x["path"]),
            "cc0_folder_claim_count":sum(x["source_license_scope_claimed"] for x in annotated),
            "outside_license_scope_count":sum(not x["source_license_scope_claimed"] for x in annotated),
            "license": licenses[0]}


def mirror_kaykit_pack(repo, commit, store_root, *, expected_sha256=None, opener=urlopen):
    if repo not in KAYKIT_REPOS:
        raise ValueError("unapproved kit repository; review its own license first")
    if not isinstance(commit, str) or re.fullmatch("[0-9a-f]{40}", commit) is None:
        raise ValueError("must pin the exact Git commit SHA")
    if expected_sha256 is not None and not re.fullmatch("[0-9a-f]{64}", expected_sha256):
        raise ValueError("expected sha256 must be a lowercase digest")
    link = f"https://codeload.github.com/KayKit-Game-Assets/{repo}/zip/{commit}"
    request = Request(link, headers={"User-Agent": "MGR-3D-FORGE-Preservation/1.0"})
    with opener(request, timeout=45) as response:
        final = urlsplit(response.geturl())
        if final.scheme != "https" or final.hostname != "codeload.github.com" or final.port not in (None, 443):
            raise ValueError("kit download redirected off official GitHub archive host")
        declared = response.headers.get("Content-Length")
        if declared is not None and int(declared) > MAX_ARCHIVE_BYTES:
            raise ValueError("pack archive exceeds download budget")
        blob = response.read(MAX_ARCHIVE_BYTES + 1)
    digest = hashlib.sha256(blob).hexdigest()
    if expected_sha256 and expected_sha256 != digest:
        raise ValueError("download changed from pinned digest")
    inspection = _scan_archive(blob)
    source = f"https://github.com/KayKit-Game-Assets/{repo}/tree/{commit}"
    store = Path(store_root)
    registry = AssetRegistry(store)
    saved = registry.add(blob, owner="Kay Lousberg / KayKit",
                         license_id="CC0-PARTIAL-SCOPE-UNREVIEWED", source=source,
                         extra={"title": repo, "category": "game-kits",
                                "provider_id": "kaykit", "source_slug": commit,
                                "rights_reviewed": False,
                                "geometry_status": "UNEXTRACTED_PACK_INSPECTED"})
    receipt = {"schema": "mgr.forge.pack-preservation.v2",
               "status": "PRESERVED_QUARANTINED_RIGHTS_AND_QUALITY",
               "official_source": source, "commit": commit,
               "archive_sha256": digest, "archive_bytes": len(blob),
               "content_object": saved["relative_path"],
               "license_claim": "CC0 evidence applies to the license folder, not automatically every file",
               "license_scope": inspection["license"]["scope"],
               "license_notice": inspection["license"],
               "file_count": inspection["file_count"],
               "cc0_folder_claim_count": inspection["cc0_folder_claim_count"],
               "outside_license_scope_count": inspection["outside_license_scope_count"],
               "expanded_bytes": inspection["expanded_bytes"],
               "files": inspection["files"],
               "rights_reviewed": False, "safe_to_redistribute": False,
               "model_import_verified": False, "external_spend_usd": 0}
    receipts = store / "pack-receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    target = receipts / (digest + ".scope-v2.json")
    serialized = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != serialized:
            raise ValueError("conflicting receipt for same archive")
    else:
        temporary = target.with_suffix(".tmp")
        temporary.write_text(serialized, encoding="utf-8")
        temporary.replace(target)
    return {"status": receipt["status"], "archive_sha256": digest,
            "archive_bytes": len(blob), "files": receipt["file_count"],
            "receipt": str(target), "rights_reviewed": False,
            "source": source, "external_spend_usd": 0}
