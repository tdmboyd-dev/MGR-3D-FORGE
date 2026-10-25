# MGR Neural Shape Intelligence & World Perception

**Scope:** S16 generative 3D, image-to-mesh, NeRF, Gaussian splatting, neural reconstruction, video/world models and the gap between plausible images and editable physical worlds. **Owner:** MGR. **Date:** 2026-10-25. **Evidence maturity:** primary developer papers, repositories, model cards, technical setup/licensing inspected; **not** an end-to-end source audit, downloaded-model benchmark or model license clearance. **Build maturity:** MGR-native architecture and acceptance contracts proposed below, unless verified elsewhere by code/test receipts.

## Core verdict

Time's instinct is partly right: open 3D technology has advanced well past early image-to-mesh systems. **But a single attractive novel view, a navigable Gaussian-splat scene, a riggable deformable mesh and a persistent simulated world are different products.** Nobody should label all four “full 3D world creation” without separate evidence. Likewise, CPU geometry/Blender editing is feasible; frontier image-to-3D 4B-parameter inference still demands substantial GPU according to its own creators. The winning MGR-native play is a **quality-controlled hybrid forge**: cheap native geometric and procedural construction → optional licensed neural candidate → camera/material/shape/rigging truth audit → separate editable-asset and world-state output. No provider becomes the source of truth.

## 16-field research contract

### 1. Definition

- **Mesh-generative model:** predicts volumetric/latent/implicit representations and exports surfaces, texture and sometimes separated parts. Unseen surfaces are probabilistic guesses.
- **NeRF:** learns a scene radiance/density field from calibrated views, primarily for rendering new views rather than collision geometry.
- **3D Gaussian splatting:** optimizes spatial Gaussian primitives with appearance and projects them for efficient novel-view rendering. It is not inherently a watertight editable mesh or robust collision collider.
- **World model:** predicts sequences of visual/physical state conditioned on observations/actions; may synthesize plausible video without guaranteeing a persistent exact 3D map or game-engine assets.
- **Physically usable world:** editable assets, stable topology, semantic partitions, rigging, transforms, occlusion, lighting/materials, collision/nav and reconstructible world state.

### 2. Production uses

- Tevin: candidate likeness body/face/hair/clothing sculpt, separated clothing meshes and accessories, multi-view identity-preserving review, retopo and rig preparation.
- Objects: create base props from references; verify backside and undersides; produce GLB/USD/Blender assets with editable normals/UV/PBR.
- Environments: reconstruct spaces from calibrated capture using NeRF/splats as **visual references**; use mesh/procedural layers for playable collision/nav/world persistence.
- Camera director: orbit and coverage constraints, hidden geometry confidence, shot-by-shot visual quality comparisons.
- Optional simulation-informed priors: propose candidate future frames but validate collisions and causal world state in deterministic MGR physics layer.

### 3. Mathematical contracts and representations

**NeRF model:** scene function maps position and ray/view direction to opacity/density and color; render by integrating samples along camera rays. **Splat model:** 3D Gaussian mean/covariance, color/transmittance and camera projection. **Mesh model:** vertices, faces, UVs, normals, materials, skin weights/skeleton, separate part IDs, dimensions and coordinate frame. These representations are convertible only with information loss/extra reconstruction assumptions. Train/score with held-out camera reprojection, silhouette, depth agreement when available, normals and surface consistency; hold aside known camera poses to prevent overfitting training views. Canonical 3D identity is not a CLIP/image similarity threshold alone.

### 4. Primary research and current 2025–2026 advancements

- *TRELLIS* (Microsoft/CVPR 2025) structured 3D latents; *TRELLIS.2* (2025/2026 repository) 4B-parameter native compact 3D latents with image-to-3D and PBR textures; **official Linux + ≥24GB NVIDIA VRAM requirement**.
- *Hunyuan3D-2.1* (2025) shape and PBR texture models, upstream reports about **10GB shape / 21GB textures / 29GB combined** GPU VRAM; custom geographic/community licensing.
- *SPAR3D* single-image point-aware shape editing with published Stability Community License, containing revenue-triggered enterprise obligations.
- *HunyuanWorld 1.0* (2025 paper) integrates panoramic world representation with layered meshes, export and object separation; this is a research world synthesis framework, not proof of stable physics or released unrestricted commercial rights.
- *3D Gaussian Splatting* (SIGGRAPH 2023 paper) and its active follow-on ecosystem; **original INRIA reference code is research/non-commercial restricted**, while independent Apache-licensed `gsplat` and Nerfstudio tools exist with different terms.
- NVIDIA Cosmos family (2025–2026) targets world foundation models and physical AI video/scene prediction; models/weights have custom terms and substantial hardware needs; not a plug-and-play playable world generator.

