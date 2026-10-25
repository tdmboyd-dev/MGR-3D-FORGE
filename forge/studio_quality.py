"""Ten bounded MGR-native studio-quality *measurement primitives*.

These are independently executable contracts, not film-quality shading,
cloth physics, photogrammetry, a live game renderer, or a semantic AI judge.
Their scopes and missing real-world acceptance are explicit in every receipt.
"""

import hashlib
import json
import math

from .spatial_truth import camera_project
from .streaming import plan_chunk_residency
from .surface_truth import inspect_surface_edges


def _finite(number):
    return type(number) in (int,float) and math.isfinite(number)


def _xyz(value):
    return isinstance(value,(tuple,list)) and len(value)==3 and all(_finite(v) for v in value)


def material_reality_witness(materials):
    """Check authoring parameters; this does NOT measure a real BRDF."""
    if not isinstance(materials,list) or not 1<=len(materials)<=10_000:
        raise ValueError("bounded material list required")
    rejected=[]
    for i,mat in enumerate(materials):
        if not isinstance(mat,dict):
            raise ValueError("material dictionary required")
        color=mat.get("base_color")
        valid=_xyz(color) and all(0<=x<=1 for x in color)
        valid=valid and all(_finite(mat.get(k)) and 0<=mat[k]<=1 for k in ("metallic","roughness"))
        if not valid:
            rejected.append(i)
    return {"schema":"mgr.forge.material-witness.v1", "status":"PASS" if not rejected else "FAIL",
            "materials":len(materials),"invalid_material_indices":rejected,
            "limitations":["bounded PBR authoring parameters only; no measured BRDF, UV, energy or render proof"]}


def adaptive_light_orchestra(lights, camera_xyz, *, max_active=8):
    """Deterministically plan light budgets by inverse-distance importance."""
    if not _xyz(camera_xyz) or type(max_active) is not int or not 1<=max_active<=1_000:
        raise ValueError("finite camera and bounded light budget required")
    if not isinstance(lights,list) or len(lights)>100_000:
        raise ValueError("bounded light list required")
    ranked=[]
    seen=set()
    for light in lights:
        if not isinstance(light,dict) or not isinstance(light.get("id"),str) or not light["id"]:
            raise ValueError("light ID required")
        if light["id"] in seen or not _xyz(light.get("position")):
            raise ValueError("duplicate light or invalid position")
        energy=light.get("energy")
        if not _finite(energy) or energy<0:
            raise ValueError("nonnegative finite light energy required")
        seen.add(light["id"])
        distance=math.dist(camera_xyz,light["position"])
        score=energy/(1+distance*distance)
        ranked.append(((-score),light["id"]))
    ranked.sort()
    ids=[name for _,name in ranked]
    return {"schema":"mgr.forge.light-budget.v1","active":ids[:max_active],
            "deferred":ids[max_active:],"status":"PLAN_ONLY",
            "limitations":["distance-and-energy heuristic; no shadow visibility, luminance or photometric calibration",
                           "scheduler does not execute renderer lights"]}


def flesh_translucence_witness(thicknesses_m, absorption_per_m):
    """Lambert-Beer slab reference for volumetric light transmission."""
    if not isinstance(thicknesses_m,(tuple,list)) or not 1<=len(thicknesses_m)<=100_000:
        raise ValueError("bounded thickness samples required")
    if not _finite(absorption_per_m) or not 0<=absorption_per_m<=1e6:
        raise ValueError("finite nonnegative absorption required")
    if any(not _finite(t) or not 0<=t<=1e6 for t in thicknesses_m):
        raise ValueError("finite nonnegative thicknesses required")
    values=[math.exp(-absorption_per_m*t) for t in thicknesses_m]
    return {"schema":"mgr.forge.translucence-reference.v1","status":"PASS",
            "transmission":values,"limitations":["homogeneous absorption only; no multiple scattering, skin layers or RGB spectral fit"]}


def surface_anatomy_guardian(mesh):
    """Named studio QA adapter over edge topology; not a sculpt judgement."""
    receipt=inspect_surface_edges(mesh)
    return {"schema":"mgr.forge.surface-anatomy.v1","status":receipt["status"],
            "edge_audit":receipt,"limitations":["no anatomy, UV, subdivision, self-intersection or skinned-deformation checks"]}


