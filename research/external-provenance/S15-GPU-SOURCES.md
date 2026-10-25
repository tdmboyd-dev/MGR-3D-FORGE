# S15 — External provenance: GPU architecture, shader compilers, performance

Date checked: **2026-10-25**. This file documents first-party sources and verification limits for the MGR-native `S15-GPU-HARDWARE.md` design. Documentation review is not implementation, source audit or performance proof. No driver/SDK/tool was installed and no GPU benchmark run by this research wave.

| Primary source | Specific relevant evidence | Depth | MGR disposition and limitations |
| --- | --- | --- | --- |
| [Khronos Vulkan synchronization chapter](https://docs.vulkan.org/spec/latest/chapters/synchronization.html) | Explicit execution and memory dependencies; stages alone do not implicitly provide all memory ordering | Official spec reviewed | **ADOPT concepts** for validating compute hazards; device code untested. |
| [Khronos Vulkan essentials](https://docs.vulkan.org/samples/latest/samples/vulkan_basics.html) | Vulkan pushes memory, work dependency and CPU/GPU synchronization to caller; hardware performance may vary | Official project docs reviewed | **STUDY** not an MGR renderer dependency by default. |
| [Vulkan memory budget extension](https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_memory_budget.html) | Query mechanism for driver-exposed memory budget | Official extension ref reviewed | **ADAPT probe** only when extension present; reported budget is not a reservation nor exact guarantee. |
| [Vulkan memory budget sample](https://docs.vulkan.org/samples/latest/samples/extensions/memory_budget/README.html) | Example feature use | Official sample overview reviewed, code not executed | **STUDY**; check dependency licenses before vendoring. |
| [Vulkan pipeline cache guide](https://docs.vulkan.org/guide/latest/pipeline_cache.html) | Saved pipeline caches can reduce pipeline creation costs on suitable execution paths | Official guide reviewed | **ADAPT measured cold/warm startup**; cache portability and eviction must be tested. |
| [Direct3D 12 memory residency](https://learn.microsoft.com/en-us/windows/win32/direct3d12/residency) | Application responsibility for resource residence and pressure | Official Microsoft docs reviewed | **ADOPT acceptance concern**, Windows-specific backend only. |
| [Direct3D 12 resource barriers](https://learn.microsoft.com/en-us/windows/win32/direct3d12/using-resource-barriers-to-synchronize-resource-states-in-direct3d-12) | Resource state transitions and synchronization requirements | Official Microsoft docs reviewed | **STUDY** direct shader execution controls; shader/runtime not compiled. |
| [Direct3D 12 memory management](https://learn.microsoft.com/en-us/windows/win32/direct3d12/memory-management) | Management burden and CPU/GPU synchronization | Official Microsoft docs reviewed | **STUDY** resource-management budget. |
| [NVIDIA current CUDA programming guide](https://docs.nvidia.com/cuda/cuda-programming-guide/) | GPU compute model, memory hierarchy, parallelism and scheduling | Official vendor docs reviewed | **STUDY/optional adapter**, CUDA does not cover AMD/Apple GPU/console and should not be mandatory for Forge scene generation. |
| [CUDA unified memory](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/unified-memory.html) | Unified/managed allocations have synchronization and placement semantics | Official vendor docs reviewed | **ADAPT memory accounting**; unified does not mean unlimited memory or no transfer cost. |
| [Apple Metal resource creation](https://developer.apple.com/documentation/metal/resource-creation) | Resource heaps, buffers, textures, command queues and shader libraries | Official Apple docs reviewed | **STUDY** macOS path; no Apple device benchmark. |
| [Metal memory heaps](https://developer.apple.com/documentation/metal/memory-heaps) | Heap synchronization/resource hazard modes | Official docs reviewed | **STUDY** portability and hazard contract; cannot assume behavior identical to Vulkan. |
| [WebGPU specification](https://gpuweb.github.io/gpuweb/) | Device features/limits, validation and device loss | Living community standard spec reviewed | **ADOPT feature-negotiation semantics**, not a guarantee browser/device support; pin normative version for build. |
| [WebGPU Shading Language](https://gpuweb.github.io/gpuweb/wgsl/) | Portable shading language grammar/validation and limit-related errors | Official spec reviewed | **STUDY** cross-backend shader pipeline. |
| [wgpu repository](https://github.com/gfx-rs/wgpu) | Cross-platform Rust graphics API; backend/shader translation path | Official repo index and source metadata viewed, not audited | **STUDY/ADAPT candidate** only after exact version, license/transitives and device tests. |
| [Khronos glslang](https://github.com/KhronosGroup/glslang) | GLSL/ESSL parsing, HLSL subset, SPIR-V generation | Official repo README/source tree identified | **STUDY**; review exact SPDX/component notices before bundling; no sample compiled. |
| [Khronos glslang license file](https://github.com/KhronosGroup/glslang/blob/main/LICENSE.txt) | Multiple licensed components/notices may be represented | Primary license file located | **License review pending exact revision/dependencies**; don't simplify to one blanket grant. |
| [Microsoft DXC repository](https://github.com/microsoft/DirectXShaderCompiler) | HLSL Shader Model 6+, DXIL compilation, and SPIR-V backend developments | Official repo README and releases inspected | **STUDY** shader toolchain, pinned binary/compiler validation required. |
| [DXC README](https://github.com/microsoft/DirectXShaderCompiler/blob/main/README.md) | Official README states University of Illinois Open Source License distribution | README reviewed; bundled third-party licenses not exhaustively audited | **License review pending** before inclusion. |
| [NVIDIA Nsight Graphics tools](https://developer.nvidia.com/nsight-graphics-features) | Frame capture/profiling and GPU resource diagnostics | Vendor overview reviewed | **ADAPT testing approach**; commercial runtime features change and device compatibility may vary. |
| [NVIDIA Nsight Graphics 2026.1 release notes](https://developer.nvidia.com/nsight-graphics/getting-started/release-note-v2026.1) | Example of tool feature changes; standalone Generate C++ Capture removed | Release note snippet checked | **Do not hard-code historic tool workflows**. |

## Production inferences versus sourced facts

**Sourced:** Vulkan/D3D12/Metal expose explicit resource/state/synchronization requirements; CUDA offers NVIDIA-specific compute; WebGPU validates against device limits and handles device loss; shader compiler output must match runtime/API requirements; device-specific memory budget and cache behavior are significant engineering considerations.

**MGR inference to test:** a unified admission layer around Forge-native scenes can select between CPU geometry, Blender rendering and optional GPU compute. This is an architectural proposal, not benchmark-backed superiority over existing engines. Pure CPU math can generate standard meshes, while high-end real-time rendering remains workload-dependent and normally benefits greatly from GPU hardware.

**Not verified:** owner Windows GPU model, memory, driver, CUDA support, Blender backend/device selection, actual cloud GPU billing, Max/MS/Intel support, macOS/console target execution, any frame rate/VRAM threshold for Forge assets, shader validity on production devices, or exact license grants for a planned pinned binary release.

## MGR rights and cost gate

1. Separate specification learning from code copy. For adopted binaries/code, pin upstream commit/release, component licenses, required notices, third-party bundled subprojects, patent/SDK conditions and export controls if applicable.
2. Proprietary console hardware/SDKs and distribution portals require authorization; no public GitHub source grants access to console build chains.
3. External GPU/cloud prices shift by region, quota, hardware and duration. Record live offers only when a deployment is chosen and separate monetary cost from creator waiting time.
4. GPU tools can collect full frame content and buffers; treat captures and asset references as sensitive, restrict uploads, and redact secrets/tokens from diagnostic logs.

## Field-test matrix required

- **Profiles:** no dedicated GPU/CPU renderer; low VRAM integrated; commodity discrete Windows GPU; high-end renderer; browser WebGPU where enabled; Mac Metal if hardware available; consoles only with authorized developer access.
- **Scenes:** tiny procedural cube; posed skinned hero; multiple 2K/4K texture variants; hundreds of animated actors; fog/FX; streaming world sectors; varying light/particles; ray-traced hero.
- **Telemetry:** scene hash, output image checksum, quality comparisons, cold/warm times, p50/p95/p99 frame/render, VRAM/RAM peak, transfer bytes, driver/tool version, graphics feature list, temperature/power if available and safe, failure/recovery observations.
- **Negative tests:** OOM simulation, unsupported feature, bad shader, invalid barrier, device loss, slow renderer, cache miss, oversized textures, nonfinite shader parameters, wrong gamma, cancellation mid-render, corrupted assets.
- **Pass/fail:** record target-specific thresholds **before** experiments; report UNKNOWN on missing hardware and never convert a CPU source-only test into GPU runtime proof.

Research provenance stage: `SOURCED`; strategic specifications partly inspected; **not** comprehensive tool source audit nor practical verification. Build-stage evidence must be tracked separately.
