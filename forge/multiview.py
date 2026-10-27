"""MGR-native multi-view silhouette reconstruction (space carving).

This module turns *measured* orthographic silhouettes into real triangle
geometry. It is deliberately honest about what it can and cannot know:

- Occupancy is constrained by every supplied silhouette at once.
- Concavities and surfaces no view can see are **not** measured; they are
  bounded by the visual hull, never invented.
- No neural model, no external API, no GPU is involved.

Coordinate convention: Y is up, X is width, Z is depth. Front/back views look
along -Z/+Z, so image X maps to world X. Left/right views look along +X/-X, so
image X maps to world Z. Image Y always maps to world Y with the top row at the
top of the bounds.

Back and right cameras sit on the far side of the subject, so their masks are
mirrored horizontally before carving. Supply each mask exactly as that camera
sees it; an unmirrored back/right mask makes the supplied silhouettes
contradict each other and the fit gate fails loudly instead of guessing.
"""

import hashlib
import json
import math
from pathlib import Path

from .geometry import Mesh
from .glb import export_glb, inspect_glb
from .image_relief import MAX_SOURCE_BYTES, decode_png
from .obj import export_obj
from .receipt import file_receipt

SCHEMA = "mgr.forge.multiview-silhouette.v1"
EVIDENCE_LEVEL = "MEASURED_SILHOUETTE_HULL"
AXES = ("front", "back", "left", "right")
DEPTH_AXES = ("front", "back")
WIDTH_AXES = ("left", "right")
MIRRORED_AXES = ("back", "right")
MAX_GRID = 96
MIN_GRID = 8
MAX_VIEWS = len(AXES)
MAX_FACES = 400_000
FIT_THRESHOLD = 0.97
HULL_MATERIALS = (("mgr-measured-hull", [0.72, 0.74, 0.78, 1]),)

LIMITATIONS = (
    "orthographic silhouettes only; perspective references need rectification",
    "concave detail no view can see is bounded by the hull, not measured",
    "a silhouette set constrains shape; it does not prove identity or likeness",
    "masks must be pre-segmented by the owner/segmentation stage",
    "voxel resolution bounds surface fidelity",
)


def _axis_of(view):
    axis = view.get("axis")
    if axis not in AXES:
        raise ValueError(f"unknown silhouette axis: {axis!r}")
    return axis


def _mask_threshold(view):
    threshold = view.get("threshold", 128)
    if type(threshold) is not int or not 1 <= threshold <= 254:
        raise ValueError("mask threshold must be an integer in 1..254")
    return threshold


