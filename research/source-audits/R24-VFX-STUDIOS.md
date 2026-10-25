# R24 — MGR Hollywood-Layer Visual Effects Research Audit

**Date:** 2026-10-25. **Studios covered separately:** Wētā FX, Industrial Light & Magic (ILM), DNEG. **Evidence level:** first-party published research, original studio breakdowns, selected authored SIGGRAPH technical publications, NOT access to proprietary studio tools/production files or source. Technical upstream names/URLs reside in `research/external-provenance/R24-VFX-SOURCES.md`; MGR product creation names below are wholly native.

## What really matters

The blockbuster quality gap is rarely one secret model. It's repeated **layered work with ground truth**: anatomical rigs deform physically, moving fabrics/hair and fluids interact, every camera's geometry/light is agreed, simulations pass through a shot, and many rendered elements are assembled with correct depth/color to preserve continuity. These studio disclosures prove that the finished shot is a combined geometry, physics, performance, material, lighting, compositing and editorial problem. MGR should independently build interoperable contracts and measurable proof gates, not claim another studio's closed technology.

## Studio 1: Wētā FX — five distinct public technical themes

1. **Creature internal dynamics.** Studio technical history describes a linear-elastic finite-element musculoskeletal/skin/fat framework, where bones and muscle masses cause skin deformation. In numerical terms, discretized displacements `u` obey a force balance approximated by `M ü + C u̇ + K u = f_external` under linear assumptions; large strain/contact may need nonlinear material or constraints. **Native use:** `MGR Body Layers` drives skin via distinct anatomical layers instead of only a visible bone pose. Not a promise of medically calibrated muscles.
2. **Coupled cloth/hair/creature motion.** Public SIGGRAPH-indexed technical studies describe bodies, fabrics and fur interacting rather than running visually unrelated passes. **Native use:** `MGR Contact Weave` computes collision/contact receipts across character, garment and strand systems, with weak coupling acceptable for previews and tighter substeps for cinematic output.
3. **Water, bubbles and foam.** Original studio pipeline publications describe unified water workflows, foam/bubble art direction and render graph handoffs. **Native use:** `MGR Water Stage` links surface waves/particles/whitewater and compositing masks with common timestamps; avoids declaring a pretty shader equivalent to volumetric fluid dynamics.
4. **Physically-based layered surface appearance.** Studio renderer/material publications discuss layered material interactions, detailed hair/skin reflectance and complex pass management. **Native use:** `MGR Surface Witness` evaluates energy/roughness, subsurface/strand appearance and AOV numerical checks under controlled lights, not only uncontrolled beauty renders.
5. **Deep compositing.** Public studio technique documentation highlights retaining **depth-resolved sample/layer information**, enabling better holdouts/edge blending/depth-of-field than simple flat RGBA element stacking. **Native use:** `MGR Depth Compositor` carries `rgba + Z/coverage/transmittance` (or bounded deep samples) and compositing order tests with known occluders. Distinguish physically meaningful volume integration from arbitrary alpha overlays.

**Wētā validation lesson:** Facial performance, internal tissue, coat/hair, water and final pixels may each be owned by different subsystems yet must share stable asset and shot IDs. Unrendered physics is not output; output-looking good does not prove simulation.

## Studio 2: ILM — five distinct public technical themes

1. **Camera-calibrated virtual environments.** Studio's virtual-production explanation describes on-camera perspective correct LED backgrounds with tracked camera parallax and light interaction. **Native use:** `MGR Camera Reality Wall` takes measured lens/frustum, camera motion, scene coordinates and frame-locked content, then independently compares parallax/occlusion as camera moves. A huge LED wall is not required for mathematical camera proof.
2. **Previsualization and virtual art department.** Studio practice designs/scouts virtual/physical spaces ahead of shooting. **Native use:** `MGR Scene Scout` checks playable camera paths, lighting/floor plans, practical-vs-digital boundaries and shot feasibility before render expenditure.
3. **Layered surface materials.** Public studio research explains layered networks that model how light behaves through interacting surface layers rather than a single diffuse texture. **Native use:** `MGR Material Stack` compiles bounded, explicit coat/roughness/tint/subsurface combinations and verifies plausible energy response across a light sweep.
4. **Image-conditioned scene reconstruction.** Studio-described partnership on neural radiance fields uses a set of real-world photographs to build view-dependent photoreal virtual environments. **Native use:** `MGR Photo Space` stores calibrated capture provenance, scene depth uncertainty and camera path validation, with a separate editable-mesh recovery lane. Novel-view imagery does **not** imply directly animatable/watertight meshes.
5. **Performance capture and synchronized production.** Public tools include motion capture and precise camera/LED/content synchronization; some studio exhibits describe frame-level clock sync. **Native use:** `MGR Performance Clock` binds actors, motion, lens, lighting, playback and FX to the same frame/timecode and rejects desynchronization. A recorded movement still needs retarget/deformation truth.

