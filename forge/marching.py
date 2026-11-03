"""Bounded native surface nets over binary voxel-centre samples.

One vertex is placed in each mixed sample cell; one oriented quad is emitted
ONLY for a sign-changing sample edge. Outside padding closes subjects touching
capture bounds. This is a smooth voxel-field approximation, not learned hidden
geometry, a guarantee of arbitrary topology, or Constrained Elastic SurfaceNets.
The historical ``marching_cubes`` name remains an API alias, not an algorithm claim.
"""
import math

from .geometry import Mesh

_CORNERS = ((0,0,0), (1,0,0), (0,1,0), (1,1,0),
            (0,0,1), (1,0,1), (0,1,1), (1,1,1))
_EDGES = ((0,1), (2,3), (4,5), (6,7), (0,2), (1,3),
          (4,6), (5,7), (0,4), (1,5), (2,6), (3,7))


def _validate(occupancy, bounds, grid):
    if type(grid) is not int or not 2 <= grid <= 96:
        raise ValueError('surface grid must be an integer in 2..96')
    if not isinstance(bounds, (tuple, list)) or len(bounds) != 3 or any(
            type(v) not in (int,float) or not math.isfinite(v) or not .01 <= v <= 100 for v in bounds):
        raise ValueError('finite positive bounded surface dimensions required')
    if not isinstance(occupancy, (tuple,list)) or len(occupancy) != grid:
        raise ValueError('occupancy shape disagrees with its grid')
    for plane in occupancy:
        if not isinstance(plane, (tuple,list)) or len(plane) != grid:
            raise ValueError('occupancy shape disagrees with its grid')
        for row in plane:
            if not isinstance(row, (tuple,list)) or len(row) != grid:
                raise ValueError('occupancy shape disagrees with its grid')
            if any(type(v) not in (int,bool) or v not in (0,1) for v in row):
                raise ValueError('binary occupancy required')


def surface_nets(occupancy, bounds, grid):
    """Extract a deterministic oriented sample-field surface, including boundaries.

    Occupancy is indexed [y][z][x], with centres at (index+.5)*step.
    Diagonally touching/disconnected sheets can remain topologically ambiguous;
    callers must inspect the final mesh rather than assume manifoldness.
    """
    _validate(occupancy,bounds,grid)
    width,height,depth=bounds
    steps=(width/grid,height/grid,depth/grid)
    origin=(-width/2,0.,-depth/2)
    def value(x,y,z):
        return occupancy[y][z][x] if 0 <= x < grid and 0 <= y < grid and 0 <= z < grid else 0
    vertices={}
    positions=[]
    for x in range(-1,grid):
        for y in range(-1,grid):
            for z in range(-1,grid):
                samples=[value(x+dx,y+dy,z+dz) for dx,dy,dz in _CORNERS]
                if all(v == samples[0] for v in samples):
                    continue
                if len(vertices) >= 400_000:
                    raise ValueError('surface vertex budget exceeded')
                intersections=[]
                for a,b in _EDGES:
                    if samples[a] != samples[b]:
                        ca,cb=_CORNERS[a],_CORNERS[b]
                        intersections.append(tuple(origin[i]+((x,y,z)[i]+.5+(ca[i]+cb[i])/2)*steps[i]
                                                   for i in range(3)))
                vertices[x,y,z]=len(positions)//3
                positions.extend(sum(p[i] for p in intersections)/len(intersections) for i in range(3))
    indices=[]
    def face(cells,inside_first):
        if len(indices) >= 400_000 * 6:
            raise ValueError('surface face budget exceeded')
        quad=[vertices[cell] for cell in cells]
        if not inside_first:quad.reverse()
        a,b,c,d=quad
        indices.extend((a,b,c,a,c,d))
    for y in range(grid):
        for z in range(grid):
            for x in range(-1,grid):
                a,b=value(x,y,z),value(x+1,y,z)
                if a != b:
                    face(((x,y-1,z-1),(x,y,z-1),(x,y,z),(x,y-1,z)),a)
    for x in range(grid):
        for z in range(grid):
            for y in range(-1,grid):
                a,b=value(x,y,z),value(x,y+1,z)
                if a != b:
                    face(((x-1,y,z-1),(x-1,y,z),(x,y,z),(x,y,z-1)),a)
    for x in range(grid):
        for y in range(grid):
            for z in range(-1,grid):
                a,b=value(x,y,z),value(x,y,z+1)
                if a != b:
                    face(((x-1,y-1,z),(x,y-1,z),(x,y,z),(x-1,y,z)),a)
    normals=[0.] * len(positions)
    for offset in range(0,len(indices),3):
        a,b,c=indices[offset:offset+3]
        p,q,r=(positions[i*3:i*3+3] for i in (a,b,c))
        u=tuple(q[i]-p[i] for i in range(3))
        v=tuple(r[i]-p[i] for i in range(3))
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        for index in (a,b,c):
            for axis in range(3):normals[index*3+axis]+=cross[axis]
    for offset in range(0,len(normals),3):
        length=math.sqrt(sum(v*v for v in normals[offset:offset+3]))
        if length <= 1e-15:
            raise ValueError('ambiguous surface normal; use voxel surface or revise masks')
        normals[offset:offset+3]=[v/length for v in normals[offset:offset+3]]
    return Mesh(positions=positions,normals=normals,indices=indices)


marching_cubes=surface_nets
