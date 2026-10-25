# MGR Depth Perception & Observation Intelligence

**Scope:** Human vision S01 + computer vision S12 dependency, under MGR Reality-to-Space. **Date:** 2026-10-25. **Owner:** MGR. **Research maturity:** primary technical sources inspected and 16-field specification authored; **not** an end-to-end source code audit, production algorithm benchmark or clinical neuroscience review. **Implementation maturity:** the related `forge/spatial_truth.py` monocular projection/ray proof exists; camera calibration, stereo inference and quality gates below are proposed/not built unless separately verified.

## Core finding and native direction

The human brain infers depth using **multiple imperfect cues**, rather than reading a depth coordinate directly from a retinal picture. Binocular disparity, occlusion, perspective, familiar size, shading, texture gradients and movement parallax can reinforce or contradict one another. A single monocular image often leaves multiple 3D explanations consistent with the same pixels. The engine therefore needs *evidence-specific spatial confidence* rather than conflating (a) authored geometry, (b) camera-measured observations, (c) physics/geometry-derived estimates and (d) learned AI guesses.

The native target is **MGR Observation Intelligence**, composed of: camera-ray solver → view/calibration registry → correspondence tracker → triangulation candidate → multiview reprojection checker → uncertainty ledger → owner-editable geometry proposal. It will output *reconstructed evidence* and an explicit *unseen geometry hypothesis* separately.

## 16-field research contract

### 1. Definition

Perception converts binocular and monocular signals into perceived depth. Computational observation estimates camera intrinsics, extrinsics and 3D point positions from images, correspondence and assumptions. Distinguish: **relative depth** (ordering/scale-invariant), **metric depth** (physical units with scale reference or learned prior), **geometry** (surfaces/topology) and **appearance** (view-dependent radiance). These are not interchangeable.

### 2. Production uses

- Image-to-3D: recover visible geometry and propose missing backside surfaces.
- Tevin character continuity: compare pose, camera and silhouette while preserving owner-approved identity.
- Scene/world capture: determine when a camera view or landmark constrains real 3D location.
- AR/VR: align spatial anchors and warn about tracking drift, stereo discomfort and inconsistent parallax.
- Visual VFX judge: demand multi-view consistency instead of one-frame similarity.

### 3. Standards and mathematical contracts

Pinhole projection: \(p \sim K[R|t]P\). Rectified stereo approximates \(Z=fB/d\), where focal length \(f\) in pixels, camera baseline \(B\) in length units, and disparity \(d\) in pixels. At disparity near zero, depth becomes numerically unstable; at unknown baseline scale, absolute depth cannot be recovered without extra information. Correct lens distortion before triangulation; represent camera coordinate systems and units explicitly.

Observation datum should include `(image_id, pixel_xy, camera_intrinsics, camera_pose, distortion_model, timestamp, visibility, correspondence_id, source_rights, confidence_type)`. Reconstruction datum should include `(point_xyz, units, method, support_views, residual_px, uncertainty, observed_vs_hypothesized, revision)`. Never claim a single ray has a unique Z value.

### 4. Research / papers

- Human depth cues: NCBI/Webvision *The Perception of Depth* explains binocular stereopsis and motion parallax.
- Multi-view reconstruction: Schönberger & Frahm, *Structure-from-Motion Revisited* (CVPR 2016), and Schönberger et al., *Pixelwise View Selection for Unstructured Multi-View Stereo* (ECCV 2016), as linked from the COLMAP project.
- Modern learned prior: *Depth Pro: Sharp Monocular Metric Depth in Less Than a Second* (2024/2025); strong appearance-conditioned prediction but not a physical sensor measurement.
- Relative depth baselines: MiDaS; Depth Anything V2. Their prediction scale and weight/data licenses require explicit review.

### 5. Open implementations and architecture lesson

