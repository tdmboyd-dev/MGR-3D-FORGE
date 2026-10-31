"""MGR native procedural imagination: new mesh geometry, not preset-kit selection.

Honesty boundary: bounded rule-driven prototype; neither trained AI imagination
nor anatomically accurate sculpture. No remote provider, API charge or weights.
"""
import hashlib
import json
import math
from pathlib import Path
import random
import re

from .geometry import Mesh
from .glb import export_glb, inspect_glb
from .meshqa import analyze_mesh
from .morph_engine import morph_mesh,normalize_morph

PALETTES = (
    ((0.13, 0.20, 0.31, 1), (0.37, 0.55, 0.59, 1)),
    ((0.29, 0.13, 0.09, 1), (0.62, 0.43, 0.20, 1)),
    ((0.19, 0.32, 0.22, 1), (0.65, 0.72, 0.40, 1)),
    ((0.44, 0.11, 0.34, 1), (0.77, 0.43, 0.68, 1)),
    ((0.21, 0.18, 0.40, 1), (0.68, 0.68, 0.87, 1)),
    ((0.38, 0.36, 0.29, 1), (0.75, 0.76, 0.64, 1)),
)
MATERIAL_NAMES=("body", "belly", "horns-and-claws", "eyes", "wings")
FEATURE_TOKENS={
    "winged": ("wing", "wings", "winged", "flying", "flight", "dragon", "bird", "sky"),
    "horned": ("horn", "horns", "horned", "antler", "antlers", "demon", "dragon", "unicorn"),
    "long_tailed": ("tail", "tailed", "serpent", "dragon", "reptile"),
    "aquatic": ("water", "aquatic", "ocean", "sea", "fish", "underwater"),
    "armored": ("armor", "armored", "crystal", "stone", "rock", "metal", "robot"),
    "spider": ("spider", "arachnid", "eight"),
    "serpent": ("snake", "serpent", "worm"),
    "biped": ("two", "biped", "humanoid", "person", "bird", "human"),
    "colossal": ("giant", "colossal", "massive", "huge"),
}


def _validate(prompt, seed, variants):
    if not isinstance(prompt, str) or not 8 <= len(prompt.strip()) <= 500 or any(
            ord(ch) < 32 and ch not in "\t\n" for ch in prompt):
        raise ValueError("creature prompt needs 8..500 printable characters")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("seed must be an unsigned 32-bit integer")
    if type(variants) is not int or not 1 <= variants <= 12:
        raise ValueError("variants must be between 1 and 12")


def _meaning(prompt):
    tokens=set(re.findall(r"[a-z]+",prompt.lower()))
    return {key for key, words in FEATURE_TOKENS.items() if tokens.intersection(words)}


def _triangle(mesh, p, q, r):
    u=tuple(q[i]-p[i] for i in range(3))
    v=tuple(r[i]-p[i] for i in range(3))
    n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    length=math.sqrt(sum(x*x for x in n))
    if length<=1e-8:
        raise ValueError("degenerate procedural surface")
    base=len(mesh.positions)//3
    for vertex in (p,q,r):
        mesh.positions.extend(vertex)
        mesh.normals.extend(x/length for x in n)
    mesh.indices.extend((base,base+1,base+2))


def _ellipsoid(mesh, center, radii, *, steps=12, rings=8):
    if min(radii)<=0:
        raise ValueError("ellipsoid radii must be positive")
    cx,cy,cz=center
    def p(lat, angle):
        return (cx+radii[0]*math.cos(lat)*math.cos(angle),
                cy+radii[1]*math.sin(lat),
                cz+radii[2]*math.cos(lat)*math.sin(angle))
    # Latitude increments exclude poles; pole triangles seal the manifold.
    layers=[-math.pi/2+math.pi*i/rings for i in range(1,rings)]
    bottom=(cx,cy-radii[1],cz)
    top=(cx,cy+radii[1],cz)
    for j in range(steps):
        th=2*math.pi*j/steps
        nxt=2*math.pi*(j+1)/steps
        _triangle(mesh,bottom,p(layers[0],nxt),p(layers[0],th))
        for low,high in zip(layers,layers[1:]):
            mesh.quad(p(low,th),p(high,th),p(high,nxt),p(low,nxt))
        _triangle(mesh,top,p(layers[-1],th),p(layers[-1],nxt))


def _append_beam(mesh, start, finish, thickness):
    mesh.beam(start,finish,thickness)


