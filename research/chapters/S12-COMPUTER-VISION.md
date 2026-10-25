# S12 — MGR Spatial Sight: Computer Vision, Camera Motion and Evidence-Based Space

**Owner:** MGR · **Research date:** 2026-10-25 · **Evidence lifecycle:** Primary OpenCV, COLMAP and authored SLAM publications selectively studied. The packet proposes MGR-native capabilities; it **does not** assert that a complete SLAM, photogrammetry or recognition system has been implemented. Citations/licenses: `research/external-provenance/S12-VISION-SOURCES.md`.

## Native verdict

Give Forge **eyes that distinguish observation from inference**. A character picture is a measurement of projected color—not an X-ray of exact hidden limbs, hair roots, skeleton or backside. A verified multiview sequence plus calibrated camera and feature tracks can recover actual constrained depth and camera motion; some scales, unseen surfaces and dynamics remain fundamentally ambiguous. Forge should carry explicit confidence, occlusion and unobserved-region labels, render hypotheses, then demand geometric consistency before claiming a canonical editable world.

## 1 — Definition and boundaries

- **2D features:** corners, descriptors, segmentation and keypoints extracted from individual frames. **Tracking:** correspondence over time or views.
- **Optical flow:** apparent image displacement; not necessarily actual 3D velocity (camera movement, projection and occlusion contribute).
- **Calibration:** intrinsics (focal length, principal point, distortion), extrinsics (rotation/translation), image dimensions, timing and shutter behavior.
- **Epipolar geometry:** corresponding rays restrict relative pose and triangulation given appropriate scene parallax.
- **SLAM:** estimate camera trajectory while mapping; loop closure corrects drift. **SfM:** recover cameras and sparse scene from images, often offline. **MVS:** infer denser depth/surface from registered views.
- **Neural depth:** can predict plausible depth from one frame; absent external measured scale or constraints, prediction is not recovered metric truth.

## 2 — Production application chain

1. Ingest image/video and declared provenance; inspect orientation, focal metadata, rolling-shutter exposure, resolution, frame times.
2. Calibrate camera with independent checkerboard or fiducial observations; record covariance/reprojection residuals.
3. Detect and match robust image features; reject outliers geometrically.
4. Track across frames, estimate relative pose, triangulate well-conditioned points.
5. Optimize pose/map with bundle adjustment or a supported SfM/SLAM backend; detect relocalization and loop closure.
6. Produce sparse/dense point hypotheses, depth/normal/confidence/occlusion masks.
7. Build/edit actual mesh and navigability after geometric cleanup and independent viewpoint checks.
8. Compare novel-view projections and preserve failures, not only visually impressive outputs.

## 3 — Standards, coordinate contracts and invariants

- Fixed camera model selection: perspective/pinhole, fisheye, RGB-D or stereo with explicit distortion coefficients; never mix undistorted vs original pixels in one solve.
- Pixel coordinates, intrinsics matrix `K`, right/left-handed world axes, camera-to-world vs world-to-camera convention, units and timestamp scale all recorded.
- `R` remains a proper rotation (`RᵀR≈I`, `det(R)≈+1`). A pose must identify coordinate frame and camera origin.
- Preserve transformation chains and reference anchors; monocular reconstructed translation/structure ordinarily has unknown absolute scale without additional measurements.
- Every confidence score reports method, calibration state, inliers, geometric baseline, reprojection errors and expected degradation.

## 4 — Primary theories and algorithms

- Pinhole perspective `u≈fx X/Z + cx`, `v≈fy Y/Z + cy`, after distortion correction; an infinite family of `(X,Y,Z)` maps to one pixel without depth.
- Two-view matching: fundamental/essential matrix enforces epipolar constraints; RANSAC rejects mismatches; essential decomposition has pose/sign and cheirality choices.
- Known 3D landmarks and 2D measurements: perspective-n-point (PnP) estimates camera pose, often robustly with RANSAC then nonlinear refinement.
- Triangulation becomes poorly conditioned with tiny baseline, near-parallel rays or points at infinity; small reprojection residual does not guarantee reliable depth.
- Sparse Lucas–Kanade relies on brightness consistency/local motion assumptions; dense Farnebäck produces per-pixel apparent displacement with smoothing tradeoffs.
- Loop closure limits long-run drift but wrong loop matches can warp a map. Moving people, reflection, repetitive patterns and rolling shutter violate simplistic static-scene assumptions.

## 5 — Existing implementation families to study

