"""Create a new editable material-separated character project without modifying input."""

import json
from pathlib import Path
import sys

import bpy


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 3:
        raise ValueError("original.blend new-separated.blend new-report.json required")
    original, output, receipt = map(Path, args)
    if original.resolve() == output.resolve() or output.exists() or receipt.exists():
        raise ValueError("separation must create new outputs, preserving source")
    bpy.ops.wm.open_mainfile(filepath=str(original.resolve()), load_ui=False)
    digest = bpy.context.scene.get("mgr_character_source_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("saved project lacks source admission SHA")
    original_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    if not original_meshes:
        raise ValueError("no meshes to separate")
    originals = len(original_meshes)
    before_triangles = 0
    for item in original_meshes:
        item.data.calc_loop_triangles()
        before_triangles += len(item.data.loop_triangles)
        if item.get("mgr_character_source_sha256") != digest:
            raise ValueError("mesh source fingerprint mismatch")
    for obj in original_meshes:
        if len(obj.data.materials) < 2 or len({p.material_index for p in obj.data.polygons}) < 2:
            continue
        if obj.hide_get():
            obj.hide_set(False)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type="MATERIAL")
        bpy.ops.object.mode_set(mode="OBJECT")
    after_meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    after_triangles = 0
    parts = []
    for obj in sorted(after_meshes, key=lambda item: item.name):
        obj.data.calc_loop_triangles()
        triangles = len(obj.data.loop_triangles)
        after_triangles += triangles
        mats = sorted({obj.material_slots[p.material_index].material.name
                       for p in obj.data.polygons
                       if p.material_index < len(obj.material_slots)
                       and obj.material_slots[p.material_index].material})
        obj["mgr_character_source_sha256"] = digest
        obj["mgr_part_materials"] = ",".join(mats)
        parts.append({"object": obj.name, "triangles": triangles, "materials": mats,
                      "vertex_groups": len(obj.vertex_groups),
                      "armature_modifiers": sum(m.type == "ARMATURE" for m in obj.modifiers)})
    if before_triangles != after_triangles:
        raise RuntimeError("material separation changed source triangle count")
    bpy.context.scene["mgr_material_separation"] = "material-boundaries-only"
    bpy.ops.wm.save_as_mainfile(filepath=str(output.resolve()))
    result = {"schema": "mgr.forge.material-separated-character.v1", "status": "PASS",
              "source_sha256": digest, "blender_version": bpy.app.version_string,
              "source_mesh_objects": originals, "separated_mesh_objects": len(after_meshes),
              "triangle_count_before": before_triangles, "triangle_count_after": after_triangles,
              "parts": parts, "semantic_garment_labels_verified": False,
              "pose_deformation_verified": False}
    receipt.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
