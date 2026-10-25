"""Render two keyframes of a Blender rig from one fixed QA camera.

blender -b --factory-startup --python THIS -- rig.blend frame1.png frame12.png report.json
"""

import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def main():
    args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if len(args)!=4:
        raise ValueError("expected rig.blend frame1.png frame12.png report.json")
    source,first,second,report=map(Path,args)
    if source.suffix.lower()!=".blend" or not source.is_file():
        raise ValueError("existing Blender project required")
    bpy.ops.wm.open_mainfile(filepath=str(source.resolve()))
    objects=[obj for obj in bpy.data.objects if obj.type=="MESH"]
    rigs=[obj for obj in bpy.data.objects if obj.type=="ARMATURE"]
    if not objects or len(rigs)!=1:
        raise RuntimeError("one actual armature and mesh parts required")
    scene=bpy.context.scene
    scene.frame_set(1)
    vertices=[obj.matrix_world @ Vector(c) for obj in objects for c in obj.bound_box]
    minimum=Vector(tuple(min(v[i] for v in vertices) for i in range(3)))
    maximum=Vector(tuple(max(v[i] for v in vertices) for i in range(3)))
    center=(minimum+maximum)/2
    span=max(maximum-minimum)
    camera_data=bpy.data.cameras.new("MGR Fixed QA Camera")
    camera=bpy.data.objects.new("MGR Fixed QA Camera",camera_data)
    scene.collection.objects.link(camera)
    camera.location=center+Vector((span*1.4,-span*2,span*1.2))
    camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO"
    camera_data.ortho_scale=span*2.6
    scene.camera=camera
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.render.resolution_x=900
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=True
    scene.render.image_settings.color_mode="RGBA"
    receipt={"schema":"mgr.forge.pose-render.v1","blender_version":bpy.app.version_string,
             "source":source.name,"rig_count":len(rigs),"part_count":len(objects),"frames":[]}
    for frame,path in ((1,first),(12,second)):
        path.parent.mkdir(parents=True,exist_ok=True)
        scene.frame_set(frame)
        scene.render.filepath=str(path.resolve())
        bpy.ops.render.render(write_still=True)
        receipt["frames"].append({"frame":frame,"file":path.name,
                                  "bytes":path.stat().st_size if path.exists() else 0})
    receipt["status"]="PASS" if all(item["bytes"]>0 for item in receipt["frames"]) else "FAIL"
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if receipt["status"]!="PASS":
        raise RuntimeError("rendered animation frames missing")
    print("MGR_POSE_RENDER_PASS")


if __name__=="__main__":
    main()
