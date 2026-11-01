"""Independent Blender reopen/render of real Forge biome, not synthetic test only."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
if "--" not in sys.argv:raise ValueError("output path required")
args=sys.argv[sys.argv.index("--")+1:]
if len(args)!=1:raise ValueError("output path required")
root=Path(args[0])
report=json.loads((root/"biome-proof.json").read_text(encoding="utf8"))
source=root/"biome-editable.blend"
if hashlib.sha256(source.read_bytes()).hexdigest()!=report["saved_blend_sha256"]:
    raise ValueError("biome Blender project changed")
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()))
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
faces=sum(len(o.data.polygons) for o in meshes)
if faces!=report["imported_faces"]:raise RuntimeError("biome triangles did not survive Blender second process")
bounds=[obj.matrix_world@Vector(c) for obj in meshes for c in obj.bound_box]
center=sum(bounds,Vector())/max(len(bounds),1)
extent=max(max(p[k] for p in bounds)-min(p[k] for p in bounds) for k in range(3))
camera_data=bpy.data.cameras.new("MGR_Biome_Camera")
camera=bpy.data.objects.new("MGR_Biome_Camera",camera_data)
bpy.context.scene.collection.objects.link(camera)
camera.location=center+Vector((extent*.75,extent*1.2,extent*1.3))
camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.type="ORTHO";camera.data.ortho_scale=extent*1.3
sc=bpy.context.scene;sc.camera=camera
sc.render.engine="BLENDER_WORKBENCH"
sc.render.resolution_x=640;sc.render.resolution_y=640
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.render.filepath=str((root/"biome-preview.png").resolve())
bpy.ops.render.render(write_still=True)
im=Path(sc.render.filepath)
if im.stat().st_size<1200:raise RuntimeError("independent Blender terrain render missing")
report.update({
 "status":"BLENDER_BIOME_INDEPENDENT_REOPEN_RENDER_PASS",
 "reopened":True,"reopened_faces":faces,"reopened_meshes":len(meshes),
 "preview_sha256":hashlib.sha256(im.read_bytes()).hexdigest(),
 "owner_art_approved":False})
(root/"biome-proof.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print("MGR_BIOME_BLENDER_REOPEN="+json.dumps({"faces":faces,"preview_sha256":report["preview_sha256"]}))
