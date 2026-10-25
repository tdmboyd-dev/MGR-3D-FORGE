"""Read real editable Blender objects and export Forge's bounded world-edit contract."""

import json
import math
from pathlib import Path
import sys

import bpy


MATERIALS = {"building-brick", "building-stone", "building-blue", "building-gold", "building-emerald"}


def main(arguments):
    if len(arguments) != 2:
        raise ValueError("expect WORLD_EDITS.json and RECEIPT.json")
    out, report = [Path(s) for s in arguments]
    if out.exists() or report.exists():
        raise FileExistsError("Blender roundtrip cannot overwrite existing output")
    scene = bpy.context.scene
    asset_sha = scene.get("mgr_source_sha256")
    if (scene.get("mgr_edit_schema") != "mgr.forge.world-edit.v1" or
            type(asset_sha) is not str or len(asset_sha) != 64 or
            any(c not in "0123456789abcdef" for c in asset_sha)):
        raise ValueError("MGR editable source scene marker missing")
    buildings = []
    seen = set()
    for obj in bpy.data.objects:
        if "mgr_id" not in obj:
            continue
        name, material = obj["mgr_id"], obj.get("mgr_material")
        if (type(name) is not str or name in seen or obj.type != "MESH" or
                material not in MATERIALS or len(buildings) >= 128):
            raise ValueError("invalid editable object identity/material")
        seen.add(name)
        # Reject non-box topology and rotations; editor contract is still axis-aligned boxes.
        if len(obj.data.vertices) != 8 or len(obj.data.polygons) != 6:
            raise ValueError("unsupported non-cuboid mesh modification")
        if any(abs(angle) > 0.00001 for angle in obj.rotation_euler):
            raise ValueError("rotation is not yet supported by browser scene schema")
        x, z, y = obj.location.x, -obj.location.y, obj.location.z
        width, depth, height = obj.dimensions.x, obj.dimensions.y, obj.dimensions.z
        values = (x, y, z, width, height, depth)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("nonfinite Blender transform")
        # Blender cube center sits at half height; Forge buildings are ground-based.
        if abs(y - height / 2) > 0.0001:
            raise ValueError("building must remain ground-based")
        buildings.append({"id": name, "center": [round(x, 6), 0, round(z, 6)],
                          "size": [round(width, 6), round(height, 6), round(depth, 6)],
                          "material": material})
    document = {"schema": "mgr.forge.world-edit.v1", "asset_sha256": asset_sha,
                "buildings": buildings}
    out.write_text(json.dumps(document, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    report.write_text(json.dumps({"schema": "mgr.forge.blender-roundtrip.v1", "status": "EXPORTED",
                                  "editable_buildings": len(buildings),
                                  "source_sha256": asset_sha}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "EXPORTED", "editable_buildings": len(buildings)}))


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