**ILM validation lesson:** Real-time means a consistent tracked *image from the actual camera*, not merely a gaming FPS number. Parallax, chroma, exposure, rolling frame delays and shadow alignment remain essential.

## Studio 3: DNEG — five distinct public technical themes

1. **Anatomical character simulation.** Studio technology pages describe layered musculature, skin and real-time approximations for digital humans/creatures. **Native use:** `MGR Creature Solver` separates accurate offline deformation from machine-learned/fast approximation with holdout pose validation. Real-time surrogate predictions must not be mistaken for exact physics.
2. **Large sand/pyro and terrain-destruction dynamics.** Studio breakdown of giant creature traversing dunes shows plate footfall/dust restored and extended to larger CG collapses and simulations. **Native use:** `MGR Ground Impact` couples collision impulse, ground deformation, particles/dust, volumetric smoke and camera-correct shadow/holdouts with named causality.
3. **Crowd and swarm authoring.** Studio-authored production technical brief describes artist-driven controllable crowd behavior; creature swarm briefs explain procedural locomotion and coherent group effects. **Native use:** `MGR Swarm Choreographer` links agents/formation/avoidance to physically plausible speed and collision limits; constrain intentional director overrides.
4. **Plate-to-FX-to-composite handoff.** Sandworm workflow links restored practical evidence, simulated FX and compositing. **Native use:** `MGR Plate Truth` tracks original footage, camera solve, mattes, AOVs, holdout conditions, recreated footfalls and final render continuity receipts.
5. **Production-specific FX blocking.** Studio practitioners emphasize locking broad timing/performance before tuning costly detailed simulations. **Native use:** `MGR Impact Preview` creates fast blocking movement/FX anchors and only moves to expensive high-resolution simulation after camera/timing approval.

**DNEG validation lesson:** Cinematic dust and creature motion rely on impact cause, camera tracking and composited integration; simply throwing volumetric particles on a character does not reproduce the film workflow.

## Independent MGR production architecture

`ShotContract` and `StageReceipt` are the shared authority. A shot declares scene/actor IDs, immutable reference asset hashes, timecode/FPS, camera/lens/transform, lights/color pipeline, physics scale, contact geometry, render passes/AOV channels and editorial intent. Stages then issue proof:

1. **MGR Director Plan:** shot coverage, blocking, camera composition and cut continuity.
2. **MGR Geometry Truth:** object scale/pose, hidden surface coverage, cloth/skin topology and stable IDs.
3. **MGR Performance Clock:** actor motion and time-aligned capture/animation curves.
4. **MGR Contact Lab:** skin/tissue, cloth, hair, collisions, ground impact and constraint residuals.
5. **MGR Element Forge:** liquids, fire/smoke, foam, dust, sparks and magic as controllable volumetric/particle/surface outputs.
6. **MGR Look Lab:** physically interpretable material/light/optics and HDR color/exposure with expected numerical ranges.
7. **MGR Depth Compositor:** layered color/depth/coverage, object holdouts, shadows, defocus and motion blur.
8. **MGR Shot Continuity Judge:** matched camera/actor/material and cause/effect across cuts; rejects generated artifacts that merely look cinematic in isolation.
9. **MGR Production Receipt:** independent frame samples, computation budgets, errors, software versions and source/rights lineage.

No new studio product name becomes MGR canon. These native modules reuse existing Forge pipelines and Visual Judge, animation, director, physics/material/fx/Blender bridges where actually implemented; **the advanced features listed here are not automatically built**.

## Practical mathematical/process research

