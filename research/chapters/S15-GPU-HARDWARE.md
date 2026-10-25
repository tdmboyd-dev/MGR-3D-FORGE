# S15 — MGR Native Render Hardware & Compute Admission

**Status:** 16-field research/specification packet, sourced 2026-10-25. GPU execution and cross-platform metrics are NOT yet proven by this chapter. Evidence and third-party attribution are isolated to `research/external-provenance/S15-GPU-SOURCES.md`. MGR's owned contract is **Forge Hardware Admission**, a truthful route-selector and measured proof gate, not a copied engine/API.

## 1. Definition

GPU engineering covers graphics/compute API capabilities, render/compute queues, shaders, raster/ray/path tracing, vertex/texture/buffer allocation, transfer, scheduling, synchronization, profiling, shader compiler, device-loss recovery, heterogeneous CPU/GPU execution and target-device portability. The task is to decide **whether a Forge job can run, where it should run, at what visual quality, with what measured runtime/cost, and what happened if the device failed.** Shader portability is not identical to device support, functional output parity or frame-rate parity.

## 2. Production use

- Offline production: deterministic CPU procedural authoring, Blender scene creation, full-quality offline rendering when hardware permits, denoising, physical simulation and neural mesh reconstruction.
- Interactive 3D worlds: render frames at consistent target time, texture/geometry streaming, animation skinning, LOD, occlusion/frustum culling, particles/FX, GPU/CPU simulation and device capability fallbacks.
- Cinematics: path-traced hero renders may be offline, so interactive FPS requirements differ; motion blur samples, volumetrics, cloth and multi-pass compositing drive cost.
- Creator experience: local job starts with a short hardware check; risky or very expensive options require an actual measured estimate, not unconditional promises.

## 3. Standards and backend contracts

Backend candidates: Vulkan, Direct3D 12, Metal, WebGPU (API+WGSL), OpenGL compatibility and CUDA compute where NVIDIA hardware and licensing permit. Platforms have disjoint feature/format/shader limits; choose a capability intersection only after enumeration, then isolate advanced paths.

Canonical MGR `mgr.forge.hardware-admission.v1` concept:

```json
{
  "job_kind": "viewport|offline_render|compute|simulation|model_inference",
  "scene_requirements": {"vram_estimate_bytes": 0, "peak_ram_estimate_bytes": 0, "features": [], "quality_tier": "draft|preview|final"},
  "candidate_backends": ["cpu", "vulkan", "d3d12", "metal", "webgpu", "cuda"],
  "admission": "accepted|downgraded|rejected|unknown",
  "selected_backend": "cpu",
  "measured_receipt_id": null
}
```

Treat this as proposed schema, NOT a currently deployed component. `unknown` never means pass; actual device name/driver/feature support, backend, resource estimates and benchmark receipts are attached when measured. Standards-derived formats require per-backend feature negotiation and shader validation.

## 4. Scientific and algorithmic foundation

The critical variables are GPU/CPU latency, throughput, memory locality/bandwidth, transfer overhead, occupancy, divergence, cache pressure, command submission/compilation stalls and synchronization. GPU wins require enough parallel work to repay dispatch and copy costs. Real-time budgets at 60/30/24 FPS are respectively ~16.67/33.33/41.67 ms **whole-frame** intervals, not a promise that the GPU can consume all of it. Reserve share for game logic, simulation, CPU and OS scheduling. Frame averages conceal stutter; record p50/p95/p99, spikes, compilation, asset loads, peak residence and thermal steady state. Render-time/shader quality is measured on real images, not FPS alone.

## 5. Open implementations and code study

- Khronos Vulkan specification/guide + synchronization and pipeline caching: fine-grained explicit state/cache responsibilities.
- `wgpu` native implementation: cross-platform API and WGSL translation concept; candidate **study/adapt**, not default dependency before target coverage and license audit.
- Khronos glslang and Microsoft DXC: HLSL/GLSL to SPIR-V/DXIL and shader compilation pipeline lessons. Compile output and target runtime must be validated independently.
- Blender installed render pipeline and Python scene automation: first pragmatic production runtime. Avoid rebuilding its full renderer to satisfy a 3D-generation goal.
- Vendor profilers and GPU diagnostic tooling, e.g. NVIDIA Nsight, demonstrate trace-based resource reasoning; availability varies by driver/device/version.

## 6. Models

