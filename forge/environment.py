"""Reusable CPU procedural greenery for undeveloped grid lots."""

import random

from .geometry import Mesh


ENVIRONMENT_MATERIALS=(
    ("trunk",[0.29,0.17,0.09,1]),
    ("foliage",[0.12,0.37,0.16,1]),
    ("park-path",[0.57,0.5,0.38,1]),
)


def generate_parks(world, *, trees_per_lot=3):
    if type(trees_per_lot) is not int or not 0<=trees_per_lot<=20:
        raise ValueError("trees_per_lot must be 0..20")
    spec=world["spec"]
    occupied={tuple(b["lot"]) for b in world["buildings"]}
    meshes=[Mesh() for _ in ENVIRONMENT_MATERIALS]
    stride=spec["lot_size"]+spec["road_width"]
    rng=random.Random(spec["seed"]+517)
    parks=[]
    for row in range(spec["rows"]):
        for col in range(spec["columns"]):
            if (col,row) in occupied:
                continue
            x=(col-(spec["columns"]-1)/2)*stride
            z=(row-(spec["rows"]-1)/2)*stride
            max_offset=spec["lot_size"]*0.28
            park={"id":f"park-{row:03d}-{col:03d}", "lot":[col,row],
                  "tree_ids":[], "ground_plan":"procedural-not-observed"}
            meshes[2].box(x,-0.025,z,spec["lot_size"]*0.7,0.03,0.7)
            for t in range(trees_per_lot):
                tx=x+rng.uniform(-max_offset,max_offset)
                tz=z+rng.uniform(-max_offset,max_offset)
                height=rng.uniform(2.7,5.5)
                meshes[0].box(tx,0,tz,0.3,height*0.68,0.3)
                meshes[1].box(tx,height*0.45,tz,1.7,height*0.60,1.7)
                park["tree_ids"].append(f"{park['id']}-tree-{t:02d}")
            parks.append(park)
    return meshes,{"schema":"mgr.forge.environment.v1","parks":parks,
                   "tree_count":sum(len(p["tree_ids"]) for p in parks),
                   "provenance":"MGR procedural generated assets"}


# MGR World Forge: optional terrain outside the existing editable city grid.
# Existing roads, buildings and deterministic city manifests are unmodified.
import hashlib
import math
from pathlib import Path
from .glb import export_glb, inspect_glb

BIOME_TYPES={
    "forest":((0.25,0.47,0.21,1.0),(0.48,0.56,0.31,1.0)),
    "desert":((0.73,0.59,0.35,1.0),(0.85,0.70,0.44,1.0)),
    "tundra":((0.65,0.75,0.78,1.0),(0.90,0.94,0.95,1.0)),
    "volcanic":((0.20,0.19,0.18,1.0),(0.42,0.20,0.14,1.0)),
    "alien":((0.29,0.19,0.46,1.0),(0.58,0.34,0.59,1.0)),
}

def _height_world(x,z,seed,biome):
    # Pinned stable math, intentionally modest, no model/texture license.
    v=.50*math.sin((x+seed*0.017)*.23)+.30*math.cos((z-seed*.013)*.27)
    v+=.20*math.sin((x+z+seed*.009)*.48)
    amp=2.2 if biome!="volcanic" else 4.3
    return round(amp*v,5)

