"""Independent CPU format parity audit for Forge's own GLB and OBJ exports.

Counts and vertex bounds are geometry evidence; material/render parity is not.
"""

import math
import struct
import json
from .glb import inspect_glb


def _bounds(points):
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]


def _read_glb_positions(blob):
    json_len = struct.unpack_from("<I", blob, 12)[0]
    doc = json.loads(blob[20:20 + json_len].decode("utf-8"))
    binary_offset = 20 + json_len + 8
    pts = []
    for mesh in doc["meshes"]:
        for primitive in mesh["primitives"]:
            accessor = doc["accessors"][primitive["attributes"]["POSITION"]]
            view = doc["bufferViews"][accessor["bufferView"]]
            if accessor["componentType"] != 5126 or accessor["type"] != "VEC3":
                raise ValueError("only Forge float3 positions supported")
            stride = view.get("byteStride", 12)
            if stride != 12:
                raise ValueError("interleaved mesh not accepted by bounded Forge parity witness")
            start = binary_offset + view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
            pts.extend(struct.unpack_from("<fff", blob, start + i * stride)
                       for i in range(accessor["count"]))
    return pts


def _read_obj(obj, *, max_vertices=2_000_000):
    pts = []
    faces = 0
    for row in obj.splitlines():
        if row.startswith("v "):
            coords = row.split()
            if len(coords) != 4:
                raise ValueError("invalid OBJ vertex")
            point = tuple(float(x) for x in coords[1:])
            if not all(math.isfinite(x) for x in point):
                raise ValueError("nonfinite OBJ vertex")
            pts.append(point)
            if len(pts) > max_vertices:
                raise ValueError("OBJ vertex budget exceeded")
        elif row.startswith("f "):
            values = row.split()[1:]
            if len(values) != 3:
                raise ValueError("only triangulated OBJ faces accepted")
            for item in values:
                raw = item.split("/")[0]
                if not raw.isdecimal() or not 1 <= int(raw) <= len(pts):
                    raise ValueError("out-of-bounds OBJ triangle index")
            faces += 1
    if not pts or faces == 0:
        raise ValueError("empty OBJ geometry")
    return pts, faces


def audit_export_parity(glb_bytes, obj_text, *, tolerance_m=0.001):
    """Fail closed if independent exported geometry counts or bounds differ."""
    if type(tolerance_m) not in (float, int) or not math.isfinite(tolerance_m) or not 0 <= tolerance_m <= 0.1:
        raise ValueError("bounded finite geometry tolerance required")
    glb = inspect_glb(glb_bytes)
    if glb["vertices"] > 2_000_000 or glb["triangles"] > 2_000_000:
        raise ValueError("geometry exceeds audit limit")
    glb_points = _read_glb_positions(glb_bytes)
    obj_points, triangles = _read_obj(obj_text)
    gb, ob = _bounds(glb_points), _bounds(obj_points)
    drift = max(abs(gb[k][i] - ob[k][i]) for k in range(2) for i in range(3))
    passed = glb["triangles"] == triangles and len(glb_points) == len(obj_points) and drift <= tolerance_m
    return {"schema": "mgr.forge.export-parity.v1", "status": "PASS" if passed else "FAIL",
            "glb_triangles": glb["triangles"], "obj_triangles": triangles,
            "glb_vertices": len(glb_points), "obj_vertices": len(obj_points),
            "bounds_drift_m": round(drift, 9), "tolerance_m": tolerance_m,
            "limitations": ["does not compare normals, UVs, textures or material appearance",
                            "does not prove independent application import, animation or FPS"]}
