"""MGR Creature DNA -> transform-compatible rig blueprint.

This is an authored skeleton blueprint, not automatic skin weight inference.
It shares the *same* morph field used by generated surface geometry.
"""
import json
import math
from pathlib import Path

from .morph_engine import morph_point, normalize_morph


def creature_leg_landmarks(genome):
    """Share original rest-space attachment/knee/foot points with the mesh.

    These authored landmarks are a prototype anatomy convention, not inferred
    animal anatomy. Both mesh and bones apply the same later morph field.
    """
    legs=genome["legs"]
    length,width,high=(genome[k] for k in ("body_length","body_width","standing_height"))
    if type(legs) is not int or legs not in (0,2,4,8) or any(
            type(v) not in (int,float) or not math.isfinite(v) or v<=0
            for v in (length,width,high)):
        raise ValueError("invalid creature leg anatomy")
    points=[]
    for index in range(legs):
        count=max(legs//2,1)
        row=index//2
        sign=-1 if index%2==0 else 1
        x=-0.38*length+0.76*length*(row/max(count-1,1))
        # At x=+/-.38*length and y=standing_height, .5*width is
        # inside the original torso ellipsoid. The older .79*width root
        # could float outside the body, especially with narrow limb radii.
        points.append(((x,high,width*sign*0.5),
                       (x,high*0.47,width*sign*1.22),
                       (x+(-0.05 if row%2==0 else 0.06),0.04,width*sign*1.46)))
    return points


def creature_preview_bones(skeleton):
    """Choose existing authored bones for a bounded deformation witness."""
    names={bone["name"] for bone in skeleton}
    chosen=[name for name in ("tail_01","tail_02","left_wing_01","right_wing_01") if name in names]
    if not chosen:
        chosen=[bone["name"] for bone in skeleton
                if bone["role"]=="leg" and bone["name"].endswith("_upper")][:2]
    if not chosen and "head" in names:chosen=["head"]
    if not chosen:raise ValueError("no authored bone available for deformation witness")
    return chosen


def creature_bones(genome, *, morph=None, axis_extent=None):
    if not isinstance(genome,dict):
        raise ValueError("genome document required")
    required=("legs","wing_pairs","body_length","body_width","body_height",
              "standing_height","head_scale","tail_length","wing_span")
    if any(key not in genome for key in required):
        raise ValueError("incomplete creature genome")
    length,width,bodyh,high=(genome[k] for k in
                              ("body_length","body_width","body_height","standing_height"))
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0
           for v in (length,width,bodyh,high,genome["head_scale"],
                     genome["wing_span"])):
        raise ValueError("invalid genome anatomy dimensions")
    if type(genome["tail_length"]) not in (int,float) or not math.isfinite(genome["tail_length"]) or genome["tail_length"]<0:
        raise ValueError("invalid genome tail dimension")
    legs,wings=genome["legs"],genome["wing_pairs"]
    if type(legs) is not int or legs not in (0,2,4,8) or type(wings) is not int or wings not in (0,1):
        raise ValueError("unsupported anatomy family")
    cy=high+bodyh*0.4
    hx=length*0.54+0.22*genome["head_scale"]
    hy=cy+bodyh*0.33
    items=[]
    def add(name,parent,head,tail,role):
        if name==parent:
            raise ValueError("circular creature bone")
        items.append({"name":name,"parent":parent,"head":head,
                      "tail":tail,"role":role})
    add("root",None,(0,0,0),(0,high,0),"root")
    add("body","root",(-length*0.35,cy,0),(length*0.35,cy,0),"torso")
    add("neck","body",(length*0.35,cy,0),(hx-0.1,hy,0),"neck")
    add("head","neck",(hx-0.1,hy,0),(hx+0.32*genome["head_scale"],hy,0),"head")
    tail_base=(-length*0.48,cy,0)
    tail_previous=tail_base
    tail_count=3 if genome["tail_length"]>0 else 0
    for i in range(tail_count):
        ratio=(i+1)/tail_count
        end=(-length*0.48-genome["tail_length"]*ratio,
             cy+0.18*math.sin(ratio*math.pi*1.35),
             0.25*math.sin(ratio*math.pi*1.5))
        add(f"tail_{i+1:02}", "body" if i==0 else f"tail_{i:02}",
            tail_previous,end,"tail")
        tail_previous=end
    for index,(upper,knee,foot) in enumerate(creature_leg_landmarks(genome)):
        add(f"leg_{index+1:02}_upper","body",upper,knee,"leg")
        add(f"leg_{index+1:02}_lower",f"leg_{index+1:02}_upper",knee,foot,"leg")
    if wings:
        for side,sign in (("left",-1),("right",1)):
            start=(-length*0.10,cy+0.2,width*sign*0.86)
            joint=(-length*0.35,cy+genome["wing_span"]*0.48,
                   sign*(width+genome["wing_span"]*0.45))
            tip=(-length*0.20,cy+genome["wing_span"]*0.8,
                 sign*(width+genome["wing_span"]))
            add(f"{side}_wing_01","body",start,joint,"wing")
            add(f"{side}_wing_02",f"{side}_wing_01",joint,tip,"wing")
    names={item["name"] for item in items}
    if len(names)!=len(items):
        raise ValueError("duplicate rig bones")
    # Morphed mesh uses the globally shared height extent, not per-submesh extents.
    extent=axis_extent if axis_extent is not None else high+bodyh*1.6
    settings=normalize_morph(morph)
    for b in items:
        if b["parent"] is not None and b["parent"] not in names:
            raise ValueError("missing parent skeleton bone")
        b["head"]=list(morph_point(b["head"],settings,axis_extent=extent))
        b["tail"]=list(morph_point(b["tail"],settings,axis_extent=extent))
        distance=math.dist(b["head"],b["tail"])
        if distance<=0.01 or not math.isfinite(distance):
            raise ValueError("bone collapsed after morph")
    return {"schema":"mgr.forge.creature-rig-blueprint.v1",
            "skeleton":items, "bones":len(items),
            "preview_animation_bones":creature_preview_bones(items),
            "applied_morph":settings, "axis_extent":extent,
            "status":"BLUEPRINT_NOT_SKINNED",
            "deforming_skin_verified":False,
            "animation_ready":False,
            "limitations":["bone template from parametric anatomy, not learned retargeted rig",
                           "weights, joints, motion and physics need independent Blender proof"]}


def save_creature_rig_recipe(creature_json, output):
    source,target=Path(creature_json),Path(output)
    if target.exists():
        raise FileExistsError("refusing to replace rig blueprint")
    if source.stat().st_size>3_000_000:
        raise ValueError("creature manifest oversized")
    doc=json.loads(source.read_text(encoding="utf-8"))
    if doc.get("schema")!="mgr.forge.imagination-creature.v1":
        raise ValueError("not an original creature manifest")
    recipe=creature_bones(doc["selected_genome"],morph=doc.get("applied_morph"),
                          axis_extent=doc.get("morph_axis_extent"))
    recipe["mesh_sha256"]=doc["artifact"]["sha256"]
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(recipe,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return recipe
