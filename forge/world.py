"""Deterministic road graph, building entrances and coarse collision checks.

This is grid-road pathfinding over the prototype world, not a navmesh or
animation-ready pedestrian locomotion system.
"""

from collections import deque
import math


def _validate_manifest(world):
    spec = world["spec"]
    if spec["columns"] < 1 or spec["rows"] < 1:
        raise ValueError("invalid world grid")
    if len({item["id"] for item in world["buildings"]}) != len(world["buildings"]):
        raise ValueError("duplicate building ID")
    for item in world["buildings"]:
        col, row = item["lot"]
        if not (0 <= col < spec["columns"] and 0 <= row < spec["rows"]):
            raise ValueError("out-of-grid building")
    return spec


def graph_for_world(world):
    """Every road intersection is a node; neighboring nodes share a road."""
    spec = _validate_manifest(world)
    cols, rows = spec["columns"], spec["rows"]
    stride = spec["lot_size"] + spec["road_width"]
    nodes = {}
    for row in range(rows + 1):
        for col in range(cols + 1):
            key = f"r{row}-c{col}"
            neighbors = []
            for dc, dr in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                c, r = col + dc, row + dr
                if 0 <= c <= cols and 0 <= r <= rows:
                    neighbors.append(f"r{r}-c{c}")
            nodes[key] = {
                "position": [round((col-cols/2)*stride, 5), 0,
                             round((row-rows/2)*stride, 5)],
                "neighbors": sorted(neighbors),
            }
    return nodes


def entrance_for_building(world, building_id):
    """Return nearest north-facing boundary road node of a building's lot."""
    _validate_manifest(world)
    building = next((item for item in world["buildings"]
                     if item["id"] == building_id), None)
    if building is None:
        raise KeyError(f"unknown building: {building_id}")
    col, row = building["lot"]
    return f"r{row}-c{col}"


def shortest_road_path(world, from_building, to_building):
    """Shortest intersection path, with reproducible tie-breaking."""
    graph = graph_for_world(world)
    start = entrance_for_building(world, from_building)
    target = entrance_for_building(world, to_building)
    pending = deque([start])
    previous = {start: None}
    while pending:
        node = pending.popleft()
        if node == target:
            break
        for neighbor in graph[node]["neighbors"]:
            if neighbor not in previous:
                previous[neighbor] = node
                pending.append(neighbor)
    if target not in previous:
        raise ValueError("disconnected road graph")
    chain = []
    pointer = target
    while pointer is not None:
        chain.append(pointer)
        pointer = previous[pointer]
    chain.reverse()
    return {"from": from_building, "to": to_building,
            "intersection_ids": chain,
            "waypoints": [graph[node]["position"] for node in chain]}


def overlaps_building(world, x, y, z, radius=0):
    """Simple stationary horizontal disk vs building AABB, with vertical test."""
    if not all(math.isfinite(n) for n in (x, y, z, radius)) or radius < 0:
        raise ValueError("invalid collision query")
    _validate_manifest(world)
    collisions = []
    for b in world["buildings"]:
        bx, _, bz = b["center"]
        width, height, depth = b["size"]
        if not 0 <= y <= height:
            continue
        cx = max(bx - width/2, min(x, bx + width/2))
        cz = max(bz - depth/2, min(z, bz + depth/2))
        if (x-cx)**2 + (z-cz)**2 <= radius**2:
            collisions.append(b["id"])
    return collisions
