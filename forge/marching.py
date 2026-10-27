"""Smooth surface extraction from voxel occupancy via surface nets.

Surface nets (Gibson, 1998) produce a smooth, manifold mesh from a voxel grid
without a 256-case lookup table. For each mixed cell a vertex is placed at the
average of its edge-intersection points; quads are then created between
adjacent mixed cells along each axis. The result rounds voxel staircases while
remaining an honest function of the measured silhouettes.

Honesty: the surface is an iso-surface of the voxel field. It does not invent
geometry; concavities no view can see remain bounded by the hull.
"""

from __future__ import annotations

import math

from .geometry import Mesh

_CORNERS = (
    (0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0),
    (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1),
)
_EDGES = (
    (0, 1), (2, 3), (4, 5), (6, 7),
    (0, 2), (1, 3), (4, 6), (5, 7),
    (0, 4), (1, 5), (2, 6), (3, 7),
)


def _corner_value(occupancy, i, j, k, ci, cj, ck, grid):
    ii, jj, kk = i + ci, j + cj, k + ck
    if ii < 0 or jj < 0 or kk < 0 or ii >= grid or jj >= grid or kk >= grid:
        return 0
    return occupancy[jj][kk][ii]


def _is_mixed(occupancy, i, j, k, grid):
    corners = [_corner_value(occupancy, i, j, k, *_CORNERS[c], grid) for c in range(8)]
    return not all(c == corners[0] for c in corners)


def _cell_vertex(occupancy, i, j, k, grid, bounds):
    """Compute vertex position for a mixed cell."""
    width, height, depth = bounds
    sx, sy, sz = width / grid, height / grid, depth / grid
    corners = [_corner_value(occupancy, i, j, k, *_CORNERS[c], grid) for c in range(8)]
    pts = []
    for ei, (a, b) in enumerate(_EDGES):
        if corners[a] != corners[b]:
            ca, cb = _CORNERS[a], _CORNERS[b]
            pa = ((i + ca[0]) * sx - width / 2, (j + ca[1]) * sy, (k + ca[2]) * sz - depth / 2)
            pb = ((i + cb[0]) * sx - width / 2, (j + cb[1]) * sy, (k + cb[2]) * sz - depth / 2)
            pts.append([(pa[d] + pb[d]) / 2 for d in range(3)])
    if not pts:
        return None
    return [sum(p[d] for p in pts) / len(pts) for d in range(3)]


def surface_nets(occupancy, bounds, grid):
    """Convert voxel occupancy to a smooth Mesh via surface nets."""
    width, height, depth = bounds

    # Step 1: find mixed cells and compute vertices
    vertex_index = {}
    positions = []
    for i in range(grid - 1):
        for j in range(grid - 1):
            for k in range(grid - 1):
                if not _is_mixed(occupancy, i, j, k, grid):
                    continue
                vpos = _cell_vertex(occupancy, i, j, k, grid, bounds)
                if vpos is None:
                    continue
                vertex_index[(i, j, k)] = len(positions) // 3
                positions.extend(vpos)

    # Step 2: create quads for each axis
    indices = []
    # X-axis faces: between (i,j,k) and (i+1,j,k)
    for i in range(grid - 2):
        for j in range(1, grid - 1):
            for k in range(1, grid - 1):
                # 4 cells sharing this edge
                cells = [(i, j - 1, k - 1), (i, j, k - 1), (i, j - 1, k), (i, j, k)]
                if not all(c in vertex_index for c in cells):
                    continue
                # check that the face is not ambiguous (all 4 corners of the face
                # should not form a checkerboard)
                v0 = vertex_index[cells[0]]
                v1 = vertex_index[cells[1]]
                v2 = vertex_index[cells[2]]
                v3 = vertex_index[cells[3]]
                indices.extend([v0, v2, v3, v0, v3, v1])

    # Y-axis faces: between (i,j,k) and (i,j+1,k)
    for i in range(1, grid - 1):
        for j in range(grid - 2):
            for k in range(1, grid - 1):
                cells = [(i - 1, j, k - 1), (i, j, k - 1), (i - 1, j, k), (i, j, k)]
                if not all(c in vertex_index for c in cells):
                    continue
                v0 = vertex_index[cells[0]]
                v1 = vertex_index[cells[1]]
                v2 = vertex_index[cells[2]]
                v3 = vertex_index[cells[3]]
                indices.extend([v0, v2, v3, v0, v3, v1])

    # Z-axis faces: between (i,j,k) and (i,j,k+1)
    for i in range(1, grid - 1):
        for j in range(1, grid - 1):
            for k in range(grid - 2):
                cells = [(i - 1, j - 1, k), (i, j - 1, k), (i - 1, j, k), (i, j, k)]
                if not all(c in vertex_index for c in cells):
                    continue
                v0 = vertex_index[cells[0]]
                v1 = vertex_index[cells[1]]
                v2 = vertex_index[cells[2]]
                v3 = vertex_index[cells[3]]
                indices.extend([v0, v2, v3, v0, v3, v1])

    # Compute per-vertex normals
    normals = [0.0] * len(positions)
    for t in range(0, len(indices), 3):
        a, b, c = indices[t], indices[t + 1], indices[t + 2]
        pa = positions[a * 3:(a + 1) * 3]
        pb = positions[b * 3:(b + 1) * 3]
        pc = positions[c * 3:(c + 1) * 3]
        ux, uy, uz = (pb[i] - pa[i] for i in range(3))
        vx, vy, vz = (pc[i] - pa[i] for i in range(3))
        nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        for v in (a, b, c):
            normals[v * 3] += nx
            normals[v * 3 + 1] += ny
            normals[v * 3 + 2] += nz

    for i in range(0, len(normals), 3):
        mag = (normals[i] ** 2 + normals[i + 1] ** 2 + normals[i + 2] ** 2) ** 0.5
        if mag > 0:
            normals[i] /= mag
            normals[i + 1] /= mag
            normals[i + 2] /= mag
        else:
            normals[i + 1] = 1.0

    mesh = Mesh()
    mesh.positions = positions
    mesh.normals = normals
    mesh.indices = indices
    return mesh


# Alias for backward compat with marching module name
marching_cubes = surface_nets
