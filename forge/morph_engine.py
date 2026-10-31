"""Safe non-destructive 3D mesh morphs; preserves vertices/faces/material groups.

Designed as a geometry kernel, NOT a likeness morph, rig or AI model. Morphs
operate on meshes produced by Forge; import pipeline can later use same kernel.
"""
import math
from .geometry import Mesh
from .meshqa import analyze_mesh

DEFAULTS={"length":1.0,"height":1.0,"width":1.0,"twist_degrees":0.0}
BOUNDS={"length":(0.5,2.2),"height":(0.5,2.2),"width":(0.5,2.2),
        "twist_degrees":(-45.0,45.0)}


def normalize_morph(spec):
    if spec is None:
        return dict(DEFAULTS)
    if not isinstance(spec,dict) or set(spec)-set(DEFAULTS):
        raise ValueError("unsupported morph parameters")
    settings={}
    for name,default in DEFAULTS.items():
        value=spec.get(name,default)
        low,high=BOUNDS[name]
        if type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"morph {name} outside safe bounds")
        settings[name]=float(value)
    return settings


def morph_point(point, settings=None, *, pivot_y=0.0, axis_extent=1.0):
    """Transform one Y-up position with the same field used by mesh and rig.

    Shared axis_extent across material meshes prevents different twist rates.
    """
    recipe=normalize_morph(settings)
    if (type(point) not in (list,tuple) or len(point)!=3 or
            any(type(v) not in (int,float) or not math.isfinite(v) for v in point) or
            type(pivot_y) not in (int,float) or not math.isfinite(pivot_y) or
            type(axis_extent) not in (int,float) or not math.isfinite(axis_extent) or
            axis_extent<=0):
        raise ValueError("invalid morph point, pivot or shared extent")
    x,y,z=point
    theta=math.radians(recipe["twist_degrees"])*(y-pivot_y)/axis_extent
    cs,sn=math.cos(theta),math.sin(theta)
    xx=x*recipe["length"]
    zz=z*recipe["width"]
    return (xx*cs-zz*sn,pivot_y+(y-pivot_y)*recipe["height"],xx*sn+zz*cs)


def morph_mesh(mesh,settings=None,*,pivot_y=0.0,axis_extent=None):
    recipe=normalize_morph(settings)
    if type(pivot_y) not in (int,float) or not math.isfinite(pivot_y):
        raise ValueError("invalid morph pivot")
    quality=analyze_mesh(mesh)
    if not quality["passed"]:
        raise ValueError("cannot morph invalid source triangle geometry")
    if not mesh.indices:
        return Mesh(),{"vertices":0,"triangles":0,"morph":recipe,"quality_pass":True}
    out=Mesh(indices=list(mesh.indices))
    ys=mesh.positions[1::3]
    effective_extent=axis_extent if axis_extent is not None else max(max(ys)-pivot_y,0.01)
    for x,y,z in zip(mesh.positions[0::3],ys,mesh.positions[2::3]):
        out.positions.extend(morph_point((x,y,z),recipe,pivot_y=pivot_y,
                                         axis_extent=effective_extent))
    accum=[[0.0,0.0,0.0] for _ in range(len(out.positions)//3)]
    for ti in range(0,len(out.indices),3):
        ids=out.indices[ti:ti+3]
        a,b,c=[[out.positions[i*3+j] for j in range(3)] for i in ids]
        u=[b[j]-a[j] for j in range(3)]
        v=[c[j]-a[j] for j in range(3)]
        n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        mag=math.sqrt(sum(t*t for t in n))
        if mag<1e-9:
            raise ValueError("morph collapsed triangle")
        for i in ids:
            for j in range(3): accum[i][j]+=n[j]/mag
    for n in accum:
        mag=math.sqrt(sum(t*t for t in n))
        if mag<1e-9:
            raise ValueError("morph created unsupported orphan vertex")
        out.normals.extend(v/mag for v in n)
    status=analyze_mesh(out)
    if not status["passed"]:
        raise ValueError("morphed mesh has invalid triangles")
    return out,{"vertices":len(out.positions)//3,"triangles":len(out.indices)//3,
                "morph":recipe,"quality_pass":True,"indices_preserved":out.indices==mesh.indices}