- **Skin/cloth:** time integration stable only with appropriate timestep, collision/substep resolution, damping, stiffness and limits; quantify penetration depth and spring/mass conservation rather than sim-frame aesthetics. Finite elements/position-based constraints represent different physical approximations.
- **Water/smoke/fire:** incompressible flow commonly uses discretized velocity/advection/pressure projection, with mass divergence and solver stability tests; highly artistic flames may combine particles, volume density, temperature and lighting. Keep color/effects distinct from physical state.
- **Hair/strand:** roots attached to deforming scalps, curve-based mass/inertia/collision and anisotropic optical response; leaf/strand instancing/LOD for preview. Track strand count and clipping.
- **Layered BRDF:** evaluate energy/fresnel, normal/tangent stability, roughness and color-space under controlled scenes; proper coat-layer math differs from naïve alpha blending.
- **Deep composites:** a deep sample is more than an RGBA texture: ordered depth/coverage or optical-opacity values allow depth-aware holdout; test occlusion and correct accumulation. Not all target viewers support deep EXR directly.
- **Shot continuity:** geometric reprojection using exact camera transforms, motion vectors and identities provides stronger acceptance than unrelated still-image comparison. Match FPS, shutter, depth-of-field, exposure and tone map.

## Rights, closed-source and realistic hardware

The studio-named solvers, renderers, proprietary pipelines, performance capture techniques and partner film assets are **not MGR-owned code**. Public publication descriptions are legitimate research lessons but do not grant code, weights, proprietary footage, models or trademark access. Every externally sourced sample must be version/license approved; no production clips or character models copied by this audit.

CPU procedural meshes, simple animation, depth/AOV math and deterministic quality checks need no huge GPU. High-quality tissue simulation, coupled millions-of-strand hair, fluid volumes, multiple high-res passes, final path tracing and deep compositing may consume substantial multi-core CPU/GPU, VRAM/RAM and render time. Use a **preview→validated hero-shot→optimized final** hierarchy and measure actual machine limits before asserting price, speed, realism or “Hollywood parity.”

## Acceptance gates (reproducible, not beauty-only)

1. **Anatomical layers:** a skinned arm/leg at T, A and 12 poses preserves connected joints, muscle/skin volumes and valid landmark endpoints; compare base pose vs tissue/skin output for fold/penetration with signed residual.
2. **Wardrobe coupling:** coat/skin/fur penetration count, max depth and frame count stay under configured limits; intentionally faulty cloth path fails. All garments still separately editable after GLB export.
3. **Fluid and contact causality:** known object impacts pool/ground, and wave/dust onset follows actual contact time, has controlled nonnegative mass/source terms and frame-aligned shadows. No dust-before-impact hallucination.
4. **Volume/light:** held-out smoke/fire/foam view receives correct occlusion and accumulated density/attenuation; synthetic zero density yields no volume element.
5. **AOV/deep compositing:** exact 2-layer and 3-layer depth/color/alpha fixtures composite in known order; overlapping hair/thin glass/motion-blur edge cases compare to analytic expectation where available.
6. **Material test:** canonical matte, rough metal, coat, skin and fur strip across 3 calibrated lights, preserving energy/tone and plausible consistency through camera rotations.
7. **Camera virtual space:** tracked moving virtual camera produces measured parallax and correct occlusion behind static room; wrong calibration/clock offset must fail.
8. **Shot clock:** camera/exposure, motion and FX elements at frame N all reference same timecode; introduce a one-frame offset and ensure Judge rejects it.
9. **Image/mesh truth:** 360° controlled turntable and depth/silhouette/landmark checks for approved synthetic character; a pose-changed correct identity scores identity separately from pixel equality, and fake back view fails.
10. **Compute and fallback:** benchmark proxy and final settings, memory/seconds/frame, CPU vs GPU lanes if available, per-shot retries and recoverable cancellation; no arbitrary high-budget render launches.
11. **External exchange:** opening actual export in Blender and independent viewer verifies scale, asset names, AOV channel interpretation and visual/geometry reconciliation. Mark unimplemented deep/volume consumers as skipped, never passed.
12. **Legal/attribution:** scan source receipts for restricted film footage, unlicensed proprietary models/weights and studio branding contamination before packaging.

## Status verdict

**Technical research:** R24 primary public references reviewed with per-studio distinctions. **Implementation:** native advanced body, coupled fluid/cloth/hair and deep compositing currently **SPECIFIED ONLY** by this audit; no proprietary studio solver reproduced or certified. Highest leverage next build is shared `ShotContract`/`StageReceipt`, ground-truth camera/timecode matching, layered rendering tests and contact-triggered FX—these improve every subsequent creature/fantasy shot without committing to a giant GPU stack prematurely.