def _load_mask(path, threshold):
    source = Path(path)
    if not source.is_file():
        raise ValueError(f"missing silhouette mask: {source.name}")
    if source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("silhouette mask exceeds bounded size")
    data = source.read_bytes()
    image = decode_png(data)
    rows = [[1 if value >= threshold else 0 for value in row] for row in image["luminance"]]
    covered = sum(sum(row) for row in rows)
    if not covered:
        raise ValueError(f"silhouette mask is empty: {source.name}")
    return {
        "path": str(source.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": image["width"],
        "height": image["height"],
        "coverage": round(covered / (image["width"] * image["height"]), 6),
        "cells": rows,
    }


def _validate_views(views):
    if type(views) is not list or not 1 <= len(views) <= MAX_VIEWS:
        raise ValueError("invalid silhouette view list")
    axes = [_axis_of(view) for view in views]
    if len(set(axes)) != len(axes):
        raise ValueError("duplicate silhouette axis")
    if not any(axis in DEPTH_AXES for axis in axes):
        raise ValueError("front or back silhouette required")
    if not any(axis in WIDTH_AXES for axis in axes):
        raise ValueError("left or right silhouette required")
    return axes


def _validate_bounds(bounds):
    if not isinstance(bounds, dict):
        raise ValueError("bounds object required")
    values = []
    for key in ("width", "height", "depth"):
        value = bounds.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or not 0.01 <= value <= 100:
            raise ValueError(f"invalid bounds.{key}")
        values.append(float(value))
    return tuple(values)


def _check_scale_consistency(loaded, axes):
    """Reject reference sets whose views disagree about the subject's size."""
    by_axis = {item["axis"]: item["mask"] for item in loaded}
    for pair in (("front", "back"), ("left", "right")):
        present = [axis for axis in pair if axis in by_axis]
        if len(present) == 2:
            left, right = (by_axis[axis] for axis in present)
            if (left["width"], left["height"]) != (right["width"], right["height"]):
                raise ValueError("opposing silhouettes disagree on image size")
            left_cover = _profile_extent(left)
            right_cover = _profile_extent(right)
            if abs(left_cover - right_cover) > 0.05:
                raise ValueError("opposing silhouettes disagree on subject scale")
    heights = [by_axis[axis]["height"] for axis in axes]
    if heights and abs(min(heights) - max(heights)) > 0.05 * max(heights):
        raise ValueError("silhouette masks disagree on subject height")


def _profile_extent(mask):
    rows = mask["cells"]
    top = next((index for index, row in enumerate(rows) if any(row)), None)
    bottom = next((len(rows) - 1 - index for index, row in enumerate(reversed(rows)) if any(row)), None)
    if top is None or bottom is None:
        raise ValueError("silhouette mask is empty")
    return (bottom - top + 1) / len(rows)


def _sample(mask, u, v):
    """Sample a normalised mask coordinate with v=0 at the top of the image."""
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        return 0
    x = min(mask["width"] - 1, int(u * mask["width"]))
    y = min(mask["height"] - 1, int(v * mask["height"]))
    return mask["cells"][y][x]


def _project_u(axis, u):
    """Back and right cameras are on the far side, so their images are mirrored."""
    return 1.0 - u if axis in MIRRORED_AXES else u


def _voxel_center(index, size, origin, count):
    return origin + (index + 0.5) * (size / count)


def carve(views, bounds, grid):
    """Return occupancy indexed [iy][iz][ix] plus per-view acceptance metrics."""
    width, height, depth = bounds
    x_origin, y_origin, z_origin = -width / 2, 0.0, -depth / 2
    occupancy = []
    for iy in range(grid):
        y = _voxel_center(iy, height, y_origin, grid)
        v = 1.0 - y / height
        plane = []
        for iz in range(grid):
            z = _voxel_center(iz, depth, z_origin, grid)
            row = []
            for ix in range(grid):
                x = _voxel_center(ix, width, x_origin, grid)
                inside = True
                for view in views:
                    axis = view["axis"]
                    if axis in DEPTH_AXES:
                        u = _project_u(axis, (x + width / 2) / width)
                    else:
                        u = _project_u(axis, (z + depth / 2) / depth)
                    inside = _sample(view["mask"], u, v)
                    if not inside:
                        break
                row.append(1 if inside else 0)
            plane.append(row)
        occupancy.append(plane)
    return occupancy


def _bbox(occupancy, bounds, grid):
    width, height, depth = bounds
    counts = [grid, grid, grid]
    lows = [None, None, None]
    highs = [None, None, None]
    for iy, plane in enumerate(occupancy):
        for iz, row in enumerate(plane):
            for ix, value in enumerate(row):
                if not value:
                    continue
                for axis, index in enumerate((ix, iy, iz)):
                    if lows[axis] is None or index < lows[axis]:
                        lows[axis] = index
                    if highs[axis] is None or index > highs[axis]:
                        highs[axis] = index
    if lows[0] is None:
        raise ValueError("silhouettes are inconsistent: no occupancy survived carving")
    spans = [(highs[axis] - lows[axis] + 1) * (bounds[axis] / counts[axis]) for axis in range(3)]
    origin = (-width / 2, 0.0, -depth / 2)
    minimum = [origin[axis] + lows[axis] * bounds[axis] / counts[axis] for axis in range(3)]
    maximum = [minimum[axis] + spans[axis] for axis in range(3)]
    return minimum, maximum


def _emit_surface(occupancy, bounds, grid):
    width, height, depth = bounds
    sx, sy, sz = width / grid, height / grid, depth / grid
    mesh = Mesh()
    faces = 0
    for iy in range(grid):
        plane = occupancy[iy]
        for iz in range(grid):
            row = plane[iz]
            for ix in range(grid):
                if not row[ix]:
                    continue
                x0, x1 = -width / 2 + ix * sx, -width / 2 + (ix + 1) * sx
                y0, y1 = iy * sy, (iy + 1) * sy
                z0, z1 = -depth / 2 + iz * sz, -depth / 2 + (iz + 1) * sz
                if ix == 0 or not row[ix - 1]:
                    mesh.quad((x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)); faces += 1
                if ix == grid - 1 or not row[ix + 1]:
                    mesh.quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)); faces += 1
                if iy == 0 or not occupancy[iy - 1][iz][ix]:
                    mesh.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)); faces += 1
                if iy == grid - 1 or not occupancy[iy + 1][iz][ix]:
                    mesh.quad((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)); faces += 1
                if iz == 0 or not plane[iz - 1][ix]:
                    mesh.quad((x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)); faces += 1
                if iz == grid - 1 or not plane[iz + 1][ix]:
                    mesh.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)); faces += 1
                if faces > MAX_FACES:
                    raise ValueError("reconstruction exceeds bounded face count; lower grid")
    return mesh, faces