### 5. Implementations and evidence limits

| Candidate | What's real according to primary project | MGR role | Inspection depth |
|---|---|---|---|
| Microsoft TRELLIS.2 | 4B image-to-3D + PBR mesh, MIT stated in README; NVIDIA ≥24GB, Linux-tested | High-end offline comparison, optional licensed worker | Official README/project site/model card; no model run |
| Microsoft TRELLIS | Earlier structured latent 3D model, multiple representation decoders | Benchmark fallback for lower hardware than TRELLIS.2 **only after measurement** | README/project site |
| Tencent Hunyuan3D-2.1 | Shape/paint models with listed VRAM and community license | Structured shape/texture candidate under regional/rights gate | README/license; no installation |
| Tencent HunyuanWorld 1.0 | Text/image to panoramic world proxy + layered meshes and object segmentation | Architectural study for native world layering | Research paper/README/license overview |
| Stability SPAR3D | Fast single-image mesh plus point editing | Small asset prior candidate, conditional commercial license | Publisher/model card/README |
| Nerfstudio + gsplat | Apache-2.0 codebase for NeRF/splats and CUDA 3DGS | Calibrated multiview capture and visual proxy reference | Upstream README and official method docs |
| INRIA Gaussian Splatting | Original research implementation and paper | Scientific baseline **only**, no assumed commercial reuse | Paper/repository and restrictive license |
| NVIDIA Cosmos | World-model generation/prediction aimed at physical AI | Research architecture and video foresight proposal | Official project/license overviews, not inference tested |

### 6. Models and selection algorithm

Treat **task class** separately: `single_view_object`, `multi_view_object`, `human_avatar`, `captured_room`, `cinematic_environment`, `interactive_world`. Each route has required output contract (mesh vs splat vs radiance field vs video), minimum hardware, latency, permitted commercial purpose and quality score. Lightweight geometry/procedural native modeling is always a viable baseline for controlled primitives and stylized worlds. Optional model inferencers may receive scene-specific requests only if the owner's hardware and licensing gates pass; do not infer “GPU-free” from a model being open weights.

### 7. Datasets and quality corpus

Use self-authored Blender assets and calibrated multi-view render sets for known topology, silhouette and physical scale. Create MGR corpus covering a hand with five fingers from 12 camera views, a fully separated coat/shirt/boot/chain avatar, translucent object, reflective metal, thin ornament, concave chair, multiroom floor plan, nonvisible back side and articulated poses. Save training/view partitions and owner-approved identity references. Public benchmark sets (Objaverse/Google Scanned Objects/DTU/Mip-NeRF360/Tanks-and-Temples) are candidates only after rights and per-asset terms checks; publication does **not** imply commercial training or redistribution rights.

### 8. Licenses and rights

- TRELLIS.2 **project states MIT model and code**; audit repository submodules, pipelines, dependencies, safety/deployment terms and exact weights before commercial inclusion. MIT cannot guarantee provenance rights in all training assets.
- Hunyuan3D-2.1 is under a **Tencent community agreement**, **not universal MIT/Apache**; upstream LICENSE excludes EU/UK/South Korea territory, with further terms. Geographic/commercial contract review mandatory.
- Stability SPAR3D community license publisher/model card states a **US$1M annual-revenue** enterprise threshold for commercial use; owner company revenue and exact terms require counsel/verification.
- INRIA/MPII original Gaussian Splatting reference is research/evaluation rights restricted; **never vendor it into proprietary MGR production solely because GitHub is public**. Independent `gsplat` / Nerfstudio repositories state Apache-2.0; dependent modules and models separately audited.
- NVIDIA Cosmos has an NVIDIA model license/custom terms and forbids some conduct. Different releases may not share identical obligations.
- Tevin likeness, source images, actor consent, face-biometric permissions and generated output licenses remain separate owner-controlled records.

### 9. APIs and adapters

