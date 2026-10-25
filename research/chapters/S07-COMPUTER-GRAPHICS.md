# S07 — MGR Reality Renderer: Computer Graphics, Pixels and Light Transport

**Owner:** MGR · **Date:** 2026-10-25 · **Scope:** Rasterization, path tracing, physically based shading, acceleration, temporal image formation, color-managed high dynamic range and CPU/GPU execution.

**Evidence state:** Primary reference documentation and published algorithms reviewed at chapter/API level. This is actionable research, not a claim that every reference source line was audited or that a new renderer has been implemented and measured. External provenance is quarantined in `research/external-provenance/S07-GRAPHICS-SOURCES.md`; all below is an MGR-native design proposal.

## MGR-native verdict

The goal is **one semantic world, multiple verified views**: editable meshes and materials feed a rapid navigable preview and a slower physical reference render, while both produce labeled passes, scene metadata and discrepancy evidence. Do **not** independently implement an entire production ray tracer before shipping: use a native orchestration, validation and learning layer around proven rendering runtimes, with tiny math/reference implementations only where tests require them. GPU is an optional speed multiplier, not a prerequisite for basic still generation on CPU; real-time, dense simulation and high-quality ray tracing shift that tradeoff sharply.

## 1 — Definition and boundaries

- A renderer converts scene geometry, surface properties, light, camera and sampling into image measurements. The projected image is not identical to an editable 3D scene.
- Rasterization projects triangles to pixel sample positions, resolves visibility/depth and shades fragments. Ray tracing intersects rays against geometry. Path tracing stochastically estimates multiple reflection/transmission paths and the light-transport integral.
- PBR means shading follows broadly physical material/light response; a metallic-roughness texture alone does not guarantee a physically correct output. Tonemapping and denoising are post/inference stages, not evidence of geometry correctness.
- Real-time navigability, cinematic reference, neural/point-cloud visualization, and editable scene reconstruction must be separately evaluated.

## 2 — Production functions

1. Author and validate assets, topology, UVs, textures, materials, normals and transforms.
2. Assemble a scene with cameras, lights, volumes and world scale; resolve missing textures.
3. Generate an immediate viewport/raster preview, then a path-traced reference when needed.
4. Store normals, depth, object/material IDs, motion vectors, cryptomatte or equivalent evidence passes as supported by the runtime.
5. Composite effects and map high-range linear color to intended displays; preserve raw scene-linear measurements.
6. Reconcile discrepancies, optimize frame-time/memory, package engine-friendly glTF/USD as appropriately supported.

## 3 — Standards, interchange and invariants

- **Data:** glTF 2.0 for interoperable real-time metallic-roughness assets, OpenUSD for richer scene description/workflows when warranted, EXR for scene-linear render intermediates. Each exporter has limits; roundtrip fidelity is measured, never assumed.
- **Color:** declared input texture color spaces, scene-linear working space, explicit OpenColorIO config/view/display; ordinary JPEG/PNG cannot be treated as equivalent to scene-linear EXR.
- **Math:** meters and right/left-handed axes clearly tagged; normal transformations correct under nonuniform scale; positive/negative winding explicitly handled; camera clipping and near-plane precision recorded.
- **Determinism:** output depends on renderer/device/version, random seed, tile and sampling method, scene hash, denoiser and color transform. Equivalent images need tolerances, not bit-perfect promises across GPU backends.

## 4 — Theory to understand before native invention

The rendering equation describes outgoing surface radiance as emission plus hemispheric reflection integral. A raster pass approximates local visibility/shading efficiently; a path tracer estimates multi-bounce contributions with finite noisy Monte Carlo samples. Multiple-importance sampling reduces wasted samples when balancing light and BSDF sampling. Acceleration structures (BVH, spatial hierarchy) skip irrelevant primitive intersections. Temporal antialiasing accumulates samples across frames, but may create ghosting around movement, transparency and disocclusion. Denoisers infer cleaner images from noisy ones; they can erase true small details and should never count as unaltered reference truth.

## 5 — Existing implementation families to study and interoperate with

- Blender/Cycles: CPU and GPU production path tracing, multiple-importance sampling, bounce and denoising controls. Blender interactive renderer for authoring, look development and script execution.
- Vulkan/OpenGL graphics concepts: mesh/vertex, primitive setup, raster, fragments, depth, multisampling, synchronization and presentation for a live game-world preview.
- PBRT v4: independently inspectable physically based reference algorithms for integrators, sampling, spectral and volumetric rendering; start from its small public example scenes before any claims of equivalence.
- OpenEXR and OpenColorIO: retained high-dynamic-range render passes plus reproducible display/technical transforms.
- Optional engine frontends should remain replaceable adapters. No external project's brand is an MGR feature contract.

## 6 — Building-block models and equations

