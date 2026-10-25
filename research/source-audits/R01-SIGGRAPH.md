# R01 — SIGGRAPH Research Extraction for MGR Forge

**Research pass:** 2026-10-25. **Scope:** four selected high-value original SIGGRAPH/SIGGRAPH Asia graphics works; **not the entire proceedings or archive**. This is a deeper *method/selected entrypoint* review than a title catalog, but **not** a full proof reproduction or exhaustive source audit. External attribution stays in `research/external-provenance/R01-R02-SOURCES.md`; this report defines MGR-owned opportunities.

## Decision table

| Selected paper | Practical algorithm to learn | Native feature derived | Adoption gate |
|---|---|---|---|
| SIGGRAPH 2023: 3D Gaussian Splatting | Optimizable 3D anisotropic Gaussians, adaptive densification, visibility-aware projected alpha compositing | **MGR View Fabric** — transient visual surface proxy with camera+uncertainty | Mathematical idea only: INRIA reference is research/evaluation-only |
| SIGGRAPH 2024: 2D Gaussian Splatting | Oriented 2D surfel disk projection, geometry-consistent depth/normal reconstruction and TSDF surface extraction | **MGR Surface Witness** — compare observed geometry against renderable appearance | CUDA source reference restricted; calibration/pinhole assumptions |
| SIGGRAPH 2024: Hierarchical 3D Gaussians | Coarse-to-fine partition and hierarchy for large scenes, varying detail by view | **MGR Infinite District LOD** — multi-resolution streaming and coverage receipts | Existing reference source rights unresolved; no code imported |
| SIGGRAPH Asia 2025: MILo | Couple splat photometric optimization with differentiable surface mesh; align SDF/mesh-render consistency during reconstruction | **MGR Mesh Reality Loop** — appearance/mesh disagreement audit and mesh refinement | Contains original 3DGS licensed components; not cleared commercially |

## Technique 1 — Visual primitives and camera-based evidence

**Read depth:** INRIA original project abstract plus original Gaussian-splatting paper landing; inspected linked upstream repo/license during S16 and this pass. Method from original authors: start from structure-from-motion calibrated sparse points; attach anisotropic covariance (ellipsoid footprint), opacity and direction-dependent color to each Gaussian; project into the camera and alpha-blend by visibility; optimize color/covariance/position and split/prune primitives guided by gradient/density. Mathematical 3D Gaussian density proportional to `exp(-0.5 (x-μ)^T Σ^{-1} (x-μ))`, with positive-definite `Σ=R S S^T R^T` parameterization. Front-to-back transmittance accumulation follows `C = Σ_i T_i α_i c_i`, `T_i = Π_{j<i}(1-α_j)` after visibility/depth ordering. This is a radiance *proxy*, not proof of solid surfaces, topology or collision.

**MGR translation:** `VisualProxy` carries source camera evidence, approximate view confidence, splat bounds and output rights; `PhysicalMesh` remains separate. At near-unseen views, lower trust and request new capture rather than hallucinating geometry as ground truth. **Acceptance:** synthetic known 3D scene, train/view split, image and depth differences; no collider automatically created from translucent splat density. **Compute:** official implementation uses CUDA rasterizers/GPU and trained optimization; CPU analytic projection math alone is affordable but not comparable to full scene training. **License:** original repo explicitly limits use to research/evaluation; do not vendor. Independent Apache `gsplat` can be assessed with pinned dependency rights.

## Technique 2 — Surface-first radiance from oriented disks

**Read depth:** original 2DGS project/repo README, listed supported ideal pinhole camera assumption, `render.py` actual entrypoint and selected `gaussian_renderer`/`gaussian_model` source snippets. Instead of free-floating volumetric ellipsoids, each primitive is an oriented 2D disk/surfel embedded in 3D, with perspective-correct differentiable rasterization; the geometric orientation supports normal/depth regularization. Observations across cameras should constrain a shared surface. The repository's actual `render.py` renders training/held-out cameras and calls extraction with bounded `voxel_size`, `sdf_trunc`, `depth_trunc`, plus unbounded `mesh_res`; mesh export uses Open3D and post-processes clusters. This concrete code path is **inspected via public source**, not executed. Its camera assumption may break for fisheye/uncorrected lenses.

**MGR translation:** a native *surface observation layer* stores `(surfel_position, normal, camera_support, depth_uncertainty)` separate from retopologized mesh. Compare extracted mesh silhouettes and held-out depth against measured rays; an incorrectly connected thin chain/Tevin hand fails even if one angle looks great. **Acceptance:** known box/concave synthetic scene from 8 cameras, recomputed normals, depth consistency, hole and self-intersection tally, fisheye input rejection unless undistorted. **GPU/rights:** CUDA rasterizer; repo `LICENSE.md` carries research/evaluation-only original terms. No MGR commercial code copy.