def living_hair_director(frames, *, max_root_travel_m=0.2, max_segment_stretch_ratio=0.15):
    """Detect root teleport/stretch in a known strand track, not simulate hair."""
    if not isinstance(frames,list) or not 2<=len(frames)<=10_000:
        raise ValueError("at least two bounded strand frames required")
    if not all(_finite(t) and t>=0 for t in (max_root_travel_m,max_segment_stretch_ratio)):
        raise ValueError("finite nonnegative hair tolerances required")
    count=None
    for frame in frames:
        if not isinstance(frame,list) or not 2<=len(frame)<=10_000 or not all(_xyz(p) for p in frame):
            raise ValueError("valid strand frame with two or more XYZ points required")
        if count is None: count=len(frame)
        if len(frame)!=count: raise ValueError("stable strand topology required")
    if len(frames)*count>1_000_000:
        raise ValueError("strand track exceeds bounded point budget")
    base=[math.dist(a,b) for a,b in zip(frames[0],frames[0][1:])]
    violations=[]
    for i,frame in enumerate(frames[1:],1):
        if math.dist(frames[i-1][0],frame[0])>max_root_travel_m:
            violations.append({"frame":i,"reason":"root jump"})
        for segment,(a,b) in enumerate(zip(frame,frame[1:])):
            current=math.dist(a,b)
            if base[segment]<1e-9 or abs(current-base[segment])>base[segment]*max_segment_stretch_ratio:
                violations.append({"frame":i,"segment":segment,"reason":"segment stretch/zero length"})
    return {"schema":"mgr.forge.hair-track.v1","status":"PASS" if not violations else "FAIL",
            "violations":violations,"limitations":["known strand points only; no collisions, aerodynamic forces or hair shading"]}


def layered_world_dna(base_objects, overlays):
    """Pure, fail-closed ID-based scene revisions; no silent object creation."""
    if not isinstance(base_objects,dict) or not isinstance(overlays,list) or len(overlays)>100_000:
        raise ValueError("bounded scene/overlay structures required")
    if len(base_objects)>100_000 or not all(isinstance(k,str) and isinstance(v,dict) for k,v in base_objects.items()):
        raise ValueError("stable keyed scene objects required")
    current={k:dict(v) for k,v in base_objects.items()}
    for patch in overlays:
        if not isinstance(patch,dict) or patch.get("id") not in current or patch.get("operation")!="set":
            raise ValueError("only explicit updates of existing owned IDs allowed")
        values=patch.get("properties")
        if not isinstance(values,dict) or any(key in ("id","owner") for key in values):
            raise ValueError("only ordinary editable properties may be overlaid")
        current[patch["id"]].update(values)
    canonical=json.dumps(current,sort_keys=True,separators=(",",":"),allow_nan=False)
    return {"schema":"mgr.forge.layered-world.v1","status":"PASS","objects":current,
            "scene_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
            "limitations":["in-memory deterministic composition; not USD layer composition or concurrent DB transactions"]}


def horizon_truth_streaming(chunks, camera_xyz, **budget):
    """Engine-neutral wrapper: no claim that assets actually streamed."""
    receipt=plan_chunk_residency(chunks,camera_xyz,**budget)
    return {"schema":"mgr.forge.horizon-truth.v1","residency":receipt,
            "status":"PLAN_ONLY","limitations":["actual GPU residency, colliders and FPS require live runtime"]}


def visual_surface_reconciler(reference_pixels, candidate_pixels, *, max_displacement_px=2):
    """Compare corresponded projected silhouette landmarks, NOT texture pixels."""
    if not _finite(max_displacement_px) or max_displacement_px<0:
        raise ValueError("finite nonnegative pixel tolerance required")
    if not isinstance(reference_pixels,dict) or not isinstance(candidate_pixels,dict) or not reference_pixels or set(reference_pixels)!=set(candidate_pixels):
        raise ValueError("matched nonempty landmark IDs required")
    deviations={}
    for name,point in reference_pixels.items():
        other=candidate_pixels[name]
        if not isinstance(name,str) or not isinstance(point,(tuple,list)) or not isinstance(other,(tuple,list)) or len(point)!=2 or len(other)!=2 or not all(_finite(x) for x in (*point,*other)):
            raise ValueError("finite XY landmark coordinates required")
        deviations[name]=round(math.dist(point,other),6)
    bad=[name for name,delta in deviations.items() if delta>max_displacement_px]
    return {"schema":"mgr.forge.lod-silhouette.v1","status":"PASS" if not bad else "FAIL",
            "deviations_px":deviations,"violating_landmarks":bad,
            "limitations":["requires externally established landmark correspondence; not a renderer or LOD pop-in simulation"]}


