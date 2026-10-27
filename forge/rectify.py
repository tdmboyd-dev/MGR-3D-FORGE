"""Perspective-to-orthographic rectification for multi-view reconstruction.

Converts a perspective view (with known 4-point correspondences) into an
orthographic silhouette mask that can feed `forge.multiview`. Pure Python, no
OpenCV dependency. Honest limitation: quality depends entirely on the accuracy
of the 4-point correspondences; a bad correspondence produces a bad mask.
"""

from __future__ import annotations

import math
from typing import Sequence

SCHEMA = "mgr.forge.rectify.v1"


def _solve_3x3(a, b):
    """Solve A x = b for a 3x3 system using Gaussian elimination."""
    # augment
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    n = 3
    for col in range(n):
        # pivot
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-12:
            return None
        m[col], m[piv] = m[piv], m[col]
        pv = m[col][col]
        m[col] = [x / pv for x in m[col]]
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            m[r] = [m[r][k] - factor * m[col][k] for k in range(n + 1)]
    return [m[i][n] for i in range(n)]


def homography(src: Sequence[Sequence[float]], dst: Sequence[Sequence[float]]):
    """Compute 3x3 homography H such that dst = H @ src (homogeneous).

    src, dst: 4 point pairs, each a (x, y) sequence. Returns a flat list of 9
    floats (row-major) or None if degenerate.
    """
    if len(src) != 4 or len(dst) != 4:
        raise ValueError("homography requires exactly 4 point pairs")
    # Build 8x8 system: for each point pair, two equations.
    A = []
    bb = []
    for (sx, sy), (dx, dy) in zip(src, dst):
        A.append([sx, sy, 1, 0, 0, 0, -dx * sx, -dx * sy])
        bb.append(dx)
        A.append([0, 0, 0, sx, sy, 1, -dy * sx, -dy * sy])
        bb.append(dy)
    # Solve 8x8 via Gaussian elimination.
    n = 8
    m = [A[i][:] + [bb[i]] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-12:
            return None
        m[col], m[piv] = m[piv], m[col]
        pv = m[col][col]
        m[col] = [x / pv for x in m[col]]
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            m[r] = [m[r][k] - factor * m[col][k] for k in range(n + 1)]
    h = [m[i][n] for i in range(n)] + [1.0]
    return h


def apply_homography(H, x, y):
    """Apply homography H (flat 9) to point (x,y). Returns (x', y') or None."""
    a, b, c, d, e, f, g, h, i = H
    denom = g * x + h * y + i
    if abs(denom) < 1e-12:
        return None
    xp = (a * x + b * y + c) / denom
    yp = (d * x + e * y + f) / denom
    return (xp, yp)


def warp_perspective_to_orthographic(src_pixels, src_size, dst_size, H):
    """Warp a (width,height) grayscale image using inverse homography.

    src_pixels: list of rows (each a list of 0/255 ints), size src_size=(w,h).
    dst_size: (w,h) of output.
    H: 3x3 homography mapping dst -> src (inverse). Pass the inverse if needed.
    Returns a list of rows of 0/255 ints.
    """
    sw, sh = src_size
    dw, dh = dst_size
    # compute inverse if H maps src->dst? We assume H maps dst coords -> src coords.
    out = []
    for dy in range(dh):
        row = []
        for dx in range(dw):
            pt = apply_homography(H, dx + 0.5, dy + 0.5)
            if pt is None:
                row.append(0)
                continue
            sx, sy = pt
            # bilinear sample
            x0 = int(math.floor(sx))
            y0 = int(math.floor(sy))
            if x0 < 0 or y0 < 0 or x0 + 1 >= sw or y0 + 1 >= sh:
                row.append(0)
                continue
            fx = sx - x0
            fy = sy - y0
            v00 = src_pixels[y0][x0]
            v10 = src_pixels[y0][x0 + 1]
            v01 = src_pixels[y0 + 1][x0]
            v11 = src_pixels[y0 + 1][x0 + 1]
            val = (v00 * (1 - fx) * (1 - fy) + v10 * fx * (1 - fy)
                   + v01 * (1 - fx) * fy + v11 * fx * fy)
            row.append(255 if val >= 128 else 0)
        out.append(row)
    return out


def rectify_mask(src_pixels, src_size, dst_size, src_quad, dst_quad):
    """Convenience: compute H from src_quad->dst_quad and warp.

    src_quad, dst_quad: 4 corner points each. H maps dst -> src (inverse of src->dst).
    """
    H_forward = homography(src_quad, dst_quad)
    if H_forward is None:
        raise ValueError("degenerate homography")
    # invert H_forward to get dst->src
    a, b, c, d, e, f, g, h, i = H_forward
    # compute inverse of 3x3
    det = (a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g))
    if abs(det) < 1e-12:
        raise ValueError("singular homography")
    inv = [
        (e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det,
        (f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det,
        (d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det,
    ]
    return warp_perspective_to_orthographic(src_pixels, src_size, dst_size, inv)
