# S13 — MGR Reality Capture: photographs into verifiable 3D

**Decision:** Build an MGR-native **Capture Truth** pipeline that differentiates *measured depth* from *plausible invented depth*. The shortest reliable path uses multiple overlapping calibrated photographs, robust 2D feature tracks, camera-pose optimization, dense geometry, measured scale and independent novel-view/geometry checks. Keep optional licensed reconstruction tools behind adapters; do not claim a single image determines full 3D anatomy.

**2026-10-25 status:** researched architecture, data contracts, reference algorithms, rights, hardware and acceptance tests. Prototype camera projection/ray/parallel-view triangulation exists in `forge/spatial_truth.py`, but **full SfM, bundle adjustment, multi-view dense fusion, texturing and measured scale are not claimed implemented**. Detailed outside evidence is quarantined in [S13 sources](../external-provenance/S13-PHOTOGRAMMETRY-SOURCES.md).

## 1. What photogrammetry actually is

Photogrammetry uses geometric relationships among photographs, camera lenses and a scene to estimate positions, dimensions and 3D surface information. A photo contains rays of light projected onto a 2D sensor; distance along each ray is generally unknown. Two well-calibrated camera observations of the *same* 3D feature from meaningfully different positions constrain its 3D location; additional images improve robustness, visibility and surface coverage. A machine-learned “image-to-3D” model may guess hidden geometry, but that is a different evidence class.

## 2. Fundamental geometry and optical model

Pinhole projection: homogeneous pixel `p ~ K [R | t] P`, where `K` is camera intrinsics, `R,t` extrinsics and `P` world-space point. Real lenses add radial/tangential distortion. Corresponding points in calibrated views obey epipolar geometry and an essential matrix constraint; uncalibrated views use a fundamental matrix. Triangulation minimizes reprojection error from multiple rays; camera solving and 3D structure are jointly refined using bundle adjustment. Similarity-scale ambiguity means unconstrained SfM alone cannot establish meters. Keep coordinate-handedness/up-axis transforms explicit at every export/import.

## 3. Complete production pipeline

**Capture**: plan overlapping views, diffuse stable lighting, locked focus/exposure if practical, known length/scale board, controlled backgrounds where possible, and front/back/top/underside observations. Store camera calibration, focal settings and provenance. **Preflight**: inspect blur, exposure, missing angles, image duplication, motion, rolling shutter and privacy/consent. **Track**: detect and match stable features between views, reject outliers with robust geometry, form multi-image tracks. **Pose**: solve relative camera positions and sparse landmarks; optimize via bundle adjustment; reject unobservable scale or degeneracy. **Dense**: compute multi-view depths, normal confidence and fuse surfaces/points; label holes rather than invent surfaces. **Mesh**: reconstruct triangles, repair verified small holes, retopologize for animation where required. **Texture**: multi-view projection, UV, exposure/color balancing, seam and occlusion validation. **QA**: measured scale, independent held-out camera reprojection, silhouette and 3D reference tests; export as structured asset with visible/inferred regions.

## 4. Acquisition rules by subject type

| Subject | Minimum practical approach | Special risk |
|---|---|---|
| Hard prop/statue | Orbit photos with good overlapping textured views and known scale | Specular/transparent surface, glossy highlights move with camera |
| Living adult character | Multi-camera synchronized rig or rapid capture while still; separate apparel and anatomy afterward | Facial micro-movement, hair, eyes, jewelry, privacy/identity consent |
| Entire room | Multiple pathways, corners, ceiling and floor overlap, measuring reference | Featureless walls, window reflections, hidden wall backs |
| Exterior building/street | Multiple baselines/heights and surveyed scale anchors | Traffic, sun changes, GPS drift, airborne capture rules |
| Terrain/large world | Calibrated aerial/ground images plus independently surveyed markers/depth | Drift, vegetation movement, accumulated global error |
| Single concept image | MGR inferred modeling lane + explicit artist review | Cannot certify hidden geometry, meter scale or independent motion |

## 5. Key algorithms to research and implement by layer

Camera calibration and image undistortion; corner/blob/feature detection and learned matching (only if licensed); essential/fundamental matrix RANSAC with degeneracy guards; calibrated PnP; 2-/N-view triangulation; incremental or global structure from motion; robust bundle adjustment; depth hypotheses with multi-view photo-consistency; confidence masks, occlusion and visibility; depth fusion, point-cloud registration and surface reconstruction; UV atlas and multi-image texture selection. Exposure equalization should not falsify surface geometry. Independent native MGR implementations need conformance tests against analytic calibrated cameras before any large real-world dataset.

## 6. Available engineering candidates and legal choice

