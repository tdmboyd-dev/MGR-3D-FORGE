"""MGR-native editable world roundtrip: browser JSON -> real, independently inspectable 3D files."""

import hashlib
import json
import math
import re
from pathlib import Path

from .geometry import MATERIALS, Mesh, create_neighborhood
from .glb import export_glb, inspect_glb
from .obj import export_obj
from .preview import render_world_svg
from .receipt import file_receipt
from .spec import WorldSpec
from .web_runtime import make_world_flight


EDITOR_MATERIALS = MATERIALS + (
    ("building-gold", [0.68, 0.48, 0.13, 1]),
    ("building-emerald", [0.12, 0.48, 0.34, 1]),
)
BUILDING_MATERIALS = {name: index for index, (name, _) in enumerate(EDITOR_MATERIALS)
                      if name.startswith("building-")}


def _load_json(path, max_bytes=1_000_000):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > max_bytes:
        raise ValueError("missing or oversized JSON input")
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_edits(document, originals, world_sha, grounds):
    if (not isinstance(document, dict) or set(document) != {"schema", "asset_sha256", "buildings"}
            or document["schema"] != "mgr.forge.world-edit.v1"
            or document["asset_sha256"] != world_sha):
        raise ValueError("editor schema or source world fingerprint mismatch")
    changed = document["buildings"]
    if not isinstance(changed, list) or len(changed) > 128:
        raise ValueError("invalid building count")
    half_width, half_depth = grounds["width"] / 2, grounds["depth"] / 2
    original_by_id = {item["id"]: item for item in originals}
    seen, normalized = set(), []
    for item in changed:
        if (not isinstance(item, dict) or set(item) != {"id", "center", "size", "material"}
                or type(item["id"]) is not str or item["id"] in seen
                or item["material"] not in BUILDING_MATERIALS):
            raise ValueError("building identity/material mismatch")
        seen.add(item["id"])
        base = original_by_id.get(item["id"])
        if base is None and not re.fullmatch(r"mgr-created-[0-9]{4,6}", item["id"]):
            raise ValueError("unrecognized authored building identity")
        center, size = item["center"], item["size"]
        if (not isinstance(center, list) or len(center) != 3
                or not isinstance(size, list) or len(size) != 3
                or any(type(v) not in (int, float) or not math.isfinite(v) for v in center + size)
                or center[1] != 0
                or not 2 <= size[0] <= max(40, base["size"][0] if base else 40)
                or not 2 <= size[2] <= max(40, base["size"][2] if base else 40)
                or abs(center[0]) + size[0] / 2 > half_width
                or abs(center[2]) + size[2] / 2 > half_depth
                or not 2 <= size[1] <= 100):
            raise ValueError("invalid building transform or dimension")
        if base is None:
            normalized.append({"id": item["id"], "center": center[:], "size": size[:],
                               "material": item["material"], "lot": None,
                               "entry_road_distance": None, "origin": "mgr-editor-created"})
        else:
            normalized.append({**base, "center": center[:], "size": size[:], "material": item["material"]})
    return normalized


def apply_world_edits(world_dir, edits_path, output):
    """Verify source and edits, export a fresh world bundle without modifying the original."""
    source = Path(world_dir).resolve()
    target = Path(output)
    if target.exists():
        raise FileExistsError("edited world destination already exists")
    if not source.is_dir() or not (source / "world.glb").is_file():
        raise ValueError("original world directory and GLB required")
    original = _load_json(source / "manifest.json", max_bytes=10_000_000)
    source_blob = (source / "world.glb").read_bytes()
    sha = hashlib.sha256(source_blob).hexdigest()
    if sha != original.get("artifact", {}).get("sha256"):
        raise ValueError("original GLB fingerprint mismatch")
    inspect_glb(source_blob)
    spec = WorldSpec(**original["spec"])
    meshes, reproducible = create_neighborhood(spec)
    if reproducible["buildings"] != original["buildings"]:
        raise ValueError("source geometry does not match deterministic MGR manifest")
    document = _load_json(edits_path)
    changed = _validate_edits(document, reproducible["buildings"], sha, reproducible["grounds"])
    original_by_id = {b["id"]: b for b in reproducible["buildings"]}
    generated = [Mesh() for _ in EDITOR_MATERIALS]
    generated[0], generated[1] = meshes[0], meshes[1]
    for building in changed:
        x, _, z = building["center"]
        width, height, depth = building["size"]
        generated[BUILDING_MATERIALS[building["material"]]].box(x, 0, z, width, height, depth)
        generated[5].box(x, height, z, width + 0.3, 0.3, depth + 0.3)
    manifest = {**reproducible, "buildings": changed,
                "editable_building_count": len(changed),
                "material_count": len(EDITOR_MATERIALS),
                "triangle_count": sum(len(mesh.indices) // 3 for mesh in generated),
                "vertex_count": sum(len(mesh.positions) // 3 for mesh in generated)}
    blob = export_glb(generated, name=spec.name, materials=EDITOR_MATERIALS)
    glb_quality = inspect_glb(blob)
    obj_data, mtl_data = export_obj(generated, materials=EDITOR_MATERIALS)
    target.mkdir(parents=True, exist_ok=False)
    (target / "world.glb").write_bytes(blob)
    (target / "world.obj").write_text(obj_data, encoding="utf-8")
    (target / "world.mtl").write_text(mtl_data, encoding="utf-8")
    (target / "preview.svg").write_text(render_world_svg(manifest), encoding="utf-8")
    manifest["artifact"] = {"path": "world.glb", **file_receipt(target / "world.glb")}
    manifest["glb_quality"] = glb_quality
    manifest["edit_provenance"] = {
        "schema": "mgr.forge.edited-world.v1", "original_glb_sha256": sha,
        "edit_sha256": hashlib.sha256(json.dumps(document, sort_keys=True,
                                                separators=(",", ":")).encode()).hexdigest(),
        "edit_count": sum(original_by_id.get(b["id"]) != b for b in changed)
                      + len({b["id"] for b in reproducible["buildings"]}
                            - {b["id"] for b in changed}),
    }
    manifest["execution"] = {"compute": "CPU", "external_api_calls": 0,
                             "model_inference": False, "blender_verified": False,
                             "independent_engine_import_verified": False}
    manifest["artifact_inventory"] = {name: file_receipt(target / name)
                                      for name in ("world.glb", "world.obj", "world.mtl", "preview.svg")}
    (target / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    viewer = make_world_flight(target, target / "world-editor.html")
    return {"schema": "mgr.forge.edited-world.v1", "status": "MATERIALIZED",
            "output": str(target.resolve()), "changed_buildings": manifest["edit_provenance"]["edit_count"],
            "buildings": len(changed), "triangles": glb_quality["triangles"],
            "glb_sha256": manifest["artifact"]["sha256"], "viewer": viewer["html"]}
