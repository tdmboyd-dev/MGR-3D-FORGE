"""MGR Beyond Imagery: generated, editable room hypotheses inside buildings.

Not photogrammetry. Given a known external footprint, generate two plausible
rooms with door openings, while preserving that they are invented geometry.
"""

from .geometry import Mesh, MATERIALS


def generate_interiors(world):
    """Return separated interior mesh and labeled room/floor-plan provenance."""
    meshes = [Mesh() for _ in MATERIALS]
    rooms = []
    floor = meshes[3]
    walls = meshes[2]
    for b in world["buildings"]:
        x, _, z = b["center"]
        width, exterior_height, depth = b["size"]
        w, d = width-0.4, depth-0.4
        height = min(3.0, exterior_height-0.4)
        t = 0.18
        door = min(1.2, d/3)
        door_height = min(2.1, height-0.3)
        # Floor and four perimeter walls, with one centered entrance in south wall.
        floor.box(x, -0.12, z, w, 0.12, d)
        walls.box(x, 0, z+d/2-t/2, w, height, t)
        for side in (-1, 1):
            walls.box(x+side*(w+door)/4, 0, z-d/2+t/2,
                      (w-door)/2, height, t)
        walls.box(x, door_height, z-d/2+t/2, door, height-door_height, t)
        for side in (-1, 1):
            walls.box(x+side*(w/2-t/2), 0, z, t, height, d)
        # Two rooms, split along the X axis, with a center passage in the partition.
        for side in (-1,1):
            side_length = (d-door)/2
            walls.box(x, 0, z+side*(d+door)/4, t, height, side_length)
        walls.box(x, door_height, z, t, height-door_height, door)
        rooms.append({"building_id": b["id"], "count": 2,
                      "room_ids": [f"{b['id']}-west", f"{b['id']}-east"],
                      "floor_elevation": 0, "wall_height":round(height,4),
                      "door_width":round(door,4),
                      "provenance":"MGR-procedural-hypothesis",
                      "reference_observed":False,
                      "owner_approved":False})
    return meshes, {"schema":"mgr.forge.interiors.v1", "room_sets":rooms,
                    "source":"generated design hypothesis, not sensed reality"}
