"""Blender: add original facial controls to the CURRENT Forge Human mannequin.

Usage: blender --background --factory-startup --python script -- SOURCE_DIR TIMELINE_DIR OUTPUT_DIR
Original MGR mesh and manually aligned phoneme curves. Not audio inference.
"""
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector

CHANNELS=("jawOpen","mouthWide","mouthFunnel","mouthPucker","mouthSmile",
          "lipsPress","tongueOut","mouthShrug")

def add_mat(name,color,metallic=0.0):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1.0)
    mat.use_nodes=True
    node=mat.node_tree.nodes.get("Principled BSDF")
    if node:
        node.inputs["Base Color"].default_value=(*color,1.0)
        node.inputs["Roughness"].default_value=0.65
        node.inputs["Metallic"].default_value=metallic
    return mat

def sphere(name,location,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,
                                          location=location)
    ob=bpy.context.object
    ob.name=name
    ob.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    return ob

def lip_geometry():
    n=32;vertices=[];faces=[]
    for outer in (True,False):
        for i in range(n):
            a=2*math.pi*i/n
            # The head front faces +Y in Blender's imported glTF frame.
            width=.18 if outer else .115
            height=.039 if outer else .015
            vertices.append((width*math.cos(a),
                             0.19 if outer else 0.193,
                             1.683+height*math.sin(a)))
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new("MGR_Mouth_Ring_Source")
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new("MGR_Human_Mouth_Lips",mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(add_mat("MGR_Lip_Material",(0.48,0.19,0.20)))
    obj.shape_key_add(name="Basis",from_mix=False)
    base=[v.co.copy() for v in obj.data.vertices]
    for channel in CHANNELS:
        key=obj.shape_key_add(name=channel,from_mix=False)
        for idx,co in enumerate(base):
            x,y,z=co.x,co.y,co.z
            dz=z-1.683
            if channel=="jawOpen":
                z+=(-.11 if dz<0 else .018)*(min(1.0,abs(dz)/.038))
            elif channel=="mouthWide":
                x*=1.47
            elif channel=="mouthFunnel":
                x*=.66
                z=1.683+dz*1.33
            elif channel=="mouthPucker":
                x*=.57
                y+=.062
            elif channel=="mouthSmile":
                z+=.055*min(1.0,abs(x)/.17)
            elif channel=="lipsPress":
                z=1.683+dz*.28
            elif channel=="tongueOut":
                z-=.012 if dz<0 else 0
                y+=.008
            elif channel=="mouthShrug":
                z+=.032 if dz>=0 else .012
            key.data[idx].co=(x,y,z)
    return obj

def build_lipsync(source,lines,out):
    if out.exists():raise FileExistsError("Never overwrite owner face/rigger output")
    original=(source/"mannequin.glb").read_bytes()
    spec=json.loads((lines/"lipsync.json").read_text(encoding="utf8"))
    if spec["schema"]!="mgr.forge.viseme-curves.v1":
        raise ValueError("bad authored viseme timeline")
    if tuple(spec["channels"])!=CHANNELS:
        raise ValueError("timeline channel schema does not match face rig")
    out.mkdir(parents=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str((source/"mannequin.glb").resolve()))
    mannequin_meshes=[o for o in bpy.data.objects if o.type=="MESH"]
    if not mannequin_meshes:raise ValueError("Forge Human source model not imported")
    lip=lip_geometry()
    face_skin=add_mat("MGR_Face_Skin",(0.42,0.29,0.23))
    eyes=add_mat("MGR_Eye_Black",(0.015,0.02,0.028))
    whites=add_mat("MGR_Eye_White",(0.92,0.91,0.85))
    brows=add_mat("MGR_Brows",(0.045,0.035,0.032))
    mouth_back=add_mat("MGR_Mouth_Interior",(0.06,0.008,0.01))
    sphere("MGR_Mouth_Interior",(0,.181,1.683),(.115,.005,.017),mouth_back)
    sphere("MGR_Human_Nose",(0,.175,1.725),(.048,.055,.072),face_skin)
    for side,sign in (("Left",-1),("Right",1)):
        sphere("MGR_Human_Eye_White_"+side,(sign*.095,.170,1.765),(.056,.014,.033),whites)
        sphere("MGR_Human_Eye_Pupil_"+side,(sign*.095,.187,1.765),(.024,.012,.025),eyes)
        sphere("MGR_Human_Brow_"+side,(sign*.095,.165,1.833),(.071,.025,.012),brows)
    scene=bpy.context.scene
    scene.render.film_transparent=False
    scene.frame_start=1
    scene.frame_end=max(2,len(spec["frames"]))
    scene.render.fps=spec["fps"]
    for frame in spec["frames"]:
        for channel in CHANNELS:
            shape=lip.data.shape_keys.key_blocks[channel]
            shape.value=frame["weights"][channel]
            shape.keyframe_insert(data_path="value",frame=frame["frame"])
    scene.frame_set(max(2,scene.frame_end//2))
    editable=out/"human-lipsync.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(editable.resolve()))
    bpy.ops.object.select_all(action="DESELECT")
    # Export the imported MGR human plus original face controls with generated timeline.
    for obj in bpy.data.objects:
        if obj.type=="MESH":obj.select_set(True)
    scene.frame_set(1)
    target=out/"human-lipsync.glb"
    bpy.ops.export_scene.gltf(filepath=str(target.resolve()),export_format="GLB",
                              use_selection=True,export_animations=True,
                              export_morph=True,export_morph_normal=True)
    raw=target.read_bytes()
    if len(raw)<10000 or raw[:4]!=b"glTF":
        raise RuntimeError("Blender did not export a real human animation GLB")
    report={"schema":"mgr.forge.human-lipsync-blender.v1",
            "status":"HUMAN_FACE_BLENDSHAPES_CREATED_RECEIVER_PENDING",
            "input_mannequin_sha256":hashlib.sha256(original).hexdigest(),
            "timeline_source_sha256":spec["source_input_sha256"],
            "export_sha256":hashlib.sha256(raw).hexdigest(),
            "export_bytes":len(raw),"blender_version":bpy.app.version_string,
            "morph_shape_keys":list(CHANNELS),
            "morph_key_count":len(CHANNELS),
            "source_mannequin_meshes":len(mannequin_meshes),
            "animation_frames":len(spec["frames"]),
            "audio_alignment_verified":False,"owner_visual_accepted":False,
            "real_human_likeness_verified":False,
            "receiver_independently_reimported":False,
            "quality_notes":["original MGR generic proxy human, not a real identity",
                             "visemes driven by caller-supplied timing, not inferred from audio",
                             "facial topology is a rough 3D proxy, not film-grade"]}
    (out/"lipsync-blender-proof.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("MGR_HUMAN_FACIAL_EXPORT="+json.dumps({"sha":report["export_sha256"],
        "bytes":report["export_bytes"],"keys":report["morph_key_count"]}))

if __name__=="__main__":
    if "--" not in sys.argv:raise ValueError("need source/timeline/out arguments")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=3:raise ValueError("need exactly source, timeline, output")
    build_lipsync(*map(Path,args))