Native `Neural3DJob`: `job_id`, `task_class`, `input_reference_digests`, `owner_rights`, `model_id/version/weights_hash/license`, `seed`, `camera_bundle`, `output_contract`, `hardware_budget`, `reconstruction_vs_hypothesis`, `quality_targets`, `manual_approval`. Worker adapters can invoke local CLI/Python model in a **dedicated Forge workspace** with jobsandbox resources and no personal secrets; optional cloud inference uses provider adapter only with owner-approved spend. Output `Candidate3D` includes typed mesh/splat/field, multimodal previews, confidence/provenance and QA receipt. Blender handles retopo/rigging, PBR/UV and review.

### 10. MGR-native inventions

1. **MGR Reality Truth Splitter:** source-observed geometry, learned inferred geometry and artist-invented hidden geometry stored in separate masks/layers.
2. **MGR Neural Arena:** identical assets/model prompts, seeds and budget across providers; ranks only real QA metrics + owner feedback, not marketing screenshots.
3. **MGR Cross-View Lie Detector:** tests held-out camera views, 3D silhouette/depth, symmetry/identity, part count, occlusion consistency and surface thickness; flags uncertainty.
4. **MGR Topology Doctor:** manifold repair, retopology/UV/watertightness checks, part separation, missing hands/fingers, skeleton fit and Blender-ready delivery.
5. **MGR World Twin:** visual splat/NeRF as high-detail scenery plus synchronized editable mesh/collider/nav world, with semantic overlays and provenance.
6. **MGR GPU-Free First Planner:** routes deterministic CAD/noise/geometry and low-cost tests on CPU before considering a licensed heavy model or remote worker.
7. **MGR World Memory Seal:** a generated scene must preserve landmarks, physics interactions and camera/identity continuity across regeneration and revisits.

### 11. Hardware and reality check

- CPU-only: mesh validation, rays/triangulation, procedural scenes, simple PBR preview, geometry scripting, some small/quantized model research. **No blanket claim that 4B 3D generators train/infer on ordinary CPU at interactive speed.**
- TRELLIS.2 primary README requires Linux and NVIDIA GPU **at least 24GB VRAM** (officially verified on A100/H100). Attempting direct Windows ordinary CPU is unsupported by its stated baseline.
- Hunyuan3D-2.1 primary README lists shape ~10GB, texture ~21GB, combined ~29GB VRAM. Exact optimized build may vary; these are developer-reported, not local benchmarks.
- NeRF/3DGS training generally benefits substantially from CUDA GPUs; `gsplat` is CUDA-accelerated. Capture pose estimation and rasterized view-only preview may run different resource tiers.
- World-model video generation has massive model and temporal-memory budgets; no credible claim it creates game-ready mesh/nav automatically.
- **Decision gate:** collect Time's actual Windows CPU/GPU model, dedicated VRAM, RAM, disk, CUDA/driver, Blender version before selecting local worker.

### 12. Cost and scheduling

An open project might remove per-call API fees but not hardware, electricity, download storage, GPU rentals, model rights, artist repair and failed candidates. Model price and GPU rental rate are temporal and **not verified here**; no invented per-asset dollar figure. Collect elapsed compute seconds, peak VRAM, inference count, model load time, repair labor, acceptance ratio and total cost per approved riggable model/interactive world. Use CPU smoke tests first and capped GPU trial only after QA baseline.

### 13. Failure modes

| Failure | Why it happens | Required MGR check |
|---|---|---|
| Correct front image, fake back | Single-view inverse problem underconstrained | Label hidden surface hypothesis, orbit and extra reference gate |
| Missing hands/fingers, melted chain | Fine geometry/occlusion resolution and learned priors | Skeleton/hand anatomy counts, part masks, multi-view review |
| Splat looks solid but not collidable | View-dependent radiance primitives lack watertight topology | Parallel semantic collision mesh and contact/nav receipt |
| Geometry/texture mismatch | Mesh and texture separate generators | UV/PBR maps, silhouette, geometric correspondence across orbit |
| Floating accessories | No rig/cloth/body attachment semantic | Object separation + skeleton anchors + motion stress test |
| Model claims metric size from one picture | Missing physical scale | Metric reference or explicit relative-scale uncertainty |
| Video/world changes when returning | Generative temporal drift | Persistent state and landmark/hash continuity check |
| Reflections/transparent surfaces distort geometry | View-dependent radiance cues | Multiview triangulation/specularity-aware validation |
| Commercial rights contaminated | Distinct code, weights, images and outputs licenses | Model/asset-specific rights and territory gate |
| OOM/crash or inaccessible GPU | VRAM, OS or CUDA mismatch | Preflight and limited job budget/fallback |
| High photo resemblance but unusable asset | Nonmanifold topology, no UV/rig/collider | Game-ready contract and Blender render/animation tests |

