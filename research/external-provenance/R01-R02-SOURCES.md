# External source audit ledger — R01 SIGGRAPH + R02 NVIDIA Research

**Inspected 2026-10-25.** Source statuses distinguish full original-paper reading, abstracts/project explanations, selected upstream entrypoint fragments and licenses. This batch **does not** cover entire SIGGRAPH proceedings or NVIDIA Research catalogs. No code copied into Forge, no papers reproduced, no test result claimed. MGR's native names and build decisions live in `research/source-audits/R01-SIGGRAPH.md` and `R02-NVIDIA.md`.

## R01 primary sources

| Selected research | Primary source | Depth of inspection | Code/rights status |
|---|---|---|---|
| Kerbl et al., *3D Gaussian Splatting for Real-Time Radiance Field Rendering* (SIGGRAPH 2023) | https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/ | Author project technical abstract, three contributions (sparse point start, anisotropic densification, visibility-aware splat); paper landing and published implementation pointer | https://github.com/graphdeco-inria/gaussian-splatting ; license https://github.com/graphdeco-inria/gaussian-splatting/blob/main/LICENSE.md is research/evaluation restricted; no commercial code adoption |
| Huang et al., *2D Gaussian Splatting for Geometrically Accurate Radiance Fields* (SIGGRAPH 2024) | https://surfsplatting.github.io/ | Original project method (oriented 2D surface disks), README plus selected actual `render.py` public source: render train/test views, bounded/unbounded surface extraction; ideal pinhole camera restriction | https://github.com/hbb1/2d-gaussian-splatting ; license https://github.com/hbb1/2d-gaussian-splatting/blob/main/LICENSE.md carries research/evaluation restriction; CUDA source and full modules not audited |
| *A Hierarchical 3D Gaussian Representation for Real-Time Rendering of Very Large Datasets* (SIGGRAPH 2024) | https://repo-sam.inria.fr/fungraph/hierarchical-3d-gaussians/ | Original technical overview, upstream README and public `render_hierarchy.py` output metrics/LOD parameter call signatures; **did not** derive precise tau semantics from optimizer | https://github.com/graphdeco-inria/hierarchical-3d-gaussians ; exact rights/submodules unresolved, no adoption |
| *Mesh-In-the-Loop Gaussian Splatting for Detailed and Efficient Surface Reconstruction* (SIGGRAPH Asia 2025) | https://anttwo.github.io/milo/ | Original project method description + implementation README: splat/SDF mesh consistency and differentiable extraction, install instructions | https://github.com/wei042/MILo ; README states code parts under original Gaussian-Splatting license; not cleared commercially |
| SIGGRAPH official proceedings index (context only) | https://www.siggraph.org/wp-content/uploads/2024/09/Conference-Papers.html | Index and high-level source discovery only; **not** reviewed each paper | No software permission inferred |

## R02 NVIDIA first-party sources

| Selected research | Primary source | Depth of inspection | Code/rights status |
|---|---|---|---|
| Bitterli et al., *Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting* (2020) | https://research.nvidia.com/sites/default/files/pubs/2020-07_Spatiotemporal-reservoir-resampling/ReSTIR.pdf | Original 17-page PDF accessible, method/weighted-reservoir formula and reuse principle; **not** a page-by-page mathematical proof reproduction | Research publication != software license; NVIDIA RTXDI SDK separately licensed |
| ReSTIR authors' official research page | https://research.nvidia.com/publication/2020-07_spatiotemporal-reservoir-resampling-real-time-ray-tracing-dynamic-direct | Original project summary emphasizing millions of dynamic lights and neighbor/frame reuse | RTXDI SDK https://github.com/NVIDIAGameWorks/RTXDI/; SDK terms https://github.com/NVIDIAGameWorks/RTXDI/blob/main/LICENSE.txt custom NVIDIA agreement; not blanket MIT |
| Zeltner et al., *Real-Time Neural Appearance Models* (SIGGRAPH 2024) | https://research.nvidia.com/labs/rtr/neural_appearance_models/ | Original project paper/architecture: hierarchical learned textures, decoder reflectance and importance-sampled directions, microfacet prior; PDF https://research.nvidia.com/labs/rtr/neural_appearance_models/assets/nvidia_neural_materials_author_paper.pdf inspected for available methods | No public code/weight reuse license verified from project reading |
| Wang et al., *Real-Time Level-of-Detail Rendering with ReSTIR* (SIGGRAPH 2026) | https://research.nvidia.com/labs/rtr/publication/wang2026levelOfDetail/wang2026levelOfDetail.pdf | Original PDF intro/abstract, surface-point mapping across topology-changing LoD, paper's example error comparison; detailed appendix/code not inspected | No source license/integration confirmed |
| Wu et al., *GATOR: Generative and Agentic 3D Object Reconstruction From Casual Images* (2026) | https://research.nvidia.com/labs/lpr/gator/ | Author method and examples; image/mask/geometry-to-Blender iterative edits; model/solver details not exposed in inspected page | Site stated **Code (Coming Soon)** as inspected; no public installable or licensed GATOR source attested |
| NVIDIA real-time graphics research index | https://research.nvidia.com/labs/rtr/ | Discovery list for additional related work only, e.g. radiance cache, ReSTIR variants, geometry LoD | Index is not full research extraction |

## Specific source-inspection limitations

1. **Math beyond summaries:** R01 3DGS and R02 ReSTIR concepts/equations are standard derivations from method descriptions; implementation edge cases, numerical proof and actual optimizer weights were not verified end-to-end. R01 2DGS had actual selected public source entrypoint inspected; the others were primarily author paper/project/readme content.
2. **Hardware:** These are primarily CUDA/GPU accelerated research methods. No benchmark/driver/platform test was performed on Time's Windows Blender machine. CPU-native *validation* is distinct from high-fidelity GPU *training/rendering*.
3. **Licenses:** Research publication permits study of ideas; it does **not** grant source code redistribution. The exact separately licensed implementation/submodules, model weights, sample images and output rights must be reviewed on a pinned commit.
4. **Reproducibility:** Publications may select favorable test scenes; Forge acceptance requires its own multi-view and physically collidable benchmark corpus with full per-scene receipts.
5. **Remaining queue:** full supplementary paper reading, pinned source trees and end-to-end setup, empirical hardware benchmarks, 2025/2026 wider SIGGRAPH paper scan, more NVIDIA materials/physics/caustics/radiance cache research, legal sign-off for production dependencies.

## Provenance-to-MGR mapping

| Scientific evidence | MGR design application | Must pass before production |
|---|---|---|
| Anisotropic splatting and surfel surface extraction | Visual/Physical Twin + Surface Witness | Held-out views, collider geometry, source rights |
| Hierarchical splat LOD | Hierarchical World Witness | Frustum/LOD transitions, native landmark IDs, memory budget |
| Mesh-in-loop optimization | Mesh Reality Loop | Geometry editability and cross-camera discrepancies |
| ReSTIR reservoirs and frame reuse | Light Memory | Moving occluders/lights, no ghosting, reference error |
| Neural hierarchical materials | Material Mind | BRDF/energy response, color consistency and rendering cost |
| Cross-topology LoD mapping | Scene Continuity Renderer | Detail switching and camera motion flicker bound |
| Agent-assisted mesh refinement | Reconstruction Inspector | Actual Blender edits, owner-locked identities and 3D QA |
