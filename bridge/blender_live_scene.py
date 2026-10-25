"""Blender-side native scene builder, callable only with validated world bundle paths."""

import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


PALETTE = {
    "building-brick": (0.52, 0.25, 0.19, 1),
    "building-stone": (0.55, 0.54, 0.51, 1),
    "building-blue": (0.16, 0.31, 0.47, 1),
    "building-gold": (0.68, 0.48, 0.13, 1),
    "building-emerald": (0.12, 0.48, 0.34, 1),
}


def main(argv):
    if len(argv) != 3:
        raise ValueError("usage: blender --python blender_live_scene.py -- BUNDLE SCENE.blend REPORT.json")
    folder, blend, report = Path(argv[0]), Path(argv[1]), Path(argv[2])
    if blend.exists() or report.exists():
        raise FileExistsError("Blender outputs must not exist")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    glb_sha = hashlib.sha256((folder / "world.glb").read_bytes()).hexdigest()
    if manifest.get("artifact", {}).get("sha256") != glb_sha or manifest.get("edit_provenance", {}).get("schema") != "mgr.forge.edited-world.v1":
        raise ValueError("Blender input integrity failed")
    buildings = manifest["buildings"]
    if not isinstance(buildings, list) or len(buildings) > 128:
        raise ValueError("invalid building inventory")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    materials = {}
    for name, rgb in PALETTE.items():
        mat = bpy.data.materials.new(name=f"MGR {name}")
        mat.diffuse_color = rgb
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Base Color"].default_value = rgb
            shader.inputs["Roughness"].default_value = 0.72
        materials[name] = mat
    names = set()
    for item in buildings:
        name, center, size, color = item["id"], item["center"], item["size"], item["material"]
        if type(name) is not str or name in names or color not in materials:
            raise ValueError("unsafe or duplicate building")
        names.add(name)
        if len(center) != 3 or len(size) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) for v in center + size):
            raise ValueError("invalid building transform")
        if center[1] != 0 or min(size) < 2 or max(size) > 100:
            raise ValueError("unsafe geometry")
        # MGR is Y-up, Blender is Z-up; preserve horizontal handedness.
        bpy.ops.mesh.primitive_cube_add(size=1, location=(center[0], -center[2], size[1] / 2))
        obj = bpy.context.object
        obj.name = name
        obj.dimensions = (size[0], size[2], size[1])
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.data.materials.append(materials[color])
        obj["mgr_id"] = name
        obj["mgr_material"] = color
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.15))
    ground = bpy.context.object
    ground.name = "MGR Ground"
    grounds = manifest["grounds"]
    ground.dimensions = (grounds["width"], grounds["depth"], 0.3)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    lamp_data = bpy.data.lights.new(name="MGR Key Sun", type="SUN")
    lamp_data.energy = 2.0
    lamp = bpy.data.objects.new("MGR Key Sun", lamp_data)
    bpy.context.collection.objects.link(lamp)
    lamp.rotation_euler = (0.5, -0.35, -0.45)
    camera_data = bpy.data.cameras.new(name="MGR Creation Camera")
    camera = bpy.data.objects.new("MGR Creation Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (38, -52, 38)
    direction = Vector((0, 0, 4)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
    data = {"schema": "mgr.forge.blender-live-scene-proof.v1", "status": "PASS",
            "blender_version": bpy.app.version_string, "editable_buildings": len(names),
            "object_names": sorted(names), "source_glb_sha256": glb_sha,
            "blend_bytes": blend.stat().st_size, "scene": str(blend.resolve())}
    report.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "editable_buildings": len(names), "blend": str(blend)}))


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
