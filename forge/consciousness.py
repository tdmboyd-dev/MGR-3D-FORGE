"""MGR Scene Consciousness: deterministic facts about generated worlds.

No hidden-space inference or computer vision is claimed by this module.
"""

import math

from forge.world import _validate_manifest, entrance_for_building, shortest_road_path


def scene_facts(world):
    """Create a queryable, evidence-tagged inventory from generated geometry."""
    _validate_manifest(world)
    facts = []
    for building in sorted(world["buildings"], key=lambda item: item["id"]):
        coords = building["center"]
        dims = building["size"]
        if len(coords) != 3 or len(dims) != 3:
            raise ValueError("invalid building dimensions")
        if not all(type(n) in (int, float) and math.isfinite(n) for n in (*coords, *dims)):
            raise ValueError("nonfinite scene geometry")
        if any(n <= 0 for n in dims):
            raise ValueError("nonpositive scene dimensions")
        facts.append({
            "id": building["id"], "kind": "building",
            "position_m": list(coords), "dimensions_m": list(dims),
            "lot": list(building["lot"]),
            "road_entrance": entrance_for_building(world, building["id"]),
            "evidence": "generated-scene-geometry",
            "confidence": "exact-generated-data",
        })
    return {
        "schema": "mgr.forge.scene-consciousness.v1",
        "objects": facts,
        "limitations": ["generated objects only", "road entrance is a grid heuristic",
                        "no verified door portal or interior access", "no image sensing"],
    }


def scene_query(world, *, building_id=None, route_to=None):
    """Return only known objects and explicitly qualified road routes."""
    facts = scene_facts(world)
    if building_id is None:
        if route_to is not None:
            raise ValueError("route_to needs building_id")
        return facts
    matches = [item for item in facts["objects"] if item["id"] == building_id]
    if not matches:
        raise KeyError(f"unknown generated building: {building_id}")
    response = {"schema": facts["schema"], "object": matches[0]}
    if route_to is not None:
        response["route"] = shortest_road_path(world, building_id, route_to)
        response["route_evidence"] = "generated-road-graph-only; not navmesh verified"
    return response
