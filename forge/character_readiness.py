"""Evidence-only character part inventory and rig readiness for admitted GLB models."""

import hashlib
import json
from pathlib import Path

from .character_glb import parse_character_glb


def inventory_character(source):
    path = Path(source)
    if not path.is_file() or path.is_symlink() or path.suffix.lower() != ".glb":
        raise ValueError("ordinary existing source .glb required")
    blob = path.read_bytes()
    doc, geometry = parse_character_glb(blob)
    meshes, nodes, skins = doc["meshes"], doc.get("nodes", []), doc.get("skins", [])
    if len(nodes) > 10000 or len(skins) > 128:
        raise ValueError("character hierarchy exceeds bounded audit limits")
    for node in nodes:
        index = node.get("mesh")
        if index is not None and (type(index) is not int or not 0 <= index < len(meshes)):
            raise ValueError("node references nonexistent mesh")
    materials = doc.get("materials", [])
    parts = []
    for index, mesh in enumerate(meshes):
        uses = [n for n, node in enumerate(nodes) if node.get("mesh") == index]
        primitive_infos = []
        for primitive in mesh["primitives"]:
            mat_id = primitive.get("material")
            if mat_id is not None and (type(mat_id) is not int or not 0 <= mat_id < len(materials)):
                raise ValueError("primitive references nonexistent material")
            attrs = primitive["attributes"]
            primitive_infos.append({
                "vertices": doc["accessors"][attrs["POSITION"]]["count"],
                "material": materials[mat_id].get("name", f"Material {mat_id}") if mat_id is not None else None,
                "has_uv": "TEXCOORD_0" in attrs,
                "has_joint_weights": "JOINTS_0" in attrs and "WEIGHTS_0" in attrs,
                "incomplete_joint_weights": ("JOINTS_0" in attrs) != ("WEIGHTS_0" in attrs),
                "morph_targets": len(primitive.get("targets", [])),
            })
        parts.append({"mesh_index": index, "name": mesh.get("name", f"Mesh {index}"),
                      "node_instances": uses, "primitives": primitive_infos,
                      "independently_named_mesh": len(meshes) > 1})
    rig_issues = []
    for i, skin in enumerate(skins):
        joints = skin.get("joints", [])
        if not joints or len(joints) != len(set(joints)):
            rig_issues.append(f"skin {i}: empty or duplicate joints")
        if any(type(j) is not int or j < 0 or j >= len(nodes) for j in joints):
            rig_issues.append(f"skin {i}: out-of-range joint node")
        if "inverseBindMatrices" in skin:
            idx = skin["inverseBindMatrices"]
            if type(idx) is not int or not 0 <= idx < len(doc["accessors"]):
                rig_issues.append(f"skin {i}: invalid inverse-bind accessor")
            else:
                accessor = doc["accessors"][idx]
                if (accessor["type"] != "MAT4" or accessor["componentType"] != 5126
                        or accessor["count"] < len(joints)):
                    rig_issues.append(f"skin {i}: inverse-bind matrices mismatch")
    for i, node in enumerate(nodes):
        skin_index = node.get("skin")
        if skin_index is not None:
            if type(skin_index) is not int or not 0 <= skin_index < len(skins) or "mesh" not in node:
                rig_issues.append(f"node {i}: invalid skin binding")
            elif not all(p["has_joint_weights"] for p in parts[node["mesh"]]["primitives"]):
                rig_issues.append(f"node {i}: skinned mesh missing joint weights")
    if not skins:
        rig_issues.append("no skin data; model cannot be called deforming-rig ready")
    elif not any(node.get("skin") is not None for node in nodes):
        rig_issues.append("skin declared but not bound to mesh node")
    if any(p["incomplete_joint_weights"] for part in parts for p in part["primitives"]):
        rig_issues.append("JOINTS_0 and WEIGHTS_0 must be paired")
    return {
        "schema": "mgr.forge.character-readiness.v1", "source_sha256": hashlib.sha256(blob).hexdigest(),
        "geometry": geometry, "parts": parts, "skins": len(skins),
        "joint_references": sum(len(s.get("joints", [])) for s in skins),
        "rig_structure": "STRUCTURALLY_PLAUSIBLE" if not rig_issues else "NOT_READY",
        "rig_issues": rig_issues,
        "garments_semantically_verified": False, "hair_semantically_verified": False,
        "hands_anatomically_verified": False, "pose_deformation_verified": False,
        "owner_approved_identity": False,
        "notes": ["Mesh names/materials are inventory hints, not proof of body-part identity.",
                  "A structurally plausible skin does not prove pose or deformation quality."],
    }


def write_character_readiness(source, output):
    target = Path(output)
    if target.suffix.lower() != ".json" or target.exists():
        raise ValueError("new JSON report path required; overwrite refused")
    result = inventory_character(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return result
