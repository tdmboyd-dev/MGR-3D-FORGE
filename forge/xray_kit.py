"""REA Evidence -> Forge Vault cross-check. No copying third-party code/assets.

The optional adapter checks independent REA ZIP observations against the
existing per-file Forge source/rights receipt. It makes a *capability plan*,
not a claim of rights clearance or quality.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
from collections import Counter

MAX_EVIDENCE_BYTES = 16_000_000
MAX_SOURCE_RECEIPT_BYTES = 10_000_000
MAX_FILES = 50_000


def _read(path, limit):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>limit:
        raise ValueError("missing/symlink/oversized X-Ray evidence input")
    return json.loads(p.read_text(encoding="utf-8"))


def _hash(value):
    return isinstance(value,str) and len(value)==64 and all(c in "0123456789abcdef" for c in value)


def audit_kit_with_rea(rea_bundle, forge_pack_receipt):
    bundle=_read(rea_bundle,MAX_EVIDENCE_BYTES)
    saved=_read(forge_pack_receipt,MAX_SOURCE_RECEIPT_BYTES)
    if not isinstance(bundle,dict) or not isinstance(saved,dict):
        raise ValueError("REA and Forge documents must be objects")
    if saved.get("schema") not in ("mgr.forge.pack-preservation.v1",
                                   "mgr.forge.pack-preservation.v2"):
        raise ValueError("unsupported Forge pack receipt")
    archive_sha=saved.get("archive_sha256")
    if not _hash(archive_sha):
        raise ValueError("Forge receipt has invalid source SHA")
    artifacts=bundle.get("artifacts")
    if not isinstance(artifacts,list) or len(artifacts)!=1 or (
            artifacts[0].get("digest",{}).get("sha256")!=archive_sha):
        raise ValueError("REA and Forge refer to different source archives")
    if artifacts[0].get("format")!="zip":
        raise ValueError("X-Ray asset comparison requires ZIP inventory")
    records=bundle.get("records")
    if not isinstance(records,list):
        raise ValueError("REA Evidence records absent")
    inventories=[r for r in records if isinstance(r,dict) and
                 isinstance(r.get("normalized_result"),dict) and
                 r["normalized_result"].get("coverage",{}).get("scope")=="container-entries"]
    if len(inventories)!=1:
        raise ValueError("one complete REA container inventory required")
    rec=inventories[0]
    tree=rec["normalized_result"]
    if tree["coverage"].get("status")!="complete" or tree.get("integrity_contradictions"):
        raise ValueError("REA source inventory incomplete or contradictory")
    nodes=tree.get("nodes")
    occurrences=tree.get("occurrences")
    if not isinstance(nodes,list) or not isinstance(occurrences,list) or (
            len(occurrences)>MAX_FILES*2):
        raise ValueError("invalid REA package graph")
    node_lookup={}
    for node in nodes:
        key=node.get("artifact_id")
        if not isinstance(key,str) or key in node_lookup:
            raise ValueError("duplicate or invalid REA artifact IDs")
        node_lookup[key]=node
    inspected={}
    for item in occurrences:
        if item.get("entry_kind")!="file" or item.get("logical_path")==".":
            continue
        path=item.get("logical_path")
        if not isinstance(path,str) or path.startswith("/") or (
                ".." in PurePosixPath(path).parts) or "\\" in path:
            raise ValueError("unsafe REA ZIP member path")
        if path in inspected:
            raise ValueError("REA ZIP contains duplicate file path")
        node=node_lookup.get(item.get("artifact_id"))
        if not isinstance(node,dict) or item.get("hash_status")!="verified":
            raise ValueError("REA file bytes are not independently checked")
        digest=node.get("sha256")
        size=node.get("size")
        if not _hash(digest) or type(size) is not int or size<0:
            raise ValueError("REA lacks verified file hash and length")
        inspected[path]=(digest,size)
    expected=saved.get("files")
    if not isinstance(expected,list) or len(expected)>MAX_FILES:
        raise ValueError("invalid Forge source inventory")
    by_path={}
    for f in expected:
        if not isinstance(f,dict) or type(f.get("bytes")) is not int or not _hash(f.get("sha256")):
            raise ValueError("invalid Forge stored item")
        name=f.get("path")
        if not isinstance(name,str) or name in by_path:
            raise ValueError("invalid or duplicate Forge pack path")
        by_path[name]=(f["sha256"],f["bytes"])
    if len(inspected)!=len(by_path) or inspected!=by_path:
        missing=sorted(set(by_path)-set(inspected))[:4]
        extra=sorted(set(inspected)-set(by_path))[:4]
        mismatched=sorted(k for k in set(inspected)&set(by_path)
                          if inspected[k]!=by_path[k])[:4]
        raise ValueError(f"Independent REA/Forge ZIP evidence mismatch: missing={missing}, extra={extra}, changed={mismatched}")
    names=sorted(by_path)
    extensions=Counter(PurePosixPath(f).suffix.lower() or "(none)" for f in names)
    categories={
        "gltf_candidates":sum(extensions.get(ext,0) for ext in (".gltf",".glb")),
        "obj_candidates":extensions.get(".obj",0),
        "texture_candidates":sum(extensions.get(ext,0) for ext in (".png",".jpg",".jpeg",".webp",".exr")),
        "animation_candidates":sum(extensions.get(ext,0) for ext in (".bvh",".fbx",".anim")),
        "other_files":len(names)
    }
    categories["other_files"]-=sum(categories.values())-categories["other_files"]
    # Category/file-name counts do not establish rigging, animations or usable rights.
    return {
        "schema":"mgr.forge.xray-kit-audit.v1",
        "status":"INDEPENDENT_BYTES_MATCH_RIGHTS_AND_ART_REVIEW_PENDING",
        "source":saved.get("official_source"),
        "archive_sha256":archive_sha,
        "rea_source_record":rec.get("evidence_id"),
        "rea_coverage":tree["coverage"],
        "source_file_count":len(names),
        "source_file_sha256_matched":len(names),
        "extension_counts":dict(sorted(extensions.items())),
        "categories":categories,
        "rights_reviewed":False,
        "safe_to_redistribute":False,
        "actual_glb_import_verified":False,
        "actual_skinning_or_animation_verified":False,
        "code_copying_permitted_by_analysis":False,
        "feature_build_targets":[
            {"owner":"Forge Vault","outcome":"portable pinned asset intake with scoped rights and original-file digests"},
            {"owner":"Creation Forge","outcome":"import glTF models with dependency closure and original editor-compatible source"},
            {"owner":"Human/Creature Forge","outcome":"original parametric body mesh, morph DNA, joint-aware rig and animation acceptance"},
            {"owner":"World Forge","outcome":"original scene-placement, geometry synthesis, material pairing and engine round-trip"},
            {"owner":"MGR Beast X-Ray","outcome":"repeat evidence comparison when a source archive changes"}
        ],
        "limitations":[
            "REA confirms recorded ZIP bytes, not third-party license clearance",
            "Filename extensions do not prove rigged/animated/visually acceptable geometry",
            "MGR-native implementations must use permitted methods and separately created original work",
            "ReA analysis does not reveal inaccessible original generation source code"
        ]
    }


def write_xray_kit_receipt(rea_bundle, forge_pack_receipt, output):
    target=Path(output)
    if target.exists():
        raise FileExistsError("X-Ray audit receipt already exists; no overwrite")
    result=audit_kit_with_rea(rea_bundle,forge_pack_receipt)
    target.parent.mkdir(parents=True,exist_ok=True)
    # Fail-safe new file; do not delete or overwrite another author's work.
    with target.open("x",encoding="utf-8") as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
        stream.write("\n")
    return result
