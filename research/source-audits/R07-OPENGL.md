# R07 — MGR Graphics Driver Audit: OpenGL

**Date:** 2026-10-25. **Authoritative baseline:** Khronos OpenGL **4.6 Core Profile** specification, May 5, 2022, and GLSL **4.60** specification; current registry on research date. **Audit maturity:** official specification/API and shader pipeline **research reviewed**, NOT end-to-end implementer source audit and NOT hardware/runtime acceptance. Upstream source links and licensing caveats live in `research/external-provenance/R07-R08-SOURCES.md`.

## 1. Definition

OpenGL is a stateful cross-platform graphics API for issuing drawing and compute commands to an installed driver-backed rendering context. It does not itself model characters, infer geometry, bake PBR materials or provide an entire game/world engine. Its programmable vertex/fragment shader stages, buffers, textures, framebuffers and synchronization can underpin an original MGR-native viewport with controlled hardware acceleration, provided Forge owns correct scene/mesh/material contracts.

## 2. Forge usage

GPU real-time preview, independent GLB mesh sanity render, multi-camera turntables, scene-occlusion/depth maps, UV checker panels, skeletal mesh display, procedural geometry visualization, world chunk culling, FX particles, image difference and near-real-time quality receipt capture. CPU procedural creation and export stay functional when GL context is absent.

## 3. Standards and precise conventions

- Default OpenGL clip coordinates: homogeneous `-w≤x,y,z≤w`; perspective division produces NDC `x,y,z ∈[-1,+1]`. With default depth range, viewport maps z to `[0,1]`. Extensions/core control can change clipping convention; **record the actual clip-control state**.
- Column/row matrix layout is a storage issue independent from matrix-multiplication semantics. Shader projection/view/world transformations must follow S04 frame tags and prove orientation by rendered axis fixtures.
- Face winding/cull mode, normal inverse-transpose for nonuniform scale, primitive topology, indexed drawing and buffer offsets require explicit validation.
- sRGB textures/framebuffer conversions and linear-space physically based material calculations are separate choices. OpenGL **does not mandate a PBR BRDF or material authoring model**.
- OpenGL 4.6 availability depends on GPU driver/context. Query API/profile, extension support, GLSL version and limits instead of assuming runtime presence.

## 4. Rendering mathematics

Vertex path converts local mesh to world/view/clip then rasterizes interpolated attributes, resolves depth and shades fragments. Color correctness requires linear-light work, texture decode (sRGB where appropriate), normal and roughness interpretation and output-space management. Depth precision depends on z-near/far ratio and chosen projection/depth mapping; a too-small near plane can destroy distance precision. Shadow algorithms and environment lighting are Forge choices rather than OpenGL guarantees.

## 5. Primary engineering lessons

- State objects for VAOs, VBOs/EBOs, programs, textures, FBOs and samplers must be updated in defined order and scoped/cleaned with lifecycle receipts.
- Shader compile/link reports are runtime evidence; GLSL syntax acceptance alone does not guarantee correct pixels, physically realistic shading or cross-driver determinism.
- Compute shaders are possible on supporting core contexts; shared memory access requires defined barriers and memory visibility. A compute shader is not automatically faster than CPU at small workloads.
- Context/thread ownership and asynchronous GPU completion affect readback and frame capture. Errors must be surfaced and logged, not silently ignored.

## 6. Tools/models

Official spec and reference pages are sufficient to define a minimal renderer. A shader compiler, driver-debug layer or wrapper might be used after exact license/version review. **Neural generation is unrelated** to the OpenGL ABI; models may provide texture candidates but do not implement rasterization correctness.

## 7. Fixtures/data

Native synthetic geometry only: axis tripod, winding cube, mirrored normals, tangent-space sphere, UV checker, roughness/metal grids, 16-bit/32-bit depth gradient, overlap/depth occlusion, skinning pose samples, shader compile-negative fixtures, empty and oversized buffers.

## 8. Licensing

Specification learning does not import source. Context/window libraries, shader compilers, sample shaders, glTF demo meshes and texture imagery require their own version/asset licenses. Link to original references in external provenance. No API keys or paid providers needed.

