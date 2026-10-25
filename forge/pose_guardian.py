"""MGR pose acceptance: measurable rig and detachable-part continuity.

This does not infer a person's identity or guarantee realistic deformation.
Snapshots are measured by the Blender bridge from evaluated scene data.
"""

import math


REQUIRED_BONES = (
    "root", "torso", "head", "left_upper_arm", "left_forearm", "left_hand",
    "right_upper_arm", "right_forearm", "right_hand", "left_leg", "right_leg",
)
JOINTS = (
    ("left_upper_arm", "left_forearm"),
    ("left_forearm", "left_hand"),
    ("right_upper_arm", "right_forearm"),
    ("right_forearm", "right_hand"),
)


def validate_pose_frames(frames, *, joint_tolerance_m=0.06, bone_length_tolerance=0.005,
                         minimum_movement_m=0.01):
    """Fail closed for absent parts, detached arm joints, bad lengths or frozen clips.

    ``frames`` is a list of {frame, bones:{name:{head:[x,y,z],tail:[x,y,z]}},
    parts:{name:{vertices:int, weighted_vertices:int, armature_modifier:bool}}}.
    """
    if not isinstance(frames, list) or len(frames) < 2:
        raise ValueError("at least two evaluated pose frames required")
    if not all(math.isfinite(v) and v >= 0 for v in (
            joint_tolerance_m, bone_length_tolerance, minimum_movement_m)):
        raise ValueError("pose QA tolerances must be nonnegative finite values")
    errors = []
    measurements = []
    baseline = {}
    previous_frame = None
    for frame in frames:
        frame_number = frame.get("frame")
        if not isinstance(frame_number, int) or (previous_frame is not None and frame_number <= previous_frame):
            errors.append("frames must have strictly increasing integer frame IDs")
        previous_frame = frame_number
        bones = frame.get("bones", {})
        parts = frame.get("parts", {})
        if not isinstance(bones, dict) or not isinstance(parts, dict):
            errors.append(f"frame {frame_number}: invalid bones/parts map")
            continue
        valid = {}
        for name in REQUIRED_BONES:
            item = bones.get(name, {})
            endpoints = (item.get("head"), item.get("tail")) if isinstance(item, dict) else (None, None)
            if not all(isinstance(p, (list, tuple)) and len(p) == 3 and
                       all(type(v) in (int, float) and math.isfinite(v) for v in p)
                       for p in endpoints):
                errors.append(f"frame {frame_number}: missing/invalid bone {name}")
                continue
            head, tail = endpoints
            length = math.dist(head, tail)
            if length < 1e-5:
                errors.append(f"frame {frame_number}: degenerate bone {name}")
            if name in baseline and abs(length - baseline[name]) > max(1e-5, baseline[name] * bone_length_tolerance):
                errors.append(f"frame {frame_number}: bone length changed {name}")
            baseline.setdefault(name, length)
            valid[name] = (head, tail)
        max_gap = 0.0
        for parent, child in JOINTS:
            if parent in valid and child in valid:
                gap = math.dist(valid[parent][1], valid[child][0])
                max_gap = max(max_gap, gap)
                if gap > joint_tolerance_m:
                    errors.append(f"frame {frame_number}: disconnected joint {parent}->{child} ({gap:.4f} m)")
        if not parts:
            errors.append(f"frame {frame_number}: no skinned mesh parts")
        for name, item in parts.items():
            if not isinstance(item, dict) or item.get("vertices", 0) <= 0 or (
                item.get("weighted_vertices") != item.get("vertices") or
                item.get("armature_modifier") is not True
            ):
                errors.append(f"frame {frame_number}: missing geometry/skin coverage {name}")
            elif item.get("max_weight_sum_error", 0) > .01:
                errors.append(f"frame {frame_number}: skin weights not normalized {name}")
            elif name.endswith("_elbow_sleeve") and item.get("dual_weight_vertices", 0) < 1:
                errors.append(f"frame {frame_number}: elbow sleeve missing mixed bone weights {name}")
        measurements.append({"frame": frame_number, "joint_max_gap_m": round(max_gap, 6),
                             "bone_count": len(valid), "skinned_part_count": len(parts)})
    first_bones = frames[0].get("bones", {})
    last_bones = frames[-1].get("bones", {})
    moved = []
    for name in ("left_hand", "right_hand"):
        a, b = first_bones.get(name, {}), last_bones.get(name, {})
        if isinstance(a, dict) and isinstance(b, dict) and "tail" in a and "tail" in b:
            try:
                moved.append(math.dist(a["tail"], b["tail"]))
            except (TypeError, ValueError):
                pass
    max_movement = max(moved, default=0.0)
    if max_movement < minimum_movement_m:
        errors.append("animation frozen: neither hand passed movement threshold")
    return {"schema": "mgr.forge.pose-guardian.v1", "status": "PASS" if not errors else "FAIL",
            "errors": errors, "frames": measurements,
            "maximum_hand_motion_m": round(max_movement, 6),
            "limitations": ["bone-chain continuity does not verify watertight mesh seams",
                            "most parts use rigid 1.0 single-bone weights; elbow sleeves alone blend two bones",
                            "does not establish human identity or artistic quality"]}
