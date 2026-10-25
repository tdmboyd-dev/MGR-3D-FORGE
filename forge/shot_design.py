"""MGR Cinematic Director contract for portable, reproducible world shots."""

import math


def validate_shot_reel(reel, *, max_shots=5000):
    if not isinstance(reel, dict) or not isinstance(reel.get("shots"), list):
        raise ValueError("camera reel missing shots")
    shots=reel["shots"]
    if not 1 <= len(shots) <= max_shots:
        raise ValueError("camera reel empty or too large")
    seen=set()
    for shot in shots:
        if not isinstance(shot, dict) or not isinstance(shot.get("id"), str) or not shot["id"] or shot["id"] in seen:
            raise ValueError("shot IDs must be present and unique")
        seen.add(shot["id"])
        for field in ("camera", "look_at"):
            value=shot.get(field)
            if not isinstance(value, list) or len(value)!=3 or not all(
                type(v) in (int,float) and math.isfinite(v) for v in value):
                raise ValueError(f"invalid shot {field}")
        if "camera_end" in shot:
            end=shot["camera_end"]
            if (shot.get("movement")!="smooth-dolly" or not isinstance(end,list) or len(end)!=3
                or not all(type(v) in (int,float) and math.isfinite(v) for v in end)):
                raise ValueError("invalid directed shot movement")
            if math.dist(shot["camera"],end)<.01:
                raise ValueError("directed dolly must move")
        if math.dist(shot["camera"],shot["look_at"]) < .01:
            raise ValueError("camera cannot occupy target position")
        seconds=shot.get("hold_seconds")
        if type(seconds) not in (int,float) or not math.isfinite(seconds) or not .05<=seconds<=60:
            raise ValueError("invalid shot duration")
    return {"schema":"mgr.forge.shot-plan-qa.v1", "status":"PASS", "shots":len(shots),
            "duration_seconds":round(sum(s["hold_seconds"] for s in shots),4)}


def lighting_recipe(*, mood="daylight"):
    recipes={
        "daylight":{"sun_strength":2.0,"sun_color":[1.0,.94,.84],"ambient_strength":.5,"exposure":0},
        "golden-hour":{"sun_strength":1.5,"sun_color":[1.0,.64,.39],"ambient_strength":.35,"exposure":.2},
        "moonlit":{"sun_strength":.25,"sun_color":[.38,.53,1.0],"ambient_strength":.16,"exposure":-.6},
    }
    if mood not in recipes:
        raise ValueError("unsupported lighting mood")
    return {"schema":"mgr.forge.lighting.v1","mood":mood,**recipes[mood]}


def validate_camera_clearance(world, reel, *, overhead_clearance=2.0):
    """Conservative camera-center AABB test against all authored buildings."""
    validate_shot_reel(reel)
    errors=[]
    for shot in reel["shots"]:
        start=shot["camera"]
        end=shot.get("camera_end",start)
        for t in (0,.25,.5,.75,1):
            x,y,z=(a+(b-a)*t for a,b in zip(start,end))
            for building in world.get("buildings",[]):
                bx,by,bz=building["center"]
                width,height,depth=building["size"]
                if (abs(x-bx) <= width/2 + .25 and
                    abs(z-bz) <= depth/2 + .25 and
                    by-.25 <= y <= by+height+overhead_clearance):
                    errors.append(f"camera for {shot['id']} intersects {building['id']} along motion")
                    break
    return {"schema":"mgr.forge.camera-clearance.v1",
            "status":"PASS" if not errors else "FAIL","errors":errors}