def cross_view_reality_judge(world_landmarks, camera_views, *, required_landmarks=("head","left_hand","right_hand"), max_reprojection_px=3):
    """Validate annotated 3D landmarks across calibrated camera views.

    A missing hand, changed camera pose or mismatch fails. A passing reprojection
    proves only supplied landmarks, not face identity or occluded surface shape.
    """
    if not isinstance(world_landmarks,dict) or not isinstance(camera_views,list) or not 1<=len(camera_views)<=1000:
        raise ValueError("bounded landmark model and camera observations required")
    if not isinstance(required_landmarks,(tuple,list)) or not 1<=len(required_landmarks)<=500 or not all(isinstance(v,str) for v in required_landmarks):
        raise ValueError("nonempty bounded required landmark IDs")
    if not _finite(max_reprojection_px) or max_reprojection_px<0:
        raise ValueError("finite nonnegative reprojection tolerance required")
    if any(name not in world_landmarks or not _xyz(world_landmarks[name]) for name in required_landmarks):
        raise ValueError("required anatomy landmarks missing from 3D model")
    failures=[]
    for index,view in enumerate(camera_views):
        if not isinstance(view,dict) or not _xyz(view.get("position")):
            raise ValueError("finite camera pose required")
        rotation=view.get("camera_to_world")
        if not isinstance(rotation,(tuple,list)) or len(rotation)!=3 or not all(_xyz(row) for row in rotation):
            raise ValueError("3x3 camera rotation required")
        for i in range(3):
            for j in range(3):
                dot=sum(rotation[i][k]*rotation[j][k] for k in range(3))
                if abs(dot-(1 if i==j else 0))>1e-5:
                    raise ValueError("orthonormal camera orientation required")
        cross=(rotation[0][1]*rotation[1][2]-rotation[0][2]*rotation[1][1],rotation[0][2]*rotation[1][0]-rotation[0][0]*rotation[1][2],rotation[0][0]*rotation[1][1]-rotation[0][1]*rotation[1][0])
        if abs(sum(cross[i]*rotation[2][i] for i in range(3))-1)>1e-5:
            raise ValueError("right-handed orientation required")
        observed=view.get("observed")
        if not isinstance(observed,dict): raise ValueError("annotated observations required")
        for name in required_landmarks:
            if name not in observed or not isinstance(observed[name],(tuple,list)) or len(observed[name])!=2 or not all(_finite(v) for v in observed[name]):
                failures.append({"view":index,"landmark":name,"reason":"missing/unusable 2D annotation"})
                continue
            xyz=tuple(world_landmarks[name][i]-view["position"][i] for i in range(3))
            local=tuple(sum(rotation[i][j]*xyz[i] for i in range(3)) for j in range(3))
            if local[2]<=0:
                failures.append({"view":index,"landmark":name,"reason":"behind camera / occluded not certified"})
                continue
            projected=camera_project(local,focal_px=view.get("focal_px"),center_px=view.get("center_px",(0,0)))
            if math.dist(projected,observed[name])>max_reprojection_px:
                failures.append({"view":index,"landmark":name,"reason":"reprojection mismatch"})
    return {"schema":"mgr.forge.cross-view-truth.v1","status":"PASS" if not failures else "FAIL",
            "views":len(camera_views),"failures":failures,
            "limitations":["requires measured cameras and annotated corresponding landmarks",
                           "no face identity, hidden-surface proof or semantic image recognition"]}


def atmosphere_memory(field_frames, *, max_temporal_delta=0.05):
    """Detect abrupt density-cache changes for fixed indexed 3D samples."""
    if not _finite(max_temporal_delta) or not 0<=max_temporal_delta<=1:
        raise ValueError("finite density jump threshold required")
    if not isinstance(field_frames,list) or not 2<=len(field_frames)<=10_000:
        raise ValueError("bounded temporal field required")
    count=None
    for frame in field_frames:
        if not isinstance(frame,(tuple,list)) or not 1<=len(frame)<=100_000 or any(not _finite(v) or not 0<=v<=1 for v in frame):
            raise ValueError("bounded normalized densities required")
        if count is None: count=len(frame)
        if count!=len(frame): raise ValueError("stable sample locations required")
    if len(field_frames)*count>1_000_000:
        raise ValueError("temporal field exceeds bounded sample budget")
    jumps=[]
    for index,(prior,next_frame) in enumerate(zip(field_frames,field_frames[1:]),1):
        diff=max(abs(a-b) for a,b in zip(prior,next_frame))
        if diff>max_temporal_delta:
            jumps.append({"frame":index,"max_density_delta":round(diff,6)})
    return {"schema":"mgr.forge.atmosphere-memory.v1","status":"PASS" if not jumps else "FAIL",
            "unexpected_jumps":jumps,
            "limitations":["fixed sample locations only; intended changes must be segmented",
                           "no ray-marched volume or scattering/temporal render proof"]}
