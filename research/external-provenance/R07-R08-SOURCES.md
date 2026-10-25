# R07–R08 — Khronos Technical Source and Licensing Ledger

**Reviewed:** 2026-10-25. **MGR-native audits:** `research/source-audits/R07-OPENGL.md` and `research/source-audits/R08-VULKAN.md`. This file records external technical provenance; it is not the MGR product feature namespace. All claims are research-level, not hardware-tested.

| Source owner | Authoritative source | Version/date observed | Supported architectural finding | Review depth / next verification |
|---|---|---|---|---|
| Khronos OpenGL working group | https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf | **OpenGL 4.6 Core Profile**, released May 5, 2022 | Defines stateful programmable graphics operations, clip/depth, buffer/texture/FBO operations and context-level rules. | Formal spec discovery and key semantic review, not full 700+ page clause-by-clause audit. Pin immutable PDF hash before coding. |
| Khronos OpenGL registry | https://registry.khronos.org/OpenGL/index_gl.php | Registry checked 2026-10-25 | Maintained list of current core API/GLSL, extension and platform bindings. | Registry page inspected; extensions and minimum context requirements need exact runtime checks. |
| Khronos GLSL official language specification | https://github.com/KhronosGroup/OpenGL-Registry/blob/main/specs/gl/GLSLangSpec.4.60.pdf | **GLSL 4.60** | Shader semantics, stage/interface, type rules and programmable shading expectations. | Official PDF/source path discovered; local compiler/driver shader behavior untested. |
| Khronos GL reference pages | https://registry.khronos.org/OpenGL-Refpages/gl4/html/start.html | 4.6 core docs | Individual command semantics and relevant feature errors for implementation-time contract tests. | Official documentation only; no GL function called locally for this audit. |
| Khronos Vulkan registry | https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html | **Vulkan 1.4.366** with registered extensions observed 2026-10-25 | Explicit commands, object lifetime, shader modules, feature queries, descriptors, memory and synchronization. | **Mutable latest URL**. Pin exact specification revision/core vs registered-extensions scope and source commit before code; this is not complete 40MB source inspection. |
| Khronos ratified Vulkan publication | https://registry.khronos.org/vulkan/specs/latest-ratified/pdf/vkspec.pdf | Latest ratified distribution indexed October 2026 | Stable baseline may differ from unratified/provisional extensions published in the mutable all-registered spec. | Verify revision/release and extensions explicitly; don't assume all extension features are available. |
| Khronos Vulkan depth guide | https://docs.vulkan.org/guide/latest/depth.html | First-party latest guide, accessed 2026-10-25 | Vulkan viewport depth mapping and clipping depend on selected projection/depth configuration. | Official guide inspected, shader/projection executable proof still required. |
| Khronos Vulkan synchronization guide | https://docs.vulkan.org/guide/latest/synchronization.html | First-party latest guide | Synchronization primitives establish execution/memory dependencies and explicit application responsibility. | Guide reviewed; test barriers with actual validation layers and runtime. |
| Khronos Vulkan synchronization examples | https://docs.vulkan.org/guide/latest/synchronization_examples.html | First-party latest guide | WAW/RAW hazard, image layout and command dependency patterns must be tied to actual stages/access masks. | Illustrative patterns inspected; must be adapted to exact pipeline rather than copied indiscriminately. |
| Khronos SPIR-V / GLSL ecosystem | https://github.com/KhronosGroup/glslang | Maintained upstream | GLSL/ESSL shader frontend and SPIR-V generator; compiler target environment matters. | Repository description inspected, no source vendoring or binary run. Pin commit/release, license and build flags before adoption. |

## Explicit distinction between API and Forge-native render design

- OpenGL defaults to symmetric clip-space Z before viewport transform; Vulkan uses zero-to-one Z clipping. A conversion or appropriate projection is required and must be tested with camera geometry.
- Both APIs supply programmable raster/compute mechanics but **neither standardizes physically based BRDF, artistic lights, camera continuity, animation topology or game world creation**. Those remain independently designed MGR systems.
- “Ray tracing,” “mesh shading,” certain compute features and hardware-backed acceleration are **feature-/extension-/device-specific**; spec listing does not guarantee availability on the owner's Windows computer.
- GPU shader outputs may be visually similar while physically wrong: compare exact numerical depth/UV/normal/linear-light fixtures and source geometry receipts before quality claims.
- Vulkan's explicit synchronization and memory management offer opportunities for throughput but create complex failure cases; adding it before an operational need is proven can slow Forge development.

## Legal and cost checks

Reading official Khronos specifications is not license to copy sample shaders, extension source, vendor demos, test textures, asset packs, SDK source or external graphics wrappers into a commercial product. Audit each installed tool/library at exact release and independently track the license, binary redistribution terms, attribution and any GPU-driver deployment limits. The APIs themselves do not require metered model API payments; hardware, support, engineering and compute time are real costs. No external assets or code were copied into these reports.

## Open independent verification

Need actual Windows GPU/vendor/driver enumeration, driver context creation and shader toolchain checks; device-independent synthetic projection expectations; shader compilation diagnostics; canonical offscreen images; barrier/host coherence tests; cross-driver tests if available; CPU fallback and Blender import/render comparison. **These source audits are research artifacts, not proof of an installed or passing native GPU renderer.**