Neural rendering/geometry models can consume GPU memory and acceleration, and some algorithms support CPU inference (often slower). Auto-configuration requires exact model parameters, quantization, precision/backend, working-set peak, input image/resolution, batch count and host transfer measurements. No single universal VRAM requirement exists. Rasterization, camera transforms, procedural geometry and traditional polygon export do **not** require a neural network or proprietary API; CPU fallback is honest where complexity fits.

## 7. Data and benchmark corpus

Create MGR-owned scene suite: empty/cube control, skinned hero + separated wardrobe, 100/1000 crowd actors, procedural street blocks, high-poly asset, 1K/2K/4K textures, alpha foliage, volumetric fog, shadows, particles, transparent layers, multiple active lights, motion blur, camera teleport and continuously streamed region. Include low, mid and high scene scale plus valid shader variants. Record hardware, driver, OS, Blender version, backend, resolution, viewport/render config, lighting, quality, scene checksum and fixed seed. Use adversarial malformed assets and intentionally exhausted memory budgets. Avoid importing copyrighted game assets just to benchmark a Fortnite-like target.

## 8. Licensing and platform restrictions

- Vulkan, CUDA, DirectX, Metal, WebGPU documentation and SDKs do **not** have interchangeable terms; an SDK or sample license must be checked at the exact revision. GPU drivers and closed vendor tools may have redistribution restrictions.
- DXC, glslang, wgpu licenses can permit reuse subject to their specific notices and transitive dependencies, but must be reviewed at chosen lockfile revisions before vendoring.
- Console development is not inferred from desktop GPU support. PlayStation/Xbox/Nintendo proprietary SDK access, certification, deployment permissions and commercial relationships are separate requirements; do not claim console builds or SDK parity without authorized developer kits and tests.
- Compute model weights, example datasets, capture tools and commercial shader packs are rights-separate from engine source.

## 9. APIs / providers

No GPU vendor API is intrinsically required for CPU-only procedural Forge functionality. Optional local CUDA/Vulkan/Metal compute and offline/cloud GPU render/inference workers should sit behind `ComputeBackend` with per-job estimated spend, opt-in provider credentials, privacy, timeout/retries, quota and downloadable receipts. The price of a desktop GPU, cloud instance or hosted graphics API is unstable and unmeasured for Forge workloads; do not hard-code speculative costs as facts.

## 10. MGR-native architecture

Propose four additive modules with strict boundaries (paths provisional until implementation audit):

1. `forge/hardware_probe.py`: ask operating system/Blender and selected runtime for devices, versions, limits and current availability; never guess GPU from brand name alone.
2. `forge/hardware_admission.py`: input scene and job contract, memory estimator, feature negotiation, backend choice, quality-tier offer, explicit UNKNOWN or REJECT and safe CPU downgrade.
3. `forge/render_budget.py`: scene-centric memory/texture budget ledger, frame-time targets, streaming and LOD. Preserve authored asset fidelity outside viewport-specific LOD.
4. `forge/performance_receipt.py`: schema for warm/cold compile times, CPU/GPU timings, variance, peak memory, render sample artifacts, hash, kernel/device loss and fallback reason.

Native innovation candidates: **Reality-Based Budget Broker** (actual measured quality/time/cost options, automatic cheapest reproducible legal execution), **Graceful Scene Descent** (deterministic tier reduction preserving subject silhouette, hands/face, frame composition and owner locks before reducing secondary FX), **Dual-Truth Renderer** (CPU reference vs accelerated backend image/geometry comparisons), **Scene Pressure Map** (object-level attribution to memory, draw work and render bottlenecks), **No-GPU Proof Badge** (only awarded for tested job+scene+device; never blanket marketing).

## 11. Hardware/runtime truth

**No dedicated GPU needed for:** deterministic low-poly scene math, glTF/OBJ geometry generation, transformations, many procedural mesh tasks, analytical quality metrics and metadata. A CPU software renderer may cover simple proof imagery with potentially slow execution. **GPU usually beneficial/necessary for desired time budgets:** modern interactive high-resolution scenes, large deforming crowds, heavy ray/path tracing, complex volumetric FX, high-res texture workloads and many neural models. Integrated/shared-memory GPU differs from a discrete VRAM device and must be measured. CPU-only Blender renders are possible for supported CPU render paths; feature/device configurations differ. Portable across desktop GPUs ≠ console-ready. No unsupported claim that a GPU can be eliminated through research alone.

## 12. Total cost