### 14. Evaluation metrics

Track calibrated held-out view metrics (PSNR/SSIM/LPIPS *where licensed and appropriate*), silhouette IoU, edge/chamfer and known-view reprojection, depth metric error only where ground-truth scale exists, surface Hausdorff/chamfer on synthetic known mesh, manifold/watertightness, UV coverage, material map validity, separated/semantic part IDs, skeletal joint count and posing deformation, physics penetration, Blender export/reimport fidelity, owner-approved identity score, output reproducibility, CPU/VRAM/RAM/time and license check result. A metric optimized on training views alone is not a novel-view trust score. Proposed QA gates (not measured): zero missing core fingers on synthetic anthropomorphic corpus, all owner-declared separate garment groups independently editable, no engine crash/OOM in declared budget, perfect provenance completeness.

### 15. MGR Forge integration boundary

Use an MGR-owned `Neural3DJob` schema, adapter registry, calibration evaluator, world truth layers, topology/rigging doctor and QA receipts. Reuse existing source-of-truth and routing if already present rather than duplicating. Integrate Blender for mesh edits and game engine for physics/collision/nav; no vendor or neural output may overwrite owner-approved Tevin parts, canonical world geometry or world laws by default. The neural system produces proposals; owner/QA gates publish assets.

### 16. Acceptance tests and build sequence

1. Synthetic known mesh rendered into 12 views; hold 4 out. Reconstruction/generation must report held-out silhouette + geometry quality and identify nonvisible hypothesized areas.
2. Identical single-view image representing two possible depths is labeled ambiguous; camera metric inference must fail without scale.
3. Tevin hand/coat/boot/chain test: correct digit count, visible hand in all poses, semantic part separation, editable object transforms and stable skinning on 20+ poses.
4. Splat/NeRF room requires *separate* valid collision/navigation mesh and real-time collision traversal; splat render alone cannot pass interactive-world gate.
5. Pose-orbit quality suite: front/back/left/right/top/bottom plus occlusion cases; log bad views, holes, disocclusion hallucinations, material texture drift.
6. Known PBR sphere/metal/roughness set: textured output must preserve material channel semantics; no lighting baked into albedo without declaration.
7. Scene revisit: navigate away and back after 100 state updates; landmark/asset IDs, physics state and approved overrides remain stable.
8. License gates reject models with restricted territory/revenue/NC rights unless authorized license is recorded; weight/hash/code and input rights included.
9. GPU budget preflight rejects TRELLIS.2 requests on unsupported base hardware and chooses CPU native geometry fallback without false “model completed” result.
10. Compare at least 3 different authorized pipelines on same test set, with model version/seed/VRAM/latency/acceptance ratio and owner visual score in receipt. No production claim before actual execution.

## Practical native delivery decision

**Ship first:** deterministic geometry, calibrated multi-view truth judge, Blender asset separation/rig QA, game-ready export and persistent world-state contracts. **Then** trial permission-cleared heavy generators on a suitable GPU worker using identical MGR QA. For a true world, stitch **procedural/explicit editable mesh + collision/nav + optional high-end splat/NeRF scenery + state machine**, rather than betting the entire world on image-to-video output. This is MGR's strongest path to both speed and defensible correctness.

## Remaining depth without false completion

- Full pinned code and weight-license audit of each candidate plus transitive dependencies/submodules.
- Local test receipts for actual Windows hardware (no GPU assumptions), peak RAM/VRAM, CPU model fallback latency and Windows/Linux compatibility.
- Novel-view benchmark with owner-owned synthetic/captured corpus, dynamic objects, separate garments, thin surfaces and transparent objects.
- Commercial counsel review for Tencent geographic terms, Stability revenue threshold, original INRIA reference restrictions, NVIDIA model conditions and likeness rights.
- Source/paper benchmark replication and controlled ablation rather than relying on published cherry-picked examples.
