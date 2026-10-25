# Deep Dive: Worlds, Reconstruction, Parts and Rigging

2026-10-25. Evidence from official releases/papers. No code execution by MGR.

## HY-World 2.0 — real 3D scene generation / reconstruction

1 Definition: Text/image -> persistent scene and multi-view/video -> reconstruction in meshes and 3D Gaussian splats.
2 Production: World generation pipeline stages: panorama, planned camera paths, expansion, world reconstruction and 3DGS training.
3 Standards: 3DGS and meshes are different; collision, nav, LOD, PBR and engine roundtrip remain separate work.
4 Research: HY-World 2.0 authors publish multi-modal world architecture (2026).
5 Code: https://github.com/Tencent-Hunyuan/HY-World-2.0 ; worldgen worldrecon sources available.
6 Weights: WorldMirror-2 (~1.2B), HY-Pano-2 (~80B), HY-Pano-2-Qwen (~425M), WorldStereo-2 (~17B) published in Model Zoo.
7 Data: training source rights and any external weights need audit.
8 License: Tencent HY-WORLD 2.0 Community License, additional commercial terms; DO NOT treat as MIT.
9 API: local Python pipeline and reconstruction CLI; separate navigation planning.
10 MGR Native: study scene graph/expansion and rebuild original CPU procedural core; licensed neural backend only if allowed.
11 Hardware: CUDA 12.8 recommended; GPU and sometimes multi-GPU path. No verified CPU-only full pipeline.
12 Cost: high potential memory/inference demand; time/storage and 3DGS fitting.
13 Failures: drift, wrong depth, incomplete meshes, glossy scene with unusable collision, huge GPU requirement, proprietary terms.
14 Evaluation: world traversal, spatial coherence, mesh editability, nav/collision, render vs real geometry, cost.
15 Placement: isolated optional scene-reconstruction worker, not core world engine.
16 Acceptance: license approval, pinned weights, multi-view sample, exported geometry, navigation and editable scene proof. NOT TESTED.

## WorldClaw / WorldGen — agentic scene layout

1 Definition: Global-to-regional structured world plans, terrain and local asset placement (WorldClaw); text-to-traversable hybrid procedural/AI generation (WorldGen).
2 Production: Design lessons for future world director, not drop-in API assumed.
3 Standards: world graph, transform/unit contracts, nav mesh, export.
4 Papers: https://arxiv.org/html/2608.05248v1 and https://arxiv.org/abs/2511.16825 .
5 Code: availability and license need independent repo inspection, paper does not imply product availability.
6 Models: modular LLM/planner, asset retrieval, procedural and diffusion models may be combined.
7 Data: Scene rules, approved asset library and licensed public geometry datasets.
8 License: paper ideas vs code/assets differ; do not copy protected implementations.
9 API: MGR-owned scene plan JSON and planner.
10 MGR Native: core world director/region graph.
11 Hardware: planner can be small model/CPU or rules; expensive assets optional remote GPU.
12 Cost: high reuse leverage; measure planner/asset synthesis.
13 Failures: coherence across regions, spatial overlap and invalid routes.
14 Evaluation: geography continuity, 1,000-building load and navigation tests.
15 Placement: packages/world.
16 Acceptance: persistent seeded world with reloaded landmarks and validated reachable regions. NOT TESTED.

## Hunyuan3D-Part — part surgery

1 Definition: P3-SAM part segmentation + X-Part part completion on a mesh.
2 Production: Reconstruct separately manipulable objects; test whether soft clothing and thin chains are actually accurate.
3 Standards: separated mesh components, pivots, UV/material, bindings.
4 Papers linked in official README.
5 Code: https://github.com/Tencent-Hunyuan/Hunyuan3D-Part ; P3-SAM and XPart folders.
6 Weights: official Tencent Hugging Face model; only light X-Part version in local release per README.
7 Data: training and derivative-output restrictions need exact license review.
8 License: Tencent custom community terms, not automatic unrestricted commercial use; derivative/distillation language.
9 API: candidate local segmentation/complete pipeline with explicit trust boundaries.
10 MGR Native: geometry-part contract plus manual/procedural fallback; no vendor dependence.
11 Hardware: exact VRAM must be measured and documented.
12 Cost: compute + quality review; tiny accessories may need manual cleanup.
13 Failures: jacket/body merge, lost fingers, incorrect cap surfaces, disconnected accessories.
14 Evaluation: component IoU/semantic purity, part material retention, attachment accuracy, after rigging.
15 Placement: packages/character and packages/quality behind optional adapter.
16 Acceptance: separate Tevin jacket, pants, boots and chains from approved source without damage to body. NOT TESTED.

## UniRig

1 Definition: data-driven automatic skeleton inference/rigging.
2 Production: speeds up initial skeletons but does not prove usable face/hands or weights.
3 Standards: bone hierarchy, skin weights, FBX/GLB, rest pose.
4 Project: https://zjp-shadow.github.io/works/UniRig/
5 Code: exact upstream repo/revision/license to inspect before adoption.
6 Weights: availability/license pending.
7 Data: Rig-XL paper project reports 14k diverse 3D models.
8 License: pending primary source inspection.
9 API: to be resolved.
10 MGR Native: use as optional proposal then validate with Blender/Rigify fallback.
11 Hardware: pending.
12 Cost: generation + correction labor.
13 Failures: bend distortions, missing bones, bad weight painting.
14 Evaluation: canonical pose suite and export/reimport.
15 Placement: packages/character.
16 Acceptance: stable T/A/idle/walk result with correct deformation; NOT TESTED.

**Decision:** Study HY-World 2.0 and Hunyuan3D-Part, but do not commercialize their weights without license clearance. Borrow agentic planning insight independently. Tevin base preservation remains an explicit acceptance condition.
