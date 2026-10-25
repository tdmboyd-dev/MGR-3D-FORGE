"""Inspect actual saved Blender multi-camera cut sequence independently."""

import json
from pathlib import Path
import sys

import bpy


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=2:
        raise ValueError("expected input.blend report.json")
    project,report=map(Path,args)
    bpy.ops.wm.open_mainfile(filepath=str(project.resolve()),load_ui=False)
    scene=bpy.context.scene
    markers=sorted(scene.timeline_markers,key=lambda item:item.frame)
    cameras=[o for o in bpy.data.objects if o.type=="CAMERA"]
    errors=[]
    if len(markers)<2:
        errors.append("no multi-shot cut markers")
    if len(cameras)<len(markers):
        errors.append("missing physical cameras")
    if len({m.frame for m in markers})!=len(markers):
        errors.append("duplicate cut frame")
    for marker in markers:
        if marker.camera is None or marker.camera not in cameras:
            errors.append(f"cut marker has no valid camera: {marker.name}")
        if not scene.frame_start<=marker.frame<=scene.frame_end:
            errors.append(f"cut outside frame range: {marker.name}")
    cuts=[]
    for index,marker in enumerate(markers):
        if marker.camera is None:
            continue
        stop=(markers[index+1].frame-1 if index+1<len(markers) else scene.frame_end)
        scene.frame_set(marker.frame)
        start_position=marker.camera.matrix_world.translation.copy()
        scene.frame_set(stop)
        end_position=marker.camera.matrix_world.translation.copy()
        cuts.append({"frame":marker.frame,"last_frame":stop,
                     "name":marker.name,"camera":marker.camera.name,
                     "measured_motion_m":round((end_position-start_position).length,6)})
    result={"schema":"mgr.forge.director-blender-audit.v1",
            "status":"PASS" if not errors else "FAIL","errors":errors,
            "blender_version":bpy.app.version_string,
            "frame_start":scene.frame_start,"frame_end":scene.frame_end,
            "camera_count":len(cameras),
            "moving_shots":sum(cut["measured_motion_m"]>.01 for cut in cuts),
            "cuts":cuts}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if errors:
        raise RuntimeError("invalid saved MGR camera cut scene")
    print("MGR_DIRECTOR_AUDIT_PASS")


if __name__=="__main__":
    main()
