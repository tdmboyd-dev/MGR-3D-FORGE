"""Independent Blender validation of one true MGR city + biome combined GLB."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
if "--" not in sys.argv:raise ValueError("combined dir needed")
parts=sys.argv[sys.argv.index("--")+1:]
if len(parts)!=1:raise ValueError("one combined dir needed")
root=Path(parts[0])
proof=json.loads((root/"world-composed-proof.json").read_text(encoding="utf8"))
blob=(root/"world-composed.glb").read_bytes()
if hashlib.sha256(blob).hexdigest()!=proof["combined_glb_sha256"]:
    raise ValueError("Composed GLB changed")
bpy.ops.wm.read_factory_settings(use_empty=True)
if "FINISHED" not in bpy.ops.import_scene.gltf(filepath=str((root/"world-composed.glb").resolve())):
    raise RuntimeError("Merged asset could not be imported")
meshes=[obj for obj in bpy.data.objects if obj.type=="MESH"]
city=[obj for obj in meshes if obj.name.startswith("MGR_City_Original_")]
biome=[obj for obj in meshes if obj.name.startswith("MGR_Biome_")]
if not city or not biome:
    raise RuntimeError("Merged GLB does not actually contain BOTH source roles")
city_faces=sum(len(o.data.polygons) for o in city)
biome_faces=sum(len(o.data.polygons) for o in biome)
if city_faces!=proof["original_city_faces"] or biome_faces!=proof["original_biome_faces"]:
    raise RuntimeError("Merged world lost faces from either source")
scene=bpy.context.scene
if scene.world is None:scene.world=bpy.data.worlds.new("MGR World")
scene.world.color=(.2,.22,.27)
cam_data=bpy.data.cameras.new("MGR_World_Composition_Camera")
cam=bpy.data.objects.new("MGR_World_Composition_Camera",cam_data)
scene.collection.objects.link(cam)
bounds=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
center=sum(bounds,Vector())/len(bounds)
size=max(max(p[i] for p in bounds)-min(p[i] for p in bounds) for i in range(3))
cam.location=center+Vector((size*.8,size*.65,size*.95))
cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO";cam.data.ortho_scale=size*1.45
scene.camera=cam
scene.render.engine="BLENDER_WORKBENCH"
scene.render.resolution_x=720;scene.render.resolution_y=480
scene.render.resolution_percentage=100
scene.render.filepath=str((root/"world-composed-preview.png").resolve())
scene.render.image_settings.file_format="PNG"
bpy.ops.render.render(write_still=True)
png=Path(scene.render.filepath)
if png.stat().st_size<1400:raise RuntimeError("Composed world render missing")
# Also reopen the ACTUAL editable .blend in this second independent process.
# A merged GLB import alone would not prove owner editability.
bpy.ops.wm.open_mainfile(filepath=str((root/"world-composed.blend").resolve()))
opened_city=[o for o in bpy.data.objects if o.type=="MESH" and o.name.startswith("MGR_City_Original_")]
opened_biome=[o for o in bpy.data.objects if o.type=="MESH" and o.name.startswith("MGR_Biome_")]
if (sum(len(o.data.polygons) for o in opened_city)!=city_faces or
    sum(len(o.data.polygons) for o in opened_biome)!=biome_faces):
    raise RuntimeError("Editable Blender scene lost city or terrain geometry")
proof.update({"status":"WORLD_COMPOSITION_INDEPENDENT_IMPORT_RENDER_PASS",
 "independent_reopen_verified":True,
 "editable_blend_independently_reopened":True,
 "reopened_city_meshes":len(city),"reopened_biome_meshes":len(biome),
 "reopened_city_faces":city_faces,"reopened_biome_faces":biome_faces,
 "reopened_total_faces":city_faces+biome_faces,
 "preview_sha256":hashlib.sha256(png.read_bytes()).hexdigest()})
(root/"world-composed-proof.json").write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n",encoding="utf8")
print("MGR_WORLD_COMPOSE_REIMPORT="+json.dumps({"city":city_faces,"biome":biome_faces,"preview":proof["preview_sha256"]}))
