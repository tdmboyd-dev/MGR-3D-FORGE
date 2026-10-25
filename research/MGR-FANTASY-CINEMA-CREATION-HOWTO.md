# MGR Fantasy Cinema — lighting, illusion, magic, graphics and full-effects blueprint

MGR-owned capability specification. Current evidence: official/public technical
sources researched, synthetic CPU fantasy geometry implemented, full production
capabilities queued. This document does **not** claim studio trade secrets or
completed Hollywood-level results.

## 1. Definition

The fantasy pipeline creates controllable *world events*, not flat overlays:
light/shadow, energy, atmosphere, portals, altered gravity, illusions, particles,
material transformations, camera tricks, destruction, character/body mutations,
graphics, compositing and sound-reactive motion. Every effect needs a position,
time, source, physical/artistic rules, quality gate and reversible recipe.

## 2. Production use: end-to-end

Brief → scene/world ownership → performance and action choreography →
concept boards → previsualization → asset/rig/material prep → simulations →
procedural layers → lighting → camera → render passes → compositing →
color/mastering → audio/graphics → QC → target-specific export.

For a portal opening in an iKickItz world: stable anchor, opening/closing
animation, front/back geometry, inner-space illusion, parallax/occlusion,
participating fog, emissive ring, embers, wall/ground light spill, traversable
collision, sound/light events, and frame-to-frame character continuity.
The current Forge portal is only the editable ring/arc/ember geometry subset.

## 3. Relevant standards and formats

- glTF 2.0 for geometry, PBR, emissive materials and sampled animation.
- MaterialX for advanced portable node-based look definitions (future adapter).
- OpenUSD for layering scene variants, animation and shot assembly (future).
- OpenVDB for sparse smoke/fog/fire volumes (not presently implemented).
- ACES and OpenColorIO for color management consistency (future pipeline).
- EXR multilayer / AOV passes, depth, normal, emissive, motion vector and matte
  layers for VFX compositing and temporal quality gates (future pipeline).
- Browser Canvas/WebGL/WebGPU for interactive graphics, separate from
  Blender scene materials and geometry.

## 4. Production research and top techniques

Study lighting transport and exposure, light linking, reflections/refraction,
real and fake volumetrics, physically based and nonphotorealistic materials,
particle/field/simulation nodes, SDF geometry, sparse voxel techniques,
mesh displacement, procedural noise, ray marching, 2.5D matte projection,
depth compositing, camera tracking, illusion/misdirection, color pipeline,
temporal motion estimation, GPU/CPU tradeoffs and managed render jobs.

**Critical distinction:** a cheap shader trick can sell a believable fantasy
effect at one viewpoint; the same trick often fails as the user walks behind
it. Every effect must declare whether it is a fixed-shot illusion, a stereo/VR
illusion, or actual navigable 3D geometry.

## 5. Public open technical systems

Blender 5.2 LTS: shaders, Geometry/Simulation Nodes, Cycles, compositor,
Grease Pencil, camera/rig animation. Unreal: world/runtime lighting and Niagara
GPU particle/fluid systems, with separate hardware/platform support checks.
Houdini: particle/pyro/Vellum strategies, licensing and automation reviewed
before any integration. OpenVDB, MaterialX and ACES provide portability ideas.
These are places to *study*, not native MGR product identities.

## 6. Models (optional enhancements)

Prompt→effect graph, depth/normal estimation, image/video segmentation,
motion tracking, human motion synthesis, differentiable scene inference,
style transfer and AI artifact/continuity judging. Research and license each
weights release, minimum VRAM, RAM, CUDA requirements, output quality and
privacy separately. None is mandatory for the existing CPU geometric effects.

## 7. Datasets and quality fixtures

Use owned synthetic portal/beam/particle clips with known geometry/motion,
visibility/occlusion ground truth, matte masks and rendered test scenes;
licensed public production footage only with rights. Create reference sets
across frontal, side, rear, high and moving-camera views.

## 8. Licensing

Public documentation and standards inform architecture. Vendor source code,
prebuilt shaders, marketplace designs, footage, LUTs, studio assets and models
are not automatically redistributable. Preserve source evidence under
`research/external-provenance/`; native feature branding stays MGR-only.

## 9. Providers and runtimes

CPU procedural native geometry is first choice for editable prototypes.
Blender is local DCC and proof renderer. Optional Godot/Unreal receivers,
GPU geometry/volume effects, model APIs and remote farms sit behind cost,
licensing, performance and owner-approval contracts. MotionSites.ai is a
public website-prompt/design catalogue, not a documented 3D VFX renderer;
21st.dev is useful mainly as a user-interface/motion-graphics study source.

## 10. Native product architecture