def generate_biome_shell(world, *, biome="forest", seed=42, resolution=28):
    """Terrain ring outside world roads; optional additive world asset.

    Results fit the owner's existing world schema and do not re-author roads,
    architecture or the original world GLB. No imported third-party meshes.
    """
    if biome not in BIOME_TYPES or type(seed) is not int or not 0<=seed<2**32:
        raise ValueError("invalid biome name or seed")
    if type(resolution) is not int or not 10<=resolution<=64:
        raise ValueError("biome resolution must be 10..64")
    spec=world["spec"]
    halfW=(spec["columns"]*(spec["lot_size"]+spec["road_width"])+spec["road_width"])/2
    halfD=(spec["rows"]*(spec["lot_size"]+spec["road_width"])+spec["road_width"])/2
    extent=max(18.0,spec["lot_size"]*1.75)
    outerW=halfW+extent
    outerD=halfD+extent
    innerW=halfW+.40
    innerD=halfD+.40
    meshes=[Mesh(),Mesh()]
    created=0
    # Use aligned grid with a city-centered hollow. Each terrain tile consists
    # of two independently checked triangles via Mesh.quad.
    for ix in range(resolution):
        x1=-outerW+2*outerW*ix/resolution
        x2=-outerW+2*outerW*(ix+1)/resolution
        for iz in range(resolution):
            z1=-outerD+2*outerD*iz/resolution
            z2=-outerD+2*outerD*(iz+1)/resolution
            midx=(x1+x2)/2;midz=(z1+z2)/2
            if abs(midx)<innerW and abs(midz)<innerD:
                continue
            # Clamp city-facing samples so the terrain begins as a gentle bank
            # immediately beyond the generated ground boundary.
            def vertex(x,z):
                shore=max(0.0,abs(x)-innerW,abs(z)-innerD)
                damp=min(1.0,shore/5.0)
                return (round(x,5),_height_world(x,z,seed,biome)*damp,round(z,5))
            a,b,c,d=(vertex(x1,z1),vertex(x2,z1),vertex(x2,z2),vertex(x1,z2))
            if abs(a[1]-b[1])<1e-7 and abs(a[1]-c[1])<1e-7 and abs(a[1]-d[1])<1e-7:
                # perfectly flat cells remain valid via world X/Z rectangle
                pass
            tileset=0 if _height_world(midx,midz,seed,biome)<.6 else 1
            # Winding is XZ with Y-up; camera/reimport checks face orientation.
            meshes[tileset].quad(a,d,c,b)
            created+=1
    if created<20:
        raise RuntimeError("biome shell has too few independent terrain cells")
    metadata={"schema":"mgr.forge.biome-shell.v1","biome":biome,"seed":seed,
              "resolution":resolution,"tiles":created,
              "source_world_glb_sha256":world.get("artifact",{}).get("sha256"),
              "city_unchanged":True,"biome_as_optional_layer":True,
              "underlying_model":"MGR-own-CPU-procedural-only",
              "collision_navigation_built":False,"blender_verified":False}
    return meshes,metadata

def write_biome_shell(world_dir,out,*,biome="forest",seed=42,resolution=28):
    import json
    from .receipt import file_receipt
    root=Path(world_dir)
    source=root/"manifest.json"
    glb=root/"world.glb"
    if not source.is_file() or not glb.is_file() or source.stat().st_size>4_000_000:
        raise ValueError("verified owner world bundle required")
    world=json.loads(source.read_text(encoding="utf8"))
    sha=hashlib.sha256(glb.read_bytes()).hexdigest()
    if sha!=world.get("artifact",{}).get("sha256"):
        raise ValueError("source world SHA changed; do not build biome over altered world")
    inspect_glb(glb.read_bytes())
    meshes,meta=generate_biome_shell(world,biome=biome,seed=seed,resolution=resolution)
    rootout=Path(out)
    if rootout.exists():raise FileExistsError("biome layer cannot overwrite earlier world")
    palette=BIOME_TYPES[biome]
    raw=export_glb(meshes,name=f"MGR Native {biome} World Shell",
                   materials=(("biome-base",list(palette[0])),("biome-detail",list(palette[1]))))
    inspected=inspect_glb(raw)
    rootout.mkdir(parents=True)
    (rootout/"biome.glb").write_bytes(raw)
    meta.update({"status":"NATIVE_OPTIONAL_TERRAIN_GLTF","source_world_glb_sha256":sha,
                 "artifact":{"path":"biome.glb",**file_receipt(rootout/"biome.glb")},
                 "geometry_quality":inspected,
                 "rights":"MGR-authored procedural geometry, no external asset kits or model weight",
                 "world_original_untouched":hashlib.sha256(glb.read_bytes()).hexdigest()==sha})
    (rootout/"biome.json").write_text(json.dumps(meta,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return meta
