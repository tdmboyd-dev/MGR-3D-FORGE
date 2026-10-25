"""MGR-native PNG-to-2.5D relief: actual geometry, not imagined hidden 3D surfaces.

Dependency-free PNG decoder, bounded memory/mesh sizes, deterministic exports.
"""

import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

from .geometry import Mesh
from .glb import export_glb, inspect_glb
from .obj import export_obj
from .receipt import file_receipt


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_SOURCE_BYTES = 4_000_000
MAX_PIXELS_AXIS = 256
MAX_GRID = 48


def decode_png(data):
    """Read non-interlaced, 8-bit grayscale/RGB/RGBA PNG with all five scan filters."""
    if type(data) is not bytes or len(data) > MAX_SOURCE_BYTES or not data.startswith(PNG_SIGNATURE):
        raise ValueError("invalid or oversized PNG")
    offset = 8
    header = None
    compressed = bytearray()
    seen_end = False
    seen_data = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("truncated PNG chunk")
        length = struct.unpack_from(">I", data, offset)[0]
        if length > MAX_SOURCE_BYTES or offset + 12 + length > len(data):
            raise ValueError("PNG chunk exceeds bounds")
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        checksum = struct.unpack_from(">I", data, offset + 8 + length)[0]
        if zlib.crc32(kind + payload) != checksum:
            raise ValueError("PNG CRC mismatch")
        offset += 12 + length
        if header is None and kind != b"IHDR":
            raise ValueError("IHDR must be first")
        if kind == b"IHDR":
            if header is not None or len(payload) != 13:
                raise ValueError("invalid PNG header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if (not 1 <= width <= MAX_PIXELS_AXIS or not 1 <= height <= MAX_PIXELS_AXIS
                    or depth != 8 or color not in (0, 2, 6) or compression or filtering or interlace):
                raise ValueError("unsupported PNG geometry or pixel encoding")
            header = (width, height, {0: 1, 2: 3, 6: 4}[color])
        elif kind == b"IDAT":
            if seen_end:
                raise ValueError("PNG data after end")
            seen_data = True
            compressed.extend(payload)
            if len(compressed) > MAX_SOURCE_BYTES:
                raise ValueError("compressed PNG exceeds budget")
        elif kind == b"IEND":
            if len(payload) or not seen_data or offset != len(data):
                raise ValueError("invalid PNG trailer")
            seen_end = True
            break
        elif kind[0] & 0x20 == 0:
            raise ValueError("unsupported critical PNG chunk")
    if not seen_end:
        raise ValueError("PNG missing end marker")
    width, height, channels = header
    stride = width * channels
    expected = height * (stride + 1)
    inflater = zlib.decompressobj()
    try:
        raw = inflater.decompress(bytes(compressed), expected + 1)
        raw += inflater.flush()
    except zlib.error as error:
        raise ValueError("invalid PNG compression") from error
    if not inflater.eof or inflater.unused_data or inflater.unconsumed_tail or len(raw) != expected:
        raise ValueError("PNG decompressed-size mismatch")
    scanlines = []
    previous = bytearray(stride)
    for row in range(height):
        index = row * (stride + 1)
        filter_type = raw[index]
        if filter_type > 4:
            raise ValueError("unknown PNG filter")
        current = bytearray(raw[index + 1:index + 1 + stride])
        for i in range(stride):
            left = current[i - channels] if i >= channels else 0
            up = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            if filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                p = left + up - upper_left
                distances = (abs(p - left), abs(p - up), abs(p - upper_left))
                predictor = (left, up, upper_left)[distances.index(min(distances))]
            else:
                predictor = 0
            current[i] = (current[i] + predictor) & 255
        previous = current
        values = []
        for x in range(width):
            sample = current[x * channels:(x + 1) * channels]
            if channels == 1:
                gray = sample[0]
            else:
                gray = round((sample[0] * 0.2126 + sample[1] * 0.7152 + sample[2] * 0.0722))
            alpha = sample[3] / 255 if channels == 4 else 1
            values.append(round(gray * alpha))
        scanlines.append(values)
    return {"width": width, "height": height, "luminance": scanlines,
            "source_sha256": hashlib.sha256(data).hexdigest()}


def make_relief(image, *, width=8.0, height=8.0, depth=2.0, base=0.2, grid=32):
    """Extrude image luminance as relief columns. Y is up; this is not 3D inference."""
    if (any(type(x) not in (int, float) or not math.isfinite(x) for x in (width, height, depth, base))
            or not 0.1 <= width <= 100 or not 0.1 <= height <= 100 or not 0.01 <= depth <= 50
            or not 0.01 <= base <= 5 or type(grid) is not int or not 1 <= grid <= MAX_GRID):
        raise ValueError("invalid physical dimensions or sample grid")
    image_width, image_height = image["width"], image["height"]
    nx, nz = min(grid, image_width), min(grid, image_height)
    mesh = Mesh()
    sample_luma = []
    for z in range(nz):
        for x in range(nx):
            px = min(image_width - 1, int((x + 0.5) * image_width / nx))
            pz = min(image_height - 1, int((z + 0.5) * image_height / nz))
            lum = image["luminance"][pz][px] / 255
            sample_luma.append(lum)
            mesh.box(-width / 2 + (x + 0.5) * width / nx,
                     0,
                     -height / 2 + (z + 0.5) * height / nz,
                     width / nx, base + lum * depth, height / nz)
    return mesh, {"schema": "mgr.forge.image-relief.v1", "source_sha256": image["source_sha256"],
                  "source_pixels": [image_width, image_height], "grid": [nx, nz],
                  "height_range": [round(base + min(sample_luma) * depth, 6),
                                   round(base + max(sample_luma) * depth, 6)],
                  "triangles": len(mesh.indices) // 3, "method": "luminance-to-column-relief",
                  "inference_of_hidden_surfaces": False, "external_api_calls": 0}


def export_image_relief(png, output, **options):
    source, target = Path(png), Path(output)
    if target.exists():
        raise FileExistsError("new relief destination required")
    if not source.is_file() or source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("invalid PNG source")
    image = decode_png(source.read_bytes())
    mesh, manifest = make_relief(image, **options)
    materials = (("mgr-image-relief", [0.67, 0.68, 0.74, 1]),)
    blob = export_glb([mesh], name="MGR Image Relief", materials=materials)
    geometry = inspect_glb(blob)
    obj, mtl = export_obj([mesh], mtl_name="relief.mtl", materials=materials)
    target.mkdir(parents=True, exist_ok=False)
    (target / "relief.glb").write_bytes(blob)
    (target / "relief.obj").write_text(obj, encoding="utf-8")
    (target / "relief.mtl").write_text(mtl, encoding="utf-8")
    manifest["glb_quality"] = geometry
    manifest["artifact_inventory"] = {name: file_receipt(target / name)
                                      for name in ("relief.glb", "relief.obj", "relief.mtl")}
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "MATERIALIZED", "output": str(target.resolve()), **manifest}