1. MGR Light Sculptor: rigs, bounce/fill/rim/gobo, time/weather, lighting QA.
2. MGR Shadow Intelligence: real/virtual shadows, contact/volumetric cues.
3. MGR Atmosphere Field: fog, cloud, haze, dust and depth attenuation.
4. MGR Particle Architect: seed-stable emitters, trails, forces, LOD and pools.
5. MGR Elemental Simulator: water/fire/smoke/wind/cloth/rigid bodies, caches.
6. MGR Portal Intelligence: geometry, inside-space, transform and traversal.
7. MGR Energy Weave: beams, auras, shields, glyphs and charging/discharge.
8. MGR Illusion Architect: depth, parallax, mirrors, distortion, portal views.
9. MGR Metamorphosis Director: reversible shape/material/persona mutations.
10. MGR Shader Alchemist: native PBR/emission/procedural node recipes.
11. MGR Compositor: layered render passes, glow, blur, lens, keying, grain.
12. MGR Color Master: scene-referred grading, ACES/OCIO import/export tests.
13. MGR Motion Graphics: 2D/3D kinetic text, typographic timing, HUD.
14. MGR Sound-Reactive FX: beat/envelope/event-driven scene parameters.
15. MGR Destruction Director: fracture, physics caches, debris and restoration.
16. MGR Spell Continuity Brain: action state, character/world locks and replay.
17. MGR FX Judge: cross-view/motion/material/occlusion/temporal approval.

## 11. Hardware and deployment reality

Native ring/particle geometry and reproducible phase sampling run on CPU with
stdlib. Blender 5.2.2 can import/render GLB on owner Intel Iris Xe/CPU. Dense
fluids, long animated feature films, real-time path tracing, neural generative
FX and high-resolution volumetrics can be expensive; run micro-benchmarks and
use a quality/budget ladder before making speed or GPU-free promises.

## 12. Cost measurement protocol

Per effect and frame: generation ms, triangle count, RAM, GPU VRAM if used,
render time, storage/GB, extra API credits, artist-edit time, failed takes,
asset rights, optimization/LOD cost, FPS on target device. Benchmark both
low-end Windows laptop and intended production/viewer engine.

## 13. Failure cases and prevention

- Portal geometry flat in side/rear view → world-space assets + view sweep.
- Emission is bright but never glows → explicit postprocess/glare receipt.
- Fire/smoke seems frozen → time/seed and simulation cache acceptance.
- Particle shower changes every render → stable deterministic seeds.
- Illusion breaks walking behind it → known-camera limitation or proper 3D.
- Effect penetrates characters → scene graph/collision and depth testing.
- Cloth and hair clip in action → skin/physics/collision QA with pose sweep.
- FX causes huge latency → particle budgets, LOD, instancing, chunk streaming.
- Magic power changes character identity → continuity locks and owner approval.
- Inconsistent shots → consistent color space, exposure and timed VFX states.

## 14. Quality measurements

Structural GLB validity, emissive RGB values, Blender imported materials,
camera-angle visibility, bounding-box completeness, real rendered sample
images, temporal difference, loop seam, frame timing, depth-order error,
particle drift/reproducibility, motion jitter, color clipping, memory/time,
cross-engine import and user aesthetic acceptance. Tests of pixels alone do
not amount to human film-quality judgment.

## 15. Architecture placement

- `forge/fx.py`: pure CPU geometry, effect manifest, frame parameter.
- `forge/glb.py`: standard glTF emissive-factor interchange.
- `bridge/blender_fx_render.py`: real emissive-material Blender CPU preview.
- `forge/director.py`: effect/actor/camera timeline synchronization foundation.
- `forge/creation_memory.py`: planned effect-state and asset continuity.
- `forge/visualqa.py`: pixel QA; not multimodal artistic understanding.
- Future FX graph compiler, physics worker, volume importer, compositor,
  motion-graphics renderer and real-time runtime adapter all stay replaceable.

## 16. Acceptance and the research/build queue

**Proven at CPU/unit level:** deterministic 3D portal, spell-orbit and aura
meshes, fixed particle budgets, time-phase changes, no API calls, glTF emissive
materials, invalid input rejection. **Blender actual test pending** at initial
spec checkpoint. All 17 FX branches require child-by-child source and Blender
5.2.2 execution studies, then specs/tests, then production acceptance.

Immediate next ladder:

1. Render + visually inspect one actual 3D portal with emissions.
2. Build 3- to 5-frame animation/storyboard and save a reproducible scene.
3. Test compositor glow/fog and distinguish fake screen-space from world-space.
4. Add occlusion/body intersection tests across moving camera and avatar.
5. Introduce actual time-continuous VFX/particle simulation nodes with caches.
6. Export/import to intended live world viewer, measure FPS on owner hardware.
7. Compare visual/aesthetic quality against approved reference targets.

**Research remains incomplete across the advanced branches.** This ledger is
the scope and acceptance roadmap; do not inflate SOURCED into VERIFIED.
