"""MGR material recipes: portable, CPU-authored physically-based parameters.

No third-party texture downloads and no claim of photorealism. These are
editable base-color/metallic/roughness recipes for standard glTF materials.
"""

import math


MGR_MATERIAL_PRESETS = {
    "weathered-brick": {"base_color": [0.53, .22, .16, 1], "metallic": 0, "roughness": .9},
    "matte-stone": {"base_color": [.55, .54, .51, 1], "metallic": 0, "roughness": .84},
    "painted-metal": {"base_color": [.12, .31, .48, 1], "metallic": .67, "roughness": .36},
    "leather": {"base_color": [.11, .072, .045, 1], "metallic": 0, "roughness": .58},
    "fabric": {"base_color": [.14, .18, .24, 1], "metallic": 0, "roughness": .94},
    "gold": {"base_color": [.78, .58, .19, 1], "metallic": .95, "roughness": .22},
    "asphalt": {"base_color": [.105, .11, .14, 1], "metallic": 0, "roughness": .95},
}


def validate_pbr_recipe(recipe):
    """Return a GLB-compatible material contract or reject invalid values."""
    if not isinstance(recipe, dict):
        raise ValueError("material recipe must be an object")
    color = recipe.get("base_color")
    if not isinstance(color, (list, tuple)) or len(color) != 4:
        raise ValueError("PBR base color requires RGBA")
    for key, values in (("base_color", color),
                        ("metallic", (recipe.get("metallic"),)),
                        ("roughness", (recipe.get("roughness"),))):
        if not all(type(value) in (int, float) and math.isfinite(value) and
                   0 <= value <= 1 for value in values):
            raise ValueError(f"PBR {key} components must be finite in [0,1]")
    return {"baseColorFactor": list(color), "metallicFactor": recipe["metallic"],
            "roughnessFactor": recipe["roughness"]}


def make_material(name, preset):
    if not isinstance(name, str) or not name.strip() or len(name) > 100:
        raise ValueError("material name must be 1..100 visible characters")
    profile = MGR_MATERIAL_PRESETS[preset]
    return {"name": name, "doubleSided": False,
            "pbrMetallicRoughness": validate_pbr_recipe(profile)}
