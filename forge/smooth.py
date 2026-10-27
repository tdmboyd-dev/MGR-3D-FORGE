"""Vertex de-duplication and normal averaging for honest smooth shading.

The Forge voxel hulls are intentionally flat-shaded so their voxel origin is
visible. This module produces a *smoothly shaded* copy of the same geometry by
averaging face normals at shared vertices. It changes **shading only**: the
triangle set, vertex positions and volume are identical, so the GLB/OBJ receipts
remain comparable and no geometry is invented.
"""

from __future__ import annotations

from collections import defaultdict

from .geometry import Mesh


def _key(position):
    return (round(position[0], 9), round(position[1], 9), round(position[2], 9))


def smooth_normals(mesh: Mesh) -> Mesh:
    """Return a copy of *mesh* with shared vertices and averaged normals."""
    if not mesh.indices:
        return Mesh()

    # De-duplicate vertices by position.
    index_map = {}
    new_positions = []
    key_to_new = {}
    for old in range(len(mesh.positions) // 3):
        key = _key(mesh.positions[old * 3:(old + 1) * 3])
        if key not in key_to_new:
            key_to_new[key] = len(new_positions) // 3
            new_positions.extend(mesh.positions[old * 3:(old + 1) * 3])
        index_map[old] = key_to_new[key]

    # Remap indices to de-duplicated vertices.
    new_indices = [index_map[i] for i in mesh.indices]

    # Accumulate face normals per de-duplicated vertex.
    accum = defaultdict(lambda: [0.0, 0.0, 0.0])
    for t in range(0, len(new_indices), 3):
        a, b, c = new_indices[t], new_indices[t + 1], new_indices[t + 2]
        pa = new_positions[a * 3:(a + 1) * 3]
        pb = new_positions[b * 3:(b + 1) * 3]
        pc = new_positions[c * 3:(c + 1) * 3]
        ux, uy, uz = (pb[i] - pa[i] for i in range(3))
        vx, vy, vz = (pc[i] - pa[i] for i in range(3))
        nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        for v in (a, b, c):
            accum[v][0] += nx
            accum[v][1] += ny
            accum[v][2] += nz

    new_normals = []
    for v in range(len(new_positions) // 3):
        nx, ny, nz = accum[v]
        mag = (nx * nx + ny * ny + nz * nz) ** 0.5
        if mag == 0:
            new_normals.extend((0.0, 1.0, 0.0))
        else:
            new_normals.extend((nx / mag, ny / mag, nz / mag))

    result = Mesh()
    result.positions = new_positions
    result.normals = new_normals
    result.indices = new_indices
    return result
