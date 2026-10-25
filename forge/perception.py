"""MGR Spatial Eyes — geometry-grounded scene visibility and evidence labels.

Ray tests operate only on known building AABBs; not AI image understanding.
"""

import math


def _segment_hits_box(origin, target, center, dimensions):
    x, _, z = center
    width, height, depth = dimensions
    bounds = ((x-width/2, x+width/2), (0, height), (z-depth/2, z+depth/2))
    enter, leave = 0.0, 1.0
    for axis in range(3):
        movement = target[axis] - origin[axis]
        low, high = bounds[axis]
        if abs(movement) < 1e-12:
            if origin[axis] < low or origin[axis] > high:
                return False
            continue
        t1 = (low-origin[axis])/movement
        t2 = (high-origin[axis])/movement
        enter = max(enter, min(t1,t2))
        leave = min(leave, max(t1,t2))
        if enter > leave:
            return False
    return leave >= 0 and enter < 1.0 and enter <= leave


def scene_overview(world, *, camera=(0, 45, 0)):
    """Identify scene entities, distances and possible occlusion from camera.

    The geometry is known because Forge generated it; results must not be
    represented as measurements of a real building or inferred hidden spaces.
    """
    if len(camera) != 3 or not all(type(value) in (int,float) and math.isfinite(value)
                                       for value in camera):
        raise ValueError("camera must be finite XYZ")
    buildings = world["buildings"]
    observations = []
    for subject in buildings:
        x, _, z = subject["center"]
        target = (x, subject["size"][1]/2, z)
        occluded_by = []
        for obstacle in buildings:
            if obstacle["id"] == subject["id"]:
                continue
            if _segment_hits_box(camera, target, obstacle["center"], obstacle["size"]):
                occluded_by.append(obstacle["id"])
        distance = math.dist(camera,target)
        observations.append({"id":subject["id"], "category":"building",
                             "position":list(target), "distance_m":round(distance,4),
                             "visible_center":not occluded_by,
                             "occluded_by":sorted(occluded_by),
                             "evidence":"generated-scene-geometry",
                             "real_world_verified":False})
    return {"schema":"mgr.forge.spatial-eyes.v1", "camera":list(camera),
            "observations":sorted(observations,key=lambda item:item["id"]),
            "limitations":["box geometry only", "single ray to each building center",
                           "not real-world sensing", "cannot infer invisible details"]}