Treat camera solving/feature tracking, dense depth/mesh fusion and texturing as separate replaceable adapters. Favor a clearly licensed camera/SfM implementation as a verified interoperability reference; evaluate open geometric computer-vision operations for small native kernels. A dense MVS library with AGPL obligations must not be silently embedded into commercial MGR core. Node-graph tools suggest how to support visible restartable pipeline DAGs; they are not the canonical MGR design or a dependency requirement. External source names/URLs/licenses are in the provenance packet, not hardcoded MGR product promises.

## 7. Models and new research opportunities

Learned depth estimators, feature matchers, normal predictors, neural radiance reconstruction and Gaussian splat tools may speed exploratory previews when multi-view data is scarce. Their outputs must declare `model_id`, weight/license, confidence, capture basis and `INFERRED` surface regions. A radiance field can create convincing new camera views while lacking a clean watertight animated mesh. Gaussian splats are not automatically skeletal rigs, collision surfaces or printer solids. Photogrammetry can provide supervised pairs for MGR shape models only if images, people/places and dataset rights permit training.

## 8. Datasets and benchmark access

Start with MGR-created synthetic cameras and geometric fixtures: plane, textured cube, statue-like mesh, articulated figure and room with known ground truth. Add staged scans whose subject/photographer permission and units are recorded. Academic evaluation corpora with reference laser scans are useful for accuracy/completeness comparisons; some impose noncommercial/share-alike terms and cannot be blindly absorbed into a commercial data lake. Maintain a machine-readable rights and capture ledger per scene rather than a generic downloaded dataset directory.

## 9. Camera/asset data contracts

```python
CameraObservation = {
  "schema": "mgr.forge.capture-observation.v1",
  "image_hash": "sha256:...",
  "intrinsics": {"fx_px": 0.0, "fy_px": 0.0, "cx_px": 0.0, "cy_px": 0.0},
  "distortion": {"model": "named_and_versioned", "params": []},
  "extrinsics_world_to_camera": "4x4_matrix_or_unknown",
  "capture_time": "ISO-8601", "subject_rights_ref": "record-id",
  "pose_status": "UNSOLVED", "scale_status": "UNANCHORED"
}
```

Proposed interfaces (not currently implemented): `preflight_images` → `solve_camera_tracks` → `triangulate_observations` → `bundle_adjust` → `recover_dense_geometry` → `fuse_surface` → `project_texture` → `verify_capture_truth`. Outputs retain original source-image hashes, camera transform, scale anchors, per-point observation count and uncertainty; no destructive original-image modification.

## 10. MGR-native inventions

1. **MGR Capture Truth Ledger** ties every reconstructed point/surface patch to actual camera rays and input frame IDs.
2. **Visibility Quilt** partitions surfaces into `OBSERVED`, `INTERPOLATED`, `INFERRED` and `UNSEEN` with owner approval status.
3. **Scale Lock** requires known physical length, stereo rig baseline, marker survey or validated depth source before claiming real-world meters.
4. **Orbit Gap Radar** computes camera-visible patch coverage and recommends missing camera angles before expensive dense reconstruction.
5. **Multi-Pose Identity Lock** distinguishes pose/camera changes from altered body geometry and wardrobe identity; expects correct correspondence under animation.
6. **Capture-to-Living-Asset** routes verified scans into separate clothes/boots/hair, rigging/retopo, collision and world deployment without flattening components.
7. **Reflection Skeptic** flags moving specular glare, glass and mirrors as unreliable features rather than reconstructing them as physical solid forms.
8. **Scene Evidence Director** generates a standard held-out orbit, closeups and section views for honest visual and geometric QA.

## 11. Hardware and speed

Basic pinhole projection, calibration, feature checks and small sparse triangulation can run on CPU. Many photographs and millions of candidate feature tracks increase RAM/CPU costs; dense multiview stereo/depth fusion and neural rendering commonly benefit greatly from a modern GPU and substantial memory. Dense workloads should stream/batch image pyramids, cap feature counts, process spatial tiles, cache verified stages, and never force a recompute of everything after a one-image correction. Blender can visually inspect resulting meshes but is not a substitute for camera baseline/scale measurements.

## 12. Cost and alternatives

Local open-source reconstruction avoids per-photo SaaS charges, but does not avoid capture labor, storage, GPU rental, processing time, optional license review and artist cleanup. A paid API may win for one-shot preview; an auditable local workflow wins long-run reproducibility and proprietary data control. For stylized Tevin-like concept art with a single source image, controlled native sculpting/rig/part assembly is more truthful than pretending conventional photogrammetry can reconstruct unseen features. For a physically scanned prop or room, dense multiview SfM/MVS can be the right first path.

## 13. Failure and illusion cases

