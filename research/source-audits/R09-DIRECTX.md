# R09 — Direct3D / DirectX Research-to-Native Source Audit

**Maturity:** `SOURCED / SELECTIVE OFFICIAL DOCUMENTATION REVIEW`; no SDK sample built, source cloned or GPU runtime validated. Source URLs and legal boundaries are in `research/external-provenance/R09-R10-SOURCES.md`. MGR's resulting designs are native; Direct3D is one possible Windows backend, not a new canonical engine.

## Scope and reading depth

Official Microsoft Direct3D 12 pages checked 2026-10-25: introductory platform capabilities, D3D11→D3D12 differences, resource residency, tiled resources/reserved resource sample overview, command lists/queues, resource-state barriers, pipeline state objects, DXC shader model guidance and Advanced Shader Delivery. Reviewed **documentation and named APIs at conceptual/API-description level**. Did not walk Microsoft DirectX sample trees, read all source implementation files, execute validation layers or verify Windows GPU availability.

## High-value technique 1 — MGR Resource Pressure Controller

**Observed upstream idea:** D3D12 places explicit resource allocation/residency management on the application; physical memory pressure can demand residency policies. D3D12 reserved/tiled resources allow mapping resource regions to memory blocks when supported.

**Native design:** `Forge Render Budget` receives scene/asset estimates and measured heap budgets, then selects texture mip level, mesh LOD, material variants and sector streaming; it preserves hero/face/hand geometry first. A separate renderer adapter may use D3D12 `QueryVideoMemoryInfo`/residency/tile support **only when exposed by actual driver and tested**. The resource-budget algorithm should also work with Vulkan/Metal/WebGPU or with no hardware metrics (`unknown`).

**Tests:** low VRAM/forced-budget admission, reserve/release stress, out-of-budget fallback before allocation, streamed sector return without missing texture or inconsistent collision, no asset deletion, peak RAM/VRAM and p99 stutter receipts. Pixel-perfect quality is not guaranteed when tiers differ; owner locks constrain reductions.

## High-value technique 2 — Deterministic Render Task Graph

**Observed:** D3D12 uses command queues/lists, descriptor heaps and explicit resource barriers rather than relying entirely on the driver to manage states and dependencies.

**Native design:** model Forge render tasks as a backend-agnostic dependency DAG: upload geometry → skin/particle compute → shadow/depth → material/lighting → transparencies/FX → composite → readback. Each resource declares read/write/alias and lifetime states. A D3D12 adapter may translate into actual barriers; CPU reference executes a sequential DAG. Never copy D3D12 states into portable schema as if universally supported.

**Tests:** intentionally missing write-read dependency, circular work graph, double-free, invalid resource state, cancellation midframe, deterministic command ordering and image parity versus a CPU reference. GPU data races require real validation-layer execution; a passing Python topological-sort test is not enough.

## High-value technique 3 — Shader Variant Gate and Warmup

**Observed:** pipeline state objects group graphics state; D3D12 shader model 6 DXIL compilation commonly uses DXC. Advanced Shader Delivery describes a Windows 11 shader-preparation/distribution path intended to reduce first-use compilation stutters.

**Native design:** a provider-neutral `MGR Shader Receipt` maps authored material graph to variant key (backend, driver, feature set, shader hash, render options), compile status, warm/cold duration and output images. Prepare required variants before a live shot/game region; graceful fallback to a simpler material if a compiler or feature is unavailable. Do not assume Windows Advanced Shader Delivery is available on every system or can be transplanted into other OSs.

**Tests:** cold/warm cache, malformed HLSL, unsupported shader model, driver change, shader source invalidation, compile interruption, variant explosion, color-space/output regressions and p95/p99 first-frame spikes. Test DXC compiler with the real installed binary before claiming success.

## High-value technique 4 — World Streaming Tiles

**Observed:** reserved resources and tiling provide one low-level means to manage huge textures and partial resource commitment with hardware-dependent tiers.

**Native design:** Forge worlds divide scene assets into stable spatial sectors and mip/LOD groups, with an independent asset residency manifest. GPU-specific tiled-texture support is an optional optimization, not a condition for streaming worlds. Camera position and motion predictions request next sectors, while collision/navigation can load ahead separately. Seamless traversal requires actual runtime proof.

**Tests:** traversing repeatable path forward/back, bounded prefetch latency, degraded network/disk, fast teleport, reference asset identity after reentry, terrain seam/no missing visual, recover from asset checksum mismatch, timeline of allocations and user-visible stalls.

## High-value technique 5 — GPU Capability and Failure Admission

**Observed:** D3D12 feature tiers, WDDM-specific memory management, resource barriers and device control expose major hardware-dependent constraints.

**Native design:** `MGR Hardware Admission` reports actual adapter, OS, driver, feature flags, compiler availability and budget state; supports CPU procedural authoring independent of D3D12. A scene may be labeled `accepted`, `downgraded`, `rejected`, or `unknown`—never passed from assumed hardware.

**Tests:** no D3D12, low tier, exhausted VRAM, driver reset/device removed, remote/headless Windows, CPU fallback, non-Windows platform and repeated identical scene receipts.

## Architecture/rights decision

**MGR-NATIVE:** resource broker, render DAG, shader receipt, world-streaming manifest and admission/QA. **ADAPT selectively:** D3D12 execution APIs only behind Windows-specific feature-negotiated renderer adapter, if a genuine backend is justified by measured advantage. **STUDY:** Microsoft docs and sample structure. The Windows SDK, DXC/compiler, example source and binaries may have different licenses and redistribution conditions. Do not vendor SDK/source or claim Xbox/PlayStation portability from desktop Direct3D support. No provider costs or performance uplift were measured.

## Acceptance path and pending source audit

1. Unit-test portable DAG/resources/cache/admission contracts on CPU.
2. Record exact Windows build, GPU, driver, D3D12 feature tier, DXC/compiler and SDK versions, then compile an official minimal triangle/texture reference on an authorized machine.
3. Exercise D3D12 debug layer/GPU-based validation, resource residency queries, shader compile/warmup and device-loss recovery with negative fixtures.
4. Reconstruct same MGR scene via Blender/CPU and D3D12 adapter where available; compare geometry/image/latency and actual power/memory budgets.
5. Before any source adoption, inspect official SDK/sample revision, build scripts, test assets, licensing, sample implementation and support lifecycle end-to-end.

**What this audit can justify now:** a concrete native architecture and executable test queue. **What it cannot justify:** Direct3D support already built, Xbox deployment, universal fast rendering, or any 10× measured improvement.