def _reprojection(occupancy, bounds, grid, view):
    """Fraction of supplied mask pixels the hull's voxels actually cover.

    Voxels are splatted with their full footprint instead of point-sampled, so
    the check is not falsified by mask/voxel grid misalignment. The hull's
    shadow is always a subset of every supplied mask by construction, which is
    why coverage of the mask is the honest completeness measure: 1.0 means the
    carved geometry reaches everywhere the measured silhouette claims a
    subject exists.
    """
    width, height, depth = bounds
    mask = view["mask"]
    columns, rows = mask["width"], mask["height"]
    sx, sy, sz = width / grid, height / grid, depth / grid
    covered = [[False] * columns for _ in range(rows)]
    for iy in range(grid):
        y0, y1 = iy * sy, (iy + 1) * sy
        r0 = min(rows - 1, max(0, int((1.0 - y1 / height) * rows)))
        r1 = min(rows - 1, max(r0, int(math.ceil((1.0 - y0 / height) * rows)) - 1))
        for iz in range(grid):
            for ix in range(grid):
                if not occupancy[iy][iz][ix]:
                    continue
                if view["axis"] in DEPTH_AXES:
                    low, step, span, offset = -width / 2 + ix * sx, sx, width, width / 2
                else:
                    low, step, span, offset = -depth / 2 + iz * sz, sz, depth, depth / 2
                u0 = (low + offset) / span
                u1 = (low + step + offset) / span
                if view["axis"] in MIRRORED_AXES:
                    u0, u1 = 1.0 - u1, 1.0 - u0
                c0 = min(columns - 1, max(0, int(u0 * columns)))
                c1 = min(columns - 1, max(c0, int(math.ceil(u1 * columns)) - 1))
                for py in range(r0, r1 + 1):
                    line = covered[py]
                    for px in range(c0, c1 + 1):
                        line[px] = True
    cells = 0
    hit = 0
    for py in range(rows):
        mask_row, cover_row = mask["cells"][py], covered[py]
        for px in range(columns):
            if mask_row[px]:
                cells += 1
                if cover_row[px]:
                    hit += 1
    return round(hit / cells, 6) if cells else 0.0


def _prepare(spec):
    """Validate a spec and load its masks, returning carve-ready inputs."""
    if not isinstance(spec, dict):
        raise ValueError("reconstruction spec object required")
    grid = spec.get("grid", 48)
    if type(grid) is not int or not MIN_GRID <= grid <= MAX_GRID:
        raise ValueError(f"grid must be an integer in {MIN_GRID}..{MAX_GRID}")
    views = spec.get("views")
    axes = _validate_views(views)
    bounds = _validate_bounds(spec.get("bounds"))
    base = Path(spec.get("base_dir", "."))
    loaded = []
    for view in views:
        threshold = _mask_threshold(view)
        loaded.append({"axis": view["axis"], "mask": _load_mask(base / view["mask"], threshold)})
    _check_scale_consistency(loaded, axes)
    return grid, bounds, loaded, axes