| Candidate | Observed official capability | Architecture role | Inspection depth |
|---|---|---|---|
| OpenCV calib3d | Camera calibration, lens undistortion, solvePnP, stereo rectification, triangulation, reprojection | Portable solver baseline, not an MGR ownership contract | API docs read; source/tests not audited |
| COLMAP | Feature matching/geometric verification, incremental sparse SfM, MVS dense reconstruction, CLI and formats | Compare capture-to-pose-to-point pipeline, artifacts and failure recovery | Official tutorial, site and license overview; no local execution |
| MiDaS | Learned relative depth from single image | Optional fallback prior, never authoritative measurement | README/overview; model/runtime not run |
| Depth Anything V2 | Multiple pretrained monocular depth scales | Optional low-cost monocular prior with strict weight-license gate | README/license overview; not benchmarked |
| Apple Depth Pro | Learned metric monocular depth, high-resolution paper/weights | Study confidence/focal estimation, not silently assume metric correctness | Paper/repo/license viewed; not installed |

**MGR-native selection:** start with deterministic camera math and multi-view reprojection, plus optional licensed model adapters as assistive hypotheses. Avoid vendor hard-binding.

### 6. Models

Models relevant to uncertainty-assisted single-image priors: MiDaS relative depth, Depth Anything V2, Depth Pro. **No model was downloaded or installed in this research wave**. Compare calibration, domain bias, scale error, boundary accuracy, speed and rights before use. Unknown focal length and out-of-distribution images can undermine metric claims.

### 7. Datasets and evaluation imagery

- **Middlebury Stereo**: calibrated pairs and controlled stereo disparity benchmark; good for geometry unit/regression cases. Inspect scene-by-scene licensing before downloading or redistribution.
- **COLMAP sample datasets**: capture/matching tutorial experiments; check source-level rights and imagery-specific usage.
- **Synthetic MGR authored test rig**: preferred immediate CI baseline—known camera poses, CAD cubes/spheres, repeated textures, transparent boundaries, wrong correspondences, variable baseline, occlusions and exact ground truth.
- Future larger-scale evaluation: KITTI/ETH3D/Tanks-and-Temples candidates, after per-dataset rights, domain and ground-truth completeness review.

### 8. Licensing

- OpenCV repository currently advertises Apache-2.0; exact version, optional contrib modules and binaries/dependencies require inspection.
- COLMAP currently states a new BSD-style license, but third-party solver/GUI/GPU/build dependencies need separate verification.
- MiDaS repository advertises MIT; individual checkpoints/dependencies must still be checked.
- Depth Anything V2 **Small** is listed Apache-2.0, while Base/Large/Giant weights are CC-BY-NC-4.0. Never mix them into a commercial MGR distribution assuming they share rights.
- Apple Depth Pro uses a custom Apple `LICENSE`, including grant/disclaimer conditions. A commercial integration decision requires explicit legal/weight-license review; do not infer unrestricted rights from publication.
- Any named evaluation dataset requires dataset-specific terms; public download is not permission to embed photos in a public MGR repo.

### 9. APIs and providers

Local API choices: OpenCV `calibrateCamera`, `undistort`, `stereoRectify`, `triangulatePoints`, `projectPoints` and basic CPU math; COLMAP CLI / PyCOLMAP for tested capture jobs. Paid providers and cloud reconstruction are optional behind MGR Model Dock and task cost gate, not architectural dependencies.

### 10. Native alternative

MGR can implement small, transparent deterministic primitives: pinhole projection, camera ray, calibrated linear triangulation, reprojection, parallax-baseline checks and explicit observational provenance. For a mature SfM/MVS system with robust feature matching/bundle adjustment, benchmark a proven open component before deciding to reimplement its optimizer. Replacing highly optimized solvers without evidence is unlikely to improve delivery.

### 11. Hardware/runtime

CPU is practical for camera-ray math, small correspondence sets and simple triangulation/QA; large-scale dense MVS/feature matching, semantic models and neural depth often benefit heavily from GPU and memory. Do not extrapolate CPU performance of a ten-point synthetic scene to dense 2.25MP neural inference. Collect exact Windows CPU/GPU/RAM inventory and per-job duration/VRAM before admitting workloads.

### 12. Cost

Deterministic solver requires no paid API. Total cost includes capture time, calibration targets, memory/compute, storage, manual annotation/approval, model license, retries and output QA. Model vendors' public prices are not captured here; this chapter avoids guessed per-asset dollar estimates. A future benchmark must report average and worst-case cost **per owner-approved reconstructable asset**, not merely cost per inference.

### 13. Failure modes

