# R08 — MGR Graphics Driver Audit: Vulkan

**Date:** 2026-10-25. **Version pinned for research:** Vulkan **1.4.366** with registered extensions per Khronos online registry observed this date; select the **ratified** spec and exact SDK/driver version before production coding. The online `latest` URL is mutable. **Research maturity:** first-party specification and guide reviewed; **runtime implementation and hardware proof absent**. External source URLs/terms are kept in `research/external-provenance/R07-R08-SOURCES.md`.

## 1. Definition

Vulkan is an explicit, low-level API for graphics and general GPU compute. Applications control command buffers, resource memory, descriptors, pipeline layouts, queue submission and synchronization. It can scale to complex multi-threaded renderers, but the responsibility for safety and correctness is much larger than a stateful draw API. It does not inherently supply 3D characters, physically based materials, worlds, neural models or studio effects.

## 2. Forge applications

Long-term MGR viewport for huge instances/world chunks, high-throughput GPU procedural simulations, particle/voxel effects, large batch geometry/texture processing, cross-device compute where supported, validated multi-camera render jobs and deterministic GPU instrumentation. The immediate Forge needs are better served by keeping its current CPU output and installed Blender operational while a Vulkan adapter is separately gated by benchmarks.

## 3. Core specification and coordinate rules

- Vulkan clip coordinates satisfy `-w≤x,y≤w`, **`0≤z≤w`** by default (unlike default OpenGL symmetric clip z). After divide, normal NDC depth is `[0,1]`. Viewport min/max depth, transforms and coordinate conventions must be explicitly configured and tested.
- Viewport coordinate and front-face winding behavior depend on projection/viewport choices, including optional negative viewport height/axis inversion; never copy OpenGL projection matrices without verified conversion.
- Mesh position/normal/tangent and PBR map semantics belong to the MGR asset/material standard and its shaders; Vulkan **does not specify a PBR appearance**.
- Explicit image layouts, subresources, queue families and stages/access masks are required for correct transitions between upload, shader read/write, color/depth attachment, transfer and host readback.
- Physical device feature/extension properties must be queried. A Vulkan API version advertisement does **not** guarantee ray tracing, mesh shaders, specific subgroup operations, descriptor indexing or a desired optional extension.

## 4. Shader and projection foundations

GPU shader modules commonly carry SPIR-V instruction streams; an authoring toolchain may compile GLSL/HLSL into SPIR-V with target-environment constraints, then validate modules and pipeline interfaces. Matrix transforms and clip/depth conversion follow S04 contract. Material shading, normal/tangent frames, environment lighting and tone mapping are engine-level algorithms; verify output against calibrated reference and separate linear/shader values from display encoding.

## 5. Primary engineering findings

- Vulkan commands record to buffers and execute asynchronously on queues. Ownership, lifetime, fence/timeline conditions and host memory coherency are explicit; data races can be intermittent and visually misleading.
- Pipeline resource declarations (descriptor sets/bindings and pipeline layouts) must agree with shader resources and intended access.
- Use synchronization2 concepts where supported/selected; barriers must match both prior writers and subsequent readers and image-layout transitions. A random full-device barrier can mask issues while destroying throughput.
- Render pass/dynamic rendering capability differs across API/features; select one audited runtime path, do not mix arbitrary extension samples.
- Validation layers catch many API misuses but do not prove correct PBR appearance, physical geometry or race-free application logic in every scenario.

## 6. Tools and candidate implementations

The Vulkan SDK toolchain, official validation layers, SPIR-V validators/compilers and reference samples are candidate development aids; pin exact releases, licenses and executable hashes. Optional GPU compute can accelerate mesh evaluation, particle kernels or voxel fusion but requires CPU reference outputs before acceptance. Trained generative models are independent from graphics/compute API.

## 7. Fixtures

Owned native fixtures: camera-axis cube, UV sphere, PBR/normal/sRGB grids, near/far depth atlas, descriptor mismatch, staged image copy, storage buffer read-write, queue transfer, intentional host flush/invalidate failure, shadow map, large instance array, lost/unsupported device negative cases and zero-dimension/oversized allocations.

## 8. Licensing and version constraints

Review Khronos specification licensing separately from SDK components, VMA/allocation utilities, validation layers, shader compilers, sample imagery and third-party PBR shader sources. Avoid copying implementation code without license audit. Optional platform extension portability varies by installed GPU and operating system. The mutable latest spec must be replaced by an exact pinned registry tag/revision for shipped implementation.

## 9. Native API abstraction

