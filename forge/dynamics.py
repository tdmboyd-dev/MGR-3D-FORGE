"""MGR CPU continuous horizontal collision guard for actor motion segments.

Conservative expanded boxes prevent skipped thin walls in sampled routes.
This is not a 3D rigid-body solver, ragdoll or full character controller.
"""

import math


def first_motion_contact(start_xz, end_xz, radius_m, obstacles):
    """Return earliest sweep collision with an expanded 2D AABB.

    obstacles: iterable [{id, bounds:[xmin,zmin,xmax,zmax]}]. Tie-break by ID.
    Since rounded-box geometry is approximated by expanded AABBs, contact
    may happen conservatively early near corners.
    """
    if (not isinstance(start_xz, (list, tuple)) or len(start_xz) != 2
            or not isinstance(end_xz, (list, tuple)) or len(end_xz) != 2
            or type(radius_m) not in (int, float)):
        raise ValueError("finite two-dimensional motion points and radius required")
    values = [*start_xz, *end_xz, radius_m]
    if not all(type(v) in (int, float) and math.isfinite(v) for v in values) or not 0 <= radius_m <= 25:
        raise ValueError("motion coordinates and radius must be finite and bounded")
    if not isinstance(obstacles, list) or len(obstacles) > 100_000:
        raise ValueError("bounded obstacle list required")
    candidates = []
    direction = [end_xz[i] - start_xz[i] for i in range(2)]
    for box in obstacles:
        if not isinstance(box, dict) or set(box) != {"id", "bounds"}:
            raise ValueError("obstacle requires id and bounds")
        name, bounds = box["id"], box["bounds"]
        if not isinstance(name, str) or not name:
            raise ValueError("obstacle ID required")
        if (not isinstance(bounds, (list, tuple)) or len(bounds) != 4
                or not all(type(v) in (int, float) and math.isfinite(v) for v in bounds)
                or not bounds[0] < bounds[2] or not bounds[1] < bounds[3]):
            raise ValueError("finite increasing AABB bounds required")
        limits = ((bounds[0] - radius_m, bounds[2] + radius_m),
                  (bounds[1] - radius_m, bounds[3] + radius_m))
        entry, departure = 0.0, 1.0
        normal = (0, 0)
        for axis in range(2):
            lower, upper = limits[axis]
            origin, velocity = start_xz[axis], direction[axis]
            if velocity == 0:
                if origin < lower or origin > upper:
                    departure = -1
                    break
                continue
            near, far = ((lower - origin) / velocity, (upper - origin) / velocity)
            if near > far:
                near, far = far, near
            if near > entry:
                entry = near
                sign = -1 if velocity > 0 else 1
                normal = (sign, 0) if axis == 0 else (0, sign)
            departure = min(departure, far)
        if departure >= entry and 0 <= entry <= 1:
            candidates.append((entry, name, normal))
    if not candidates:
        return {"schema": "mgr.forge.actor-sweep.v1", "status": "CLEAR", "hit": None}
    time, name, normal = min(candidates, key=lambda item: (item[0], item[1]))
    return {"schema": "mgr.forge.actor-sweep.v1", "status": "CONTACT",
            "hit": {"obstacle_id": name, "fraction": round(time, 8),
                    "position_xz": [round(start_xz[i] + time * direction[i], 8) for i in range(2)],
                    "approx_normal_xz": list(normal)},
            "limitations": ["conservative expanded 2D AABB, not exact rounded corners",
                            "no slopes, elevation, joint solver or animated mesh collision"]}
