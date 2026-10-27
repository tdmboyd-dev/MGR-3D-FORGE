"""Generate an honest synthetic multi-view phantom silhouette set.

The subject is a *known* solid (a union of axis-aligned boxes shaped like a
standing figure), so its exact orthographic silhouettes can be computed rather
than guessed. That makes the phantom a measurement harness: any reconstruction
built from these masks can be scored against analytic ground truth instead of
against an opinion.

This writes only synthetic, self-authored masks. It never reads owner-private
references.

    python scripts/make_phantom_silhouettes.py --out examples/multiview-phantom
"""

import argparse
import json
from pathlib import Path
import struct
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PIXELS_PER_METRE = 100
BOUNDS = {"width": 0.8, "height": 1.8, "depth": 0.5}
GRID = 64

# x0, x1, y0, y1, z0, z1 in metres. Y is up, X width, Z depth.
BOXES = (
    ("head", -0.090, 0.090, 1.550, 1.750, -0.100, 0.100),
    ("neck", -0.050, 0.050, 1.450, 1.550, -0.055, 0.055),
    ("chest", -0.200, 0.200, 1.150, 1.450, -0.130, 0.130),
    ("waist", -0.150, 0.150, 0.980, 1.150, -0.105, 0.105),
    ("pelvis", -0.160, 0.160, 0.820, 0.980, -0.110, 0.110),
    ("arm_l", -0.300, -0.200, 0.900, 1.440, -0.055, 0.055),
    ("arm_r", 0.200, 0.300, 0.900, 1.440, -0.055, 0.055),
    ("thigh_l", -0.155, -0.020, 0.420, 0.820, -0.090, 0.090),
    ("thigh_r", 0.020, 0.155, 0.420, 0.820, -0.090, 0.090),
    ("calf_l", -0.140, -0.030, 0.060, 0.420, -0.075, 0.075),
    ("calf_r", 0.030, 0.140, 0.060, 0.420, -0.075, 0.075),
    ("foot_l", -0.150, -0.020, 0.000, 0.060, -0.160, 0.090),
    ("foot_r", 0.020, 0.150, 0.000, 0.060, -0.160, 0.090),
)


def _chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def write_gray_png(path, rows):
    height, width = len(rows), len(rows[0])
    packed = bytearray()
    for row in rows:
        packed.append(0)
        packed.extend(row)
    payload = (PNG_MAGIC
               + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
               + _chunk(b"IDAT", zlib.compress(bytes(packed)))
               + _chunk(b"IEND", b""))
    path.write_bytes(payload)
    return {"width": width, "height": height}


def inside(box, x, y, z):
    return (box[1] <= x <= box[2] and box[3] <= y <= box[4] and box[5] <= z <= box[6])


def covered(axis, u, v):
    """Return True when the view ray at normalised (u, v) hits the phantom solid."""
    width, height, depth = BOUNDS["width"], BOUNDS["height"], BOUNDS["depth"]
    x_near = -width / 2 + u * width
    y = (1.0 - v) * height
    for box in BOXES:
        if not box[3] <= y <= box[4]:
            continue
        if axis in ("front", "back"):
            if box[1] <= x_near <= box[2] and box[5] < box[6]:
                return True
        else:
            z = -depth / 2 + u * depth
            if box[5] <= z <= box[6]:
                return True
    return False


def render(axis):
    width, height = BOUNDS["width"], BOUNDS["height"]
    span = width if axis in ("front", "back") else BOUNDS["depth"]
    columns = int(round(span * PIXELS_PER_METRE))
    rows = int(round(height * PIXELS_PER_METRE))
    grid = []
    for py in range(rows):
        v = (py + 0.5) / rows
        row = []
        for px in range(columns):
            u = (px + 0.5) / columns
            row.append(255 if covered(axis, u, v) else 0)
        grid.append(row)
    return grid


def analytic_volume():
    total = 0.0
    for _name, x0, x1, y0, y1, z0, z1 in BOXES:
        total += (x1 - x0) * (y1 - y0) * (z1 - z0)
    return round(total, 9)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True,
                        help="new directory for phantom masks, spec and truth")
    args = parser.parse_args(argv)
    if args.out.exists():
        raise SystemExit("refusing to overwrite an existing phantom directory")

    args.out.mkdir(parents=True)
    views = []
    sizes = {}
    for axis in ("front", "back", "left", "right"):
        rows = render(axis)
        name = f"{axis}.png"
        sizes[axis] = write_gray_png(args.out / name, rows)
        views.append({"axis": axis, "mask": name, "threshold": 128})

    spec = {"bounds": dict(BOUNDS), "grid": GRID, "views": views}
    (args.out / "spec.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    truth = {
        "schema": "mgr.forge.phantom-silhouette-truth.v1",
        "subject": "synthetic-box-humanoid",
        "provenance": "self-authored analytic solid; no owner-private references",
        "bounds_m": dict(BOUNDS),
        "grid": GRID,
        "pixels_per_metre": PIXELS_PER_METRE,
        "mask_sizes": sizes,
        "boxes": [
            {"name": name, "min": [x0, y0, z0], "max": [x1, y1, z1],
             "volume_m3": round((x1 - x0) * (y1 - y0) * (z1 - z0), 9)}
            for name, x0, x1, y0, y1, z0, z1 in BOXES
        ],
        "analytic_volume_m3": analytic_volume(),
        "limitations": [
            "a synthetic solid is a harness for the method, not a character",
            "box corners are invisible to any silhouette; the hull rounds them at voxel scale",
            "silhouette agreement never proves likeness to a real person",
        ],
    }
    (args.out / "truth.json").write_text(json.dumps(truth, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "MATERIALIZED", "directory": str(args.out),
                      "subject": truth["subject"], "analytic_volume_m3": truth["analytic_volume_m3"],
                      "mask_sizes": sizes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
