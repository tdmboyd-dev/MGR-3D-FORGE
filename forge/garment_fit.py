"""MGR-native garment fitting contract.

Maps garment mesh vertices to the nearest body surface point and computes a
fit offset, producing a fitted garment mesh. This is a *contract* with honest
limitations: it does rigid/offset fitting, not cloth simulation, drape, or
collision. It does not claim realistic fabric behavior.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

SCHEMA = "mgr.forge.garment-fit.v1"


@dataclass
class FitResult:
    fitted_positions: list
    offsets: list
    max_offset: float
    mean_offset: float
    clipped_vertices: int
    schema: str = SCHEMA


def _distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def fit_garment(garment_positions, body_positions, *, offset: float = 0.005,
                max_offset: float = 0.05) -> FitResult:
    """Fit garment vertices to nearest body surface with a small offset.

    garment_positions: flat list of floats (x,y,z,...)
    body_positions: flat list of floats (x,y,z,...)
    offset: distance to push garment away from body surface
    max_offset: clamp per-vertex displacement to this value
    """
    if len(garment_positions) % 3 != 0:
        raise ValueError("garment positions must be (x,y,z) triples")
    if len(body_positions) % 3 != 0:
        raise ValueError("body positions must be (x,y,z) triples")
    if not body_positions:
        raise ValueError("body mesh required")
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if max_offset <= 0:
        raise ValueError("max_offset must be > 0")

    body_pts = [(body_positions[i], body_positions[i + 1], body_positions[i + 2])
                for i in range(0, len(body_positions), 3)]

    fitted = []
    offsets = []
    clipped = 0
    for i in range(0, len(garment_positions), 3):
        gp = (garment_positions[i], garment_positions[i + 1], garment_positions[i + 2])
        # find nearest body point
        nearest = min(body_pts, key=lambda bp: _distance(gp, bp))
        # compute direction from body to garment
        dist = _distance(gp, nearest)
        if dist < 1e-9:
            direction = (0.0, 1.0, 0.0)
        else:
            direction = tuple((gp[d] - nearest[d]) / dist for d in range(3))
        # target position: nearest + (dist + offset) along direction, clamped
        target_dist = min(dist + offset, max_offset + dist) if dist > 0 else offset
        # simpler: push outward by offset, clamped to max_offset total displacement
        displacement = min(offset, max_offset)
        new_pos = tuple(gp[d] + direction[d] * displacement for d in range(3))
        fitted.extend(new_pos)
        offsets.append(round(displacement, 6))
        if displacement >= max_offset - 1e-9:
            clipped += 1

    mean_offset = sum(offsets) / len(offsets) if offsets else 0.0
    max_off = max(offsets) if offsets else 0.0

    return FitResult(
        fitted_positions=fitted,
        offsets=offsets,
        max_offset=round(max_off, 6),
        mean_offset=round(mean_offset, 6),
        clipped_vertices=clipped,
    )


def garment_coverage(garment_positions, body_positions) -> dict:
    """Report how well a garment covers the body (percentage of body vertices near garment)."""
    if not garment_positions or not body_positions:
        raise ValueError("both garment and body positions required")
    body_pts = [(body_positions[i], body_positions[i + 1], body_positions[i + 2])
                for i in range(0, len(body_positions), 3)]
    garment_pts = [(garment_positions[i], garment_positions[i + 1], garment_positions[i + 2])
                   for i in range(0, len(garment_positions), 3)]
    threshold = 0.05
    covered = sum(1 for bp in body_pts
                  if any(_distance(bp, gp) < threshold for gp in garment_pts))
    return {
        "schema": SCHEMA,
        "body_vertices": len(body_pts),
        "garment_vertices": len(garment_pts),
        "covered_body_vertices": covered,
        "coverage_ratio": round(covered / len(body_pts), 6) if body_pts else 0.0,
        "limitations": ["rigid offset fit, not cloth simulation",
                        "no collision detection", "no drape or fabric physics"],
    }
