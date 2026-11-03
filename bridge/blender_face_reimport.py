"""Independent Blender receiver for MGR Human Forge authored facial GLB."""
import hashlib,json,struct,sys,math
from pathlib import Path
import bpy
from mathutils import Vector

if "--" not in sys.argv:raise ValueError("needs output path")
args=sys.argv[sys.argv.index("--")+1:]
if len(args)!=1:raise ValueError("needs one output path")
root=Path(args[0]).resolve()
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
fps=proof.get('animation_fps',24)
if type(fps) is not int or not 12<=fps<=60:raise ValueError('invalid authored animation fps')
bpy.context.scene.render.fps=fps
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
count=proof['animation_frames']
if type(count) is not int or not 2<=count<=7202:raise ValueError('invalid authored animation frame budget')
ranges={name:[float('inf'),-float('inf')] for name in proof['morph_shape_keys']}
base=[mouth.matrix_world@vertex.co for vertex in mouth.data.vertices]
reference=None;motion=0.;shape_response=0.;sampled={}
for frame in range(1,count+1):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    for name,limits in ranges.items():
        value=mouth.data.shape_keys.key_blocks[name].value
        if not math.isfinite(value):raise RuntimeError('receiving facial keys contain nonfinite values')
        limits[0]=min(limits[0],value);limits[1]=max(limits[1],value)
    if frame in (1,max(2,count//2),count):sampled[frame]=mouth.data.shape_keys.key_blocks['jawOpen'].value
    evaluated=mouth.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    try:points=[evaluated.matrix_world@vertex.co for vertex in mesh.vertices]
    finally:evaluated.to_mesh_clear()
    if len(points)!=len(base) or not points:raise RuntimeError('receiving facial vertex correspondence changed')
    if reference is None:reference=points
    for p,q,b in zip(points,reference,base):
        delta=(p-q).length;response=(p-b).length
        if not math.isfinite(delta+response):raise RuntimeError('receiving facial geometry contains nonfinite values')
        motion=max(motion,delta);shape_response=max(shape_response,response)
if any(high-low>1e-4 for low,high in ranges.values()) and motion<=1e-6:
    raise RuntimeError('receiving animated facial keys failed to deform imported vertices')
scene.frame_set(max(2,count//2))
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
   "actual_imported_key_samples":{"first":sampled[1],"middle":sampled[max(2,count//2)],"last":sampled[count]},
   "receiver_animation_fps":fps,"receiver_evaluated_frames":count,
   "receiver_evaluated_vertices":len(base),"receiver_evaluated_geometry_verified":True,
   "receiver_shape_key_ranges":ranges,"receiver_max_vertex_motion_m":motion,
   "receiver_max_shape_response_m":shape_response,
   "render_sha256":hashlib.sha256(img.read_bytes()).hexdigest(),
   "owner_visual_accepted":False})
proof_path.write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n")
print("MGR_FACE_REIMPORT="+json.dumps({"shapes":len(names),"targets":targets,
        "actions":len(bpy.data.actions),"render_sha256":proof["render_sha256"]}))
