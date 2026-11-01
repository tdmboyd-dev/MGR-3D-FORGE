"""Real Blender import/editable .blend for optional MGR World Forge biome layer."""
import bpy,hashlib,json,sys
from pathlib import Path
if "--" not in sys.argv:raise ValueError("biome directory required")
args=sys.argv[sys.argv.index("--")+1:]
if len(args)!=1:raise ValueError("biome directory required")
root=Path(args[0])
source=root/"biome.glb"
meta=json.loads((root/"biome.json").read_text(encoding="utf8"))
data=source.read_bytes()
if hashlib.sha256(data).hexdigest()!=meta["artifact"]["sha256"]:
    raise ValueError("biome geometry changed")
bpy.ops.wm.read_factory_settings(use_empty=True)
if bpy.ops.import_scene.gltf(filepath=str(source.resolve()))!={"FINISHED"}:
    raise RuntimeError("Blender biome import failed")
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
faces=sum(len(o.data.polygons) for o in meshes)
if faces<100 or not meshes:raise RuntimeError("biome mesh invalid after import")
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("MGR Biome World")
sc.world.color=(.17,.17,.17)
saved=root/"biome-editable.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(saved.resolve()))
report={
 "schema":"mgr.forge.biome-blender-proof.v1",
 "status":"BLENDER_IMPORT_SAVE_PASS",
 "source_sha256":meta["artifact"]["sha256"],
 "source_biome":meta["biome"],
 "source_world_sha256":meta["source_world_glb_sha256"],
 "blender_version":bpy.app.version_string,
 "imported_meshes":len(meshes),"imported_faces":faces,
 "saved_blend_sha256":hashlib.sha256(saved.read_bytes()).hexdigest(),
 "reopened":False,"owner_art_approved":False,
 "fully_merged_world_and_navmesh":False
}
(root/"biome-proof.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print("MGR_BIOME_BLENDER_IMPORT="+json.dumps(report))
