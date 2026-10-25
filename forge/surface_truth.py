"""MGR Surface Truth: conservative CPU triangle edge-manifold evidence.

An edge-closed triangle shell is not necessarily printable, self-intersection
free, or a valid solid. This is a first falsifiable geometry gate only.
"""

import math
from collections import Counter


def inspect_surface_edges(mesh, *, precision_digits=6, max_triangles=500_000):
    if type(precision_digits) is not int or not 0<=precision_digits<=9:
        raise ValueError("precision digits must be 0..9")
    if type(max_triangles) is not int or not 1<=max_triangles<=1_000_000:
        raise ValueError("bounded triangle allowance required")
    if len(mesh.positions)%3 or len(mesh.indices)%3 or len(mesh.indices)//3>max_triangles:
        raise ValueError("invalid or over-budget mesh")
    if not all(math.isfinite(v) for v in mesh.positions):
        raise ValueError("finite mesh positions required")
    count=len(mesh.positions)//3
    if any(type(i) is not int or i<0 or i>=count for i in mesh.indices):
        raise ValueError("bad mesh index")
    points=[tuple(round(v,precision_digits) for v in mesh.positions[i:i+3])
            for i in range(0,len(mesh.positions),3)]
    edges=Counter()
    degenerates=0
    for i in range(0,len(mesh.indices),3):
        a,b,c=(points[j] for j in mesh.indices[i:i+3])
        u=tuple(b[k]-a[k] for k in range(3))
        v=tuple(c[k]-a[k] for k in range(3))
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        if a==b or b==c or a==c or sum(x*x for x in cross)<1e-18:
            degenerates+=1
            continue
        for first,second in ((a,b),(b,c),(c,a)):
            edges[tuple(sorted((first,second)))]+=1
    boundary=sum(1 for times in edges.values() if times==1)
    nonmanifold=sum(1 for times in edges.values() if times>2)
    triangle_count=len(mesh.indices)//3
    candidate=triangle_count>0 and not degenerates and boundary==0 and nonmanifold==0
    return {"schema":"mgr.forge.surface-edge-audit.v1",
            "triangles":triangle_count,"unique_edges":len(edges),
            "boundary_edges":boundary,"nonmanifold_edges":nonmanifold,
            "degenerate_triangles":degenerates,
            "edge_closed_candidate":candidate,
            "status":"PASS" if candidate else "FAIL",
            "limitations":["position-based approximate welding; not exact topology",
                           "no self-intersection, winding orientation, solid volume, or thickness proof",
                           "edge-closed candidate does not imply 3D-print readiness"]}
