"""CPU mesh health checks and conservative triangle cleanup."""

import math

from .geometry import Mesh


def analyze_mesh(mesh, *, epsilon=1e-12):
    """Count invalid geometry, without trusting indices or floating coordinates."""
    if len(mesh.positions) % 3 or len(mesh.normals) != len(mesh.positions):
        raise ValueError("invalid vertex arrays")
    if len(mesh.indices) % 3:
        raise ValueError("triangle index list not divisible by three")
    count = len(mesh.positions) // 3
    if not all(math.isfinite(x) for x in mesh.positions + mesh.normals):
        raise ValueError("nonfinite coordinates")
    bad_indices, degenerate = [], []
    for triangle in range(len(mesh.indices)//3):
        a,b,c = mesh.indices[triangle*3:triangle*3+3]
        if not all(type(i) is int and 0 <= i < count for i in (a,b,c)):
            bad_indices.append(triangle)
            continue
        p,q,r = ([mesh.positions[i*3+j] for j in range(3)] for i in (a,b,c))
        u = [q[j]-p[j] for j in range(3)]
        v = [r[j]-p[j] for j in range(3)]
        cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2],
                 u[0]*v[1]-u[1]*v[0])
        if sum(x*x for x in cross) <= epsilon:
            degenerate.append(triangle)
    return {"triangles": len(mesh.indices)//3, "bad_index_triangles": bad_indices,
            "degenerate_triangles": degenerate,
            "passed": not bad_indices and not degenerate}


def remove_bad_triangles(mesh):
    """Return clean copy, keeping vertices unchanged to preserve UV/part indices.

    Only repairs index corruption and zero-area faces, not topology/manifoldness.
    """
    quality = analyze_mesh(mesh)
    excluded = set(quality["bad_index_triangles"] + quality["degenerate_triangles"])
    result = Mesh(positions=list(mesh.positions), normals=list(mesh.normals))
    for triangle in range(quality["triangles"]):
        if triangle not in excluded:
            result.indices.extend(mesh.indices[triangle*3:triangle*3+3])
    return result, {"removed_triangles": len(excluded),
                    "remaining_triangles": len(result.indices)//3,
                    "remaining_quality": analyze_mesh(result)}
