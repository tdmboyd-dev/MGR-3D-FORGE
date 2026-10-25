"""MGR Fantasy Forge: deterministic CPU-authored 3D effect geometry.

Illustrative VFX geometry, not fluid/fire simulation or production film magic.
Each frame is an independently exportable scene, no GPU or paid API needed.
"""

import math
import random

from .geometry import Mesh
from .glb import export_glb


FX_MATERIALS=(
    ("portal-cyan",[.08,.85,1,1]),
    ("arc-violet",[.52,.12,.95,1]),
    ("ember-gold",[1,.46,.06,1]),
)
FX_EMISSION={0:[.07,.75,1],1:[.45,.06,.9],2:[1,.36,.04]}


def _check(frame, count, radius):
    if type(frame) not in (int,float) or not math.isfinite(frame) or not 0<=frame<=1:
        raise ValueError("effect phase must be in [0,1]")
    if type(count) is not int or not 8<=count<=2048:
        raise ValueError("effect particle budget must be 8..2048")
    if type(radius) not in (int,float) or not math.isfinite(radius) or not .25<=radius<=100:
        raise ValueError("effect radius must be finite between .25 and 100 meters")


def create_magic_effect(*, kind="portal", phase=0.0, radius=2.0, particles=96, seed=8964):
    """Return three meshes plus a truthful time-parametric FX receipt."""
    if kind not in ("portal","spell-orbit","aura"):
        raise ValueError("unknown MGR effect type")
    _check(phase,particles,radius)
    if type(seed) is not int:
        raise ValueError("integer seed required")
    rng=random.Random(seed)
    meshes=[Mesh(),Mesh(),Mesh()]
    center=(0,radius+0.5,0)
    segments=max(32,min(256,particles))
    # Literal 3D structures: portal in X/Y plane, spell orbit horizontal,
    # aura as stacked helix. No external image masquerading as a real scene.
    def ring_point(t,r):
        angle=2*math.pi*t
        if kind=="portal":
            return (r*math.cos(angle),center[1]+r*math.sin(angle),0)
        if kind=="spell-orbit":
            return (r*math.cos(angle),center[1],r*math.sin(angle))
        return (r*math.cos(angle),.25+2*radius*t,r*math.sin(angle))
    for i in range(segments):
        a=ring_point(i/segments,radius)
        b=ring_point((i+1)/segments,radius)
        meshes[0].beam(a,b,.045*radius)
    for i in range(segments):
        start=i/segments+phase
        end=start+.30/segments
        meshes[1].beam(ring_point(start,.88*radius),ring_point(end,.88*radius),.018*radius)
    locations=[]
    for i in range(particles):
        t=i/particles+phase*.65+rng.uniform(-.008,.008)
        r=radius*(.66+.5*rng.random())
        x,y,z=ring_point(t,r)
        # Path variation is seeded and continuous across phase: no full fluid
        # simulation or physical particle collisions are implied.
        x+=.045*radius*math.sin(phase*2*math.pi+i)
        z+=.035*radius*math.cos(phase*2*math.pi+i)
        size=radius*(.012+.02*rng.random())
        meshes[2].box(x,y,z,size,size,size)
        locations.append([round(x,5),round(y,5),round(z,5)])
    receipt={"schema":"mgr.forge.fantasy-effect.v1","kind":kind,
             "phase":phase,"radius_m":radius,"seed":seed,
             "particles":particles,"mesh_layers":3,
             "triangles":sum(len(mesh.indices)//3 for mesh in meshes),
             "sample_positions":locations[:8],
             "execution":{"compute":"CPU","neural_inference":False,
                          "external_api_calls":0,"physics_simulated":False},
             "limitations":["stylized geometry, not photorealistic film VFX",
                            "motion is analytical, not fluid/cloth physics",
                            "no licensed third-party images, assets or models"]}
    return meshes,receipt


def export_effect_glb(meshes):
    return export_glb(meshes,name="MGR Fantasy Forge Effect",materials=FX_MATERIALS,
                      emissive_overrides=FX_EMISSION)
