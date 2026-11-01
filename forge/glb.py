"""Minimal glTF 2.0 binary exporter/validator, using only Python stdlib."""

import json
import math
import struct

from .geometry import MATERIALS
from .materials import validate_pbr_recipe


def _pad(blob: bytes, fill=b"\x00") -> bytes:
    return blob + fill * ((-len(blob)) % 4)


def export_glb(meshes, *, name="MGR Forge World", materials=None, pbr_overrides=None,
               emissive_overrides=None) -> bytes:
    materials = MATERIALS if materials is None else materials
    if len(meshes) != len(materials) or not materials:
        raise ValueError("mesh/material count mismatch")
    if pbr_overrides is not None and (not isinstance(pbr_overrides, dict) or
                                      any(type(i) is not int or i < 0 or i >= len(materials)
                                          for i in pbr_overrides)):
        raise ValueError("PBR override material index invalid")
    pbr_overrides = pbr_overrides or {}
    if emissive_overrides is not None and (not isinstance(emissive_overrides,dict) or
                                           any(type(i) is not int or not 0<=i<len(materials)
                                               for i in emissive_overrides)):
        raise ValueError("invalid emissive material index")
    emissive_overrides=emissive_overrides or {}
    for color in emissive_overrides.values():
        if (not isinstance(color,(list,tuple)) or len(color)!=3 or
            not all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in color)):
            raise ValueError("emissiveFactor RGB must be finite and in [0,1]")
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
                       "pbrMetallicRoughness": (validate_pbr_recipe(pbr_overrides[index])
                           if index in pbr_overrides else {
                               "baseColorFactor": rgba,
                               "metallicFactor": 0.0, "roughnessFactor": 0.9}),
                       **({"emissiveFactor": list(emissive_overrides[index])}
                          if index in emissive_overrides else {})}
                      for index, (mat_name, rgba) in enumerate(materials)],
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
    """Verify self-contained glTF2 GLB triangles, including Blender 16-bit indices.

    All accessors and referenced offsets are bounded within the original BIN.
    This verifies a structural scene/mesh, not a texture/rig/anatomy license.
    Sparse and multi-buffer glTF are explicitly unsupported until audited.
    """
    if type(blob) is not bytes or not 28<=len(blob)<=256_000_000:
        raise ValueError("GLB must be bounded binary bytes")
    magic,version,total=struct.unpack_from("<4sII",blob,0)
    if (magic,version,total)!=(b"glTF",2,len(blob)):
        raise ValueError("invalid glTF 2.0 header/length")
    cursor=12
    chunks=[]
    while cursor<len(blob):
        if cursor+8>len(blob):raise ValueError("truncated GLB chunk header")
        size,kind=struct.unpack_from("<I4s",blob,cursor)
        cursor+=8
        if size%4 or size>len(blob)-cursor:raise ValueError("invalid GLB chunk length")
        chunks.append((kind,blob[cursor:cursor+size]))
        cursor+=size
    if cursor!=len(blob) or len(chunks)!=2 or [x[0] for x in chunks]!=[b"JSON",b"BIN\x00"]:
        raise ValueError("MGR Forge requires one JSON plus one BIN GLB")
    try:doc=json.loads(chunks[0][1])
    except (UnicodeError,json.JSONDecodeError,TypeError) as error:
        raise ValueError("invalid glTF JSON") from error
    if not isinstance(doc,dict) or doc.get("asset",{}).get("version")!="2.0":
        raise ValueError("GLB is not glTF 2.0")
    binary=chunks[1][1]
    buffers=doc.get("buffers")
    views=doc.get("bufferViews")
    accessors=doc.get("accessors")
    meshes=doc.get("meshes")
    if (not isinstance(buffers,list) or len(buffers)!=1 or
        not isinstance(views,list) or len(views)>100000 or
        not isinstance(accessors,list) or len(accessors)>100000 or
        not isinstance(meshes,list) or not 1<=len(meshes)<=10000):
        raise ValueError("unsupported GLB buffer/accessor/mesh inventory")
    if (not isinstance(buffers[0],dict) or
        type(buffers[0].get("byteLength")) is not int or
        buffers[0]["byteLength"]<0 or buffers[0]["byteLength"]>len(binary) or
        "uri" in buffers[0]):
        raise ValueError("unverified binary buffer declaration")
    try:
        for view in views:
            if not isinstance(view,dict) or view.get("buffer",0)!=0:
                raise ValueError("nonlocal buffer view not accepted")
            off=view.get("byteOffset",0)
            size=view.get("byteLength")
            if (type(off) is not int or type(size) is not int or
                off<0 or size<0 or off+size>buffers[0]["byteLength"]):
                raise ValueError("buffer view escaped bounded GLB BIN")
        components={5120:(1,"b"),5121:(1,"B"),5122:(2,"h"),5123:(2,"H"),
                    5124:(4,"i"),5125:(4,"I"),5126:(4,"f")}
        dimensions={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4,
                    "MAT2":4,"MAT3":9,"MAT4":16}
        meta=[]
        for accessor in accessors:
            if not isinstance(accessor,dict) or "sparse" in accessor:
                raise ValueError("sparse or malformed GLB accessor not yet supported")
            ix=accessor.get("bufferView")
            if type(ix) is not int or not 0<=ix<len(views):
                raise ValueError("GLB accessor has no valid bufferView")
            view=views[ix]
            count=accessor.get("count")
            ctype=accessor.get("componentType")
            shape=accessor.get("type")
            if type(count) is not int or not 0<=count<=40_000_000 or (
               ctype not in components or shape not in dimensions):
                raise ValueError("invalid glTF accessor type/count")
            width=components[ctype][0]*dimensions[shape]
            stride=view.get("byteStride",width)
            offset=accessor.get("byteOffset",0)
            if (type(stride) is not int or type(offset) is not int or
                offset<0 or offset%components[ctype][0] or
                stride<width or stride%components[ctype][0] or
                (offset+(count-1)*stride+width>view["byteLength"] if count else
                 offset>view["byteLength"])):
                raise ValueError("GLB accessor exceeds its view or has invalid stride")
            meta.append((accessor,view,stride))
        triangle_count=0
        vertex_count=0
        primitive_count=0
        for mesh in meshes:
            primitives=mesh.get("primitives")
            if not isinstance(primitives,list) or not 1<=len(primitives)<=20000:
                raise ValueError("GLB mesh is missing bounded primitives")
            for primitive in primitives:
                if not isinstance(primitive,dict) or primitive.get("mode",4)!=4:
                    raise ValueError("only valid triangle-list GLB primitives accepted")
                attrs=primitive.get("attributes",{})
                if not isinstance(attrs,dict):
                    raise ValueError("invalid primitive attributes")
                pi,ni,ii=attrs.get("POSITION"),attrs.get("NORMAL"),primitive.get("indices")
                if any(type(ix) is not int or not 0<=ix<len(accessors) for ix in (pi,ni,ii)):
                    raise ValueError("primitive must have position, normal and index accessors")
                pos,norm,indices=accessors[pi],accessors[ni],accessors[ii]
                if (pos["componentType"]!=5126 or pos["type"]!="VEC3" or
                    norm["componentType"]!=5126 or norm["type"]!="VEC3" or
                    indices["type"]!="SCALAR" or
                    indices["componentType"] not in (5121,5123,5125) or
                    pos["count"]!=norm["count"] or indices["count"]%3):
                    raise ValueError("unsupported indexed triangle geometry")
                ctype=indices["componentType"]
                view=meta[ii][1]
                stride=meta[ii][2]
                start=view.get("byteOffset",0)+indices.get("byteOffset",0)
                token="<"+components[ctype][1]
                index_fmt=struct.Struct(token)
                # Scan indexed geometry without creating an unbounded huge tuple.
                for j in range(indices["count"]):
                    index=index_fmt.unpack_from(binary,start+j*stride)[0]
                    if index>=pos["count"]:
                        raise ValueError("primitive index references missing vertex")
                primitive_count+=1
                triangle_count+=indices["count"]//3
                vertex_count+=pos["count"]
        return {"valid":True,"meshes":len(meshes),"primitives":primitive_count,
                "vertices":vertex_count,"triangles":triangle_count,
                "materials":len(doc.get("materials",[])),
                "index_component_types":sorted({accessors[p["indices"]]["componentType"]
                    for m in meshes for p in m["primitives"]}),
                "limitations":["Structural triangle mesh verification only, not independent Blender rendering",
                               "Sparse, nonindexed and externally referenced glTF not yet supported"]}
    except (KeyError,IndexError,TypeError,struct.error) as error:
        raise ValueError("malformed or out-of-bounds glTF mesh") from error
