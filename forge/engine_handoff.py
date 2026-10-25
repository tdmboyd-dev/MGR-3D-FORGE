"""MGR-owned, deterministic playable-scene handoff for Godot 4.

Exports an importable source project. Its execution in Godot remains a separate
acceptance gate; Forge does not claim an engine run from file existence.
"""

import hashlib
import json
import math
from pathlib import Path
import shutil

from .glb import inspect_glb


def _vec(values):
    return "Vector3(" + ", ".join(format(float(v), ".8g") for v in values) + ")"


def export_godot_project(world, output):
    source, target = Path(world).resolve(), Path(output)
    if target.exists():
        raise FileExistsError("refusing to overwrite existing engine project")
    manifest_path, glb_path = source / "manifest.json", source / "world.glb"
    if not manifest_path.is_file() or not glb_path.is_file():
        raise ValueError("verified MGR world bundle required")
    if manifest_path.stat().st_size > 10_000_000 or glb_path.stat().st_size > 100_000_000:
        raise ValueError("source bundle exceeds validated limits")
    metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
    blob = glb_path.read_bytes()
    fingerprint = hashlib.sha256(blob).hexdigest()
    if metadata.get("artifact", {}).get("sha256") != fingerprint:
        raise ValueError("source GLB fingerprint mismatch")
    quality = inspect_glb(blob)
    buildings = metadata.get("buildings")
    if not isinstance(buildings, list) or len(buildings) > 128:
        raise ValueError("invalid authored building inventory")
    shapes = []
    nodes = []
    unique = set()
    for i, building in enumerate(buildings):
        if not isinstance(building, dict) or not isinstance(building.get("id"), str):
            raise ValueError("invalid building identity")
        identity = building["id"]
        if identity in unique or len(identity) > 100 or not identity or any(c in identity for c in '\\"\r\n'):
            raise ValueError("duplicate or unsafe building ID")
        unique.add(identity)
        center, size = building.get("center"), building.get("size")
        if (not isinstance(center, list) or not isinstance(size, list)
                or len(center) != 3 or len(size) != 3
                or any(type(v) not in (float, int) or not math.isfinite(v) for v in center + size)
                or center[1] != 0 or min(size) < 2 or max(size) > 100):
            raise ValueError("invalid building collision bounds")
        resource_id = f"Shape_{i}"
        shapes.extend([f'[sub_resource type="BoxShape3D" id="{resource_id}"]',
                       f'size = {_vec(size)}', ''])
        position = [center[0], size[1] / 2, center[2]]
        name = f"BuildingCollider_{i:03d}"
        nodes.extend([f'[node name="{name}" type="StaticBody3D" parent="."]',
                      f'position = {_vec(position)}',
                      f'metadata/mgr_id = {json.dumps(identity)}', '',
                      f'[node name="Shape" type="CollisionShape3D" parent="{name}"]',
                      f'shape = SubResource("{resource_id}")', ''])
    # A stable ground collider makes the authored project useful in a basic 3D test.
    grounds = metadata.get("grounds", {})
    width, depth = grounds.get("width"), grounds.get("depth")
    if (type(width) not in (int, float) or type(depth) not in (int, float)
            or not math.isfinite(width) or not math.isfinite(depth)
            or not 1 <= width <= 100000 or not 1 <= depth <= 100000):
        raise ValueError("ground dimensions not validated")
    shapes.extend(['[sub_resource type="BoxShape3D" id="GroundShape"]',
                   f'size = {_vec([width, 0.5, depth])}', ''])
    nodes.extend(['[node name="GroundCollider" type="StaticBody3D" parent="."]',
                  'position = Vector3(0, -0.25, 0)', '',
                  '[node name="Shape" type="CollisionShape3D" parent="GroundCollider"]',
                  'shape = SubResource("GroundShape")', '',
                  '[node name="PreviewCamera" type="Camera3D" parent="."]',
                  f'position = {_vec([0, 80, max(width, depth) * 0.65])}',
                  'rotation_degrees = Vector3(-35, 0, 0)', 'current = true', '',
                  '[node name="Sun" type="DirectionalLight3D" parent="."]',
                  'rotation_degrees = Vector3(-55, -30, 0)', ''])
    scene = ('[gd_scene load_steps=' + str(len(shapes) // 3 + 2) + ' format=3]\n\n'
             '[ext_resource type="PackedScene" path="res://assets/world.glb" id="1_world"]\n\n'
             + '\n'.join(shapes) + '\n[node name="MGRWorld" type="Node3D"]\n\n'
             '[node name="Visual" parent="." instance=ExtResource("1_world")]\n\n'
             + '\n'.join(nodes))
    target.mkdir(parents=True, exist_ok=False)
    (target / "assets").mkdir()
    shutil.copyfile(glb_path, target / "assets" / "world.glb")
    (target / "project.godot").write_text(
        'config_version=5\n\n[application]\nconfig/name="MGR Forge World"\n'
        'run/main_scene="res://world.tscn"\n\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
        encoding="utf-8")
    (target / "world.tscn").write_text(scene, encoding="utf-8")
    result = {"schema": "mgr.forge.engine-handoff.v1", "status": "MATERIALIZED",
              "engine": "Godot 4", "source_glb_sha256": fingerprint,
              "triangles": quality["triangles"], "building_colliders": len(buildings),
              "engine_import_verified": False,
              "files": ["project.godot", "world.tscn", "assets/world.glb"]}
    (target / "handoff.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
