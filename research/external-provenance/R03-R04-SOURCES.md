# R03/R04 — Primary External Provenance Ledger: Public Pixar and Disney Technical Research

**Captured:** 2026-10-25 · **Inspection depth:** Technical publication pages, selected detailed paper PDFs and official project documentation; **not** entire code repositories, complete mathematics proofs, private studio implementation or asset-license clearance. The MGR-native engineering interpretation lives in `research/source-audits/R03-PIXAR.md` and `research/source-audits/R04-DISNEY.md`, without external vendor names as feature titles.

## R03 — Pixar-origin public techniques

| Primary artifact | Technical finding | Assessment/limits |
|---|---|---|
| [Feature Adaptive GPU Rendering of Catmull–Clark Subdivision Surfaces, Niessner/Loop/Meyer/DeRose](https://graphics.pixar.com/library/GPUSubdivRenderingA/paper.pdf) | Patch refinement and feature-adaptive subdivision of Catmull–Clark surfaces for high-performance GPU display; controls can select view-dependent tessellation depth. | Detailed original paper sampled. Validate irregular vertices, crease/boundary rules, numerical limit accuracy on installed implementation. |
| [OpenSubdiv Overview](https://graphics.pixar.com/opensubdiv/overview.html); [official technology library](https://www.pixar.com/technology-libraries) | Public CPU/GPU subdivision libraries, intended for high-performance evaluation. | Official source overview; no current version's dependency/license files exhaustively inspected. |
| [OpenUSD introduction](https://openusd.org/release/intro.html); [USD composition course](https://graphics.pixar.com/usd/files/Siggraph2019_USD%20Composition.pdf) | Layered opinions, references, payloads, variants and time samples compose non-destructive reusable scenes. | Public primary docs; no promise of all exporter/importer feature equivalence. |
| [Importance Sampling of Reflections from Hair Fibers](https://graphics.pixar.com/library/ImportanceSamplingHair/paper.pdf); [published JCGT article](https://jcgt.org/published/0001/01/01/) | Importance-sampled scattering from cylindrical fibers improves Monte Carlo angular response efficiency, based on Marschner-type reflectance. | Direct Pixar-authored paper; no independent reproduction or production hair benchmark. |
| [A Data-Driven Light Scattering Model for Hair](https://graphics.pixar.com/library/DataDrivenHairScattering/paper.pdf) | Research into practical sampling/fiber light models and costly multi-fiber appearance. | Selected source abstract/text; performance and appearance cannot be asserted for MGR without running witnesses. |
| [Pixar's Foundation for Materials](https://graphics.pixar.com/library/PxrMaterialsCourse2017/paper.pdf) | Production material/fiber shading categories expose physically based appearance controls. | Public technical course; does **not** license proprietary RenderMan materials or give MGR software implementation rights. |
| [Hair Emoting public research](https://graphics.pixar.com/library/HairEmoting/index.html) | Layered, surface-aware curve deformation and level-of-detail grooming in artist-directed animation. | Public publication page; detailed source code and animation assets not inspected. |
| [Pixar global technical archive](https://graphics.pixar.com/library/index.html) | Additional source pathways for render/culling/light transport and geometric animation literature. | Index used for discovery, not evidence every archived paper was read. |

## R04 — Disney-origin public techniques

| Primary artifact | Technical finding | Assessment/limits |
|---|---|---|
| [Physically-Based Shading at Disney, Brent Burley, SIGGRAPH 2012](https://disneyanimation.com/publications/physically-based-shading-at-disney/) | Artist-facing physically based BRDF look controls for surface materials. | Paper's official summary; renderer implementations and precise equation variants must be validated separately. |
| [An Artist-Friendly Hair Shading System](https://disneyanimation.com/publications/an-artist-friendly-hair-shading-system/) | Technical scattering complexity presented through useful art-direction controls, in original studio hair workflow. | Official research publication; internal pipeline unavailable. |
| [A Practical and Controllable Hair and Fur Model for Production Path Tracing](https://www.disneyanimation.com/publications/a-practical-and-controllable-hair-and-fur-model-for-production-path-tracing/) | Energy-conserving fiber scattering, near-field evaluation and roughness/control parameterization. | Paper page reviewed; no complete shader code audit. |
| [Smoothed Aggregation Multigrid for Cloth Simulation](https://disneyanimation.com/publications/smoothed-aggregation-multigrid-for-cloth-simulation/); [original technical PDF](https://media.disneyanimation.com/uploads/production/publication_asset/131/asset/paper.pdf) | Contact-constrained cloth solving with algebraic multigrid preconditioning; reports 6–8× case-specific speedups on a 371k-vertex dressed character. | Original numerical result has no generic hardware/simulation guarantee; detailed solver implementation not reproduced. |
| [Subdivision Based Nonlinear Multiscale Cloth Simulation](https://www.disneyanimation.com/publications/subdivision-based-nonlinear-multiscale-cloth-simulation/) | Recursive multilevel trust-region solving of nonlinear cloth equations. | Official paper summary; benchmark and source not reproduced. |
| [Sackcloth or Silk? Appearance vs Dynamics Perception](https://www.disneyanimation.com/publications/sackcloth-or-silk-the-impact-of-appearance-vs-dynamics-on-the-perception-of-animated-cloth/); [perceptual garment control](https://la.disneyresearch.com/publication/garment-simulation/) | Material appearance and motion jointly affect judgments; perceptual parameters can guide a physical solver. | Public papers/pages. Perceptual data do not prove a universal numerical cloth model. |
| [Computer-Assisted Animation of Line and Paint in Paperman](https://media.disneyanimation.com/uploads/production/publication_asset/122/asset/pman.pdf); [publication page](https://www.disneyanimation.com/publications/computer-assisted-animation-of-line-and-paint-in-disneys-paperman/) | Forward/backward motion fields enable 2D vector strokes and paper texture to track 3D animated geometry over time. | Direct original technical paper inspected; proprietary authoring tool not available to MGR. |
| [Disney Hair Pipeline: Crafting Styles from Design to Motion](https://www.disneyanimation.com/publications/disneys-hair-pipeline-crafting-hair-styles-from-design-to-motion/); [public simulation process](https://www.disneyanimation.com/process/simulation/) | Separate groom/rig/simulation/look stages with two-level motion controls and art direction. | Public workflow summary; cannot imply studio's private solver/asset access. |

## MGR legal and research boundary

1. *Research source* is not *licensed source code*. A paper's publicly posted PDF does not grant rights to proprietary studio implementations, film characters, production assets, specific animations or screenshots.
2. OpenSubdiv and OpenUSD are publicly available implementations subject to their own version-specific licenses and dependency notices. Exact terms must be checked before vendoring; retain notices and record source revision.
3. Technique descriptions and mathematical foundations may inspire independent MGR designs; do not copy unreviewed shader code, proprietary textures, Disney/Pixar assets, distinctive film content or restricted datasets.
4. Tests in R03/R04 are **proposed**; none of the papers' original experiments or actual TEVIN asset proofs was rerun within this research-only branch.
5. Theoretical models, user-friendly controls, and artistic effects should be linked to measurable outputs (geometry error, hair angular scattering, garment collisions, cloth solver residual, temporal stroke coherence) before any claims of production readiness.

## MGR practical proof set

- **Subdivision:** feature-adaptive mesh with creases/UVs/extraordinary vertices and limit error vs reference.
- **Composition:** non-destructive outfit, jewelry, hair and rig layers preserve owner-approved TEVIN base across revision and export.
- **Hair:** strand attachment, scattering under angular light sweep, density/LOD and motion continuity.
- **Cloth:** separated garment simulation with stretching/shearing/bending/contact tests and independent performance numbers.
- **Hybrid animation:** view-dependent expressive strokes tracked by actual 3D motion vectors, with known occlusion masks and temporal stability.
- **Materials:** semantic parameter mapping across Blender preview/reference render, EXR numeric samples and explicit color pipeline.

**Conclusion:** These public sources support several feasible and differentiated MGR systems; they do **not** unlock hidden proprietary studio software. MGR value comes from new native orchestration, quality gates, authored source and a more flexible creator experience—not misattributed code.
