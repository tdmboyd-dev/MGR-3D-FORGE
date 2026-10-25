"""Collect evaluated Blender armature snapshots; delegate scoring to Forge QA.

blender --background --python bridge/blender_pose_inspect.py -- source.blend result.json
"""

import json
from pathlib import Path
import sys

import bpy


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) != 2:
        raise ValueError("expected source.blend report.json")
    source, output = map(Path, args)
    if source.suffix.lower() != ".blend" or not source.is_file():
        raise ValueError("existing .blend required")
    bpy.ops.wm.open_mainfile(filepath=str(source.resolve()), load_ui=False)
    rig = bpy.data.objects.get("MGR_Character_Rig")
    if rig is None or rig.type != "ARMATURE":
        raise ValueError("expected MGR_Character_Rig armature")
    observations = []
    for frame_no in (1, 12):
        bpy.context.scene.frame_set(frame_no)
        bpy.context.view_layer.update()
        bones = {}
        for bone in rig.pose.bones:
            bones[bone.name] = {
                "head": list(rig.matrix_world @ bone.head),
                "tail": list(rig.matrix_world @ bone.tail),
            }
        parts = {}
        for obj in bpy.data.objects:
            if obj.type != "MESH" or not obj.name.startswith("MGR_"):
                continue
            modifiers = [m for m in obj.modifiers if m.type == "ARMATURE" and m.object == rig]
            weighted = 0
            dual = 0
            max_error = 0.0
            for vertex in obj.data.vertices:
                active=[group.weight for group in vertex.groups
                        if obj.vertex_groups[group.group].name in bones and group.weight>0]
                if active:
                    weighted += 1
                    max_error=max(max_error,abs(sum(active)-1))
                if len(active)>=2:
                    dual += 1
            parts[obj.name] = {"vertices": len(obj.data.vertices),
                               "weighted_vertices": weighted,
                               "dual_weight_vertices":dual,
                               "max_weight_sum_error":round(max_error,6),
                               "armature_modifier": bool(modifiers)}
        observations.append({"frame": frame_no, "bones": bones, "parts": parts})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema": "mgr.forge.pose-observation.v1",
                                  "blender_version": bpy.app.version_string,
                                  "observations": observations}, indent=2) + "\n", encoding="utf-8")
    print("MGR_POSE_OBSERVATION_PASS")


if __name__ == "__main__":
    main()
