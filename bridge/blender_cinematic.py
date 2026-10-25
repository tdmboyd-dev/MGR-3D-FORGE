"""Materialize an MGR camera reel and lights in a real Blender scene.

Inputs: GLB, camera-tour JSON, mood, output.blend, preview.png, receipt.json.
"""

import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def xyz_to_blender(coords):
    return Vector((coords[0], -coords[2], coords[1]))


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=6:
        raise ValueError("expected source.glb camera_tour.json mood scene.blend preview.png receipt.json")
    source, tour_file, mood, blend, image, receipt=map(str,args)
    tour=json.loads(Path(tour_file).read_text(encoding="utf-8"))
    recipes={
        "daylight":(2.0,(1,.94,.84),.5,0),
        "golden-hour":(1.5,(1,.64,.39),.35,.2),
        "moonlit":(.25,(.38,.53,1),.16,-.6),
    }
    if mood not in recipes or not tour.get("shots"):
        raise ValueError("invalid cinematic mood or shots")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(Path(source).resolve()))
    imported=[o for o in bpy.data.objects if o.type=="MESH"]
    if not imported:
        raise ValueError("world GLB has no imported mesh")
    scene=bpy.context.scene
    fps=24
    scene.render.fps=fps
    frames=[]
    cursor=1
    for index,shot in enumerate(tour["shots"]):
        camera_data=bpy.data.cameras.new(f"MGR_Lens_{index:04d}")
        camera=bpy.data.objects.new(f"MGR_Shot_Camera_{index:04d}",camera_data)
        scene.collection.objects.link(camera)
        camera_data.type="PERSP"
        camera_data.lens=50
        point=xyz_to_blender(shot["camera"])
        look=xyz_to_blender(shot["look_at"])
        if (look-point).length<.01:
            raise ValueError("degenerate camera target")
        camera.location=point
        camera.rotation_euler=(look-point).to_track_quat("-Z","Y").to_euler()
        camera.keyframe_insert(data_path="location",frame=cursor)
        camera.keyframe_insert(data_path="rotation_euler",frame=cursor)
        stop=cursor+max(2,round(shot["hold_seconds"]*fps))-1
        camera.keyframe_insert(data_path="location",frame=stop)
        camera.keyframe_insert(data_path="rotation_euler",frame=stop)
        marker=scene.timeline_markers.new(f"MGR_{shot['id']}",frame=cursor)
        marker.camera=camera
        frames.append({"shot":shot["id"],"frame":cursor,"last_frame":stop,
                       "camera":camera.name,"lens_mm":camera_data.lens,
                       "direction":"cut with held subject framing"})
        if index==0:
            scene.camera=camera
        cursor=stop+1
    scene.frame_start=1
    scene.frame_end=cursor-1
    strength,color,ambient,exposure=recipes[mood]
    sun=bpy.data.lights.new("MGR_Cinematic_Key",type="SUN")
    sun.energy=strength
    sun.color=color
    sun_obj=bpy.data.objects.new("MGR_Cinematic_Key",sun)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler=(.5,-.7,-.4)
    if scene.world is None:
        scene.world=bpy.data.worlds.new("MGR_Cinematic_Environment")
    scene.world.use_nodes=True
    background=scene.world.node_tree.nodes.get("Background")
    background.inputs["Strength"].default_value=ambient
    scene.view_settings.view_transform="Standard"
    scene.view_settings.look="Medium High Contrast"
    scene.view_settings.exposure=exposure
    scene.render.engine="CYCLES"
    scene.cycles.samples=8
    scene.cycles.device="CPU"
    scene.render.resolution_x=640
    scene.render.resolution_y=360
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    scene.frame_set(1)
    for output in (Path(blend),Path(image),Path(receipt)):
        output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(blend).resolve()))
    scene.render.filepath=str(Path(image).resolve())
    bpy.ops.render.render(write_still=True)
    result={"schema":"mgr.forge.cinematic-materialization.v1",
            "status":"PASS" if Path(image).is_file() and Path(image).stat().st_size>0 else "FAIL",
            "blender_version":bpy.app.version_string, "mood":mood,
            "keyframes":frames,"camera_count":len(frames),
            "camera_cut_markers":len(scene.timeline_markers),"light_count":1,
            "mesh_count":len(imported),"frame_end":scene.frame_end,
            "render_engine":"CYCLES","render_device":"CPU",
            "render_bytes":Path(image).stat().st_size if Path(image).exists() else 0,
            "blend_bytes":Path(blend).stat().st_size if Path(blend).exists() else 0,
            "limitations":["8-sample CPU render is proof of pipeline, not final cinematic quality",
                           "timeline cuts and held frames only; interactive camera player and directed moving shots remain open"]}
    Path(receipt).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if result["status"]!="PASS":
        raise RuntimeError("cinematic render missing")
    print("MGR_CINEMATIC_PASS")


if __name__=="__main__":
    main()
