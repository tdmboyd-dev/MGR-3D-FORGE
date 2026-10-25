"""Bone-length-preserving procedural arm posing and animation metadata."""

import math

from .character import mannequin
from .quality import compare_character_identity, validate_character_landmarks


BONES=(
    ("left_shoulder","left_elbow"),("left_elbow","left_wrist"),
    ("left_wrist","left_hand"),("right_shoulder","right_elbow"),
    ("right_elbow","right_wrist"),("right_wrist","right_hand"),
    ("left_hip","left_knee"),("left_knee","left_ankle"),
    ("right_hip","right_knee"),("right_knee","right_ankle"),
)


def pose_landmarks(phase):
    """A pose angle from T(0) to A(1); preserves procedural segment lengths."""
    if not isinstance(phase,(float,int)) or not math.isfinite(phase) or not 0<=phase<=1:
        raise ValueError("phase must be 0..1")
    _,points,_=mannequin("T")
    angle=math.radians(35)*phase
    for side,sign in (("left",-1),("right",1)):
        for name,length in (("elbow",0.33),("wrist",0.59),("hand",0.71)):
            points[f"{side}_{name}"]=[sign*(0.28+length*math.cos(angle)),
                                      round(1.47-length*math.sin(angle),8),0]
    return points


def arm_pose_clip(samples=9):
    if type(samples) is not int or not 2<=samples<=121:
        raise ValueError("samples must be 2..121")
    reference=pose_landmarks(0)
    frames=[]
    for i in range(samples):
        t=i/(samples-1)
        # T -> A -> T wave, editable landmarks for future rig binding.
        phase=1-abs(2*t-1)
        landmarks=pose_landmarks(phase)
        checks=compare_character_identity(reference,landmarks,tolerance=0.001)
        if not validate_character_landmarks(landmarks)["passed"] or not checks["passed"]:
            raise RuntimeError(f"pose continuity failed at frame {i}")
        frames.append({"frame":i,"time_seconds":round(2*t,5),
                       "landmarks":landmarks})
    return {"schema":"mgr.forge.pose-track.v1", "fps_hint":24,
            "samples":samples,"frames":frames,"bones":list(BONES),
            "weight_painting_verified":False,"skinned_animation_exported":False,
            "note":"kinematic pose landmarks, not a rigged deforming mesh"}
