# F106 Unclothe 3D: selected primary-source evidence (2026-10-25)

## Target

Given a clothed character photograph or multi-view sheets, propose semantic separate visible assets (skin/body, hair, garments, footwear, jewelry, tattoos), review masks/labels, and create independent editable textured 3D assets without silently fabricating hidden surfaces as fact.

## Primary systems reviewed

1. Meta SAM 3 — https://github.com/facebookresearch/sam3 — **ADAPT/STUDY**, text/exemplar-prompt concept segmentation provides candidate masks/instances. Open-vocabulary text prompts are not guaranteed to distinguish overlapping chain, jacket lapel and skin; verify access, model/weights license, GPU resources, masks, accuracy on real character sheets before installing. Also see https://ai.meta.com/research/sam3/ .
2. Meta SAM 2 — https://ai.meta.com/research/sam2/ and https://github.com/facebookresearch/sam2 — **ADAPT**, interactive mask refinement for images/video. SAM 2 alone does not infer a complete semantic wardrobe inventory.
3. Microsoft TRELLIS.2 — https://github.com/microsoft/TRELLIS.2 and https://microsoft.github.io/TRELLIS.2/ — **STUDY/ADAPT** single-image to 3D candidate. Separated masked objects are plausible independent inputs, but reconstruction of obscured interior/backs and exact fit/scale across parts is unproven. Verify GPU/weights license and clean export semantics independently.
4. Tencent Hunyuan3D 2.1 — https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1 — **STUDY**, image-conditioned geometry/PBR alternative. Check its model-weight and code licensing separately prior to commercial use.

This is selected evidence and architectural comparison, **not** an end-to-end verification or installation of these large models. No paid provider, model weights or proprietary image references are checked in.

## Sixteen-field BEAST packet (initial research maturity)

1. **Definition:** semantic instance inventory, mask isolation, conditioned 3D reconstruction, part-to-body assembly.
2. **Production use:** character wardrobes, accessories, detachable game props and multiple LOD variants.
3. **Standards:** PNG RGBA and checked hashes for segmented 2D; glTF 2.0/GLB for candidate meshes; optional USD for richer assembly. Actual target runtime still open.
4. **Papers:** SAM 3 and TRELLIS.2 official technical publications/repository references above; deep reading/benchmark comparison remains open.
5. **Open implementations:** SAM 3 / SAM 2 / TRELLIS.2 / Hunyuan3D 2.1.
6. **Models:** above; versions and checkpoints must be pinned and separately licensed before actual deployment.
7. **Datasets:** synthetic occlusion and mask ground-truth test set planned; training data license selection pending.
8. **Licensing:** research access is not redistribution permission; SAM model license and 3D-model weights must be checked separately and version-pinned.
9. **APIs:** local or removable adapters recommended; no API key requirement at core.
10. **Native:** owner-owned approval receipts, independent masks, alpha isolation, 3D job tickets, body-space registration, rig fit and provenance.
11. **Runtime:** pure CPU review and PNG isolation work; neural inference may need high-VRAM NVIDIA GPU, CUDA-compatible dependencies and substantial downloads, to be measured on target hardware.
12. **Cost:** core masks/receipts no inference fee; GPU compute and model hosting unknown pending benchmarking.
13. **Failure modes:** occlusions, overlapping parts, asymmetric garments, tiny jewelry masks, inaccurate feet/hands, hallucinated backsides, inconsistent scales, source identity drift.
14. **Evaluation:** mask IoU, precision/recall by asset, human mask acceptance, face geometry alignment, contact/penetration tests, rig motion deformation, independent engine reopen.
15. **Placement:** `forge/unclothe_3d.py` for approval and independent PNG production, swappable segmentation and 3D engines behind explicit adapter contracts.
16. **Acceptance:** one image with 10+ real parts → candidate segmentation → owner approve/reject/change → real cropped alpha PNG per approved part → full textured 3D artifacts → common rig assembly → visual/physical checks → GLB reimport in a target engine. Current stage only validates already-supplied masks and alpha isolation.

## Ownership and safety gates

- The machine proposes; it never assumes a model score equals owner approval.
- Approved *images* do not automatically approve each segmentation mask, guessed hidden geometry, or generated mesh.
- Reject traversal/unsafe names, excessive image sizes, duplicate part IDs, unreviewed parts and existing output paths.
- Never expose private body or identity references to a public repository. Keep masks/images and consent decisions in the private project workspace.
- One front image cannot reveal a hidden bare body, complete back textures, exact jewelry attachment geometry or real garment thickness. Such content must be treated as new reconstructions with uncertainty, ideally informed by additional owner-approved views.

## Next native implementations

1. Optional actual local SAM3 provider yielding masks + semantic confidence; preserve original prompt/mask provenance and owner correction UI.
2. Geometric registration to approved T-pose body and multiview source images, including hand and foot anatomical checks.
3. Multi-provider 3D reconstruction jobs (TRELLIS.2/Hunyuan3D), bounded resource budgets, failure recovery and actual mesh validation.
4. Clothing thickness and hidden-surface reconstruction approvals, editable object hierarchy, rig skinning, simulation, GLB/USD independent import.