## Technique 3 — Large-world hierarchical image evidence

**Read depth:** original INRIA project page, upstream README and publicly indexed `render_hierarchy.py` source entrypoint. Large visual reconstructions need multi-resolution detail levels. The implementation's render entrypoint loops over specified hierarchy thresholds (`tau`, e.g. default `0,3,6,15`) and evaluates held-out images using PSNR/SSIM/LPIPS. This reveals a useful engineering interface—controllable LoD and quantitative output comparison—but these paper-specific threshold semantics must not be guessed from variable names without reading optimizer internals.

**MGR translation:** own spatial tile tree and `LODReceipt` linking world-coordinate region, camera distance, allowed error, mesh/splat budgets, collision fidelity and source view count. Invisible splat/mesh geometry shouldn't consume full resolution; important collision surfaces need separate representation regardless of camera distance. **Acceptance:** zoom scene by 100× with stable landmark coordinates, cross-chunk seams, visual deviation curves vs LOD, peak VRAM and visible pop rate. **Hardware/rights:** reference uses GPU-trained 3DGS; render source displayed CUDA deallocation; exact reference license/tree must be audited, no deployment authorization implied.

## Technique 4 — Put editable geometry into the optimization loop

**Read depth:** SIGGRAPH Asia 2025 MILo official paper/project summary and `README.md` technical method/installation. This architecture addresses the classic splat problem: an image renders beautifully but cannot become a usable mesh. MILo couples 3DGS image consistency to a differentiable Gaussians-to-mesh/SDF extraction, using agreement between volumetric Gaussian renders and mesh renders to initialize/fit surface estimates. Reported ability to reconstruct detailed meshes is a paper claim, not reproduced here. It builds on original 3DGS reference code and includes its restrictive license.

**MGR translation:** **MGR Mesh Reality Loop** compares render from candidate neural/splat representation against render from physical mesh under the *same calibrated cameras*, then emits region-level residuals and owner-safe mesh repair proposals. Mathematical core is a multiobjective loss such as `L = λ_img L_img + λ_sil L_sil + λ_depth L_depth + λ_surf L_surface + λ_topo L_topology`; chosen weights/coupling to true differentiable renderer must be experimentally tuned and are **MGR design**, not a reproduction of paper implementation. **Acceptance:** synthetic cup handle + chain, detect where mesh loses thin structure despite attractive splat and require edit/owner approval. **License:** pipeline's source inherits restrictions; use ideas to implement independent native validators or vetted permissive solvers.

## Cross-source extracted MGR-native feature contract

1. **MGR Visual/Physical Twin:** never conflate radiance and collision; render proxy plus editable mesh with mandatory layer alignment.
2. **MGR Evidence Occlusion Ledger:** observed cameras, unseen surfaces, generated fill and owner-authored changes tracked by region.
3. **MGR Multi-View Truth Gauntlet:** held-out images, silhouettes, depth, normals and physical interactions in one QA contract.
4. **MGR Hierarchical World Witness:** region/LOD visual confidence and performance budget, with stable landmark and collision data.
5. **MGR Mesh Reality Loop:** targeted geometry repair from known visual-vs-mesh mismatch.

## Recommended native implementation sequence

**CPU-first:** typed camera/surface/mesh contracts → synthetic multi-view Blender render corpus → held-out projection/depth and silhouette comparison → visual/physical mismatch heatmap → chunk/LOD receipts. **GPU gated:** compare allowed model output/rasterization libraries as optional high-density workers only after confirmed license and VRAM. **Stop claims:** no in-repo paper replication or owner hardware GPU measurements were performed in this research task.

## Shared acceptance suite

- One-view ambiguous backside flagged, not 'reconstructed' as observed.
- 4+ withheld camera views with logged silhouette/depth/PSNR or image metric, asset license and camera calibration.
- Physical collider test for a traversable scene, independent from splat render FPS.
- Thin/concave geometry and separated Tevin garment/chain/hand landmarks retain geometry across views and mesh conversion.
- LOD traversal has stable coordinate/asset IDs, no missing collision and bounded visual pop; record CPU/GPU/RAM plus failed jobs.
- All optimizers are replayed from pinned versions/weights/datasets before commercial use.

## Evidence gaps queued

Full paper derivation and supplementary equations for each selected method, end-to-end reading of training/renderer/densification and surface extraction code, environment setup, full license/submodule audit, reproducibility on MGR hardware, broader SIGGRAPH 2025/2026 proceedings screen and controlled baseline comparisons. **This selected four-paper packet is not completion of the SIGGRAPH archive.**
