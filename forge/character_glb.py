"""Bounded inspection of ordinary, uncompressed glTF 2.0 GLB assets.

Admits standard normals, UVs, 8/16/32-bit indices and optional attributes. It
does not decode Draco/meshopt compression or verify the artistic identity.
"""

import json
import math
import struct


COMPONENT_BYTES = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
DIMENSIONS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4,
              "MAT2": 4, "MAT3": 9, "MAT4": 16}


def parse_character_glb(blob):
    if len(blob) < 28 or len(blob) > 80_000_000:
        raise ValueError("GLB length outside safe bounds")
    magic, version, length = struct.unpack_from("<4sII", blob, 0)
    if magic != b"glTF" or version != 2 or length != len(blob):
        raise ValueError("invalid glTF 2.0 GLB header")
    cursor, chunks = 12, []
    while cursor < len(blob):
        if cursor + 8 > len(blob):
            raise ValueError("truncated GLB chunk")
        size, kind = struct.unpack_from("<I4s", blob, cursor)
        cursor += 8
        if size % 4 or cursor + size > len(blob):
            raise ValueError("invalid GLB chunk dimensions")
        chunks.append((kind, blob[cursor:cursor + size]))
        cursor += size
    if len(chunks) != 2 or chunks[0][0] != b"JSON" or chunks[1][0] != b"BIN\0":
        raise ValueError("single-buffer GLB with JSON and BIN required")
    try:
        doc = json.loads(chunks[0][1])
        binary = chunks[1][1]
        if doc["asset"]["version"] != "2.0":
            raise ValueError("unsupported glTF asset version")
        if len(doc["buffers"]) != 1 or doc["buffers"][0]["byteLength"] > len(binary):
            raise ValueError("invalid embedded GLB binary buffer")
        views, accessors = doc.get("bufferViews", []), doc.get("accessors", [])
        if len(views) > 100000 or len(accessors) > 100000:
            raise ValueError("GLB accessor limits exceeded")
        for view in views:
            offset, size = view.get("byteOffset", 0), view["byteLength"]
            if type(offset) is not int or type(size) is not int or offset < 0 or size < 0 or offset + size > len(binary):
                raise ValueError("invalid bufferView bounds")
        for accessor in accessors:
            if "sparse" in accessor:
                raise ValueError("sparse accessors require explicit normalization before admission")
            if accessor.get("componentType") not in COMPONENT_BYTES or accessor.get("type") not in DIMENSIONS:
                raise ValueError("unsupported accessor component or dimension")
            count = accessor.get("count")
            if type(count) is not int or count < 0 or count > 20_000_000:
                raise ValueError("accessor count outside limits")
            if "bufferView" not in accessor:
                raise ValueError("non-sparse accessor without bufferView")
            if (type(accessor["bufferView"]) is not int or
                    not 0 <= accessor["bufferView"] < len(views)):
                raise ValueError("accessor references nonexistent bufferView")
            view = views[accessor["bufferView"]]
            item_bytes = COMPONENT_BYTES[accessor["componentType"]] * DIMENSIONS[accessor["type"]]
            stride = view.get("byteStride", item_bytes)
            offset = accessor.get("byteOffset", 0)
            if (type(stride) is not int or type(offset) is not int or offset < 0
                    or stride < item_bytes or stride > 252 or stride % COMPONENT_BYTES[accessor["componentType"]]
                    or (offset + (count - 1) * stride + item_bytes if count else offset) > view["byteLength"]):
                raise ValueError("accessor stride or bounds invalid")
        if any(name in doc.get("extensionsRequired", []) for name in ("KHR_draco_mesh_compression", "EXT_meshopt_compression")):
            raise ValueError("compressed character mesh requires approved local decoder")
        meshes = doc.get("meshes", [])
        if not 1 <= len(meshes) <= 10000:
            raise ValueError("valid nonempty mesh inventory required")
        triangles, vertices, primitives = 0, 0, 0
        for mesh in meshes:
            for primitive in mesh.get("primitives", []):
                if "extensions" in primitive and "KHR_draco_mesh_compression" in primitive["extensions"]:
                    raise ValueError("Draco compression not admitted without decoder")
                if primitive.get("mode", 4) != 4:
                    raise ValueError("only triangles accepted for editable candidate")
                position_index = primitive["attributes"]["POSITION"]
                if type(position_index) is not int or not 0 <= position_index < len(accessors):
                    raise ValueError("mesh position accessor reference is invalid")
                pos = accessors[position_index]
                if pos["type"] != "VEC3" or pos["componentType"] != 5126:
                    raise ValueError("position vertices must be float VEC3")
                indices = primitive.get("indices")
                if indices is None:
                    count = pos["count"]
                else:
                    if type(indices) is not int or not 0 <= indices < len(accessors):
                        raise ValueError("mesh indices accessor reference is invalid")
                    element = accessors[indices]
                    if element["type"] != "SCALAR" or element["componentType"] not in (5121, 5123, 5125):
                        raise ValueError("mesh indices must be unsigned integers")
                    count = element["count"]
                    iview = views[element["bufferView"]]
                    component = element["componentType"]
                    code = {5121: "B", 5123: "H", 5125: "I"}[component]
                    stride = iview.get("byteStride", COMPONENT_BYTES[component])
                    start = iview.get("byteOffset", 0) + element.get("byteOffset", 0)
                    for n in range(count):
                        if struct.unpack_from("<" + code, binary, start + n * stride)[0] >= pos["count"]:
                            raise ValueError("triangle index exceeds vertex count")
                if count % 3:
                    raise ValueError("mesh triangle index count invalid")
                triangles += count // 3
                vertices += pos["count"]
                primitives += 1
        if triangles == 0 or triangles > 4_000_000:
            raise ValueError("triangle count outside bounds")
        return doc, {"valid": True, "meshes": len(meshes), "primitives": primitives,
                     "vertices": vertices, "triangles": triangles,
                     "materials": len(doc.get("materials", []))}
    except (KeyError, IndexError, TypeError, OverflowError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("malformed standard glTF 2.0 character structure") from error
