# External Provenance — MGR Depth Perception & Observation Intelligence

This evidence ledger is deliberately separate from the MGR-native product canon. The sources below establish physical and software constraints, not ownership or origin of MGR native capabilities. Inspected 2026-10-25 via publicly accessible official documentation, original institutional publications and repository landing pages. **No listed dependency's entire source tree, exact deployed release, binary or model weights have been audited in this pass.**

| Source | Primary URL | Evidence actually inspected | Claim supported | Adoption/license status |
|---|---|---|---|---|
| NCBI Bookshelf — Webvision | https://www.ncbi.nlm.nih.gov/books/NBK11512/ | Public indexed textbook chapter/page | Binocular retinal disparity and monocular motion parallax are distinct human depth cues | Research reference only; no code or images copied |
| NCBI Bookshelf — Spatial Orientation | https://www.ncbi.nlm.nih.gov/books/NBK518976/ | Public clinical/scientific reference page | Vestibular, proprioceptive and visual contributions to perceived spatial orientation | Research reference only |
| OpenCV calib3d official reference | https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html | API and projection/calibration documentation | Intrinsics/extrinsics, distortion, projection, triangulation, PnP and rectification | Reference algorithm contracts; API behavior must be tested with pinned installation |
| OpenCV upstream repository | https://github.com/opencv/opencv | Repository landing/license overview | Practical open-source calibration and multiview baseline | Current repository Apache-2.0; verify chosen version, third-party notices and binaries before vendoring |
| COLMAP official documentation | https://colmap.github.io/index.html | Overview and high-level documented workflow | Structure-from-Motion and Multi-View Stereo pipeline | Comparator candidate; no claim of local install or executable passing |
| COLMAP official tutorial | https://colmap.github.io/tutorial.html | Published tutorial workflow | Image import → matching → sparse reconstruction → optional dense output | Reference procedure only; no full source-level audit |
| COLMAP upstream rights notices | https://github.com/colmap/colmap/blob/main/doc/license.rst | Published license document | COLMAP's upstream license plus separate dependency obligations | BSD-style core noted; audit dependencies/versions before distribution |
| Middlebury stereo benchmark | https://vision.middlebury.edu/stereo/data/ | Dataset index and evaluation site | Calibrated stereo/data with ground truth can test disparity quality | **Dataset-specific rights unresolved**; research/evaluation proposal only, no automatic commercial reuse |
| MiDaS upstream | https://github.com/isl-org/MiDaS | README and license metadata | Monocular depth estimator provides learned depth prior, generally relative-scale | Code MIT per repository; **model-specific terms and data lineage not cleared** |
| Depth Anything V2 upstream | https://github.com/DepthAnything/Depth-Anything-V2 | README/model-license statements | General-purpose depth prior, model sizes differ | Small model Apache-2.0; Base/Large/Giant CC BY-NC 4.0 as stated upstream; commercial pipeline should exclude NC weights absent license grant |
| Apple Depth Pro upstream | https://github.com/apple-aiml-research/ml-depth-pro | README and custom license page | High-detail monocular metric-depth prediction is available as research model | **Custom terms**; separate counsel/licensing review before product incorporation |
| Apple Depth Pro paper | https://arxiv.org/html/2410.02073v2 | Public research abstract/paper | High-resolution metric monocular depth is an active research route | Reproduction/quality and license require direct benchmarking |

## Method and limits

Evidence maturity is **documentation/reference inspection**, not an end-to-end source-code audit or MGR product acceptance. Search-index snippets sometimes provide only page portions; specific equations and project claims should be rechecked against version-pinned primary texts during implementation. Dataset imagery, weights, model architecture, benchmark scores and vendor marketing are **not** imported to Forge by virtue of listing these links.

## Reproducible proof requirements

1. Pin upstream commit/release, Python dependencies, calibration data and rights notices in a separate external dependency manifest before optional integration.
2. Reconstruct a synthetic known 3D scene using a pair of calibrated cameras, multiple non-collinear observations and a positive translation baseline; compare recovered points and reprojected pixels to ground truth.
3. Prove explicit failures for pure rotation, zero baseline, occlusions, high noise, lens-distortion mismatch, inconsistent units, incorrect correspondences and behind-camera points.
4. Report uncertainty, baseline angle, reprojection error, positive-depth fraction, deterministic repeatability, peak CPU/RAM/VRAM and execution cost. Do not count attractive single-view images as verified spatial reconstruction.
5. Benchmark optional CPU/lightweight learned priors separately from measured stereo; **never assert known metric scale from a single ordinary RGB image without an external scale assumption or metric-trained model calibration**.
6. Audited provenance should identify exactly which external source informed an MGR-native mathematical or engineering decision, but customer-facing MGR feature names and internal source of truth remain MGR-native.

## Outstanding external audits

- Full source-level reading of COLMAP camera models, matching, reconstruction, bundle adjustment and tests on pinned revision.
- Version-pinned native Windows Blender/OpenCV/COLMAP compatibility and commercial rights audit.
- Middlebury individual scene terms, alternative commercially usable dataset selection, calibration rig and capture consent.
- Review licenses for each candidate pretrained weight independently of hosting repository's code license.
- Real-device CPU/GPU latency/quality measurements and human-perception psychophysics for the target display/view distance.
