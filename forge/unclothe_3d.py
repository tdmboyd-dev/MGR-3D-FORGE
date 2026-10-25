"""Unclothe 3D: bounded, owner-gated separation of visible character parts.

Segmentation providers produce candidate masks; this module does not infer them.
After approval it makes genuine transparent 2D assets and separate 3D job tickets.
Occluded geometry and actual image-to-3D must be reconstructed by an adapter.
"""

import hashlib
import json
from pathlib import Path
import re

from .reference_pack import MAX_BYTES, png_size


SCHEMA = "mgr.forge.unclothe.v1"
PARTS = frozenset({"body", "face", "feet", "hair", "coat", "shirt", "pants", "boots",
                   "chains", "rings", "bracelets", "earrings", "tattoo", "belt", "extras"})
MAX_PARTS = 64
MAX_PIXELS = 24_000_000
NAME = re.compile(r"[a-z][a-z0-9_-]{0,39}\Z")


def _local_png(directory, value):
    if not isinstance(value, str) or Path(value).name != value or value in (".", ".."):
        raise ValueError("PNG filename must be a local basename")
    path = directory / value
    png_size(path)
    return path


def _load_proposal(spec_file):
    spec_path = Path(spec_file)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("schema") != SCHEMA:
        raise ValueError("unsupported Unclothe 3D schema")
    root = spec_path.parent
    source = _local_png(root, spec.get("source"))
    entries = spec.get("parts")
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_PARTS:
        raise ValueError("1..64 identified parts required")
    seen = set()
    for part in entries:
        if not isinstance(part, dict) or part.get("kind") not in PARTS:
            raise ValueError("unknown semantic part")
        part_id = part.get("id")
        if not isinstance(part_id, str) or not NAME.fullmatch(part_id) or part_id in seen:
            raise ValueError("unsafe or repeated part id")
        seen.add(part_id)
        if part.get("decision") not in ("pending", "approved", "rejected"):
            raise ValueError("part decision must be pending, approved or rejected")
        _local_png(root, part.get("mask"))
    return spec, source, root


def inspect_unclothe(spec_file):
    """Inspect a segmentation proposal; never infer owner approval from provider scores."""
    spec, source, _ = _load_proposal(spec_file)
    counts = {k: sum(p["decision"] == k for p in spec["parts"])
              for k in ("pending", "approved", "rejected")}
    return {"schema": "mgr.forge.unclothe-review.v1", "source_sha256":
            hashlib.sha256(source.read_bytes()).hexdigest(), "part_count": len(spec["parts"]),
            "decisions": counts, "ready_to_extract": counts["pending"] == 0 and counts["approved"] > 0,
            "segmentation_model_ran": False, "image_to_3d_ran": False,
            "hidden_geometry_recovered": False}


def extract_approved_parts(spec_file, output_directory):
    """Extract visible pixels through approved masks; write distinct 3D adapter tickets.

    Pillow is loaded only for this optional raster stage; no network/model inference.
    No files are written until all input bounds, masks and approvals validate.
    """
    spec, source, root = _load_proposal(spec_file)
    summary = inspect_unclothe(spec_file)
    if not summary["ready_to_extract"]:
        raise ValueError("every part needs a decision, at least one approved")
    target = Path(output_directory)
    if target.exists():
        raise FileExistsError("refusing to overwrite Unclothe 3D output")
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for transparent PNG extraction") from exc
    with Image.open(source) as img:
        if img.width * img.height > MAX_PIXELS:
            raise ValueError("image pixel budget exceeded")
        image = img.convert("RGBA")
    prepared = []
    for part in spec["parts"]:
        if part["decision"] != "approved":
            continue
        mask_file = _local_png(root, part["mask"])
        with Image.open(mask_file) as img:
            if img.size != image.size:
                raise ValueError("segmentation mask must match source image dimensions")
            mask = img.convert("L")
        mask = mask.point(lambda value: 255 if value >= 128 else 0)
        bounds = mask.getbbox()
        if not bounds:
            raise ValueError("approved mask contains no foreground")
        prepared.append((part, mask, bounds, mask_file))
    target.mkdir(parents=True, exist_ok=False)
    tickets = []
    for part, mask, bounds, mask_file in prepared:
        isolated = image.copy()
        isolated.putalpha(mask)
        isolated = isolated.crop(bounds)
        filename = part["id"] + ".png"
        isolated.save(target / filename)
        tickets.append({"id": part["id"], "kind": part["kind"],
                        "isolated_png": filename,
                        "mask_sha256": hashlib.sha256(mask_file.read_bytes()).hexdigest(),
                        "visible_pixel_bbox_xyxy": list(bounds),
                        "geometry_status": "AWAITING_3D_RECONSTRUCTION",
                        "occluded_surfaces": "UNKNOWN_FROM_IMAGE",
                        "owner_approved": True})
    report = {"schema": "mgr.forge.unclothe-extraction.v1", "source_sha256":
              summary["source_sha256"], "part_count": len(tickets),
              "parts": tickets, "separate_transparent_assets_generated": True,
              "image_to_3d_ran": False, "rigging_performed": False,
              "status": "APPROVED_2D_PARTS_READY_FOR_3D_ADAPTER"}
    (target / "manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
