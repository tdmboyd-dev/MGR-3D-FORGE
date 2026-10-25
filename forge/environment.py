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
