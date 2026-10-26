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
              "source_dimensions": [image.width, image.height],
              "parts": tickets, "separate_transparent_assets_generated": True,
              "image_to_3d_ran": False, "rigging_performed": False,
              "status": "APPROVED_2D_PARTS_READY_FOR_3D_ADAPTER"}
    (target / "manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def materialize_unclothe_proxies(extracted_directory, output_directory, *, grid=48,
                                 pixels_per_unit=200.0, thickness=0.015):
    """Create real, editable silhouette *proxy* GLBs in shared image coordinates.

    This reconstructs only the observed mask outline with a fixed extrusion depth.
    It does NOT claim realistic 3D backside, garment volume, skinning or textures.
    """
    from .geometry import Mesh
    from .glb import export_glb, inspect_glb

    source = Path(extracted_directory)
    target = Path(output_directory)
    if target.exists():
        raise FileExistsError("refusing to overwrite proxy meshes")
    if type(grid) is not int or not 4 <= grid <= 64:
        raise ValueError("proxy grid must be 4..64")
    if not 10 <= pixels_per_unit <= 1000 or not 0.001 <= thickness <= 0.5:
        raise ValueError("invalid proxy dimensions")
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "mgr.forge.unclothe-extraction.v1":
        raise ValueError("invalid approved extraction manifest")
    size = manifest.get("source_dimensions")
    if (not isinstance(size, list) or len(size) != 2 or any(type(v) is not int or
            not 64 <= v <= 8192 for v in size)):
        raise ValueError("invalid source dimensions")
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for silhouette geometry") from exc
    results = []
    for part in manifest["parts"]:
        name = part["id"]
        if not isinstance(name, str) or not NAME.fullmatch(name) or not part.get("owner_approved"):
            raise ValueError("only approved safe part IDs allowed")
        source_file = _local_png(source, part.get("isolated_png"))
        bounds = part.get("visible_pixel_bbox_xyxy")
        if (not isinstance(bounds, list) or len(bounds) != 4 or
            any(type(v) is not int for v in bounds) or
            not 0 <= bounds[0] < bounds[2] <= size[0] or
            not 0 <= bounds[1] < bounds[3] <= size[1]):
            raise ValueError("invalid original source bounds")
        with Image.open(source_file) as image:
            if image.size != (bounds[2] - bounds[0], bounds[3] - bounds[1]):
                raise ValueError("isolated image and original bounds differ")
            alpha = image.convert("RGBA").getchannel("A")
        nx = max(1, round(grid * alpha.width / max(alpha.size)))
        ny = max(1, round(grid * alpha.height / max(alpha.size)))
        sample = alpha.resize((nx, ny), Image.Resampling.BOX)
        occupied = [[sample.getpixel((x, y)) >= 64 for x in range(nx)] for y in range(ny)]
        if not any(any(row) for row in occupied):
            raise ValueError("isolated part contains no sampled geometry")
        mesh = Mesh()
        width = (bounds[2] - bounds[0]) / nx / pixels_per_unit
        height = (bounds[3] - bounds[1]) / ny / pixels_per_unit
        for y, row in enumerate(occupied):
            for x, yes in enumerate(row):
                if not yes:
                    continue
                x0 = (bounds[0] + x * width * pixels_per_unit - size[0] / 2) / pixels_per_unit
                x1 = x0 + width
                y1 = (size[1] / 2 - bounds[1] - y * height * pixels_per_unit) / pixels_per_unit
                y0 = y1 - height
                z0, z1 = -thickness / 2, thickness / 2
                mesh.quad((x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))
                mesh.quad((x1,y0,z0),(x0,y0,z0),(x0,y1,z0),(x1,y1,z0))
                if x == 0 or not occupied[y][x-1]:
                    mesh.quad((x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0))
                if x == nx-1 or not occupied[y][x+1]:
                    mesh.quad((x1,y0,z1),(x1,y0,z0),(x1,y1,z0),(x1,y1,z1))
                if y == 0 or not occupied[y-1][x]:
                    mesh.quad((x0,y1,z1),(x1,y1,z1),(x1,y1,z0),(x0,y1,z0))
                if y == ny-1 or not occupied[y+1][x]:
                    mesh.quad((x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1))
        blob = export_glb([mesh],name=name,materials=((name,[0.64,0.65,0.67,1]),))
        geometry = inspect_glb(blob)
        results.append((name,blob,geometry))
    target.mkdir(parents=True,exist_ok=False)
    files = []
    for name, blob, geometry in results:
        filename = name + ".glb"
        (target / filename).write_bytes(blob)
        files.append({"id":name,"filename":filename,"sha256":hashlib.sha256(blob).hexdigest(),
                      "geometry":geometry,"fidelity":"OBSERVED_SILHOUETTE_2_5D_PROXY"})
    report = {"schema":"mgr.forge.unclothe-proxies.v1","parts":files,
              "source_sha256":manifest["source_sha256"],
              "body_rig_attached":False,"photorealistic_3d_reconstruction":False,
              "independent_glb_parsing_passed":True}
    (target / "manifest.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report