- OpenCV `calibrateCamera`, distortion/undistortion, `findEssentialMat`, `recoverPose`, `solvePnPRansac`, `triangulatePoints`, `calcOpticalFlowPyrLK`, `calcOpticalFlowFarneback` provide proven modules; detect installed version because OpenCV 5 reorganizes some modules.
- COLMAP SfM + MVS workflow can register cameras, triangulate sparse points, generate depth/normal/fused point clouds and surfaces; visual coverage and camera suitability govern success.
- ORB-SLAM3 paper describes visual/visual-inertial/multimap SLAM across monocular/stereo/RGB-D; inspect its precise runtime, dataset and license rather than copying indiscriminately.
- Blender cameras/renders provide MGR-owned ground-truth geometry/depth/normal/flow for synthetic verification and controlled stress tests.

## 6 — Model assumptions and scientific limits

- Depth from stereo: for rectified cameras, approximate `Z=fB/d` where `f` is pixel focal length, `B` is baseline and `d` is disparity; disparity uncertainty explodes for small `d`.
- Flow relates pixel displacement to camera motion, depth and independent object velocity. Thus pixel flow is not proof of a rotating 3D rig.
- Planar scenes, pure camera rotation, glass/mirrors, shiny textures and repeated patterns can admit multiple matching camera/scene interpretations.
- Occluded regions, image borders and new viewpoints carry missing-information zones. A model may complete them artistically, but the completion must be tagged **generated hypothesis**.
- Multiview identity for a person is challenged by soft tissue/clothing dynamics, articulated joints, appearance changes and inconsistent image generation; rigid SfM assumptions do not hold automatically.

## 7 — Benchmarks and MGR-owned witness data

- Synthetic in-house camera grid: checkerboard, ArUco-like calibration targets authored in-house, textured room, repeated-wall corridor, featureless wall, glass, reflections and moving mannequin.
- Render 3D ground-truth camera poses, depth maps, object IDs, motion vectors and occlusion masks from Blender; perturb focal length, exposure, motion blur, parallax and lens distortion systematically.
- Real footage must have owner permissions, consent for identifiable persons and declared license. Split calibration, training/threshold tuning and withheld evaluation sequences.
- Golden negative cases: pure rotation, planar card, ambiguous silhouette, fully hidden hand, crossed limbs, low texture, specular glass, two visually identical characters.

## 8 — Legal, license, privacy and dataset risk

Study and cite research, but do not republish third-party recordings/meshes or bundle SLAM code without verifying its exact license and dependencies. Facial imagery can be personal/biometric data; minimize collection, localize processing when practical and use authorized captures. Separate public geometry algorithms from consent to profile a person. Never claim facial identification from a silhouette.

## 9 — Integration APIs and execution routes

- Python OpenCV first for CPU test harness and descriptors; optional native C++ worker for high-frame-rate streaming only after performance evidence.
- Blender-synthetic witness adapter receives camera matrix, world transform, object-ID/depth/flow pass and source image.
- MGR scene export bridge receives reconstruction only with scale/reference caveats, registered camera set, confidence score and inferred geometry labels.
- Long-running SfM worker must support `job_id`, cancellation, progress, input hashes, log, resource cap, lossless artifact folder and resumable/checkpointable passes where backend supports them.

## 10 — MGR-original product capabilities and data contract

**Native components:**

- **Sight Ledger:** separates observed pixels/metadata, mathematically estimated measurements, and invented completion.
- **Blindside Truth:** identifies occlusion and unseen body/world regions before a pose or turntable is accepted.
- **Parallax Prosecutor:** detects baselines too weak for trustworthy 3D, planar/pure-rotation degeneracies and unstable points.
- **Pose Witness:** verifies camera transforms and skeleton/articulation independently from image aesthetics.
- **Spatial Replay:** reruns recorded captures through the same calibration/feature/pose pipeline for regression.
- **Never-Guess Scale:** prevents absolute real-world units unless an anchor/depth sensor/stereo baseline supplies them.

```json
{
  "capture_id": "mgr-capture-id", "camera_model": "pinhole", "calibration_id": "locked-id",
  "frames": [{"id": "frame-001", "timestamp_ms": 0, "intrinsics_id": "K-001", "pose_frame": "world_to_camera"}],
  "features": {"tracked": 0, "inlier_ratio": null, "reprojection_rmse_px": null},
  "geometry": {"source": "multiview|depth_sensor|single_view_prior", "metric_scale_verified": false,
    "observed_mask": "path", "occluded_mask": "path", "inferred_mask": "path"},
  "acceptance": {"status": "unverified", "failed_gates": []}
}
```

## 11 — Hardware and runtime constraints

Feature matching, calibration and modest SfM can run on CPU; dense MVS, neural depth and high-resolution live SLAM can be substantially faster with a supported GPU. CPU feasibility is not a real-time throughput promise. RAM/VRAM rise with image count, resolution, dense depth maps and feature graph; preflight jobs and downsample with transparent quality tradeoffs.

