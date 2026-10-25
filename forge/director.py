"""MGR Director: shots, cuts, holds and smooth camera moves in authored 3D.

This is a deterministic timeline contract, not generative filmmaking judgment.
"""

import math

from .shot_design import validate_shot_reel


def compile_director_reel(reel, *, fps=24, transition="cut"):
    validate_shot_reel(reel)
    if type(fps) is not int or not 1<=fps<=120:
        raise ValueError("frame rate out of range")
    if transition not in ("cut","smooth-dolly"):
        raise ValueError("unsupported motion direction")
    timeline=[]
    start=1
    for shot in reel["shots"]:
        duration=max(2,round(shot["hold_seconds"]*fps))
        end=start+duration-1
        timeline.append({"shot_id":shot["id"],"subject_id":shot.get("subject_id"),
                         "start_frame":start,"end_frame":end,
                         "camera":list(shot["camera"]),
                         "look_at":list(shot["look_at"]),
                         "focal_length_mm":50 if transition=="cut" else 35,
                         "motion":transition,
                         "fps":fps})
        start=end+1
    return {"schema":"mgr.forge.director-reel.v1","fps":fps,
            "frame_start":1,"frame_end":start-1,"shots":timeline,
            "source":"authored 3D world coordinates", "uses_paid_video_api":False}


def ease_fraction(t, *, mode="smoothstep"):
    """Continuous non-overshooting easing for camera and object position."""
    if type(t) not in (int,float) or not math.isfinite(t) or not 0<=t<=1:
        raise ValueError("motion time must be finite in [0,1]")
    if mode=="linear":
        return t
    if mode=="smoothstep":
        return t*t*(3-2*t)
    if mode=="smootherstep":
        return t*t*t*(t*(6*t-15)+10)
    raise ValueError("unknown easing function")


def sample_motion(start,end,*,samples=9,mode="smootherstep"):
    if not isinstance(start,(list,tuple)) or not isinstance(end,(list,tuple)) or len(start)!=3 or len(end)!=3 or not all(
        type(value) in (int,float) and math.isfinite(value) for value in (*start,*end)):
        raise ValueError("motion endpoints must be finite 3D points")
    if type(samples) is not int or not 2<=samples<=1001:
        raise ValueError("motion sample count invalid")
    points=[]
    for i in range(samples):
        t=ease_fraction(i/(samples-1),mode=mode)
        points.append([round(a+(b-a)*t,6) for a,b in zip(start,end)])
    return {"schema":"mgr.forge.motion-track.v1", "interpolation":mode,
            "samples":points,"endpoints_preserved":points[0]==list(start) and points[-1]==list(end)}