Record one-time development, host/desktop hardware, electricity, storage and texture downloads, renderer seats/licenses where applicable, cloud GPU charges, compilation/cache warming, retries, egress and maintenance. Per-approved-asset and per-approved-scene cost is more meaningful than per-attempt cost. A manual CPU fallback has low provider fees but possibly unacceptable duration; a GPU renderer may save labor/latency but cost capital or rental fees. Require measured break-even and failure rate for any backend default.

## 13. Failure modes

OOM, VRAM oversubscription and paging; transient driver/device loss; dangling command buffer; invalid resource state or missing barrier; CPU/GPU race; incorrect precision/NaN shader; shader compilation mismatch; unsupported texture/compression format; resource leak; cache invalidation after driver upgrade; long first-frame stutter; CPU synchronization stall; huge unbounded asset allocation; TDR/hung kernel; missing driver, headless compositor or display; rendering output differs in gamma/tonemapping; numeric differences across vendors; cloud instance missing GPU; console SDK inaccessible; malicious shader/resource bomb.

## 14. Evaluation gates

- **Correctness:** schema validation, shader compile+validation, same scene geometry transforms, lighting output and camera shots, acceptable CPU/GPU pixel/perceptual difference and exact asset hashes where applicable.
- **Performance:** start/cold compile, warm steady-state p50/p95/p99 CPU/GPU frame, drops, asset-streaming stalls, render seconds per image, throughput, power/thermal impacts when measurable.
- **Memory:** peak CPU RAM/VRAM/resident budget, upload volume, texture pool, eviction count, GC/allocator cost; guard large allocations.
- **Portability:** OS+API+driver+feature matrix with actual tests for candidate devices, fallbacks and reproducible shader outputs. Unavailable hardware is explicitly NOT VERIFIED.
- **Resilience:** forced device-loss/OOM, retry, idempotent scene recovery, cancelled job, cleanup, no corruption to source assets.

Quality thresholds must be negotiated for each target: real-time game scenes, Blender preview and offline film renders have different needs. Do not use a single universal FPS number to claim completion.

## 15. System placement

Keep CPU geometry and native scene canon independent of GPU API. The Director/World/FX/Animation modules emit declarative jobs and assets; Hardware Admission plans execution, a replaceable Blender/backend worker runs it, Performance Receipt records actual results, and Visual Judge verifies output quality. The CPU path remains fallback for supported operations; feature negotiation must declare missing features and downgraded tiers. Avoid creating a second canonical scene graph or reimplementing Blender's full renderer.

## 16. Acceptance suite

1. Probe actual device features, OS/driver and Blender CPU/GPU availability on Windows; report UNKNOWN if no direct access, including device string provenance.
2. Generate deterministic CPU geometry and export without a dedicated GPU; verify identical scene checksum across repeat runs.
3. Render fixed hero/world scenes on available CPU and GPU backends; measure comparable geometry and perceptual visual differences with precise render settings.
4. Warm/cold shader compilation: record elapsed time, cache invalidation after shader and driver change, and first-interaction stutter.
5. Memory-pressure fixtures approaching reported budget, with orderly reject/downgrade/eviction and no source asset damage; test no GPU and low VRAM.
6. Validate deliberately invalid shader, missing feature, unsupported texture and bad resource states; explicit error classifications and no misleading green receipts.
7. If implementing direct Vulkan/D3D12/Metal compute, exercise barriers/hazards with validation layers and compared CPU reference output; do not claim support from docs alone.
8. Force device loss, cancellation, slow backend, OOM and resumed/cached job; verify bounded retries and recoverable operations.
9. 24/30/60 FPS target workloads: record p50/p95/p99 frame, main thread, CPU/GPU overlap and motion consistency; record actual missed-frame percentage.
10. Benchmark high-poly/crowd/FX/texture-streaming scenes and maintain silhouette/identity/hero quality under native LOD policy.
11. Shader pipeline cross-compile/test WGSL/HLSL/GLSL samples per actually available backend; compare color space, precision, alpha and unsupported features.
12. Independent import/playback in each claimed runtime/device; console acceptance remains blocked without authorized platform SDK/dev kits and tests.
13. Privacy/rights/provenance and cloud cost receipt sign-off for any hosted worker.
14. Run `python3 -m unittest discover -v`, static schema checks and real rendered artifacts, then log exact environment and results. No production flag while unknown gates remain.

**Best immediate build sequence:** first hardware probe and admission truth labels, then CPU baseline/Blender renderer comparisons and repeatable stress corpus, then candidate GPU backend only where measured scene workloads justify it. This lets Forge ship real geometry and scene editing on modest machines while maintaining an honest route to blockbuster-quality rendering rather than guessing universal hardware independence.
