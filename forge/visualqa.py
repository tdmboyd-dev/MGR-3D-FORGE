"""MGR Visual Judge: exact PNG pixel QA for repeatable Blender renders.

Supports non-interlaced 8-bit RGB/RGBA PNGs. This is deterministic visual
measurement, NOT semantic AI interpretation of the rendered scene.
"""

from hashlib import sha256
import math
from pathlib import Path
import struct
import zlib


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_png(path, *, max_pixels=12_000_000):
    content = Path(path).read_bytes()
    if not content.startswith(PNG_MAGIC):
        raise ValueError("not PNG")
    pos, size, channels, chunks, seen_end = 8, None, None, [], False
    while pos < len(content):
        if pos + 12 > len(content):
            raise ValueError("truncated PNG chunk")
        length = int.from_bytes(content[pos:pos+4], "big")
        name = content[pos+4:pos+8]
        end = pos+12+length
        if length > 128_000_000 or end > len(content):
            raise ValueError("invalid PNG chunk length")
        data = content[pos+8:pos+8+length]
        crc = int.from_bytes(content[pos+8+length:end], "big")
        if zlib.crc32(name+data) & 0xffffffff != crc:
            raise ValueError("PNG CRC mismatch")
        if name == b"IHDR":
            if size is not None or len(data) != 13:
                raise ValueError("invalid IHDR")
            w,h,bit_depth,color,compression,filter_method,interlace = struct.unpack(">IIBBBBB", data)
            if not w or not h or w*h > max_pixels or bit_depth != 8 or color not in (2,6) or compression or filter_method or interlace:
                raise ValueError("unsupported PNG mode or size")
            size,channels=(w,h),(3 if color == 2 else 4)
        elif name == b"IDAT":
            if size is None:
                raise ValueError("IDAT before IHDR")
            chunks.append(data)
        elif name == b"IEND":
            seen_end = True
            break
        elif name[0] & 32 == 0 and name != b"PLTE":
            raise ValueError("unsupported critical PNG chunk")
        pos = end
    if not seen_end or size is None:
        raise ValueError("incomplete PNG")
    w,h = size
    expected = (w*channels+1)*h
    inflater=zlib.decompressobj()
    raw=inflater.decompress(b"".join(chunks), expected+1)
    if len(raw) != expected or not inflater.eof or inflater.unconsumed_tail:
        raise ValueError("invalid PNG pixel payload")
    stride=w*channels
    rows=[]
    previous=bytearray(stride)
    offset=0
    for _ in range(h):
        mode=raw[offset]
        source=raw[offset+1:offset+1+stride]
        if mode>4:
            raise ValueError("unknown PNG filter")
        reconstructed=bytearray(stride)
        for i,value in enumerate(source):
            a=reconstructed[i-channels] if i>=channels else 0
            b=previous[i]
            c=previous[i-channels] if i>=channels else 0
            if mode==0: predict=0
            elif mode==1: predict=a
            elif mode==2: predict=b
            elif mode==3: predict=(a+b)//2
            else:
                p=a+b-c
                pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
                predict=a if pa<=pb and pa<=pc else (b if pb<=pc else c)
            reconstructed[i]=(value+predict)&255
        rows.append(bytes(reconstructed))
        previous=reconstructed
        offset+=stride+1
    return {"width":w,"height":h,"channels":channels,"rows":rows,
            "sha256":sha256(content).hexdigest()}


def silhouette(image, *, background=(0,0,0), tolerance=12):
    """Bounding box and occupancy against specified RGB background."""
    if not 0<=tolerance<=255:
        raise ValueError("bad tolerance")
    count=0
    left=top=math.inf
    right=bottom=-1
    for y,row in enumerate(image["rows"]):
        stride=image["channels"]
        for x in range(image["width"]):
            rgb=row[x*stride:x*stride+3]
            if any(abs(int(rgb[i])-background[i])>tolerance for i in range(3)):
                count+=1
                left,top=min(left,x),min(top,y)
                right,bottom=max(right,x),max(bottom,y)
    return {"foreground_pixels":count,
            "foreground_fraction":round(count/(image["width"]*image["height"]),6),
            "bbox":([left,top,right,bottom] if count else None)}


def compare_pngs(reference, candidate, *, max_mean_absolute_error=0.0):
    """Reject changed dimensions and quantitatively compare RGB frames."""
    if max_mean_absolute_error<0 or max_mean_absolute_error>255 or not math.isfinite(max_mean_absolute_error):
        raise ValueError("bad threshold")
    a=read_png(reference)
    b=read_png(candidate)
    if (a["width"],a["height"])!=(b["width"],b["height"]):
        raise ValueError("render dimensions mismatch")
    sum_delta=0
    for row_a,row_b in zip(a["rows"],b["rows"]):
        for x in range(a["width"]):
            for channel in range(3):
                sum_delta+=abs(row_a[x*a["channels"]+channel]-row_b[x*b["channels"]+channel])
    mae=round(sum_delta/(a["width"]*a["height"]*3),6)
    return {"schema":"mgr.forge.visual-judge.v1", "rgb_mae":mae,
            "pass":mae<=max_mean_absolute_error,
            "reference_sha256":a["sha256"],"candidate_sha256":b["sha256"],
            "reference_silhouette":silhouette(a),"candidate_silhouette":silhouette(b),
            "limitations":["pixel comparison at fixed camera and render settings",
                           "cannot understand anatomy or identify defects semantically"]}
