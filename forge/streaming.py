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


def plan_chunk_residency(chunks, camera_xyz, *, active_radius_m=120.0,
                         prefetch_radius_m=180.0, max_active=64,
                         previously_resident=()):
    """CPU deterministic camera-distance cell scheduler, NOT asset I/O.

    Stage a bounded active/prefetch set and emit evictions. This is an
    independently testable *plan*, not proof that any renderer loaded cells,
    applied occlusion culling, or reached a particular frame rate.
    """
    if len(camera_xyz)!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in camera_xyz):
        raise ValueError("finite camera XYZ required")
    if not all(type(v) in (int,float) and math.isfinite(v) for v in (active_radius_m,prefetch_radius_m)):
        raise ValueError("finite residency radii required")
    if active_radius_m<0 or prefetch_radius_m<active_radius_m:
        raise ValueError("prefetch radius must cover active radius")
    if type(max_active) is not int or not 1<=max_active<=10_000:
        raise ValueError("bounded active-cell allowance required")
    if not isinstance(chunks,dict) or not isinstance(chunks.get("chunks"),list):
        raise ValueError("chunk registry required")
    ordered=[]
    identifiers=set()
    if len(chunks["chunks"])>100_000:
        raise ValueError("oversized chunk registry")
    for chunk in chunks["chunks"]:
        if not isinstance(chunk,dict) or not isinstance(chunk.get("id"),str) or not chunk["id"]:
            raise ValueError("stable chunk IDs required")
        origin=chunk.get("world_origin")
        if not isinstance(origin,(tuple,list)) or len(origin)!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in origin):
            raise ValueError("finite chunk origin required")
        if chunk["id"] in identifiers:
            raise ValueError("duplicate chunk identifier")
        identifiers.add(chunk["id"])
        distance=math.dist((camera_xyz[0],camera_xyz[2]),(origin[0],origin[2]))
        ordered.append((distance,chunk["id"]))
    ordered.sort(key=lambda item:(item[0],item[1]))
    active=[identifier for distance,identifier in ordered if distance<=active_radius_m][:max_active]
    prefetch=[identifier for distance,identifier in ordered if distance<=prefetch_radius_m and identifier not in active]
    previous=set(previously_resident)
    if not all(isinstance(v,str) for v in previous):
        raise ValueError("previous cells must have stable IDs")
    chosen=set(active+prefetch)
    return {"schema":"mgr.forge.chunk-residency-plan.v1",
            "active":active,"prefetch":prefetch,"evict":sorted(previous-chosen),
            "active_cap":max_active,"candidate_count":len(ordered),
            "status":"PLAN_ONLY",
            "limitations":["distance to chunk origin; no extent-aware frustum/occlusion",
                           "no asset loading, collision floor retention, memory or FPS proof",
                           "prefetch remains a proposal until a live runtime applies it"]}
