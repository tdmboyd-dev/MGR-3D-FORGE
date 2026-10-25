"""Headless Blender 5.x visual preview: GLB -> PNG plus geometry/camera receipt.

Run: blender -b --python bridge/blender_render.py -- FILE.glb OUTPUT.png REPORT.json
"""

import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def main():
    values=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if len(values)!=3:
        raise SystemExit("expected: input.glb output.png report.json")
    source,image,report=map(Path,values)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    objects=[o for o in bpy.data.objects if o.type=="MESH"]
    if not objects:
        raise RuntimeError("no Blender meshes imported")
    points=[o.matrix_world @ Vector(corner) for o in objects for corner in o.bound_box]
    minimum=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    maximum=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    center=(minimum+maximum)/2
    extent=maximum-minimum
    span=max(extent)
    camera_data=bpy.data.cameras.new("MGR QA Orthographic")
    camera=bpy.data.objects.new("MGR QA Camera",camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location=center+Vector((span*1.7,-span*1.7,span*1.4))
    direction=center-camera.location
    camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    camera_data.type="ORTHO"
    camera_data.ortho_scale=span*2.2
    scene=bpy.context.scene
    scene.camera=camera
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.render.resolution_x=900
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    scene.render.filepath=str(image.resolve())
    bpy.ops.render.render(write_still=True)
    receipt={"status":"PASS" if image.is_file() and image.stat().st_size>0 else "FAIL",
             "blender_version":bpy.app.version_string,"source":source.name,
             "image":image.name,"bytes":image.stat().st_size if image.exists() else 0,
             "object_count":len(objects),"bbox_extent":[round(v,6) for v in extent]}
    report.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if receipt["status"]!="PASS":
        raise RuntimeError("Blender render unavailable")
    print("MGR_FORGE_RENDER_REPORT="+json.dumps(receipt,sort_keys=True))


if __name__=="__main__":
    main()
