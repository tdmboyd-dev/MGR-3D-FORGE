"""Deterministic chunk registry and CPU mesh level of detail for simple worlds."""

from .geometry import Mesh, MATERIALS
import math


def chunk_world(world, *, chunk_lots=4):
    """Partition buildings into stable groups; no geometry streaming runtime yet."""
    if type(chunk_lots) is not int or not 1 <= chunk_lots <= 64:
        raise ValueError("chunk_lots must be 1..64")
    spec = world["spec"]
    stride = spec["lot_size"] + spec["road_width"]
    chunks = {}
    for building in world["buildings"]:
        col, row = building["lot"]
        c, r = col // chunk_lots, row // chunk_lots
        key = f"chunk-r{r:03d}-c{c:03d}"
        if key not in chunks:
            chunks[key] = {"id": key, "building_ids": [],
                           "lot_origin": [c * chunk_lots, r * chunk_lots]}
        chunks[key]["building_ids"].append(building["id"])
    for chunk in chunks.values():
        chunk["building_ids"].sort()
        col, row = chunk["lot_origin"]
        x = (col - (spec["columns"]-1)/2)*stride
        z = (row - (spec["rows"]-1)/2)*stride
        chunk["world_origin"] = [round(x, 5), 0, round(z, 5)]
    return {"schema": "mgr.forge.chunks.v1", "chunk_lots": chunk_lots,
            "chunks": [chunks[key] for key in sorted(chunks)]}


def simple_building_lod(world):
    """Level 1: remove separate roof geometry, retaining a single block per building.

    The generated geometry is approximately half the building triangle count
    but retains no textures/details, so this is a prototype mesh LOD.
    """
    meshes = [Mesh() for _ in MATERIALS]
    lookup = {name: i for i, (name, _) in enumerate(MATERIALS)}
    for building in world["buildings"]:
        x, y, z = building["center"]
        width, height, depth = building["size"]
        meshes[lookup[building["material"]]].box(x, y, z, width, height, depth)
    return meshes


def lod_for_distance(distance_meters, *, near=80.0, far=250.0):
    """Stable LOD budget decision; far LOD2 is a placeholder, not generated geometry."""
    if not all(math.isfinite(v) for v in (distance_meters, near, far)) or not 0 <= near < far or not 0 <= distance_meters:
        raise ValueError("invalid LOD distances")
    if distance_meters < near:
        return 0
    if distance_meters < far:
        return 1
    return 2
