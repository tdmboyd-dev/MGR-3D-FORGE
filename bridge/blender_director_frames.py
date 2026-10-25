"""Render real saved MGR Director timeline samples at reduced CPU QA quality."""

import json
from pathlib import Path
import sys

import bpy


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=3:
        raise ValueError("expected director.blend output_directory report.json")
    source,output,receipt=map(Path,args)
    bpy.ops.wm.open_mainfile(filepath=str(source.resolve()),load_ui=False)
    scene=bpy.context.scene
    cuts=sorted(scene.timeline_markers,key=lambda m:m.frame)
    if len(cuts)<2 or any(marker.camera is None for marker in cuts):
        raise RuntimeError("real multi-camera cut markers required")
    desired=sorted({cuts[0].frame,cuts[1].frame,
                    (cuts[2].frame-1 if len(cuts)>2 else scene.frame_end),
                    (cuts[2].frame if len(cuts)>2 else scene.frame_end)})
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=4
    scene.render.resolution_x=320
    scene.render.resolution_y=180
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for frame in desired:
        chosen=max((m for m in cuts if m.frame<=frame),key=lambda m:m.frame)
        scene.camera=chosen.camera
        scene.frame_set(frame)
        path=output/f"director-frame-{frame:04d}.png"
        if path.exists():
            raise FileExistsError(f"existing frame proof: {path}")
        scene.render.filepath=str(path.resolve())
        bpy.ops.render.render(write_still=True)
        rows.append({"frame":frame,"camera":chosen.camera.name,"filename":path.name,
                     "bytes":path.stat().st_size if path.exists() else 0})
    result={"schema":"mgr.forge.director-timeline-frames.v1",
            "blender_version":bpy.app.version_string,
            "status":"PASS" if all(item["bytes"]>0 for item in rows) else "FAIL",
            "render_device":"CPU","engine":"CYCLES","resolution":[320,180],
            "samples":4,"frames":rows}
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if result["status"]!="PASS":
        raise RuntimeError("director frames missing")
    print("MGR_DIRECTOR_FRAMES_PASS")


if __name__=="__main__":
    main()
