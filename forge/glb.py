"""Minimal glTF 2.0 binary exporter/validator, using only Python stdlib."""

import json
import math
import struct

from .geometry import MATERIALS


def _pad(blob: bytes, fill=b"\x00") -> bytes:
    return blob + fill * ((-len(blob)) % 4)


def export_glb(meshes, *, name="MGR Forge World", materials=None) -> bytes:
    materials = MATERIALS if materials is None else materials
    if len(meshes) != len(materials) or not materials:
        raise ValueError("mesh/material count mismatch")
    binary = bytearray()
    views, accessors, primitives = [], [], []

    def add_view(data, target):
        offset = len(binary)
        binary.extend(data)
        binary.extend(b"\x00" * ((-len(binary)) % 4))
        views.append({"buffer": 0, "byteOffset": offset,
                      "byteLength": len(data), "target": target})
        return len(views) - 1

    def add_accessor(view, count, component_type, kind, bounds=None):
        acc = {"bufferView": view, "componentType": component_type,
               "count": count, "type": kind}
        if bounds is not None:
            acc["min"], acc["max"] = bounds
        accessors.append(acc)
        return len(accessors) - 1

    for material, mesh in enumerate(meshes):
        if not mesh.indices:
            continue
        coordinates = mesh.positions
        if not all(math.isfinite(v) for v in coordinates + mesh.normals):
            raise ValueError("nonfinite geometry")
        if len(coordinates) != len(mesh.normals) or len(coordinates) % 3:
            raise ValueError("invalid position/normal array")
        vcount = len(coordinates) // 3
        if any(index < 0 or index >= vcount for index in mesh.indices):
            raise ValueError("index out of bounds")
        bounds = ([min(coordinates[i::3]) for i in range(3)],
                  [max(coordinates[i::3]) for i in range(3)])
        pv = add_view(struct.pack(f"<{len(coordinates)}f", *coordinates), 34962)
        nv = add_view(struct.pack(f"<{len(mesh.normals)}f", *mesh.normals), 34962)
        iv = add_view(struct.pack(f"<{len(mesh.indices)}I", *mesh.indices), 34963)
        pa = add_accessor(pv, vcount, 5126, "VEC3", bounds)
        na = add_accessor(nv, vcount, 5126, "VEC3")
        ia = add_accessor(iv, len(mesh.indices), 5125, "SCALAR")
        primitives.append({"attributes": {"POSITION": pa, "NORMAL": na},
                           "indices": ia, "material": material, "mode": 4})

    gltf = {
        "asset": {"version": "2.0", "generator": "MGR Forge CPU v0.1"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"name": name, "mesh": 0}],
        "meshes": [{"name": name, "primitives": primitives}],
        "materials": [{"name": mat_name, "doubleSided": False,
                       "pbrMetallicRoughness": {
                           "baseColorFactor": rgba,
                           "metallicFactor": 0.0, "roughnessFactor": 0.9}}
                      for mat_name, rgba in materials],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": views, "accessors": accessors,
    }
    json_chunk = _pad(json.dumps(gltf, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False).encode("utf-8"), b" ")
    bin_chunk = _pad(bytes(binary))
    length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    return (struct.pack("<4sII", b"glTF", 2, length)
            + struct.pack("<I4s", len(json_chunk), b"JSON") + json_chunk
            + struct.pack("<I4s", len(bin_chunk), b"BIN\x00") + bin_chunk)


def inspect_glb(blob: bytes) -> dict:
    """Read and check a GLB without trusting its declared sizes or offsets."""
    if len(blob) < 28:
        raise ValueError("GLB too small")
    magic, version, length = struct.unpack_from("<4sII", blob)
    if magic != b"glTF" or version != 2 or length != len(blob):
        raise ValueError("invalid GLB header/length")
    cursor, chunks = 12, []
    while cursor < len(blob):
        if cursor + 8 > len(blob):
            raise ValueError("truncated chunk header")
        size, kind = struct.unpack_from("<I4s", blob, cursor)
        cursor += 8
        if size % 4 or cursor + size > len(blob):
            raise ValueError("invalid chunk length")
        chunks.append((kind, blob[cursor:cursor + size]))
        cursor += size
    if cursor != len(blob) or len(chunks) != 2 or chunks[0][0] != b"JSON" or chunks[1][0] != b"BIN\x00":
        raise ValueError("GLB must contain JSON and BIN chunks")
    doc = json.loads(chunks[0][1])
    binary = chunks[1][1]
    if doc.get("asset", {}).get("version") != "2.0":
        raise ValueError("not glTF 2.0")
    if doc["buffers"][0]["byteLength"] > len(binary):
        raise ValueError("binary buffer shorter than declared")
    for view in doc["bufferViews"]:
        if view["byteOffset"] + view["byteLength"] > len(binary):
            raise ValueError("buffer view exceeds binary chunk")
    for accessor in doc["accessors"]:
        view = doc["bufferViews"][accessor["bufferView"]]
        comp_bytes = {5125: 4, 5126: 4}[accessor["componentType"]]
        dims = {"SCALAR": 1, "VEC3": 3}[accessor["type"]]
        if accessor["count"] * comp_bytes * dims > view["byteLength"]:
            raise ValueError("accessor exceeds buffer view")
    for mesh in doc["meshes"]:
        for primitive in mesh["primitives"]:
            positions = doc["accessors"][primitive["attributes"]["POSITION"]]
            normals = doc["accessors"][primitive["attributes"]["NORMAL"]]
            indices = doc["accessors"][primitive["indices"]]
            if positions["count"] != normals["count"] or indices["count"] % 3:
                raise ValueError("invalid geometry counts")
            view = doc["bufferViews"][indices["bufferView"]]
            offset = view["byteOffset"]
            ids = struct.unpack_from(f"<{indices['count']}I", binary, offset)
            if ids and max(ids) >= positions["count"]:
                raise ValueError("primitive index exceeds vertices")
    return {"valid": True, "meshes": len(doc["meshes"]),
            "primitives": sum(len(m["primitives"]) for m in doc["meshes"]),
            "vertices": sum(a["count"] for a in doc["accessors"] if a["type"] == "VEC3") // 2,
            "triangles": sum(doc["accessors"][p["indices"]]["count"] // 3
                             for m in doc["meshes"] for p in m["primitives"]),
            "materials": len(doc["materials"])}
