"""Blender-only fixed-camera import/render witness for two native creature GLBs.

Run Blender --background --factory-startup --python THIS -- BEFORE AFTER OUT.
BEFORE and AFTER are preserved creature directories. This renders actual input
meshes; it does not grade artistic quality or claim production skinning.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    manifest=json.loads((root/"creature.json").read_text(encoding="utf8"))
    glb=root/"creature.glb"
    if digest(glb)!=manifest["artifact"]["sha256"]:
        raise ValueError("original creature manifest/artifact hash mismatch")
    bpy.ops.import_scene.gltf(filepath=str(glb.resolve()))
    meshes=[obj for obj in bpy.data.objects if obj.type=="MESH"]
    if len(meshes)!=1:raise RuntimeError("expected original single creature mesh")
    obj=meshes[0]
    points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    return manifest,obj,points


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=3:raise ValueError("BEFORE AFTER OUT required")
    before,after,out=map(Path,args)
    if out.exists():raise FileExistsError("preserve existing surface proof")
    observations=[]
    all_bounds=[]
    docs=[]
    for source in (before,after):
        doc,obj,bounds=load(source)
        docs.append(doc)
        all_bounds.extend(bounds)
    if any(docs[0][key]!=docs[1][key] for key in ("prompt","seed","requested_variants","applied_morph")):
        raise ValueError("comparison input intent changed")
    # New explicit-count DNA defaults may be added without changing dimensions.
    for key,value in docs[0]["selected_genome"].items():
        if docs[1]["selected_genome"].get(key)!=value:
            raise ValueError("comparison changed original chosen anatomy")
    low=Vector(tuple(min(p[i] for p in all_bounds) for i in range(3)))
    high=Vector(tuple(max(p[i] for p in all_bounds) for i in range(3)))
    center=(low+high)/2
    extent=max(high-low)
    out.mkdir(parents=True)
    for name,source in (("before",before),("after",after)):
        doc,obj,_=load(source)
        scene=bpy.context.scene
        scene.world=bpy.data.worlds.new("MGR_Surface_Witness_World")
        scene.world.color=(.05,.06,.08)
        camera_data=bpy.data.cameras.new("MGR_Fixed_Camera")
        camera=bpy.data.objects.new("MGR_Fixed_Camera",camera_data)
        scene.collection.objects.link(camera)
        camera.location=center+Vector((extent*.8,-extent*1.5,extent*.7))
        camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
        camera.data.type="ORTHO"
        camera.data.ortho_scale=extent*1.35
        scene.camera=camera
        scene.render.engine="BLENDER_WORKBENCH"
        scene.display.shading.light="STUDIO"
        scene.display.shading.color_type="MATERIAL"
        scene.display.shading.show_shadows=True
        scene.display.shading.show_cavity=True
        scene.display.shading.background_type="WORLD"
        scene.render.resolution_x=900
        scene.render.resolution_y=650
        scene.render.resolution_percentage=100
        scene.render.image_settings.file_format="PNG"
        image=out/(name+".png")
        blend=out/(name+".blend")
        scene.render.filepath=str(image.resolve())
        bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
        bpy.ops.render.render(write_still=True)
        if not image.is_file() or image.stat().st_size<2000:
            raise RuntimeError("actual surface render missing")
        observations.append({"name":name,"input_glb_sha256":digest(source/"creature.glb"),
             "input_glb_bytes":(source/"creature.glb").stat().st_size,
             "vertices":len(obj.data.vertices),"polygons":len(obj.data.polygons),
             "material_slots":len(obj.material_slots),
             "smooth_polygons":sum(p.use_smooth for p in obj.data.polygons),
             "preview_png_sha256":digest(image),"blend_sha256":digest(blend)})
    if observations[0]["preview_png_sha256"]==observations[1]["preview_png_sha256"]:
        raise RuntimeError("surface comparison renders did not change")
    report={"schema":"mgr.forge.native-creature-surface-witness.v1",
            "status":"REAL_BLENDER_FIXED_CAMERA_IMPORT_RENDER_PASS",
            "blender_version":bpy.app.version_string,"renderer":"BLENDER_WORKBENCH",
            "same_original_anatomy_and_intent":True,"observations":observations,
            "camera_location":list(camera.location),"camera_rotation":list(camera.rotation_euler),
            "orthographic_scale":camera.data.ortho_scale,
            "owner_art_accepted":False,"production_rig_accepted":False,
            "limitations":["fixed-camera stylized surface witness, not aesthetic benchmark",
                           "separate overlapping body components are not boolean-unioned",
                           "rig deformation/import proof is separate from this render"]}
    (out/"surface-proof.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("MGR_SURFACE_WITNESS="+json.dumps(report))


if __name__=="__main__":main()