`RenderJob`, `RenderReceipt`, `GPUCapabilities`, `BufferLease`, `ImageLease`, `PipelineContract`, `QueueFence` are MGR-owned concepts with backends hidden behind one interface. Capture shader hashes, SPIR-V validation, device driver/feature ID, resource dimensions, queue/fence completion, memory usage and render frame. A refused GPU job must return an actionable reason and may trigger a CPU/Blender fallback if quality requirements allow.

## 10. MGR native engineering plan

**MGR Explicit Graphics Lane:** physical device choice with constraints → create instance/device/queues → construct memory/resource graph → compile/validate shaders → descriptor/graphics pipeline or compute pipeline → record commands → submit with precise dependencies → read back after signaled completion → compare CPU/independent raster reference → collect visual and operational receipt → cleanup by lifetime graph. Keep custom visual style and PBR rules in MGR scene contracts, not vendor samples.

## 11. Hardware and performance

Requires a conforming GPU + driver; CPU-only fallback remains essential. VRAM pressure derives from images, attachments, mesh buffers, geometry acceleration/optional ray tracing and transient memory. CPU time comes from command preparation, shaders/pipeline creation, barriers and synchronization; GPU/driver regressions are possible. Multi-threading may improve very large scenes after profiling, but setup overhead can make tiny jobs slower than CPU or a simple existing renderer. Measure relevant hardware first.

## 12. Costs

No intrinsic per-render external API bill; cost is native implementation complexity, driver test matrix, maintenance, GPU hardware and failures. A fresh Vulkan renderer is a significant engineering commitment, not a shortcut to Hollywood-quality visuals. Gate the investment on a measured feature impossible/inefficient in current Blender/viewport lanes.

## 13. Failure modes

Wrong depth range clips scenes; wrong viewport flip reverses triangles; unsynchronized storage write/read causes nondeterministic artifacts; stale image layout causes invalid access; missing host flush/invalidate yields old data; shader-resource layout mismatch draws corruption; premature resource deletion causes device faults; out-of-memory/lost device must not delete Forge project files; shader portability differs across drivers; ray tracing requested on unsupported GPU fails gracefully.

## 14. Metrics

CPU command record latency, GPU timestamped pass timings, submission/queue wait, memory peak, allocation count/fragmentation, 1st shader compilation vs warm cache, draw count, dispatch count, readback latency, image/mesh output deltas, validation message severity/count, throughput triangles/s/voxels/s/frames/s and power/temperature where available. Report *exact GPU/driver/OS/API/feature set*, not speculative 10×/100× comparisons.

## 15. Forge integration

Future optional `forge/render_backends/vulkan_adapter.py` + `forge/gpu_compute.py`, behind the same native receipt/asset interface as OpenGL and the existing Blender bridge. S04 camera/transform, S07 shader/material, S09 mesh/rig, S12 vision, S14 scan fusion, S17 VR and S20 physics research need explicit dependency declarations and proof gates. The currently reviewed Forge CPU/GLB workflow is not replaced by this audit. **No Vulkan module or real Vulkan validation execution is asserted.**

## 16. Acceptance tests

1. Query device API version, features, formats, queue families, driver and memory budget. Abort cleanly on unsupported device; do not conflate optional features with core.
2. Render known camera-axis/triangle fixtures with depth clipping `[0,1]`, winding and viewport flip; compare projected CPU landmarks and independently rendered screenshot.
3. Validate shader toolchain outputs and intentionally invalid SPIR-V, descriptor mismatch and incorrect push-constant ranges; fail with structured diagnostics.
4. Transfer staging buffer→GPU vertex buffer→image→host readback with correct stage/access/layout/queue barriers and matched contents.
5. Deliberate synchronization-hazard negative fixture under validation; production pipeline has zero applicable validation errors and deterministic readback hashes for a fixed GPU/software configuration.
6. Test host coherent vs noncoherent memory flush/invalidate, mapped buffer bounds and resource lifetime after command fence completion.
7. Run graphics and compute pipelines separately, then concurrently where queues permit; measure outputs against CPU reference before accepting speedup.
8. PBR/linear-sRGB/normal/roughness/metal grids, depth/occlusion, offscreen capture, material variant and shader NaN stress fixtures pass configured numerical and image-error gates.
9. Test 1k/100k/1m triangles, 10/100/1000 instances and voxel compute batches, with warm/cold driver runs, p50/p95 latency and peak memory.
10. Simulate allocation refusal/device lost and graceful fallback with no corrupted Forge scene state.
11. Independently open at least one exported asset in Blender, compare pose/geometry/material/scale; visual resemblance alone does not prove equivalence.

**Truthful status:** R08 source research and production gate designed. No local Vulkan device runtime, render output or benchmark is asserted complete.
