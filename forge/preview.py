"""Dependency-free, isometric SVG preview of generated world manifests.

For human inspection only. Not a replacement for viewing imported GLB.
"""

from html import escape
import math


PALETTE = {"building-brick": ("#d48165", "#8e4535", "#ad5d49"),
           "building-stone": ("#d3d1c7", "#83817d", "#aaa8a2"),
           "building-blue": ("#648eaf", "#2c4d6e", "#3f6586"),
           "building-gold": ("#d7ac54", "#8a5a20", "#ac7c2d"),
           "building-emerald": ("#56b18b", "#276c57", "#32846b")}


def render_world_svg(world, *, width=1200, height=820):
    """Project boxes in fixed isometric orientation with back-to-front draw order."""
    if not 300 <= width <= 4096 or not 200 <= height <= 4096:
        raise ValueError("preview dimensions out of bounds")
    buildings = world["buildings"]
    spec = world["spec"]
    footprint = max(spec["columns"], spec["rows"]) * (spec["lot_size"] + spec["road_width"])
    scale = min(width, height) / max(3 * footprint, 1)
    cx, cy = width/2, height*0.55

    def project(x, y, z):
        return (cx + (x-z)*0.866*scale, cy + (x+z)*0.5*scale - y*scale)

    def poly(vertices, color):
        coords = " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in vertices)
        return f'<polygon points="{coords}" fill="{color}" stroke="#17212b" stroke-width="0.7"/>'

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" role="img" aria-label="MGR Forge generated neighborhood">',
             '<rect width="100%" height="100%" fill="#0c1420"/>']
    ground = world["grounds"]
    hw, hd = ground["width"]/2, ground["depth"]/2
    parts.append(poly([project(-hw, 0, -hd), project(hw, 0, -hd),
                       project(hw, 0, hd), project(-hw, 0, hd)], "#315f49"))
    for road in world["roads"]:
        if road["axis"] == "z":
            a = road["coordinate"]
            rw = spec["road_width"]/2
            corners = [(a-rw,-hd),(a+rw,-hd),(a+rw,hd),(a-rw,hd)]
        else:
            b = road["coordinate"]
            rw = spec["road_width"]/2
            corners = [(-hw,b-rw),(hw,b-rw),(hw,b+rw),(-hw,b+rw)]
        parts.append(poly([project(x, 0.1, z) for x,z in corners], "#293443"))
    for building in sorted(buildings, key=lambda b: sum((b["center"][0],b["center"][2]))):
        x, _, z = building["center"]
        w,h,d = building["size"]
        a,b=x-w/2,x+w/2
        c,e=z-d/2,z+d/2
        left, right, roof=PALETTE[building["material"]]
        points = {
            "a":project(a,0,c),"b":project(b,0,c),"c":project(b,0,e),"d":project(a,0,e),
            "A":project(a,h,c),"B":project(b,h,c),"C":project(b,h,e),"D":project(a,h,e)}
        parts.append(poly([points[k] for k in ("d","c","C","D")], left))
        parts.append(poly([points[k] for k in ("b","c","C","B")], right))
        parts.append(poly([points[k] for k in ("A","B","C","D")], roof))
    title = escape(str(spec.get("name", "MGR Forge World")))
    parts.append(f'<text x="30" y="50" fill="white" font-family="sans-serif" font-size="28">{title}</text>')
    parts.append(f'<text x="30" y="78" fill="#9cb6c5" font-family="sans-serif" font-size="16">'
                 f'{len(buildings)} buildings · CPU procedural preview (not a GLB render)</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"
