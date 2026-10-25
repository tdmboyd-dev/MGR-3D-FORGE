"""CPU-generated, real triangle geometry. Y is up; X/Z form the ground."""

import random
from dataclasses import dataclass, field

from .spec import WorldSpec


MATERIALS = (
    ("grass", [0.19, 0.36, 0.22, 1]),
    ("asphalt", [0.105, 0.11, 0.14, 1]),
    ("building-brick", [0.52, 0.25, 0.19, 1]),
    ("building-stone", [0.55, 0.54, 0.51, 1]),
    ("building-blue", [0.16, 0.31, 0.47, 1]),
    ("roof", [0.13, 0.13, 0.16, 1]),
)


@dataclass
class Mesh:
    positions: list[float] = field(default_factory=list)
    normals: list[float] = field(default_factory=list)
    indices: list[int] = field(default_factory=list)

    def quad(self, a, b, c, d):
        # Face normals are derived from winding, so each hard edge stays flat.
        ux, uy, uz = (b[i] - a[i] for i in range(3))
        vx, vy, vz = (c[i] - a[i] for i in range(3))
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        magnitude = (nx * nx + ny * ny + nz * nz) ** 0.5
        if magnitude == 0:
            raise ValueError("degenerate quad")
        normal = (nx / magnitude, ny / magnitude, nz / magnitude)
        base = len(self.positions) // 3
        for vertex in (a, b, c, d):
            self.positions.extend(vertex)
            self.normals.extend(normal)
        self.indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))

    def box(self, x, y, z, width, height, depth):
        if min(width, height, depth) <= 0:
            raise ValueError("box dimensions must be positive")
        x0, x1 = x - width / 2, x + width / 2
        z0, z1 = z - depth / 2, z + depth / 2
        y0, y1 = y, y + height
        a, b, c, d = (x0,y0,z0), (x1,y0,z0), (x1,y0,z1), (x0,y0,z1)
        e, f, g, h = (x0,y1,z0), (x1,y1,z0), (x1,y1,z1), (x0,y1,z1)
        # Outward-facing normals in right-handed glTF coordinates.
        for face in ((a,b,c,d), (h,g,f,e), (e,f,b,a),
                     (f,g,c,b), (g,h,d,c), (h,e,a,d)):
            self.quad(*face)


def create_neighborhood(spec: WorldSpec):
    """Return material meshes and serializable world metadata."""
    rng = random.Random(spec.seed)
    meshes = [Mesh() for _ in MATERIALS]
    stride = spec.lot_size + spec.road_width
    ground_width = spec.columns * stride + spec.road_width
    ground_depth = spec.rows * stride + spec.road_width
    meshes[0].box(0, -0.55, 0, ground_width, 0.5, ground_depth)

    # Roads run between all lots, and ring the world boundary.
    road_locations = []
    for i in range(spec.columns + 1):
        x = (i - spec.columns / 2) * stride
        meshes[1].box(x, -0.045, 0, spec.road_width, 0.09, ground_depth)
        road_locations.append({"axis": "z", "coordinate": round(x, 5)})
    for i in range(spec.rows + 1):
        z = (i - spec.rows / 2) * stride
        meshes[1].box(0, -0.04, z, ground_width, 0.08, spec.road_width)
        road_locations.append({"axis": "x", "coordinate": round(z, 5)})

    lots = [(col, row) for row in range(spec.rows) for col in range(spec.columns)]
    rng.shuffle(lots)
    buildings = []
    for col, row in lots[:spec.buildings]:
        x = (col - (spec.columns - 1) / 2) * stride
        z = (row - (spec.rows - 1) / 2) * stride
        width = round(spec.lot_size * rng.uniform(0.50, 0.78), 4)
        depth = round(spec.lot_size * rng.uniform(0.50, 0.78), 4)
        height = round(rng.uniform(5, 22), 4)
        material = rng.choice((2, 3, 4))
        meshes[material].box(x, 0, z, width, height, depth)
        meshes[5].box(x, height, z, width + 0.3, 0.3, depth + 0.3)
        buildings.append({
            "id": f"building-{row:03d}-{col:03d}",
            "lot": [col, row], "center": [round(x, 5), 0, round(z, 5)],
            "size": [width, height, depth], "material": MATERIALS[material][0],
            "entry_road_distance": round((spec.lot_size - max(width, depth)) / 2 + spec.road_width / 2, 4),
        })
    buildings.sort(key=lambda item: item["id"])
    meta = {
        "schema": "mgr.forge.world.v1", "generator": "forge.cpu.neighborhood.v1",
        "spec": spec.as_dict(), "axis": "Y_UP", "unit": "meter",
        "grounds": {"width": ground_width, "depth": ground_depth},
        "roads": road_locations, "buildings": buildings,
        "material_count": len(MATERIALS),
        "triangle_count": sum(len(m.indices) // 3 for m in meshes),
        "vertex_count": sum(len(m.positions) // 3 for m in meshes),
        "status": "geometry-generated-not-engine-validated",
    }
    return meshes, meta
