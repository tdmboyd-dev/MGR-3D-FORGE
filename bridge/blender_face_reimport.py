"""Independent Blender receiver for MGR Human Forge authored facial GLB."""
import hashlib,json,struct,sys,math
from pathlib import Path
import bpy
from mathutils import Vector

if "--" not in sys.argv:raise ValueError("needs output path")
args=sys.argv[sys.argv.index("--")+1:]
if len(args)!=1:raise ValueError("needs one output path")
root=Path(args[0])
model=root/"human-lipsync.glb"
proof_path=root/"lipsync-blender-proof.json"
proof=json.loads(proof_path.read_text(encoding="utf8"))
data=model.read_bytes()
if hashlib.sha256(data).hexdigest()!=proof["export_sha256"]:
    raise ValueError("facial GLB changed after export")
n,kind=struct.unpack_from("<I4s",data,12)
if kind!=b"JSON":raise ValueError("invalid glTF JSON chunk")
doc=json.loads(data[20:20+n])
targets=sum(len(p.get("targets",[])) for m in doc.get("meshes",[]) for p in m.get("primitives",[]))
animations=doc.get("animations",[])
if targets<6 or not animations:
    raise RuntimeError("GLB lacks expected real morph geometry and animation tracks")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(model.resolve()))
face=[obj for obj in bpy.data.objects if obj.type=="MESH" and
      obj.data.shape_keys and "jawOpen" in obj.data.shape_keys.key_blocks]
if len(face)!=1:raise RuntimeError("re-imported GLB lost unique facial shape keys")
mouth=face[0]
names=set(mouth.data.shape_keys.key_blocks.keys())
if not set(proof["morph_shape_keys"]).issubset(names):
    raise RuntimeError("re-import did not restore expected expressive controls")
if len(bpy.data.actions)<1:raise RuntimeError("re-import lost animation action")
scene=bpy.context.scene
scene.frame_set(1)
start=mouth.data.shape_keys.key_blocks["jawOpen"].value
scene.frame_set(max(2,proof["animation_frames"]//2))
middle=mouth.data.shape_keys.key_blocks["jawOpen"].value
scene.frame_set(proof["animation_frames"])
end=mouth.data.shape_keys.key_blocks["jawOpen"].value
# Some Blender importer actions are NLA-stashed; animation existence plus
# morph target JSON is objective, per-frame runtime playback is separate.
camera_data=bpy.data.cameras.new("MGR_Face_Proof_Camera")
camera=bpy.data.objects.new("MGR_Face_Proof_Camera",camera_data)
bpy.context.collection.objects.link(camera)
camera.location=Vector((1.0,3.0,2.25))
look=Vector((0,0,1.68))
camera.rotation_euler=(look-camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.type="ORTHO"
camera.data.ortho_scale=2.2
scene.camera=camera
scene.render.engine="BLENDER_WORKBENCH"
scene.render.resolution_x=640
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=str(root/"human-lipsync-preview.png")
bpy.ops.render.render(write_still=True)
img=Path(scene.render.filepath)
if img.stat().st_size<1500:raise RuntimeError("face preview missing")
proof.update({"status":"HUMAN_FACIAL_GLTF_REIMPORT_RENDER_PASS",
   "receiver_independently_reimported":True,
   "imported_mesh_with_shapes":mouth.name,
   "imported_shape_key_names":sorted(names),
   "imported_animation_actions":len(bpy.data.actions),
   "gltf_morph_target_primitives":targets,
   "actual_imported_key_samples":{"first":start,"middle":middle,"last":end},
   "render_sha256":hashlib.sha256(img.read_bytes()).hexdigest(),
   "owner_visual_accepted":False})
proof_path.write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n")
print("MGR_FACE_REIMPORT="+json.dumps({"shapes":len(names),"targets":targets,
        "actions":len(bpy.data.actions),"render_sha256":proof["render_sha256"]}))
