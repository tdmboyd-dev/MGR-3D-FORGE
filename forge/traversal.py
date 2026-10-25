"""MGR World Logic: deterministic ground-route traversal rehearsal.

This is an offline road-centerline agent simulation, not a physics engine,
navmesh bake, obstacle avoidance or playable game runtime.
"""

import math

from .world import overlaps_building, shortest_road_path


def rehearse_road_walk(world, from_building, to_building, *, speed_mps=1.5,
                       sample_seconds=0.25, agent_radius_m=0.3,
                       max_samples=20_000):
    if (not all(type(x) in (float,int) and math.isfinite(x) for x in
                (speed_mps,sample_seconds,agent_radius_m)) or
            speed_mps<=0 or sample_seconds<=0 or agent_radius_m<0):
        raise ValueError("invalid movement parameters")
    route=shortest_road_path(world,from_building,to_building)
    waypoints=route["waypoints"]
    frames=[]
    total_distance=0.0
    for index,(start,end) in enumerate(zip(waypoints,waypoints[1:])):
        length=math.dist(start,end)
        if length==0:
            continue
        count=math.ceil(length/(speed_mps*sample_seconds))
        if count+len(frames)>max_samples:
            raise ValueError("route exceeds sample budget")
        for i in range(count):
            u=i/count
            pos=[round(a+(b-a)*u,5) for a,b in zip(start,end)]
            collisions=overlaps_building(world,*pos,agent_radius_m)
            if collisions:
                raise RuntimeError(f"agent hit building at road segment {index}: {collisions}")
            frames.append({"time_s":round((total_distance+length*u)/speed_mps,4),
                           "position_m":pos,"segment":index})
        total_distance+=length
    final=[round(v,5) for v in waypoints[-1]]
    if overlaps_building(world,*final,agent_radius_m):
        raise RuntimeError("destination road node intersects building")
    frames.append({"time_s":round(total_distance/speed_mps,4),
                   "position_m":final,"segment":max(0,len(waypoints)-2)})
    return {"schema":"mgr.forge.road-traversal.v1",
            "from":from_building,"to":to_building,"distance_m":round(total_distance,4),
            "duration_s":round(total_distance/speed_mps,4),"frames":frames,
            "status":"PASS_OFFLINE_ROAD_GRAPH",
            "limitations":["offline road centerline only, not navmesh validation",
                           "no dynamic obstacle avoidance, stairs or interior doors",
                           "no physics engine or animated avatar tested"]}