def _wing(mesh, root, length, sign, span):
    x,y,z=root
    # Two thin-sided fins form the silhouette, double-facing the winding.
    tip=(x-0.20*length,y+0.8*length,z+sign*span)
    back=(x-0.85*length,y+0.15*length,z+sign*span*0.45)
    front=(x+0.42*length,y+0.30*length,z+sign*span*0.35)
    for a,b,c in ((root,front,tip),(root,tip,back)):
        _triangle(mesh,a,b,c)
        _triangle(mesh,c,b,a)


def genome_candidates(prompt, seed=42, variants=6):
    """Invent parametrized anatomy using prompt traits + reproducible mutations."""
    _validate(prompt,seed,variants)
    features=_meaning(prompt)
    choices=[]
    for i in range(variants):
        digest=hashlib.sha256(f"{seed}|{i}|{prompt.strip().casefold()}".encode()).digest()
        rng=random.Random(int.from_bytes(digest[:8],"big"))
        legs=8 if "spider" in features else 0 if "serpent" in features else 2 if "biped" in features else 4
        has_wings=("winged" in features or (i>0 and rng.random()<0.22))
        horn_count=(rng.choice([2,4,6]) if "horned" in features else rng.choice([0,0,2,2,4]))
        length=round(rng.uniform(1.7,3.1),3)
        body_width=round(rng.uniform(0.30,0.60),3)
        body_height=round(rng.uniform(0.44,0.85),3)
        height=round(rng.uniform(1.4,2.15)*(1.65 if "colossal" in features else 1),3)
        tail=round(length*rng.uniform(0.45,1.20),3) if "long_tailed" in features else round(length*rng.uniform(0.25,0.9),3)
        palette=rng.randrange(len(PALETTES))
        genome={"id":f"variant-{i+1:02d}", "seed":int.from_bytes(digest[:8],"big"),
                "legs":legs,"wing_pairs":int(has_wings),"horn_count":horn_count,
                "body_length":length,"body_width":body_width,"body_height":body_height,
                "standing_height":height,"tail_length":tail,
                "wing_span":round(rng.uniform(1.2,2.6),3),
                "head_scale":round(rng.uniform(0.72,1.3),3),
                "eye_scale":round(rng.uniform(0.8,1.35),3),
                "armor_ridges":rng.randint(3,10) if "armored" in features else rng.randint(0,4),
                "palette_index":palette, "meaning_tags":sorted(features)}
        choices.append(genome)
    return choices