- Perspective projection: rays through camera intrinsics and pixel centers, invertible only with known depth/multiple views/prior geometry. Store projection, lens, crop, sensor and pose.
- Raster depth: z-buffer estimates closest sampled visible surface, not all hidden geometry; thin features and alpha are edge cases.
- Sampling: standard error for independent Monte Carlo draws usually scales approximately as `1/sqrt(N)` under finite variance; quadrupling samples may roughly halve stochastic noise, not solve caustics or bias.
- PBR: Fresnel, microfacet normal distribution, geometry/shadowing factor, diffuse/transmission terms and energy budgets; verify roughness interpolation and texture transfer functions.
- Ray budgets: intersections depend on visibility, acceleration efficiency, bounce limits, media and geometry; polygon count alone is not an accurate memory/performance predictor.

## 7 — Datasets / reference scenes

- Build **MGR-owned analytic witness pack** first: single triangle, depth-overlap planes, UV checker sphere, Cornell-style room authored in-house, reflective sphere, refractive glass, fog volume, thin wires, alpha foliage and moving objects. Avoid assuming a classic public test scene is freely redistributable.
- Test camera/reference pairs: low-resolution baseline, 1080p still, orthographic/perspective comparison, turntable, walk-through, changing materials and moving lights.
- Keep a sealed baseline with native scene source, EXR AOVs, PNG presentation, hashes, timings and acceptance envelope.

## 8 — Licensing and provenance

Study published specs and reference implementations but independently review exact license of code, shader examples, datasets, models, environment maps and textures before copying. Preserve attribution/license files for third-party runtime dependencies. Separate **ideas learned** from **external assets redistributed**. Invention claims demand patent/novelty review outside this technical packet.

## 9 — APIs, drivers and integration surfaces

- Blender Python `bpy`: scene generation, node materials, render/device settings, output EXR channels and automation. Device discovery must prove actual usable hardware; requesting GPU does not guarantee it is active.
- Native preview bridges: glTF/USD handoff, engine subprocess or local IPC with job IDs, cancellation, scene hashes and structured artifacts; no shell string-concatenation from untrusted user prompts.
- Rendering capabilities manifest: `{backend, device, features, memory_budget_mb, max_texture_size, supports_exr, supports_aov, supports_volumes}`.

## 10 — Original MGR architecture and contract

**Native capabilities:** **Twin Truth Render** (same canonical world rendered via fast preview and reference integrator); **Reality Delta Judge** (depth/normal/ID/color-aware discrepancy localization); **Pixel Genealogy** (trace final pixel to source materials, lights, settings and compositor graph); **Adaptive Fidelity Scheduler** (choose preview/reference samples by risk and machine budget); **Hidden-Surface Honesty** (only label inferred unseen geometry as inferred); **Motion Truth Pass** (temporal frame sequence and ghosting validation).

Canonical contract:

```json
{
  "scene_id": "mgr-scene-id",
  "scene_hash": "sha256:...",
  "render_intent": "interactive_preview|physical_reference|final_delivery",
  "renderer": {"name": "cycles", "version": "recorded", "device": "CPU", "samples": 64, "seed": 42},
  "camera": {"id": "cam-01", "projection": "perspective", "intrinsics_id": "locked"},
  "color": {"working_space": "scene-linear", "ocio_config_hash": "sha256:...", "display_view": "recorded"},
  "deliverables": {"beauty_exr": "render.exr", "preview_png": "render.png", "depth_exr": "depth.exr", "normal_exr": "normal.exr"},
  "proof": {"reference_scene": "witness-id", "metric_suite": "mgr-graphics-v1", "status": "unverified"}
}
```

Rules: a generated image cannot claim an accessible world without navigable geometry and collision proof; an artistic PNG cannot claim linear physical light proof; an uncalibrated image match cannot claim identity preservation under arbitrary novel viewpoints.

## 11 — Compute, memory, speed and GPU realism

- CPU-first **is viable** for small scenes and offline renders; CPU is generally slower for many heavily parallel render workloads but needs no new discrete GPU purchase.
- GPU compute can accelerate rendering significantly, subject to VRAM, backend and driver; the PBRT authors report selected 10–100× GPU ray-tracing throughput cases, **not** a universal Forge multiplier. CPU/GPU results and available features can differ.
- World throughput hinges on asset streaming, image sizes, texture residency, instances, acceleration structures, view culling, LOD, batching and shader complexity—not simply a flagship GPU.
- Use memory-budget preflight: estimate texture bytes at resolution/mip levels, geometry and BVH overhead, render buffers/AOVs and concurrent tasks; fail clearly or reduce fidelity rather than crash.
- Per-device benchmarks required on the actual Windows machine; do not infer its installed GPU from user reports of Blender availability.

