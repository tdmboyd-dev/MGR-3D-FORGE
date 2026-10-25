"""Export an actually deforming saved mannequin rig to portable animated GLB."""

import hashlib
import json
from pathlib import Path
import sys

import bpy


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 3:
        raise ValueError("original-rig.blend new-character.glb new-report.json required")
    source, output, report = map(Path, args)
    if output.exists() or report.exists() or output.suffix.lower() != ".glb":
        raise ValueError("new GLB and report required")
    bpy.ops.wm.open_mainfile(filepath=str(source.resolve()), load_ui=False)
    rigged = [o for o in bpy.data.objects if o.type == "MESH"
              and any(mod.type == "ARMATURE" and mod.object for mod in o.modifiers)
              and len(o.vertex_groups) > 0]
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not arms or not rigged:
        raise RuntimeError("cannot export animation without real skin modifiers and bones")
    frames = (1, 12)
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = frames
    specimen = next((o for o in rigged if "hand" in o.name.lower()), rigged[0])
    def points(frame):
        scene.frame_set(frame)
        graph = bpy.context.evaluated_depsgraph_get()
        evaluated = specimen.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        try:
            return [evaluated.matrix_world @ v.co for v in mesh.vertices]
        finally:
            evaluated.to_mesh_clear()
    first, last = points(frames[0]), points(frames[1])
    movement = max(((a-b).length for a, b in zip(first, last)), default=0)
    if movement <= .01:
        raise RuntimeError("evaluated skinned mesh does not move across intended frames")
    scene.frame_set(frames[0])
    bpy.ops.export_scene.gltf(filepath=str(output.resolve()), export_format="GLB",
                              export_animations=True, export_skins=True,
                              export_frame_range=True, export_force_sampling=True,
                              export_yup=True, export_extras=False)
    if not output.is_file() or output.stat().st_size < 1000:
        raise RuntimeError("no valid GLB output")
    result = {"schema": "mgr.forge.animation-export.v1", "status": "MATERIALIZED",
              "blender_version": bpy.app.version_string,
              "rigged_mesh_objects": len(rigged), "armatures": len(arms),
              "observed_motion_m": round(movement, 6),
              "output_bytes": output.stat().st_size,
              "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
              "engine_import_verified": False,
              "independent_blender_import_verified": False,
              "owner_approved_likeness": False}
    report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
