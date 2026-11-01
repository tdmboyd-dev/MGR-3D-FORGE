"""MGR World Forge: merge original authored city + verified native terrain in Blender.

This edits a COPY of the original materialized city. Leaves original source
GLB, buildings, and immutable biome untouched. No geometry invented by AI.
"""
import hashlib,json,sys
from pathlib import Path
import bpy

if "--" not in sys.argv:raise ValueError("world, biome, new output required")
args=sys.argv[sys.argv.index("--")+1:]
if len(args)!=3:raise ValueError("world, biome, output")
source,biome,out=map(Path,args)
out.mkdir(parents=True,exist_ok=False)
raw_world=(source/"world.glb").read_bytes()
raw_terrain=(biome/"biome.glb").read_bytes()
original=json.loads((source/"manifest.json").read_text(encoding="utf8"))
terrain=json.loads((biome/"biome.json").read_text(encoding="utf8"))
source_sha=hashlib.sha256(raw_world).hexdigest()
terrain_sha=hashlib.sha256(raw_terrain).hexdigest()
if source_sha!=original["artifact"]["sha256"] or source_sha!=terrain["source_world_glb_sha256"]:
    raise ValueError("terrain does not belong to exact source city")
if terrain_sha!=terrain["artifact"]["sha256"]:
    raise ValueError("altered biome source")
bpy.ops.wm.read_factory_settings(use_empty=True)
result=bpy.ops.import_scene.gltf(filepath=str((source/"world.glb").resolve()))
if "FINISHED" not in result:raise RuntimeError("city GLB failed Blender import")
city=[obj for obj in bpy.data.objects if obj.type=="MESH"]
if not city:raise RuntimeError("source city imported no model")
city_faces=sum(len(obj.data.polygons) for obj in city)
for i,obj in enumerate(city):
    obj.name=f"MGR_City_Original_{i:03}"
result=bpy.ops.import_scene.gltf(filepath=str((biome/"biome.glb").resolve()))
if "FINISHED" not in result:raise RuntimeError("biome GLB failed Blender import")
meshes=[obj for obj in bpy.data.objects if obj.type=="MESH"]
terrain_models=[obj for obj in meshes if obj not in city]
if not terrain_models:raise RuntimeError("no generated terrain in scene")
biome_faces=sum(len(obj.data.polygons) for obj in terrain_models)
if biome_faces<50:raise ValueError("terrain is unexpectedly empty")
for i,obj in enumerate(terrain_models):
    obj.name=f"MGR_Biome_{terrain['biome']}_{i:03}"
scene=bpy.context.scene
scene.frame_start=1;scene.frame_end=2
bpy.ops.wm.save_as_mainfile(filepath=str((out/"world-composed.blend").resolve()))
# Export both geometry groups. No extra objects, duplicate world copies or hidden
# arbitrary linked files. Keep material definitions imported from the original.
bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:obj.select_set(True)
merged=out/"world-composed.glb"
bpy.ops.export_scene.gltf(filepath=str(merged.resolve()),export_format="GLB",
    use_selection=True,export_animations=False)
merged_sha=hashlib.sha256(merged.read_bytes()).hexdigest()
proof={
 "schema":"mgr.forge.composed-world-blender.v1",
 "status":"COMPOSED_IN_BLENDER_RECEIVER_PENDING",
 "source_world_sha256":source_sha,"source_biome_sha256":terrain_sha,
 "combined_glb_sha256":merged_sha,"combined_bytes":merged.stat().st_size,
 "original_city_faces":city_faces,"original_biome_faces":biome_faces,
 "combined_faces":city_faces+biome_faces,
 "city_mesh_count":len(city),"biome_mesh_count":len(terrain_models),
 "blender_version":bpy.app.version_string,
 "source_city_immutable":True,"source_biome_immutable":True,
 "runtime_collision_navmesh_merged":False,"independent_reopen_verified":False,
 "game_engine_play_verified":False,"owner_art_approved":False,
 "external_neural_models":False}
(out/"world-composed-proof.json").write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n",encoding="utf8")
print("MGR_WORLD_COMPOSE="+json.dumps({"sha":merged_sha,"faces":proof["combined_faces"]}))