| Failure | Why | Native detection/response |
|---|---|---|
| One image yields conflicting 3D | Perspective projection is many-to-one | Keep candidate ray and unknown-depth label |
| Pure rotation / weak translation | Insufficient parallax baseline | Reject confident metric triangulation |
| Near-zero disparity | Depth uncertainty blows up | Flag as far/uncertain, no invented meter precision |
| Repeated or featureless textures | Ambiguous correspondence | Bidirectional consistency/epipolar residuals, confidence cap |
| Occluded or transparent surfaces | Correspondence is not observed | Mark surface unobserved/hypothesized |
| Unknown lens distortion | Pixel geometry inconsistent | Calibration/undistortion gate |
| Rolling shutter, moving subject | Camera-only static-scene model violated | Timestamp/motion class and rejection unless modeled |
| AI model hallucinated backside | Learned prior generates plausible unseen shape | Provenance/approval gate and multiple-view check |
| Unit/baseline mismatch | Metric scale unreliable | Typed units, right-handedness, baseline calibration |
| High reprojection error | Bad matching or pose | Fail job or ask for better capture, no silent smoothing |

### 14. Evaluation and metrics

Always record: calibration reprojection RMSE pixels, median/P95 triangulated reprojection residual, negative-depth fraction, baseline angle distribution, occlusion/outlier fraction, relative-depth ordering error, metric-depth scale error when physical ground truth exists, silhouette IoU/edge discrepancy across unseen views, repeatability across device/capture sessions, wall time, peak RAM/VRAM and cost. **Thresholds are proposal acceptance gates**, not established empirical norms: e.g. synthetic calibrated scene ≤0.25px P95 reprojection, 0% behind-camera triangulated points, reject underconstrained/pure-rotation inputs, >99% deterministic numeric replay within documented tolerance. Real photos need empirically calibrated thresholds by capture class.

### 15. Placement in MGR Forge

`forge/spatial_truth.py` remains small CPU proof of camera rays. The next proposed `forge/triangulation.py` should use a typed `Camera`/`Observation`/`TriangulationResult` schema with explicit units, calibration, source confidence and `observed|estimated|invented` provenance. Outputs feed MGR Beyond Imagery, Character Fabric/Tevin continuity, Spatial Eyes, camera director, Geometry QA and MGR FX Judge. Ownership and owner-approved identity must remain outside raw estimator code.

### 16. Acceptance tests before a verified claim

1. Two distinct 3D points on same camera ray project to same pixel; engine refuses to infer depth from one view (**existing basic proof**).
2. Two calibrated translated views of a known point triangulate to ground truth within numeric tolerance; held-out reprojection residual logged.
3. Pure rotation, parallel rays/zero baseline, negative depth, NaN/inf inputs, mismatched camera units and incorrect correspondences all fail closed.
4. Add noise to correspondences and verify uncertainty/error increases rather than false confidence.
5. Compare real calibrated images from owner-authorized set; evaluate known physical distances and failure scenarios with visual inspection.
6. Optional learned monocular prior cannot override measured stereo evidence without explicit conflict report.
7. Record rights, camera metadata, source asset digest, runtime, environment/solver version and output receipt for every reconstruction.
8. Test geometry in a receiving Blender/game engine, multiple cameras and animation frames; do not call one preview production-ready.

## Immediate build decision

**Proceed with a small native calibrated two-view triangulator while this research track continues.** It removes a foundation-level weakness without waiting for large model downloads. Keep COLMAP/OpenCV as comparison baselines for more demanding SfM. The visual confidence/reconstruction system must not claim full sensory human vision; the practically testable contract is accurate measurement plus honest uncertainty.

## Next research gaps

- Detailed end-to-end reading of at least one full COLMAP pipeline source entrypoint, optimizer and failure tests, pinned commit/dependencies/rights.
- Multi-camera/rolling-shutter and dynamic-object geometry research.
- Human psychophysical thresholds for stereo acuity and cue conflict by viewing setup; do not convert general clinical statements into absolute 3D reconstruction tolerances.
- Dataset licensing and ground truth audit before any model training or use in a publicly distributed product.
- CPU/GPU benchmarks and commercial permitted pretrained model comparison on the actual Windows hardware.
