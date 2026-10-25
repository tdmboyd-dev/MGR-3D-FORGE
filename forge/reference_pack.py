"""Private multi-image reference admissions and whole-character asset job graph.

This is preparation/provenance, not automatic 2D->3D reconstruction.
"""

import hashlib
import json
from pathlib import Path
import re
import struct


VIEWS = {"front", "back", "left", "right", "three_quarter", "detail", "sheet"}
TYPES = {"body", "face", "feet", "hair", "coat", "shirt", "pants", "boots", "chains", "rings",
         "bracelets", "belt", "earrings", "tattoo", "outfit", "extras"}
MAX_IMAGES = 128
MAX_BYTES = 30_000_000


def png_size(path):
    source = Path(path)
    if not source.is_file() or source.is_symlink() or source.suffix.lower() != ".png":
        raise ValueError("ordinary existing PNG required")
    if not 33 <= source.stat().st_size <= MAX_BYTES:
        raise ValueError("PNG reference size outside bounds")
    with source.open("rb") as stream:
        header = stream.read(33)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("invalid PNG reference header")
    width, height = struct.unpack_from(">II", header, 16)
    if not 64 <= width <= 8192 or not 64 <= height <= 8192:
        raise ValueError("reference dimensions out of bounds")
    return width, height


def prepare_reference_pack(spec_path, output):
    """Manifest validates all attached images together and prepares independent asset jobs."""
    spec_file, target = Path(spec_path), Path(output)
    if target.suffix.lower() != ".json" or target.exists():
        raise ValueError("new JSON output required")
    spec = json.loads(spec_file.read_text(encoding="utf-8"))
    if spec.get("schema") != "mgr.forge.reference-input.v1":
        raise ValueError("unsupported reference set schema")
    entries = spec.get("images", [])
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_IMAGES:
        raise ValueError("reference set requires 1..128 images")
    approval = spec.get("owner_approval", "pending")
    if approval not in ("pending", "owner_approved"):
        raise ValueError("owner approval must be pending or owner_approved")
    assets = {}
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("asset") not in TYPES or entry.get("view") not in VIEWS:
            raise ValueError("each image needs an approved asset and view")
        filename = entry.get("file")
        if not isinstance(filename, str) or Path(filename).name != filename or filename in (".", ".."):
            raise ValueError("image reference must be a basename beside spec")
        variant = entry.get("variant", "primary")
        if not isinstance(variant, str) or not re.fullmatch(r"[a-z0-9_-]{1,40}", variant):
            raise ValueError("variant must be a short safe slug")
        key = (entry["asset"], entry["view"], variant)
        if key in seen:
            raise ValueError("duplicate asset/view requires human resolution")
        seen.add(key)
        source = spec_file.parent / filename
        w, h = png_size(source)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assets.setdefault(entry["asset"], []).append({"view": entry["view"], "variant": variant,
                    "filename": filename, "sha256": digest, "width": w, "height": h})
    jobs = []
    for asset in sorted(assets):
        views = {image["view"] for image in assets[asset]}
        required = ({"front", "back", "left", "right"} if asset == "body" else
                    {"front", "left", "right"} if asset == "face" else
                    {"front", "left", "right", "back"} if asset == "feet" else
                    {"front", "back"})
        missing = sorted(required - views)
        status = ("REFERENCES_READY_FOR_REVIEW" if not missing else
                  "NEEDS_VIEW_EXTRACTION" if "sheet" in views else "NEEDS_MORE_VIEWS")
        jobs.append({"asset": asset, "reference_images": assets[asset],
                     "missing_recommended_views": missing,
                     "status": status,
                     "mesh_generation_performed": False,
                     "semantic_asset_verified": False})
    report = {"schema": "mgr.forge.reference-pack.v1", "character": spec.get("character", "unapproved"),
              "owner_approval": approval,
              "reference_count": len(entries),
              "unique_image_count": len({entry["file"] for entry in entries}),
              "asset_jobs": jobs,
              "all_assets_requested_together": True,
              "global_identity_consistency_verified": False,
              "reference_rights_approved": False,
              "model_generation_performed": False,
              "notes": ["Multi-view references form a coordinated batch of 3D asset jobs.",
                        "Image files remain beside input spec; no images are copied to public repo.",
                        "Matching identity, anatomy and textures across AI images needs explicit review."]}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return report