def creature_meshes(genome):
    """Return original triangle geometry; emits real volume and thin membranes."""
    materials=[Mesh() for _ in MATERIAL_NAMES]
    length=genome["body_length"]
    width=genome["body_width"]
    body_h=genome["body_height"]
    high=genome["standing_height"]
    cy=high+body_h*0.4
    _ellipsoid(materials[0],(0,cy,0),(length*0.54,body_h,width))
    head=genome["head_scale"]
    hx=length*0.54+0.22*head
    hy=cy+body_h*0.33
    _ellipsoid(materials[0],(hx,hy,0),(0.36*head,0.42*head,0.33*head))
    _ellipsoid(materials[1],(length*0.22,cy-body_h*0.45,0),
               (length*0.26,body_h*0.24,width*0.85))
    legs=genome["legs"]
    for j in range(legs):
        # Body attachment is morph-derived, not a library part.
        count=max(legs//2,1)
        row=j//2
        side=-1 if j%2==0 else 1
        x=(-0.38*length+(0.76*length*(row/max(count-1,1))))
        root=(x,high,width*side*0.79)
        foot=(x+(-0.05 if row%2==0 else 0.06),0.04,width*side*1.46)
        _append_beam(materials[0],root,foot,0.14*head)
        _ellipsoid(materials[2],foot,(0.23,0.08,0.17))
    tail_steps=max(2,int(genome["tail_length"]*2))
    previous=(-0.48*length,cy,0)
    for j in range(tail_steps):
        ratio=(j+1)/tail_steps
        point=(-length*0.48-genome["tail_length"]*ratio,
               cy+0.18*math.sin(ratio*math.pi*1.35),
               0.25*math.sin(ratio*math.pi*1.5))
        _append_beam(materials[0],previous,point,
                     max(0.07,0.23*(1-ratio*0.7)))
        previous=point
    for i in range(genome["horn_count"]):
        side=-1 if i%2==0 else 1
        row=i//2
        root=(hx-0.08-row*0.12,hy+0.29*head,side*0.18*head)
        tip=(root[0]-0.13,root[1]+0.24+row*0.10,root[2]+side*0.17)
        _append_beam(materials[2],root,tip,0.07)
    for side in (-1,1):
        _ellipsoid(materials[3],(hx+0.24*head,hy+0.04,side*0.27*head),
                   (0.045*genome["eye_scale"],0.07*genome["eye_scale"],0.029))
        if genome["wing_pairs"]:
            _wing(materials[4],(-length*0.10,cy+0.2,width*side*0.86),
                  genome["wing_span"],side,genome["wing_span"])
    if genome["armor_ridges"]:
        for j in range(genome["armor_ridges"]):
            x=(-length*0.30+j*(length*0.6/max(genome["armor_ridges"]-1,1)))
            _append_beam(materials[2],(x,cy+body_h*0.95,0),
                         (x-0.10,cy+body_h*1.23,0),0.08)
    return materials


def _score(genome, meshes):
    audits=[analyze_mesh(m) for m in meshes if m.indices]
    clean=all(v["passed"] for v in audits)
    triangles=sum(v["triangles"] for v in audits)
    # This is a deterministic production heuristic, NOT a proven creativity score.
    complexity=genome["legs"]+genome["horn_count"]+2*genome["wing_pairs"]
    score=round(0.65+min(0.20,complexity*0.008)+min(0.10,genome["armor_ridges"]*0.006)
                -max(0,triangles-40000)/100000,5)
    return {"mesh_healthy":clean,"triangles":triangles,
            "design_complexity_heuristic":score,
            "heuristic_not_external_novelty_proof":True}


def create_original_creature(prompt, output, *, seed=42, variants=6, morph=None):
    """Generate and rank bounded new shapes without downloading any pack/AI weights."""
    genomes=genome_candidates(prompt,seed,variants)
    options=[]
    for g in genomes:
        meshes=creature_meshes(g)
        audit=_score(g,meshes)
        if not audit["mesh_healthy"]:
            raise ValueError("generated non-manifold/degenerate candidate triangle")
        options.append({"genome":g,"audit":audit,"meshes":meshes})
    options.sort(key=lambda x:(-x["audit"]["design_complexity_heuristic"],
                               x["genome"]["id"]))
    selected=options[0]
    applied_morph=normalize_morph(morph)
    # One global deformation field is required for materials, bones and
    # attached props; per-material twist extents split the creature apart.
    shared_extent=max(point for mesh in selected["meshes"]
                      for point in mesh.positions[1::3])
    if shared_extent<=0:
        raise ValueError("creature vertical extent must be positive")
    morphed=[morph_mesh(mesh,applied_morph,axis_extent=shared_extent)[0]
             if mesh.indices else Mesh() for mesh in selected["meshes"]]
    palette=PALETTES[selected["genome"]["palette_index"]]
    mats=[
        ("body",list(palette[0])),
        ("belly",list(palette[1])),
        ("horns-and-claws",[0.56,0.61,0.67,1]),
        ("eyes",[0.018,0.025,0.045,1]),
        ("wings",list(palette[1])),
    ]
    payload=export_glb(morphed,name="MGR Native Invented Creature",materials=mats)
    quality=inspect_glb(payload)
    dest=Path(output)
    if dest.exists():
        raise FileExistsError("creature output already exists; never overwrite prior design")
    dest.mkdir(parents=True)
    digest=hashlib.sha256(payload).hexdigest()
    manifest={
        "schema":"mgr.forge.imagination-creature.v1","status":"NATIVE_PROCEDURAL_GEOMETRY",
        "prompt":prompt.strip(),"seed":seed,"requested_variants":variants,
        "selected_genome":selected["genome"],"applied_morph":applied_morph,
        "morph_axis_extent":shared_extent,
        "candidates":[{"genome":x["genome"],"audit":x["audit"]} for x in options],
        "artifact":{"file":"creature.glb","sha256":digest,"bytes":len(payload)},
        "glb_quality":quality,"model_inference_used":False,"preset_kit_used":False,
        "external_model_used":False,"gpu_used":False,"provider_spend_usd":0,
        "rendered_visual_accepted":False,"rigged":False,"animated":False,
        "photoreal":False,"independently_blender_verified":False,
        "novelty_worldwide_verified":False,
        "limitations":["rule-based generative geometry, not neural text-to-3D",
                       "cannot prove unseen global novelty or an imagined original style",
                       "skin, UV, hair, realistic morphs and game-ready animation not present",
                       "requires separate Blender visual and engine import acceptance"]
    }
    (dest/"creature.glb").write_bytes(payload)
    (dest/"creature.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    return manifest
