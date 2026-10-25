"""CPU-only Wavefront OBJ/MTL fallback export with stable materials."""

from .geometry import MATERIALS


def export_obj(meshes, *, mtl_name="world.mtl", materials=None):
    materials = MATERIALS if materials is None else materials
    if len(meshes) != len(materials):
        raise ValueError("mesh/material count mismatch")
    if "/" in mtl_name or "\\" in mtl_name or not mtl_name.endswith(".mtl"):
        raise ValueError("unsafe MTL name")
    lines = ["# MGR 3D Forge generated OBJ", f"mtllib {mtl_name}"]
    offset = 1
    for material_index, mesh in enumerate(meshes):
        if not mesh.indices:
            continue
        name = materials[material_index][0]
        lines.extend((f"o {name}", f"usemtl {name}"))
        for idx in range(0, len(mesh.positions), 3):
            x, y, z = mesh.positions[idx:idx+3]
            lines.append(f"v {x:.6f} {y:.6f} {z:.6f}")
        for idx in range(0, len(mesh.normals), 3):
            x, y, z = mesh.normals[idx:idx+3]
            lines.append(f"vn {x:.6f} {y:.6f} {z:.6f}")
        for idx in range(0, len(mesh.indices), 3):
            a, b, c = (offset + n for n in mesh.indices[idx:idx+3])
            lines.append(f"f {a}//{a} {b}//{b} {c}//{c}")
        offset += len(mesh.positions) // 3
    material_lines = ["# MGR Forge PBR-to-OBJ diffuse approximation"]
    for name, rgba in materials:
        material_lines.extend((f"newmtl {name}",
                          f"Kd {rgba[0]:.6f} {rgba[1]:.6f} {rgba[2]:.6f}",
                          "Ka 0.0 0.0 0.0", "Ks 0.05 0.05 0.05", "Ns 20.0"))
    return "\n".join(lines) + "\n", "\n".join(material_lines) + "\n"
