"""MGR Spatial Truth: CPU 3D↔2D perspective and geometric cross-sections.

The same pixel ray admits infinitely many 3D depths. Slicing consumes an
already-existing mesh; neither step reconstructs hidden surfaces from photos.
"""

import math


def camera_project(point, *, focal_px, center_px=(0,0)):
    """Pinhole camera looking along +Z; image +Y points up."""
    if len(point)!=3 or not all(math.isfinite(v) for v in point):
        raise ValueError("finite XYZ point required")
    if type(focal_px) not in (float,int) or not math.isfinite(focal_px) or focal_px<=0:
        raise ValueError("positive finite focal length required")
    if len(center_px)!=2 or not all(math.isfinite(v) for v in center_px):
        raise ValueError("finite principal point required")
    x,y,z=point
    if z<=0:
        raise ValueError("point lies on or behind camera")
    return (center_px[0]+focal_px*x/z,center_px[1]+focal_px*y/z)


def pixel_to_ray(pixel, *, focal_px, center_px=(0,0)):
    """A camera-space unit ray; not an inferred world-space depth."""
    if len(pixel)!=2 or not all(math.isfinite(v) for v in pixel):
        raise ValueError("finite XY pixel required")
    # Reuse validation for focal length and camera center.
    camera_project((0,0,1),focal_px=focal_px,center_px=center_px)
    ray=((pixel[0]-center_px[0])/focal_px,(pixel[1]-center_px[1])/focal_px,1.0)
    norm=math.sqrt(sum(v*v for v in ray))
    return tuple(v/norm for v in ray)


def slice_mesh_at_height(mesh, *, height_m, max_triangles=500_000):
    """Intersect triangles with a horizontal Y plane; return XZ line segments.

    A geometric section is useful to slicing, CAD and collision. It is NOT a
    watertight polygon repairer, path planner or printable G-code compiler.
    """
    if type(height_m) not in (int,float) or not math.isfinite(height_m):
        raise ValueError("finite slice height required")
    if type(max_triangles) is not int or not 1<=max_triangles<=1_000_000:
        raise ValueError("bounded maximum triangle count required")
    positions=mesh.positions
    indices=mesh.indices
    if len(positions)%3 or len(indices)%3 or len(indices)//3>max_triangles:
        raise ValueError("invalid or over-budget triangle geometry")
    if not all(math.isfinite(p) for p in positions):
        raise ValueError("non-finite mesh position")
    if any(type(i) is not int or i<0 or i>=len(positions)//3 for i in indices):
        raise ValueError("mesh contains bad vertex indices")
    segments=[]
    for index in range(0,len(indices),3):
        triangle=[tuple(positions[3*j:3*j+3]) for j in indices[index:index+3]]
        points=[]
        for first,second in ((0,1),(1,2),(2,0)):
            a,b=triangle[first],triangle[second]
            da,db=a[1]-height_m,b[1]-height_m
            if da*db<0:
                t=-da/(db-da)
                points.append((a[0]+t*(b[0]-a[0]),a[2]+t*(b[2]-a[2])))
            elif da==0 and db!=0:
                points.append((a[0],a[2]))
            # Coplanar triangles/edges deliberately excluded to avoid
            # duplicate ambiguous outlines at exact vertex/face heights.
        unique=[]
        for point in points:
            rounded=tuple(round(v,8) for v in point)
            if rounded not in unique:
                unique.append(rounded)
        if len(unique)==2 and unique[0]!=unique[1]:
            segments.append(tuple(sorted(unique)))
    return sorted(segments)
