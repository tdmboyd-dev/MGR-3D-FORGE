"""MGR-owned deterministic scene composition, independent of any vendor runtime.

This is a small CPU authoring contract, not a USD implementation or a renderer.
Layers may define objects by stable paths, and stronger layers may override
specific object fields while retaining source receipts.
"""

from copy import deepcopy
import hashlib
import json
import math


_ALLOWED_FIELDS = {"kind", "transform", "material", "asset", "visible", "metadata"}
_MAX_LAYERS = 128
_MAX_OBJECTS = 100_000


def _validate_value(value, depth=0):
    if depth > 12:
        raise ValueError("scene value nesting exceeds limit")
    if value is None or isinstance(value, (str, bool)):
        return
    if type(value) in (int, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite scene value")
        return
    if isinstance(value, list):
        if len(value) > 512:
            raise ValueError("scene array exceeds limit")
        for item in value:
            _validate_value(item, depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > 512 or not all(isinstance(k, str) for k in value):
            raise ValueError("invalid scene object")
        for item in value.values():
            _validate_value(item, depth + 1)
        return
    raise ValueError("unsupported scene value")


def compose_scene_layers(layers):
    """Compose weak-to-strong layers; return immutable-by-convention JSON data.

    Layers: {id: nonempty string, objects: {absolute/path: {known field: value}}}.
    A null object tombstones a weaker object. A reintroduction requires a valid
    new object. Field values replace (not deeply merge) earlier values.
    """
    if not isinstance(layers, list) or not 1 <= len(layers) <= _MAX_LAYERS:
        raise ValueError("bounded nonempty layer list required")
    objects = {}
    sources = {}
    layer_ids = set()
    for layer in layers:
        if not isinstance(layer, dict) or set(layer) != {"id", "objects"}:
            raise ValueError("layer must contain id and objects only")
        layer_id = layer["id"]
        if not isinstance(layer_id, str) or not layer_id or layer_id in layer_ids:
            raise ValueError("unique nonempty layer ID required")
        layer_ids.add(layer_id)
        entries = layer["objects"]
        if not isinstance(entries, dict) or len(entries) > _MAX_OBJECTS:
            raise ValueError("invalid object map")
        for path, fields in sorted(entries.items()):
            if (not isinstance(path, str) or not path.startswith("/")
                    or "//" in path or path.endswith("/") or any(part in (".", "..") for part in path.split("/"))):
                raise ValueError("absolute normalized object paths required")
            if fields is None:
                objects.pop(path, None)
                sources.pop(path, None)
                continue
            if not isinstance(fields, dict) or not fields or not set(fields) <= _ALLOWED_FIELDS:
                raise ValueError("object requires supported fields")
            _validate_value(fields)
            if "visible" in fields and type(fields["visible"]) is not bool:
                raise ValueError("visible must be boolean")
            if "transform" in fields:
                transform = fields["transform"]
                if (not isinstance(transform, list) or len(transform) != 16
                        or not all(type(v) in (float, int) and math.isfinite(v) for v in transform)):
                    raise ValueError("transform must be finite 4x4 matrix")
            if "kind" in fields and (not isinstance(fields["kind"], str) or not fields["kind"]):
                raise ValueError("kind must be named")
            if path not in objects and "kind" not in fields:
                raise ValueError("new object requires kind")
            objects.setdefault(path, {}).update(deepcopy(fields))
            sources.setdefault(path, {}).update({field: layer_id for field in fields})
            if len(objects) > _MAX_OBJECTS:
                raise ValueError("composed scene exceeds object cap")
    stable = {"objects": {p: objects[p] for p in sorted(objects)}}
    canonical = json.dumps(stable, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {"schema": "mgr.forge.layered-scene.v1", "objects": stable["objects"],
            "field_sources": {p: sources[p] for p in sorted(sources)},
            "layer_ids": [layer["id"] for layer in layers],
            "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "status": "CPU_COMPOSITION_ONLY",
            "limitations": ["no USD parser or authored USD export", "no external renderer or game engine import proof",
                            "no animation time sampling, instance arcs, variants or shader network resolution"]}