- Few viewpoints or tiny camera baseline → inaccurate/undetermined depth; large apparent image match but extreme hidden-depth error.
- Flat/low-texture walls, repetitive patterns, motion blur, strong lens distortion or incorrect EXIF focal length → false correspondences, failed pose.
- Reflective glass, chrome, water, hair strands and transparent areas violate photo-consistency assumptions; moving people/foliage invalidate static-scene reconstruction.
- Rolling shutter and unsynchronized multi-camera subject movement create warped anatomy.
- Insufficient scale calibration → shape up to arbitrary size; export cannot claim centimeter accuracy.
- Pose-fitting to same training images hides an incorrect object; always require held-out camera views and independently measured geometry.
- Dense fused texture can camouflage holes, stretched triangles, floating fragments and wrong mesh normals.
- Accidental personal/biometric information capture requires consent/security controls and retention restrictions.

## 14. Evaluation: geometry truth over pretty pictures

Required metrics: registered-image fraction, inlier feature-track ratio, landmark track length, mean/median/p95 reprojection error in pixels, matched camera baseline angles, intrinsics residuals, bundle-adjustment convergence, held-out camera view error, multi-view mask intersection-over-union, observed-surface percentage, sparse/dense point confidence, reference Chamfer and F-score (if ground truth), completeness and accuracy at fixed metric thresholds, scale error in percent, watertight/nonmanifold mesh counts where solid export requested, UV seam visibility and texture ghosting. Keep confidence intervals and missing-observation flags; one high LPIPS/SSIM score does not prove geometric fidelity.

## 15. Placement into Forge and interfaces

Add a capture module behind MGR's scene/asset identity contracts, anchored to existing `forge/spatial_truth.py` for simple camera ray and triangulation primitives. `forge/meshqa.py` and S03 geometry truth validate converted surfaces; character components receive distinct wardrobe/rig geometry; worlds receive measured placements, occlusion and navmesh input; the director/camera system renders held-out views. Interchange is metric, coordinate-frame explicit, and keeps partial scenes useful when some images fail registration. No external provider/model should become mandatory for baseline CPU capture validation.

## 16. Acceptance suite and build order

| Gate | Evidence fixture | Required observable result | State |
|---|---|---|---|
| C1 projection | Known 3D points, calibrated synthetic camera | Reprojection matches pixels under documented tolerance | Primitive exists; full regression open |
| C2 baseline truth | Two cameras with known baseline + correspondences | Correct depth, rejection of parallel/near-zero parallax | Narrow parallel-ray primitive exists; general solver open |
| C3 calibration | Checkerboard image series with known board dimensions | Intrinsic/lens estimate and held-out pixel residual report | OPEN |
| C4 matching | Synthetic known 3D scene from 8+ views | Feature tracks, outlier rejection and correspondence report | OPEN |
| C5 SfM pose | Calibrated 360° asset capture | Pose/sparse cloud up to similarity + quantified residuals | OPEN |
| C6 scale lock | Measured marker distance and one intentionally wrong anchor | Correct metric model; mismatch rejects export | OPEN |
| C7 dense fusion | Multi-view cube/statue with ground-truth mesh | Dense cloud/mesh and completeness/accuracy metrics | OPEN |
| C8 occlusion truth | Object with inaccessible underside/back | Unseen regions remain flagged; no invented measured surface | OPEN |
| C9 texture | Distinct exposures/view angles | Correct UV/color image projection without ghosted seams | OPEN |
| C10 animated human | Consent-cleared multi-camera body with coat, boots and hair | Anatomically stable full orbit; independent parts preserved | OPEN |
| C11 held-out proof | 2 unseen camera angles excluded from solving | Correct novel-view silhouettes/projection; failure if altered geometry | OPEN |
| C12 corrupted capture | Blur, glass, duplicates, motion and wrong focal data | Explicit reject/degraded grade and diagnostic messages | OPEN |
| C13 scale/performance | 10, 100, 1000 images at multiple resolutions | Recorded stage time, RAM/VRAM/throughput on named hardware | OPEN |
| C14 privacy and rights | Real subject and rights metadata | Consent gate; no raw face export to unauthorized providers | OPEN |

**Order:** capture data schema/preflight + C1–C3 → feature tracks/pose + C4–C6 → dense geometry/uncertainty + C7–C8 → texture and component identity + C9–C10 → held-out QA, reliability, profile/rights + C11–C14. Bundle reproducible fixtures into tests and record actual pass/fail evidence in the build register. No untested gate should be upgraded solely because another project's demo looks impressive.

**Bottom line:** MGR can own the crucial truth layer without inventing a new neural network or buying every API call. Real shape arises from geometric evidence and testable camera measurements; artistic guesswork is powerful but must keep its own label.
