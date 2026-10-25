"""Provisional modular mannequin proving full-frame hands and detachable parts.

NOT a scan, generated likeness, likeness-approved Tevin, or production rig.
"""

import json
import math
from hashlib import sha256
from pathlib import Path

from .geometry import Mesh
from .glb import export_glb, inspect_glb
from .quality import validate_character_landmarks
from .materials import MGR_MATERIAL_PRESETS
from .wardrobe import wardrobe_inventory


CHARACTER_PBR={3:MGR_MATERIAL_PRESETS["fabric"],
               4:MGR_MATERIAL_PRESETS["fabric"],
               5:MGR_MATERIAL_PRESETS["leather"],
               6:MGR_MATERIAL_PRESETS["gold"]}


CHARACTER_MATERIALS = (
    ("skin-placeholder", [0.36,0.22,0.15,1]),
    ("hair-placeholder", [0.06,0.05,0.05,1]),
    ("undershirt", [0.73,0.73,0.71,1]),
    ("coat", [0.09,0.12,0.15,1]),
    ("pants", [0.13,0.17,0.21,1]),
    ("boots", [0.08,0.07,0.07,1]),
    ("chain", [0.72,0.55,0.17,1]),
)


def mannequin(pose="T"):
    if pose not in ("T", "A"):
        raise ValueError("pose must be T or A")
    parts = {}
    def add(name, material, action, *args):
        mesh = Mesh()
        getattr(mesh, action)(*args)
        parts[name] = (material,mesh)
    landmarks = {"head":[0,1.72,0],
                 "left_shoulder":[-0.28,1.47,0],
                 "right_shoulder":[0.28,1.47,0],
                 "left_hip":[-0.15,0.92,0],"right_hip":[0.15,0.92,0],
                 "left_knee":[-0.15,0.52,0],"right_knee":[0.15,0.52,0],
                 "left_ankle":[-0.15,0.12,0],"right_ankle":[0.15,0.12,0]}
    for side, sign in (("left",-1),("right",1)):
        shoulder = landmarks[f"{side}_shoulder"]
        angle = math.radians(35) if pose=="A" else 0.0
        def arm_point(length):
            return [sign*(0.28+length*math.cos(angle)),
                    round(1.47-length*math.sin(angle),8),0]
        elbow = arm_point(0.33)
        wrist = arm_point(0.59)
        hand = arm_point(0.71)
        for key,point in (("elbow",elbow),("wrist",wrist),("hand",hand)):
            landmarks[f"{side}_{key}"]=point
        add(f"{side}_upper_arm",0,"beam",shoulder,elbow,0.16)
        add(f"{side}_forearm",0,"beam",elbow,wrist,0.12)
        add(f"{side}_hand",0,"beam",wrist,hand,0.11)
        # Short independent fabric bridge around the elbow. Blender applies
        # TWO bone influences to this piece rather than rigidly following one.
        sleeve_start=[elbow[i] + (shoulder[i]-elbow[i])*.26 for i in range(3)]
        sleeve_end=[elbow[i] + (wrist[i]-elbow[i])*.26 for i in range(3)]
        add(f"{side}_elbow_sleeve",3,"beam",sleeve_start,sleeve_end,0.20)
        add(f"{side}_leg",4,"beam",landmarks[f"{side}_hip"],
            landmarks[f"{side}_ankle"],0.22)
        # Detachable garment deliberately remains separate from the body mesh.
        # This is a boxy trousers proxy, not simulated cloth or fitted Tevin wear.
        add(f"{side}_pant_leg",4,"beam",landmarks[f"{side}_hip"],
            [sign*0.15,0.18,0],0.255)
        add(f"{side}_boot",5,"box",sign*0.15,0.0,-0.05,0.26,0.16,0.39)
    add("head",0,"box",0,1.58,0,0.26,0.28,0.25)
    add("hair",1,"box",0,1.84,0,0.27,0.08,0.26)
    add("torso",0,"box",0,0.92,0,0.56,0.60,0.31)
    add("shirt",2,"box",0,0.99,0,0.59,0.57,0.34)
    # Separate coat side panels intentionally reveal the shirt without
    # overlapping near-coplanar chest surfaces (avoids workbench z-fighting).
    coat=Mesh()
    coat.box(-0.245,0.91,-0.025,0.15,0.74,0.40)
    coat.box(0.245,0.91,-0.025,0.15,0.74,0.40)
    parts["coat"]=(3,coat)
    chain = Mesh()
    chain.beam((-0.16,1.44,-0.24),(0,1.31,-0.25),0.022)
    chain.beam((0,1.31,-0.25),(0.16,1.44,-0.24),0.022)
    parts["chain"]=(6,chain)
    quality=validate_character_landmarks(landmarks)
    if not quality["passed"]:
        raise RuntimeError(f"invalid procedural character anatomy: {quality['errors']}")
    return parts,landmarks,quality


def _assemble(parts):
    meshes=[Mesh() for _ in CHARACTER_MATERIALS]
    for _,(material,source) in sorted(parts.items()):
        target=meshes[material]
        offset=len(target.positions)//3
        target.positions.extend(source.positions)
        target.normals.extend(source.normals)
        target.indices.extend(index+offset for index in source.indices)
    return meshes


def build_mannequin(output,pose="T"):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    parts,landmarks,quality=mannequin(pose)
    payload=export_glb(_assemble(parts), name=f"MGR Anonymous {pose}-pose",
                       materials=CHARACTER_MATERIALS,pbr_overrides=CHARACTER_PBR)
    # The same neutral template is the identity anchor for both procedural
    # poses. It proves template lineage, NOT an owner's real-world likeness.
    rest_parts,_,_=mannequin("T")
    neutral_payload=export_glb(_assemble(rest_parts),name="MGR Anonymous Neutral Template",
                               materials=CHARACTER_MATERIALS,pbr_overrides=CHARACTER_PBR)
    rest_hash=sha256(neutral_payload).hexdigest()
    (output/"mannequin.glb").write_bytes(payload)
    part_dir=output/"parts"
    part_dir.mkdir(exist_ok=True)
    for name, material_mesh in sorted(parts.items()):
        partial=_assemble({name:material_mesh})
        (part_dir/f"{name}.glb").write_bytes(export_glb(
            partial,name=name,materials=CHARACTER_MATERIALS,pbr_overrides=CHARACTER_PBR))
    manifest={"schema":"mgr.forge.character-proxy.v1", "pose":pose,
              "owner_approved":False,"tevin_identity_verified":False,
              "asset_view":{"asset_id":"mgr-anonymous-mannequin-v1",
                            "canonical_asset_sha256":rest_hash,
                            "rest_mesh_sha256":rest_hash,
                            "pose_id":pose,"camera_id":None},
              "editable_parts":sorted(parts),"landmarks":landmarks,
              "quality":quality,"glb_quality":inspect_glb(payload),
              "status":"generic procedural mannequin, not likeness/rig verified"}
    (output/"character.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    wardrobe=wardrobe_inventory(manifest)
    if wardrobe["status"]!="PASS":
        raise RuntimeError(f"missing detachable garment: {wardrobe['errors']}")
    (output/"wardrobe.json").write_text(json.dumps(wardrobe,indent=2,sort_keys=True)+"\n")
    # Import here: animation reuses mannequin's T pose as its rest skeleton.
    from .animation import arm_pose_clip
    (output/"pose_track.json").write_text(
        json.dumps(arm_pose_clip(),indent=2,sort_keys=True)+"\n")
    return manifest