def reconstruct(spec):
    """Carve real geometry from measured silhouettes and return mesh + manifest."""
    grid, bounds, loaded, axes = _prepare(spec)

    occupancy = carve(loaded, bounds, grid)
    minimum, maximum = _bbox(occupancy, bounds, grid)
    mesh, faces = _emit_surface(occupancy, bounds, grid)
    volume = sum(sum(sum(row) for row in plane) for plane in occupancy) * (
        (bounds[0] / grid) * (bounds[1] / grid) * (bounds[2] / grid))

    per_view = []
    for view in loaded:
        per_view.append({
            "axis": view["axis"],
            "mask": Path(view["mask"]["path"]).name,
            "sha256": view["mask"]["sha256"],
            "pixels": [view["mask"]["width"], view["mask"]["height"]],
            "mask_coverage": view["mask"]["coverage"],
            "hull_shadow_iou": _reprojection(occupancy, bounds, grid, view),
        })
    worst = min(item["hull_shadow_iou"] for item in per_view)

    manifest = {
        "schema": SCHEMA,
        "status": "MATERIALIZED",
        "evidence_level": EVIDENCE_LEVEL,
        "method": "orthographic-silhouette-space-carving",
        "bounds_m": [round(value, 6) for value in bounds],
        "grid": grid,
        "voxel_size_m": [round(value / grid, 6) for value in bounds],
        "views": per_view,
        "view_axes": axes,
        "mirrored_axes": list(MIRRORED_AXES),
        "occupied_voxels": sum(sum(sum(row) for row in plane) for plane in occupancy),
        "volume_m3": round(volume, 6),
        "bbox_min_m": [round(value, 6) for value in minimum],
        "bbox_max_m": [round(value, 6) for value in maximum],
        "triangles": len(mesh.indices) // 3,
        "vertices": len(mesh.positions) // 3,
        "quads": faces,
        "fit": {
            "worst_view_iou": worst,
            "threshold": FIT_THRESHOLD,
            "status": "PASS" if worst >= FIT_THRESHOLD else "FAIL",
        },
        "hidden_surface_inference": False,
        "identity_verified": False,
        "external_api_calls": 0,
        "limitations": list(LIMITATIONS),
    }
    if manifest["fit"]["status"] != "PASS":
        raise ValueError("reconstructed hull does not reproduce the measured silhouettes")
    return mesh, manifest


SCORE_SCHEMA = "mgr.forge.hull-vs-solid-score.v1"
SCORE_EVIDENCE = "MEASURED_HULL_VS_ANALYTIC_SOLID"
MAX_BOXES = 512


def _validate_boxes(boxes, bounds):
    if type(boxes) is not list or not 1 <= len(boxes) <= MAX_BOXES:
        raise ValueError("invalid solid box list")
    parsed = []
    width, height, depth = bounds
    limits = ((-width / 2, width / 2), (0.0, height), (-depth / 2, depth / 2))
    for box in boxes:
        if not isinstance(box, dict):
            raise ValueError("solid box object required")
        low, high = box.get("min"), box.get("max")
        for value in (low, high):
            if type(value) is not list or len(value) != 3:
                raise ValueError("solid box requires 3-axis min/max")
            for item in value:
                if type(item) not in (int, float) or not math.isfinite(item):
                    raise ValueError("solid box coordinate must be finite")
        for axis in range(3):
            if low[axis] >= high[axis]:
                raise ValueError("solid box min must be below max")
            if low[axis] < limits[axis][0] - 1e-9 or high[axis] > limits[axis][1] + 1e-9:
                raise ValueError("solid box lies outside the reconstruction bounds")
        parsed.append((tuple(float(v) for v in low), tuple(float(v) for v in high)))
    return parsed


