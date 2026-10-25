"""Fixed, no-user-script Blender import into an editable character source .blend."""

import hashlib
import json
from pathlib import Path
import sys

import bpy


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 4:
        raise ValueError("source.glb new.blend new-report.json expected-sha required")
    source, output, report, expected_sha = args
    if hashlib.sha256(Path(source).read_bytes()).hexdigest() != expected_sha:
        raise ValueError("source was modified after admission")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(Path(source).resolve()))
    objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if not objects:
        raise RuntimeError("import contains no editable meshes")
    triangle_count = 0
    for obj in objects:
        obj.data.calc_loop_triangles()
        triangle_count += len(obj.data.loop_triangles)
        obj["mgr_character_source_sha256"] = expected_sha
    if triangle_count <= 0:
        raise RuntimeError("import contains no triangles")
    bpy.context.scene["mgr_character_source_sha256"] = expected_sha
    bpy.context.scene["mgr_source_status"] = "unapproved-character-candidate"
    part_inventory = []
    for obj in sorted(objects, key=lambda o: o.name):
        materials = [slot.material.name if slot.material else None for slot in obj.material_slots]
        armature_modifiers = [mod.object.name if mod.object else None for mod in obj.modifiers
                              if mod.type == "ARMATURE"]
        part_inventory.append({"object": obj.name, "vertices": len(obj.data.vertices),
                               "triangles": len(obj.data.loop_triangles),
                               "material_slots": materials,
                               "armature_modifiers": armature_modifiers,
                               "vertex_groups": len(obj.vertex_groups),
                               "shape_keys": len(obj.data.shape_keys.key_blocks)
                               if obj.data.shape_keys else 0})
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(output).resolve()))
    receipt = {"schema": "mgr.forge.blender-character-intake.v1", "status": "PASS",
               "source_sha256": expected_sha, "mesh_objects": len(objects),
               "triangles": triangle_count,
               "editable_parts": part_inventory,
               "garments_semantically_verified": False,
               "pose_deformation_verified": False,
               "armature_objects": sum(obj.type == "ARMATURE" for obj in bpy.data.objects),
               "blender_version": bpy.app.version_string,
               "owner_approved_likeness": False}
    Path(report).write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
