"""Measure how a silhouette reconstruction behaves across voxel resolutions.

Runs the phantom example at several grids and reports the silhouette fit and the
accuracy of each hull against the phantom's analytic solid. The point is to show
where resolution stops helping: the visual hull's residual error is ambiguity
between views, not voxel size, and this table proves which is which.

    python scripts/hull_resolution_sweep.py --example examples/multiview-phantom \
        --out evidence/blender/windows-wave25-multiview-sweep.json
"""

import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forge.multiview import SCORE_SCHEMA, reconstruct, score_against_solid  # noqa: E402

GRIDS = (40, 48, 56, 64, 72, 80, 96)


def sweep(example):
    root = Path(example)
    spec = json.loads((root / "spec.json").read_text(encoding="utf-8"))
    truth = json.loads((root / "truth.json").read_text(encoding="utf-8"))
    spec["base_dir"] = str(root.resolve())
    rows = []
    for grid in GRIDS:
        trial = dict(spec)
        trial["grid"] = grid
        start = time.perf_counter()
        try:
            _mesh, manifest = reconstruct(trial)
            score = score_against_solid(trial, truth["boxes"])
        except ValueError as error:
            rows.append({"grid": grid, "refused": str(error),
                         "seconds": round(time.perf_counter() - start, 3)})
            continue
        rows.append({
            "grid": grid,
            "seconds": round(time.perf_counter() - start, 3),
            "triangles": manifest["triangles"],
            "vertices": manifest["vertices"],
            "worst_view_iou": manifest["fit"]["worst_view_iou"],
            "fit": manifest["fit"]["status"],
            "hull_volume_m3": score["hull_volume_m3"],
            "solid_volume_m3": score["solid_volume_m3"],
            "hull_vs_solid_iou": score["hull_vs_solid_iou"],
            "overfill_volume_m3": score["overfill_volume_m3"],
            "missed_volume_m3": score["missed_volume_m3"],
        })
    accepted = [row for row in rows if row.get("fit") == "PASS"]
    return {
        "schema": SCORE_SCHEMA,
        "status": "MEASURED",
        "evidence_level": "RESOLUTION_SWEEP_VS_ANALYTIC_SOLID",
        "example": str(root.name),
        "subject": truth["subject"],
        "analytic_volume_m3": truth["analytic_volume_m3"],
        "grids": list(GRIDS),
        "rows": rows,
        "best_hull_vs_solid_iou": max((row["hull_vs_solid_iou"] for row in accepted), default=0.0),
        "worst_hull_vs_solid_iou": min((row["hull_vs_solid_iou"] for row in accepted), default=0.0),
        "notes": [
            "silhouette fit is measured per view at mask resolution",
            "hull accuracy is measured per voxel against the analytic solid",
            "a plateau in accuracy while triangles grow means the remaining error is view ambiguity, not voxel size",
            "coarse grids are refused by the fit gate instead of returning a blobby hull",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        raise SystemExit("refusing to overwrite an existing sweep receipt")
    receipt = sweep(args.example)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "out": str(args.out),
                      "best_hull_vs_solid_iou": receipt["best_hull_vs_solid_iou"],
                      "worst_hull_vs_solid_iou": receipt["worst_hull_vs_solid_iou"],
                      "refused_grids": [row["grid"] for row in receipt["rows"]
                                        if "refused" in row]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
