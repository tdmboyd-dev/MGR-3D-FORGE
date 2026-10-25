"""Pure, measurable checks for worlds and character landmark requirements."""

import math


def validate_neighborhood(world):
    errors = []
    spec = world["spec"]
    lots = set()
    for building in world["buildings"]:
        key = tuple(building["lot"])
        if key in lots:
            errors.append(f"overlapping lot: {key}")
        lots.add(key)
        width, height, depth = building["size"]
        if min(width, height, depth) <= 0 or max(width, depth) >= spec["lot_size"]:
            errors.append(f"invalid building dimensions: {building['id']}")
        if building["entry_road_distance"] <= 0:
            errors.append(f"no road setback: {building['id']}")
    if len(world["buildings"]) != spec["buildings"]:
        errors.append("building count mismatch")
    if len(world["roads"]) != spec["rows"] + spec["columns"] + 2:
        errors.append("road count mismatch")
    return {"passed": not errors, "errors": errors,
            "checks": ["lot uniqueness", "building bounds", "road setback",
                       "building count", "road grid"]}


REQUIRED_LANDMARKS = ("head", "left_shoulder", "right_shoulder", "left_elbow",
                      "right_elbow", "left_wrist", "right_wrist", "left_hand",
                      "right_hand", "left_hip", "right_hip", "left_knee",
                      "right_knee", "left_ankle", "right_ankle")


def validate_character_landmarks(landmarks, *, max_arm_asymmetry=0.15):
    """Early character anatomy gate; not a substitute for rig/visual review."""
    errors = []
    for key in REQUIRED_LANDMARKS:
        point = landmarks.get(key)
        if not isinstance(point, (tuple, list)) or len(point) != 3 or not all(
                type(v) in (int, float) and math.isfinite(v) for v in point):
            errors.append(f"missing or invalid {key}")
    if errors:
        return {"passed": False, "errors": errors}

    def distance(a, b):
        return math.dist(landmarks[a], landmarks[b])
    arms = [distance(f"{side}_shoulder", f"{side}_elbow")
            + distance(f"{side}_elbow", f"{side}_wrist")
            for side in ("left", "right")]
    for side, arm_length in zip(("left", "right"), arms):
        if arm_length <= 0 or distance(f"{side}_wrist", f"{side}_hand") <= 0:
            errors.append(f"degenerate {side} arm/hand")
    if max(arms) and abs(arms[0] - arms[1]) / max(arms) > max_arm_asymmetry:
        errors.append("arm length asymmetry exceeds tolerance")
    return {"passed": not errors, "errors": errors,
            "checks": ["required landmarks", "finite 3D points", "arm lengths", "hand presence"]}


def compare_character_identity(reference, candidate, *, tolerance=0.05):
    """Detect rigid-transform-independent landmark distance drift (not facial ID)."""
    a = validate_character_landmarks(reference)
    b = validate_character_landmarks(candidate)
    if not a["passed"] or not b["passed"]:
        return {"passed": False, "errors": a["errors"] + b["errors"]}
    errors = []
    # Compare distances rather than absolute coordinates so a translated pose
    # doesn't look like a new character. Baseline is rest pose only.
    bones = (("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
             ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
             ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
             ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
             ("left_shoulder", "right_shoulder"), ("left_hip", "right_hip"))
    for start, end in bones:
        expected = math.dist(reference[start], reference[end])
        observed = math.dist(candidate[start], candidate[end])
        if expected <= 0 or abs(observed - expected) > tolerance * expected:
            errors.append(f"proportion drift: {start}->{end}")
    return {"passed": not errors, "errors": errors,
            "checks": ["relative skeletal proportions"]}
