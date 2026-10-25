"""MGR-native editable 3D camera tour, independent of pre-rendered video."""

import math


def camera_tour(world, *, altitude=18.0):
    """Make a deterministic tour through every generated building by world location."""
    if not math.isfinite(altitude) or not 3 <= altitude <= 200:
        raise ValueError("camera altitude must be 3..200 m")
    buildings = sorted(world["buildings"], key=lambda item: (
        item["lot"][1], item["lot"][0], item["id"]))
    max_world_height=max((item["size"][1] for item in buildings),default=0)
    lot_size=world.get("spec",{}).get("lot_size",20)
    if not isinstance(lot_size,(int,float)) or not math.isfinite(lot_size) or lot_size<=0:
        raise ValueError("invalid lot size")
    shots = []
    for idx, building in enumerate(buildings):
        x, _, z = building["center"]
        height = building["size"][1]
        # Place the camera above ALL known roofs, not just its subject.
        # Previously the camera could sit inside a tall neighboring building;
        # real Blender renders then showed an unhelpful close-up of its roof.
        horizontal=max(24,1.6*lot_size,2*max(building["size"][0],building["size"][2]))
        height_above=max(max_world_height+16,altitude,height+horizontal*.7)
        shots.append({"id": f"shot-{idx:04d}", "subject_id": building["id"],
                      "camera": [round(x-horizontal, 4), round(height_above, 4), round(z-horizontal, 4)],
                      "look_at": [x, round(height/2,4), z],
                      "hold_seconds": 2.0})
    return {"schema": "mgr.forge.camera-tour.v1", "axis": "Y_UP",
            "mode": "native-3d-keyframes", "shots": shots,
            "requires_generated_video": False, "requires_paid_api": False}


def interpolate_shots(first, second, t):
    """Linear interpolation of camera and focus; renderer can sample per-frame."""
    if not math.isfinite(t) or not 0 <= t <= 1:
        raise ValueError("t must be between 0 and 1")
    return {field: [round(a*(1-t)+b*t, 6)
                    for a,b in zip(first[field], second[field])]
            for field in ("camera", "look_at")}