## 12 — Cost and deployment strategy

Start with free/local OpenCV calibration and Blender synthetic truth. Add COLMAP offline sparse/multiview jobs, then optional dense reconstruction only for inputs with adequate overlap and texture. Keep image resolution tiers, max frames, CPU utilization, processing time and storage budgets visible. No proprietary vision API needed for initial proof; licensing and computation are not literally zero-cost.

## 13 — Failure cases that must be seen, not hidden

1. Focal-length mismatch yields plausible scene with wrong dimensions.
2. Distorted pixels fed as undistorted create systematic pose drift.
3. Wrong camera convention flips or mirrors reconstruction.
4. Static scene assumptions fail with walking crowds/animated avatars.
5. Repeating wall patterns cause confident wrong feature matches.
6. Planar image can fit a homography while providing unreliable depth.
7. Tiny baseline makes depth huge/uncertain; pure rotation offers no triangulation.
8. Occluded hand appears to vanish; 2D judge confuses view-dependent visibility with geometry deletion.
9. Motion blur/shutter and rolling shutter break rigid pinhole solve.
10. Reflections are reconstructed as actual objects behind mirrors.
11. AI upscaling invents features, corrupting geometric match.
12. Monocular unit scale is asserted as meters without anchor.
13. Camera drift looks acceptable locally but fails on loop closure.
14. Similar images of different identity pass pixel score despite incompatible geometry.
15. Featureless backgrounds have too few reliable tracks; frame should fail honestly.

## 14 — Adversarial and quantitative proof suite

| Gate | Inputs/expected evidence | Rule |
|---|---|---|
| Camera intrinsics | Known checkerboard views, lens distortion | Reprojection RMSE tracked and statistically compared to held-out views |
| Pose | Rendered known 6DoF transforms | Rotation/translation error, frame convention, covariance measured |
| Correspondence | Synthetic visible feature IDs | Inlier precision/recall, track survival, RANSAC rejection |
| Depth | Stereo with varied baseline | Scale-anchored depth error vs known pixels; fail weak disparity |
| Geometry | Occluded mannequin/hand | Hidden regions labeled unobserved; no invented certainty |
| Optic flow | Moving camera and rigid/nonrigid targets | Endpoint/angular error and occlusion-aware scoring |
| Degeneracy | Pure rotation, plane, repeated texture | Uncertainty warning or abstention, not confident mesh |
| Loop | Closed path with repeated exposures | Drift/ATE/RPE and relocalization failure cases |
| Novel views | Held-out viewpoints | Reprojection, silhouette/depth and semantic identity consistency |
| Performance | Various resolutions/frame counts | CPU time, peak RAM, success %, cancellation/restart |

Set numeric tolerances only after baselining synthetic ground truth and camera hardware; thresholds for a realistic noisy mobile video cannot be borrowed blindly from noise-free Blender renders.

## 15 — Architecture placement and build work order

1. **Camera truth**: versioned intrinsics/distortion/extrinsics schemas, coordinate validation and image provenance.
2. **Synthetic spatial lab**: Blender scenes emitting image/depth/normal/flow, world poses and controlled occlusion masks.
3. **Tracks and pose**: OpenCV detector/flow + geometric RANSAC + PnP/essential pose, with abstention states.
4. **Reconstruction adapter**: COLMAP sparse pipeline when multiple views exist; preserve confidence and unseen regions.
5. **Vision-informed editor**: overlay observed vs proposed geometry, allow owner corrections to pose, model and clothing layers.
6. **Truth before claims**: connect the Vision Judge to S07 raw AOV/depth/object-ID and S02 lens/light data so rotated poses cannot pass solely through image similarity.

## 16 — Acceptance / research-to-production boundary

**Scoped research documented** only when primary sources, equations, design and adversarial tests exist—this file meets that documentary scope, not runtime readiness.

**Production S12 accepted only after**: camera calibration with measured holdout error; strict pose-frame/scale checks; deterministic synthetic sequence featuring occlusions and baseline variation; feature/flow residuals; robust pose and RANSAC evidence; honest failure on pure-rotation/planar cases; multiview reconstruction with provenance; novel-view silhouette/depth evaluation; memory/runtime safety and recovery; explicit ownership/privacy/licensing review; and user-facing observed/inferred/unobserved overlays. No claim of 100% accuracy can be made because underconstrained images do not contain hidden surfaces.

**Recommendation:** immediately implement **Blindside Truth + Parallax Prosecutor** as pre-generation gates. They directly address Tevin missing hands, short arms, rotating-character identity tests and false image-match confidence without waiting for a large custom neural vision model.