def score_against_solid(spec, boxes):
    """Measure the carved hull against an analytic solid at voxel resolution.

    This is the only honest way to state reconstruction accuracy: the ground
    truth has to be known independently of the silhouettes. Both occupancies are
    sampled at the same voxel centres, so the score is a like-for-like volume
    comparison, not an opinion about how the result looks.
    """
    grid, bounds, loaded, axes = _prepare(spec)
    parsed = _validate_boxes(boxes, bounds)
    occupancy = carve(loaded, bounds, grid)
    width, height, depth = bounds
    voxel = (width / grid) * (height / grid) * (depth / grid)

    hull = solid = both = missed = over = 0
    for iy in range(grid):
        y = _voxel_center(iy, height, 0.0, grid)
        for iz in range(grid):
            z = _voxel_center(iz, depth, -depth / 2, grid)
            for ix in range(grid):
                x = _voxel_center(ix, width, -width / 2, grid)
                truth = any(low[0] <= x <= high[0] and low[1] <= y <= high[1]
                            and low[2] <= z <= high[2] for low, high in parsed)
                car = bool(occupancy[iy][iz][ix])
                hull += 1 if car else 0
                solid += 1 if truth else 0
                if car and truth:
                    both += 1
                elif truth:
                    missed += 1
                elif car:
                    over += 1
    union = both + missed + over
    return {
        "schema": SCORE_SCHEMA,
        "status": "MEASURED",
        "evidence_level": SCORE_EVIDENCE,
        "grid": grid,
        "bounds_m": [round(value, 6) for value in bounds],
        "voxel_volume_m3": round(voxel, 12),
        "view_axes": axes,
        "hull_voxels": hull,
        "solid_voxels": solid,
        "agreement_voxels": both,
        "overfill_voxels": over,
        "missed_voxels": missed,
        "hull_volume_m3": round(hull * voxel, 9),
        "solid_volume_m3": round(solid * voxel, 9),
        "overfill_volume_m3": round(over * voxel, 9),
        "missed_volume_m3": round(missed * voxel, 9),
        "hull_vs_solid_iou": round(both / union, 6) if union else 0.0,
        "silhouettes_prove_identity": False,
        "limitations": list(LIMITATIONS),
    }


def export_reconstruction(spec_path, output, *, smooth=False, marching=False):
    """Write hull.glb, hull.obj/mtl and reconstruction.json into a new directory."""
    target = Path(output)
    if target.exists():
        raise FileExistsError("new reconstruction destination required")
    spec_file = Path(spec_path)
    if not spec_file.is_file():
        raise ValueError("missing reconstruction spec")
    if spec_file.stat().st_size > 1_000_000:
        raise ValueError("reconstruction spec exceeds bounded size")
    spec = json.loads(spec_file.read_text(encoding="utf-8"))
    spec = dict(spec)
    spec.setdefault("base_dir", str(spec_file.resolve().parent))
    mesh, manifest = reconstruct(spec)

    target.mkdir(parents=True)
    if marching:
        from .marching import marching_cubes
        _grid, _bounds, _loaded, _axes = _prepare(spec)
        _occupancy = carve(_loaded, _bounds, _grid)
        mesh = marching_cubes(_occupancy, _bounds, _grid)
        manifest["surface"] = "marching-cubes-fan"
        manifest["vertices"] = len(mesh.positions) // 3
        manifest["triangles"] = len(mesh.indices) // 3
    elif smooth:
        from .smooth import smooth_normals
        mesh = smooth_normals(mesh)
        manifest["smoothing"] = "taubin-averaged-normals"
        manifest["vertices"] = len(mesh.positions) // 3
    else:
        manifest["smoothing"] = "flat-per-quad"
        manifest["surface"] = "voxel-quads"
    payload = export_glb([mesh], name="MGR Multi-View Silhouette Hull",
                         materials=HULL_MATERIALS)
    quality = inspect_glb(payload)
    glb_path = target / "hull.glb"
    glb_path.write_bytes(payload)
    obj_data, mtl_data = export_obj([mesh], mtl_name="hull.mtl", materials=HULL_MATERIALS)
    obj_path = target / "hull.obj"
    obj_path.write_text(obj_data, encoding="utf-8")
    (target / "hull.mtl").write_text(mtl_data, encoding="utf-8")

    manifest["glb"] = {**file_receipt(glb_path), "inspection": quality}
    manifest["obj"] = file_receipt(obj_path)
    manifest["internally_consistent"] = bool(quality.get("valid"))
    manifest_path = target / "reconstruction.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"manifest": manifest, "manifest_path": manifest_path, "glb_path": glb_path}
