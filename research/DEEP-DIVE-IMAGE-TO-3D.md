# Deep Dive: Open Image-to-3D Foundation Models

2026-10-25. Sourced from original project READMEs and papers. No model executed by MGR.

## TripoSR — inexpensive baseline

1 Definition: 2024 feed-forward, single image -> draft 3D mesh; not current paid Tripo H3.1.
2 Production: Fast concept object reconstruction and baseline reference.
3 Standards: image conditioning; mesh/GLB export and real units need postprocessing.
4 Paper: https://arxiv.org/abs/2403.02151 ; transformer/LRM-inspired reconstruction, claims ~0.5s NVIDIA A100 under authors' settings.
5 Code: https://github.com/VAST-AI-Research/TripoSR ; explicit CPU fallback in run.py.
6 Weights: stabilityai/TripoSR checkpoint as documented in project; freeze revision/hash on download.
7 Data: Training provenance and rights require deeper audit; not license for reproducing training dataset.
8 License: Project MIT claim; verify all weights/dependencies.
9 API: Local Python, CLI `run.py`; create an MGR adapter, do not bind consumers.
10 MGR Native: CPU-only first test for 'low complexity' shape, with mesh QA.
11 Hardware: default ~6GB VRAM; CPU fallback supported, latency unknown.
12 Cost: local compute/time, no API credits.
13 Failures: unseen back geometry hallucinated, thin parts/fingers, UV/material imperfections.
14 Evaluation: same 10 reference images, image compliance and topology/latency/memory.
15 Placement: isolated packages/models adapter.
16 Acceptance: CPU run on pinned environment and 3 images, valid meshes, timed receipts and rights log. **NOT TESTED**.

## TripoSG — high-fidelity shape

1 Definition: image-conditioned rectified-flow transformer for detailed geometry.
2 Production: candidate detailed shapes when a local GPU exists; does not automatically solve rigging, parts or all texture work.
3 Standards: editable meshes, units/mesh QA and GLB export after postprocess.
4 Paper: https://github.com/VAST-AI-Research/TripoSG links shape synthesis research.
5 Code: Official repository includes inference scripts and architecture.
6 Weights: Model distribution via linked project; pin exact model/license.
7 Data: Paper describes roughly 2 million curated Image-SDF pairs; no automatic reproduction rights.
8 License: MIT repository stated; verify model card/checkpoints/dependencies.
9 API: Python inference adapter with timeout and budget.
10 MGR Native: choose only if fidelity gain beats CPU baseline.
11 Hardware: project states CUDA GPU >=8GB VRAM.
12 Cost: compute + local setup; no hosted credits if self-run.
13 Failures: memory, CUDA setup, topology, unobserved geometry, non-game-ready outputs.
14 Evaluation: same refs vs TripoSR and controlled textured pipelines.
15 Placement: replaceable models adapter.
16 Acceptance: 8GB+ eligible runtime, checkpoint hash, 10 generations, measured quality/cost. **NOT TESTED**.

## TRELLIS.2 — premium high fidelity

1 Definition: 4B model using sparse O-Voxel geometry/PBR latent representation.
2 Production: premium detailed object candidate, not a whole game-world engine.
3 Standards: mesh/PBR map, UV and GLB target.
4 Paper/research: https://microsoft.github.io/TRELLIS.2/
5 Code: https://github.com/microsoft/TRELLIS.2 with image-to-3D, texturing, data and training components.
6 Weights: TRELLIS.2-4B hosted on Hugging Face; pin exact revision.
7 Data: Verify external training data before custom training; not needed for inference baseline.
8 License: Project MIT, but dependencies nvdiffrast/nvdiffrec separately licensed.
9 API: Python from project in licensed isolated worker.
10 MGR Native: optional top-quality shape/textures behind adapter.
11 Hardware: Linux tested, NVIDIA >=24GB, CUDA tooling.
12 Cost: GPU seconds, downloads, storage, processing and export.
13 Failures: installation/CUDA extension, 24GB hard limit, game-retopo still required, texture/geometry consistency.
14 Evaluation: PBR accuracy, geometry, VRAM/time, accepted asset cost.
15 Placement: workers/gpu and packages/models.
16 Acceptance: pinned image to textured mesh, GLB roundtrip, benchmark against cheaper approach. **NOT TESTED**.

Authors' TRELLIS.2 timing: ~3s at 512 cubed on H100, ~17s at 1024 cubed, ~60s at 1536 cubed, not transferable to consumer hardware without measurement.

**Decision:** TripoSR baseline first. TripoSG and TRELLIS.2 quality candidates only after hardware/license gate. No claim that any single model preserves Tevin identity or produces a usable rig.

Sources: https://github.com/VAST-AI-Research/TripoSR ; https://github.com/VAST-AI-Research/TripoSG ; https://github.com/microsoft/TRELLIS.2.
