# S07 — External Technical Provenance: Rendering Systems

**Research date:** 2026-10-25. **Inspection depth:** Official specifications, technical manuals and selected published implementation descriptions; individual dependencies, example files and every source-code path **not exhaustively audited**. This document keeps citations and licensing limitations separate from the MGR-native design in `research/chapters/S07-COMPUTER-GRAPHICS.md`.

| Primary authority | Source | Grounded finding | Allowed MGR-derived purpose / caution |
|---|---|---|---|
| Khronos Group | [Vulkan rasterization specification](https://docs.vulkan.org/spec/latest/chapters/primsrast.html); [shader stages](https://docs.vulkan.org/spec/latest/chapters/shaders.html); [Vulkan registry](https://registry.khronos.org/vulkan/) | Primitive rasterization, fragment sampling and graphics shader stage ordering are specified. | Design renderer-neutral pixel/depth/triangle witnesses; do not imply Vulkan alone supplies a complete art/world editor. |
| Khronos Group | [OpenGL fragment shader reference](https://wikis.khronos.org/opengl/Fragment_Shader) | Fragment shaders process raster-generated fragments and may output colors/depth. | Define preview channel and fragment-depth QA; guide standards-based interoperability. |
| Pharr/Jakob/Humphreys, PBRT v4 | [Contents](https://www.pbr-book.org/4ed/contents); [light transport](https://www.pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/The_Light_Transport_Equation); [system overview](https://www.pbr-book.org/4ed/Introduction/pbrt_System_Overview) | Ray-integrator architecture and stochastic estimation of surface/lighting contributions explained with open implementation. | Study integrator contracts, sampling noise and correctness tests. No claim to have recreated the complete system. |
| PBRT maintainers | [User guide](https://pbrt.org/users-guide-v4); [public code](https://github.com/mmp/pbrt-v4) | Alternative integrators, including path and bidirectional path tracing, address different transport situations. | Optional independent reference binary and synthetic test scenes after exact license+asset provenance review. |
| PBRT v4 authors | [Preface](https://www.pbr-book.org/4ed/Preface) | GPU ray tracing can dramatically outperform CPU in selected workloads, with author examples of 10–100×. | Treat as research example, **not** a universal speed or pricing guarantee. Benchmark actual scene and Windows hardware. |
| Blender Foundation | [Rendering overview](https://www.blender.org/features/rendering/); [Cycles sampling docs](https://docs.staging.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html) | Cycles supports CPU/GPU and path tracing; noise/sample/denoiser choices impact performance and quality. | Native Blender bridge should record device, samples, seed, noise threshold, denoiser and paths. Latest docs should be checked against installed version. |
| Blender developers | [Cycles GPU rendering documentation](https://docs.staging.blender.org/manual/en/latest/render/cycles/gpu_rendering.html); [device architecture](https://developer.blender.org/docs/features//cycles/devices/) | GPU backends have availability and feature/memory constraints, device-specific implementation details. | Probe capabilities at runtime; implement CPU fallback; do not assert all GPU devices behave equivalently. |
| Blender Foundation | [Blender requirements](https://www.blender.org/download/requirements/) | Supported CPU/GPU requirements and platforms are version-dependent. | Support and installation matrix needs actual version and driver discovery. |
| OpenEXR project / Academy Software Foundation | [OpenEXR introduction](https://openexr.com/en/latest/about.html); [concepts](https://openexr.com/en/latest/concepts.html); [project overview](https://openexr.com/en/latest/) | EXR is purpose-built for high-dynamic-range, scene-linear image values and supports richer channel/multiview workflows. | Retain EXR truth passes; use PNG/JPEG only for display derivatives. Check exact dependency/codec licenses before bundling. |
| Academy Software Foundation | [OpenColorIO overview](https://opencolorio.readthedocs.io/en/latest/concepts/overview/overview.html); [color spaces](https://opencolorio.readthedocs.io/en/latest/guides/authoring/colorspaces.html) | Working-space transformations, display views and config management are explicit stages. | Hash OCIO config/view per render; reject uncalibrated sRGB/linear comparisons. Inspect exact config and font/HDRI dependencies separately. |

## S07 due-diligence distinctions

1. A published algorithm is not a complete technical implementation blueprint for a production world engine; memory management, real-time navigation, multi-platform drivers, geometry formats, QA and security remain substantial engineering.
2. Realtime raster preview, offline path-traced reference, and 3D scene inference from images solve different problems; high similarity of two rendered views does not prove unseen geometry or arbitrary viewpoint identity.
3. A machine without a discrete GPU can render basic geometry and frames on CPU; practical per-frame performance must be measured rather than declared. Rendering a large world at gaming frame rates is a different budget from rendering a still image overnight.
4. Denoising and aggressive tone mapping can conceal sampling defects. All scientific comparisons require a locked configuration and retained pre-display linear buffers.
5. Before copying example code/assets, inspect repository and **specific file/dataset** licenses. Citation of a paper does not authorize use of its referenced scene or textures.

## First experiments necessary to turn research into proof

- Execute MGR-authored single-triangle and occluded-plane tests with depth/object-mask truth and saved scene hash.
- Render fixed gray/metal/rough spheres at at least three samples budgets; preserve raw EXR, denoised output and viewed PNG. Quantify noise against higher-sample reference.
- Render the same locked scene in quick and reference modes; record projection, materials, light transport, color transforms, image metrics and visual discrepancy regions.
- Run camera motion/disocclusion clip with repeated seeds; detect temporal ghosting and disappearing thin geometry.
- Record CPU elapsed/wall times and peak working set; optionally compare GPU only when a supported device is positively discovered.

**Assessment:** Primary research supports a native MGR verification/orchestration layer wrapped around established renderers, but does not establish independent full renderer creation or production acceptance. Keep S07 research and code evidence separate.