## 9. Runtime API contract

Expose `RendererCapabilities`, `RenderJob`, `RenderReceipt`, typed `MeshHandle` and `SurfaceMaterial`; the GL-specific adapter translates them to stateful driver calls. Never make the MGR asset schema dependent on OpenGL identifiers. Support clean no-GPU fallback: offline Blender render or CPU geometric/quality checks with explicit reduced feature set.

## 10. MGR native design

**MGR Visual Core / GL Preview Adapter:** capability handshake → shader/material validation → mesh upload with attribute bounds → camera frame conversion → raster lighting/depth → offscreen FBO → GPU readback → independently check screenshot/geometry and emit signed receipt. Material design belongs to MGR Surface Truth; the adapter maps validated BRDF inputs into GLSL, not an imported studio's design language.

## 11. Hardware

GPU with matching version/driver needed for actual OpenGL 4.6 context. Texture capacity, MSAA, shadow maps, skinning joints and HDR render targets use VRAM; frequent readbacks can stall the pipeline. CPU-only machines may still run Forge's geometry, transforms, raster-independent tests and export. Profile rendering at 720p/1080p and target worlds before making performance promises.

## 12. Costs

No per-render software API fees implied. Actual costs are code/devices/test matrix, driver maintenance, electricity and memory. An OpenGL renderer is not automatically cheaper to build than using installed Blender; prioritize it only for live navigation/independent verification when the existing viewport cannot meet measured goals.

## 13. Failure modes

Wrong clip convention causes clipped meshes; row/column confusion mirrors or displaces assets; winding mismatch hides triangles; normals/tangent sign error corrupts PBR; linear/sRGB confusion causes dark/washed textures; missing memory barriers causes nondeterministic compute; unsupported context causes startup failure; bad FBO completeness yields black captures; near/far depth precision creates z-fighting. Each should have a fixture and a descriptive failure receipt.

## 14. Performance/visual metrics

Frame time median/p95, scene triangle count, draw calls and state switches, upload/readback time, VRAM peak, shader compilation time, capture determinism, depth/normal/UV reference errors, per-camera render differences, and GPU-vs-CPU correctness. Record resolution, driver/GPU/version and whether measurements include shader warmup.

## 15. Forge placement

Implement optional `forge/render_backends/opengl_adapter.py` behind shared `RenderJob`/`RenderReceipt` contracts, connecting camera S04, materials, scene geometry, rigs, FX and Visual Judge. Do not replace the already working procedural CPU baseline or its GLB exporter. This audited document alone does **not** prove a functioning OpenGL backend currently exists.

## 16. Acceptance criteria

1. Query/prove actual GL 4.6 core or downgrade/fail explicitly; refuse unsupported shader features.
2. Render exact known XYZ axes and cube against independent CPU projection; pixel landmarks/handedness/depth within configured tolerance.
3. Test perspective near/far and partially clipped geometry, reversed depth if opted in, rotated cameras and high-coordinate scenes.
4. Verify GLB imported mesh attribute lengths/indices/winding/UVs; corrupted inputs fail before GPU calls.
5. Render linear and sRGB test ramps, base-color/normal/roughness/metallic grids and UV checker; compare known reference images without claiming a universal artistic realism number.
6. Compile a deliberately malformed shader and unsupported-version fixture; shader errors appear in structured receipt, no silent black output.
7. Compute shader read/write visibility works with barrier and detects missing synchronization in controlled development tests.
8. Offscreen capture round-trips with proper FBO completeness, dimensions, color depth and frame hash. GPU capture path independent from beauty-only image.
9. Benchmark 1k/100k/1m triangles and 10/100/1000 instances on installed Windows GPU plus CPU/no-context fallback; record actual timings/VRAM.
10. Independently cross-check at least one asset in Blender or another renderer; do not label a matching screenshot as mesh/identity equivalence proof.

**Truthful status:** R07 source research and implementation/test design completed. GPU adapter and real OpenGL hardware results are **not verified** by this audit.
