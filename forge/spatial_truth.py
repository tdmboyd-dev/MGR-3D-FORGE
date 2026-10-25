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


def triangulate_parallel_views(pixel_a, pixel_b, *, camera_a, camera_b,
                               focal_px, center_px=(0,0),
                               max_separation_m=0.05, max_reprojection_px=2.0):
    """Triangulate two calibrated, *parallel-facing* cameras viewing +Z.

    This is the closest-point solution for two rays. It fails closed for poor
    parallax, points behind the cameras, inconsistent image correspondence,
    and invented/unobserved depth. It does not estimate camera orientation.
    """
    if len(camera_a)!=3 or len(camera_b)!=3 or not all(
        type(v) in (float,int) and math.isfinite(v) for v in (*camera_a,*camera_b)):
        raise ValueError("finite camera world positions required")
    for value in (max_separation_m,max_reprojection_px):
        if type(value) not in (float,int) or not math.isfinite(value) or value<=0:
            raise ValueError("positive finite error tolerances required")
    d1=pixel_to_ray(pixel_a,focal_px=focal_px,center_px=center_px)
    d2=pixel_to_ray(pixel_b,focal_px=focal_px,center_px=center_px)
    difference=[camera_a[i]-camera_b[i] for i in range(3)]
    dot=sum(d1[i]*d2[i] for i in range(3))
    denominator=1-dot*dot
    if denominator<1e-8 or sum(v*v for v in difference)<1e-10:
        raise ValueError("unobservable depth: absent or insufficient parallax")
    d=sum(d1[i]*difference[i] for i in range(3))
    e=sum(d2[i]*difference[i] for i in range(3))
    t=(dot*e-d)/denominator
    u=(e-dot*d)/denominator
    if t<=0 or u<=0:
        raise ValueError("triangulated point lies behind a camera")
    p=[camera_a[i]+t*d1[i] for i in range(3)]
    q=[camera_b[i]+u*d2[i] for i in range(3)]
    separation=math.sqrt(sum((p[i]-q[i])**2 for i in range(3)))
    if separation>max_separation_m:
        raise ValueError("rays disagree in world space")
    point=tuple((p[i]+q[i])/2 for i in range(3))
    projections=[camera_project(tuple(point[i]-camera[i] for i in range(3)),
                                focal_px=focal_px,center_px=center_px)
                 for camera in (camera_a,camera_b)]
    errors=[math.dist(projections[i],pixel) for i,pixel in enumerate((pixel_a,pixel_b))]
    if max(errors)>max_reprojection_px:
        raise ValueError("triangulated point failed image reprojection")
    return {"schema":"mgr.forge.stereo-depth.v1","point_m":point,
            "ray_separation_m":round(separation,8),
            "reprojection_errors_px":[round(v,6) for v in errors],
            "baseline_m":round(math.sqrt(sum(v*v for v in difference)),8),
            "observation":"two matched calibrated rays",
            "limitations":["assumes both camera optical axes parallel along +Z",
                           "correspondences and focal length must be measured, not guessed",
                           "a fit is not proof of unseen geometry"]}


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
