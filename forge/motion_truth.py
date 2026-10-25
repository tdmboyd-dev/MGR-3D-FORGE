"""MGR Continuous Motion Guardian: bounded, sampled 3D kinematics.

Measured finite differences test *sampled* trajectories. They do not prove
physical realism, smooth behavior between samples, or a solved dynamics model.
"""

import math


def judge_motion_samples(samples, *, max_speed_mps=12.0,
                         max_acceleration_mps2=30.0, max_samples=100_000):
    for limit in (max_speed_mps,max_acceleration_mps2):
        if type(limit) not in (int,float) or not math.isfinite(limit) or limit<=0:
            raise ValueError("positive finite kinematic limits required")
    if type(max_samples) is not int or not 3<=max_samples<=100_000:
        raise ValueError("bounded motion sample allowance required")
    if len(samples)<3 or len(samples)>max_samples:
        raise ValueError("need 3 or more bounded motion samples")
    previous_time=None
    checked=[]
    for item in samples:
        if len(item)!=2:
            raise ValueError("each sample requires time and XYZ")
        time,position=item
        if type(time) not in (int,float) or not math.isfinite(time) or len(position)!=3 or not all(
            type(v) in (int,float) and math.isfinite(v) for v in position):
            raise ValueError("finite sampled time and XYZ required")
        if previous_time is not None and time<=previous_time:
            raise ValueError("sample timestamps must increase strictly")
        checked.append((time,tuple(position)))
        previous_time=time
    velocities=[]
    for first,second in zip(checked,checked[1:]):
        dt=second[0]-first[0]
        if not math.isfinite(dt) or dt<=0:
            raise ValueError("motion time delta is not representable")
        components=tuple((second[1][axis]-first[1][axis])/dt for axis in range(3))
        if not all(math.isfinite(v) for v in components):
            raise ValueError("motion velocity overflow")
        velocities.append((components,dt))
    speeds=[math.hypot(*vel) for vel,dt in velocities]
    if not all(math.isfinite(value) for value in speeds):
        raise ValueError("motion speed overflow")
    accelerations=[]
    for earlier,later in zip(velocities,velocities[1:]):
        dt=(earlier[1]+later[1])/2
        delta=tuple((later[0][axis]-earlier[0][axis])/dt for axis in range(3))
        if not all(math.isfinite(v) for v in delta):
            raise ValueError("motion acceleration overflow")
        accelerations.append(math.hypot(*delta))
    violations=[]
    for index,speed in enumerate(speeds):
        if speed>max_speed_mps:
            violations.append({"kind":"speed","segment":index,"measured":round(speed,6)})
    if not all(math.isfinite(value) for value in accelerations):
        raise ValueError("motion acceleration magnitude overflow")
    for index,acceleration in enumerate(accelerations):
        if acceleration>max_acceleration_mps2:
            violations.append({"kind":"acceleration","junction":index+1,
                               "measured":round(acceleration,6)})
    return {"schema":"mgr.forge.motion-guardian.v1",
            "status":"PASS" if not violations else "FAIL",
            "samples":len(samples),"max_measured_speed_mps":round(max(speeds),6),
            "max_measured_acceleration_mps2":round(max(accelerations),6),
            "limits":{"speed_mps":max_speed_mps,"acceleration_mps2":max_acceleration_mps2},
            "violations":violations,
            "limitations":["finite sampled track only; cannot certify between-sample motion",
                           "cinematic cuts and teleport events need explicit segmentation",
                           "not a rigid-body, cloth or fluid physics solver"]}