## 12 — Cost and operational gates

Estimate `cost_per_scene = compute_time × local energy/cloud rate + storage + manual cleanup + failure retries`. Keep CPU prototype at effectively no external API charge using local Blender; the electricity/time/hardware costs remain real. Run quick witness passes before high samples/high resolution; bound job count, concurrency, time, disk and VRAM. Do not purchase GPUs, training runs or proprietary rendering subscriptions based on generic performance claims.

## 13 — Failure/attack cases to preempt

1. Texture interpreted as linear vs sRGB; wrong gamma/washed highlights.
2. Normals flipped or nonuniform transform corrupts shading.
3. Missing alpha cutout yields solid leaves/hair or wrong transparency sorting.
4. 8-sample sparkles mistaken for details; denoiser hallucinates smoothness.
5. Dark glossy material appears black because environment/reflection sources absent.
6. Shading comparison passes after compositor bloom but source light fails.
7. Camera or tone mapping changes between baseline and candidate.
8. Hidden geometry falsely inferred from one image.
9. Lens/perspective mismatch disguised by high pixel-similarity scores.
10. SSR/raster reflections omit off-screen objects; preview-to-reference mismatch.
11. Temporal accumulation leaves ghosts and trails at disocclusions.
12. Geometry/texture overload exhausts VRAM or produces unbounded job latency.
13. Driver/kernel nondeterminism causes false pixel-perfect test failures.
14. Unlicensed HDRI/test meshes accidentally bundled into exports.

## 14 — Quantitative evaluation matrix

| Witness | Evidence | Pass policy |
|---|---|---|
| Triangle/depth | Z-buffer and object ID | Correct visible order and clip handling at near/far edges |
| Normals/tangents | Normal AOV and UV checker | Known orientation/handedness and zero missing sampler refs |
| Energy/material | Scene-linear BRDF sphere set | Directional trends and numeric tolerance against stable reference |
| Shadow | Occluder on/off, sharp/area source | Correct visibility change, softening and geometry fidelity |
| Indirect transport | Bounce setting 0/1/multi | Measurable secondary-light differences with locked exposure |
| Transparent/glass | Depth layers and transmission | No impossible clipping or alpha-order violations |
| Media | Constant density on/off | Expected attenuation trend and stable seed variance |
| HDR/color | EXR numeric probes and viewed PNG | Correct color metadata, finite ranges, explicit transform |
| Camera | Intrinsics checkerboard and multi-view | Reprojection/pose thresholds, no orthographic proof for perspective |
| Temporal | 100+ moving frames | Ghosting, temporal stability and motion vector coverage threshold |
| Performance | CPU/GPU if available | Render ms, peak RAM/VRAM, task retries, timeout thresholds |
| Export parity | Reimport asset and render | Geometry/material/camera hashes and perceptual differences |

Every numeric acceptance tolerance is **to be empirically calibrated** with baseline evidence, not fabricated in advance. Save regressions, diff images, raw AOV files and human signoff when creative intent matters.

## 15 — Integration placement and work order

1. **Truth foundation:** canonical scene manifest and existing Blender render-bridge output fingerprints; instrument EXR/AOV preservation, renderer config/version, seeds, timing and memory.
2. **Witness suite:** independent minimal in-house scenes and deterministic CLI test harness. Reuse S02 light and S03 geometry verification.
3. **Twin render:** fast draft vs high-quality reference with shared geometry/camera and color-managed comparison.
4. **Scene-aware judge:** combine existing image visual QA with object IDs, normals and depth, and reject claims unsupported by measurable scene data.
5. **Runtime navigator:** use a mature graphics engine or web-based renderer adapter rather than coupling game input to the offline compositor.
6. **Scale tests:** animation, large worlds, streaming, cloth/volumes and camera motions, each behind explicit capability gates.

## 16 — Acceptance and completeness definitions

**S07 researched:** 16 fields, primary sources and licensing caveats recorded; DONE for scoped research, with ongoing paper/source refresh as needed.

**S07 engineering complete only if:** (a) launchable local render and live preview, (b) round-trip canonical editable scene, (c) CPU witness suite with depth/normal/ID/scene-linear EXR and deterministic metadata, (d) configurable shader/transport reference, (e) 12 witness/performance gates with actual evidence, (f) multi-frame navigation/temporal tests, (g) physical-light and camera claims backed by calibrated controls, (h) machine-specific CPU/GPU tests where a GPU exists, (i) provenance/license checks for shipped assets and (j) documented reproducible Windows setup. None are established merely by this research packet.

**Recommendation:** prioritize **EXR/AOV + scene-hash proof and Twin Truth Render** over inventing a proprietary GPU ray tracer now. That directly raises trust of every MGR character, world, director camera and effects pipeline without blocking low-GPU users.
