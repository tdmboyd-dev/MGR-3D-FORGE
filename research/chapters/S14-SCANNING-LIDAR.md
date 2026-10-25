# S14 — MGR Reality Capture and Measurement Intelligence

**Owner:** Money Grind Religion. **Date:** 2026-10-25. **Research state:** technical-source-reviewed and contract-designed. **Implementation state:** proposed capture/fusion lane, **NOT BUILT / NOT VERIFIED** as a physical LiDAR or scanner integration. Source names, links and external license caveats are isolated in `research/external-provenance/S14-SCANNING-SOURCES.md`.

## Plain-English result

We can create a native **MGR Real-Space Eye** that measures objects, rooms and worlds from actual depth sensors, mobile scans or point clouds and turns them into editable geometry with accuracy receipts. It must not claim to “see hidden surfaces” or infer perfect 3D from one picture. Depth hardware supplies imperfect sampled distances. Forge then needs calibration, noise handling, registration of multiple views, surface reconstruction, semantic cleanup, export, and verification. Real-world measurements can strengthen AI-generated scenery and characters, but scanning is **not** a shortcut around rigging, retopology, clothing, anatomy or copyright/consent.

## 1. Definition and fundamentals

Depth sensing estimates physical distances using techniques such as time of flight, structured illumination, stereo vision or direct ranging. A **depth image** stores a distance per pixel; an **organized point cloud** back-projects pixels through camera intrinsics into 3D; an unorganized cloud consists of XYZ samples and optional color, normal, intensity, confidence and timestamp attributes. LiDAR returns need not be one point per camera pixel. Registration places independently acquired scans in one coordinate system; dense fusion integrates repeated observations; mesh reconstruction infers connected surfaces. These are separate proof stages with separate uncertainty.

For ideal pinhole depth `z` (optical-axis depth), `X=(u-cx)z/fx`, `Y=(v-cy)z/fy`, `Z=z` in an explicitly declared camera frame. **Euclidean range `r` is not necessarily optical-axis `z`**: if a sensor provides radial range, back-project along the unit bearing ray with `p=r·bearing`. Pixel undistortion is mandatory when intrinsics specify lens distortion. The camera-to-world transform is an SE(3) matrix with declared frame direction, source time, units, scale and gravity/up-axis.

## 2. Production use cases

- Scan owned interior architecture for a traversable MGR room, preserving measured walls/doors and marking unseen regions as unknown.
- Scan selected physical objects/props for world placement or design recreation with dimensions and fit tolerances.
- Use smartphone LiDAR/depth maps as optional imports; also ingest offline industry point-cloud exchange packages with no device lock-in.
- Capture measured terrain/buildings from authorized aerial/terrestrial scans; distinguish asset visualization from survey-grade accuracy.
- Fuse body/character scans **only with consent and private storage**; separate geometry capture from likeness approval and automatic animation.
- Compare reconstructed digital geometry against new measurements to detect drift, wrong dimensions or fabricated surfaces.

## 3. Standards, schema and frame contracts

Define `ScanFrame` `{source_id,session_id,timestamp_ns,sensor_model,calibration_hash,width,height,depth_kind,depth_unit_scale,invalid_depth_policy,confidence_semantics,frame_id,world_T_camera,pose_covariance,cloud_hash}`. `ScanPoint` supports XYZ, optional RGB/intensity/normal, per-sample confidence, acquisition timestamp and semantic class. Cloud operations must preserve non-XYZ attributes by stable index or explicit remapping receipt.

- Physical geometry uses meters internally; converted source units and bounds are recorded. No silent LAS scaling/offset overflow and no RGB-D millimeter→meter confusion.
- For known sensor exchange, preserve named fields, datatypes, endianness, row/point strides and organized-shape metadata where applicable.
- Spatial dataset imports need coordinate-reference system, vertical datum, epoch/geoid when georeferenced. Local 3D coordinates and WGS84/ECEF/map projections are not interchangeable.
- Classification is **source-provided metadata** until validated, not an objective guarantee that a point is actually ground/tree/building/person.
- Never present a filled, smoothed or generatively inferred region as measured depth. Track sampled, interpolated, fused and inferred masks separately.

## 4. Research math and scientific mechanics

Calibration covers camera intrinsics, radial/tangential distortion and sensor-to-sensor rigid extrinsics. Temporal synchronization matters if either device/subject moves. Apply valid-depth mask and coordinate transform before any registration. Downsample in metric voxel grid with representative centroids and preserved weights. Estimate normals from local neighborhoods; reject unstable normal directions and isolated outliers. Registration needs initial alignment (known pose, features, marker or human-provided anchors) and iterative refinement.

**ICP caveat:** iterative closest point minimizes nearest-correspondence residuals locally; it is **not** a globally correct matcher. Point-to-point objective is roughly `Σ||Rp_i+t-q_i||²`, while point-to-plane minimizes `Σ[n_i·(Rp_i+t-q_i)]²`. Rejected correspondences, robust losses, multi-resolution schedules and correspondence gating can help but cannot fix insufficient geometric overlap, incorrect time alignment or a flat/symmetric scene's unobservable DOFs. A low RMSE does not imply correct alignment on a repeated corridor or circular object.

**Fusion:** signed-distance/TSDF integration averages consistent observed surfaces in a voxel structure given calibrated camera poses, truncation limits and confidence weights. No valid observation means unknown space, **not empty space** and not a fabricated solid. Surface extraction can produce holes/noisy edges; watertight cleanup is optional and provenance-labeled. Loop closure and pose graph optimization are needed to reduce long-sequence drift where sensors revisit spaces.

## 5. Open engineering and technical sources

Primary implementations teach independent lessons: camera/depth registration; point-to-point and point-to-plane ICP with robust kernels; scalable volumetric fusion; mobile-device depth confidence; structured point cloud messages; industry geospatial exchange. Their official documents/specifications are reviewed in the separate provenance ledger. None is claimed installed as an S14 runtime. Native contracts should allow optional adapter use after pinned-license/security/accuracy review.

## 6. AI / learned depth models

Monocular neural depth models can predict **relative/learned** depth priors from ordinary photos, but scale, glass, mirrors, occlusions and unusual scenes remain failure modes. If metadata cannot prove metric scale, mark such depth as estimated and never combine it with measured LiDAR at equal confidence. Foundation models may label scenes or hallucinate missing objects, but labels/holes are reviewable proposals. Proposed MGR rule: geometry inferred by AI has a distinct source mask, lower trust tier and a route to human review, not an automatic “truth” state.

## 7. Evaluation data

Prefer generated owned fixtures initially: exact calibrated pinhole depth grids; translating/rotating scan poses; orthogonal cube planes, curved object, repeated-wall corridor, polished/missing-signal patches, randomly outlying points, moving object and missing frame. Synthetic clouds supply exact registration matrices and world-space surfaces. Real scene captures then require explicit right-to-record permissions and standardized ground-truth targets measured independently with calibration tools. Avoid importing publicly released real-person scans without consent/license audit.

## 8. Licensing and privacy

Device SDK terms, software implementation license, scene photographs, captured faces/body scans, commercial database rights and geographic data terms must be checked independently. A permissive utility library does **not** legalize an unconsented scan of a person or confidential property. No model weights, scan data, geolocation secrets or owner-private images should enter the public repo. Research only uses linked primary documentation, no copied implementations.

## 9. APIs / providers / transport

MGR import-first design supports local depth frames, depth+color pairs, PLY/PCD/XYZ, scene cloud interchange and optional mobile-sensor exported arrays, then format-specific verified adapters. Device-live streaming is a separate optional tier with permission and calibration checks. Avoid forcing a paid LiDAR API; expose the same `ScanFrame` and `CloudFrame` contract regardless of sensor. Streaming/large-scene chunking must track bytes, memory and dropped packets; sign/validate manifest receipts before using a scan for asset approval.

## 10. MGR native subsystem design

1. **MGR Sensor Truth:** capability-detect device and fields, parse units/confidence, reject unsupported pose metadata.
2. **MGR Depth Lens:** undistort/back-project, distinguish radial range vs Z-depth, preserve masks and covariance.
3. **MGR Cloud Ledger:** stable point attributes, bounds, point count, invalid percentage, organized/disorganized state, lineage hashes.
4. **MGR Spatial Registration:** coarse alignment, multi-scale robust ICP, overlap/condition checks, covariance, residual and ambiguity flags.
5. **MGR Drift Guardian:** pose graph and loop closure receipts, calibration/clock drift, turntable and static background checks.
6. **MGR Volumetric Witness:** confidence-weighted TSDF/occupancy fusion; unknown/inferred/measured voxels never silently coalesce.
7. **MGR Reality Surface:** controllable mesh extraction, smoothing and decimation with nearest-surface deviations and holes retained or explicitly filled.
8. **MGR Scale Judge:** compare landmark-to-landmark distances, fit AABB dimensions, ground plane and known calibration objects; reject invented precision.
9. **MGR Scene Semantics:** optional labels for doors/walls/furniture/terrain/person with source confidence; no destructive category merging.
10. **MGR Live View:** exploratory cloud/mesh camera interface with scan coverage, uncertainty/occlusion heatmap and editable correction anchors.
11. **MGR Print/Game Bridge:** separate game collision/LOD, cinematic texture/material and printable watertight-shell outputs; scan alone proves none of them.
12. **MGR Capture Passport:** timestamped source rights, hashes, sensor/version, coordinate frame, calibration, registration transforms, RMS/fitness, uncertainty, measured-vs-inferred masks and independent render/measurement results.

## 11. Hardware requirements

No GPU is required for small synthetic point clouds, camera projection, deterministic voxel downsampling, nearest-point indexing or modest CPU ICP. Live 30–60 FPS high-resolution RGB-D fusion, millions of points and dense TSDF can benefit greatly from capable GPU/VRAM and fast RAM/storage. Do not promise realtime fusion on arbitrary laptop hardware. Sensor hardware is optional for offline testing; **actual physical scan tests require a compatible sensor or contributed capture**. Calibration accessories, stable lighting, measurement rods/targets and tripod/rig can matter more to accuracy than raw compute.

## 12. Economics and fast-path schedule

Start free with synthetic and owned offline point clouds plus native CPU transformations; introduce optimized registration/fusion adapters only after baseline accuracy and memory/time benchmarks. Export from an already owned mobile device if supported rather than buying scanning equipment before proving the pipeline. Profile sample counts, voxel size, frame rate, scene extent, RAM/VRAM, ICP iterations and input costs. No defensible price/performance promise exists until actual device, local machine and target room dimensions are measured.

## 13. Failure modes and recovery

| Failure | Why | MGR gate |
|---|---|---|
| Reflective/transparent/absorptive surfaces | Depth returns absent or biased | Low-confidence/unknown masks and scan-angle warning |
| Scan motion/rolling shutter | Time-skewed measurement frames | Timestamp sync and motion/pose residual |
| Bad camera intrinsics or mixed units | Distorted distances/shape | Calibration hash, dimension target and unit-check fixtures |
| Plane/symmetry ICP ambiguity | Insufficient constraints, local minimum | Observability spectrum, coverage and initialization proof |
| Long route drift | Accumulated pose errors | Loop closure/pose graph before final geometry commit |
| Ghost furniture/persons | Scene changed across passes | Dynamic masking and temporally segmented tracks |
| Hollow/missing rear surfaces | Occlusion | Visibility coverage, unknown-volume marking |
| Over-smoothed fusion | Fine features erased | Independent distance-to-raw scan deviation gate |
| Personal/private scan leak | Rights and identity risks | Permission/license, private storage and export redaction gate |

## 14. Metrics and benchmarking

Calibrated point-to-ground-truth RMSE/median/95th percentiles **in meters**; registration translation (m) and rotation (degrees), fitness/inlier ratio and overlap; false correspondence/outlier rate; cloud completeness/coverage; mesh-to-cloud Chamfer and signed surface distance where meaningful; reconstruction thickness/detail loss, pose drift per meter, confidence calibration, unknown-space proportion, precision/recall of occupancy, throughput points/s and frames/s, peak RAM/VRAM. Report every metric with dataset size, sensor, range, frame transforms, target tolerance and confidence interval—**not** an unsupported single quality score.

## 15. MGR repository fit

The current `forge/spatial_truth.py` demonstrates synthetic camera projection/ray depth ambiguity; `forge/meshqa.py` examines triangle indices/degenerated faces; existing procedural `forge/world.py` and `forge/geometry.py` build authored scenes. These are useful foundations **but not sensor ingestion, ICP, LiDAR, fusion or physical measurements**. Propose `forge/scan_io.py`, `forge/depth_truth.py`, `forge/cloud_truth.py`, `forge/registration.py`, `forge/fusion.py`, `forge/scan_receipt.py`; preserve existing world and source-of-truth structures and avoid duplicate competing schemas. Implement in small reversible feature slices with controlled fixtures, tests, and local Blender/engine import receipts. Read S04 transform contract before any world-frame conversion.

## 16. Hard acceptance tests

1. **Units/range:** depth-of-2.0m synthetic planar patch reconstructs within tolerance at center/corners; inputs encoded mm, m and radial range convert correctly; ambiguous unitless input fails.
2. **Calibration:** known distorted/undistorted 3D checker target projects/back-projects correctly. Deliberately corrupted focal length/extrinsics must trigger dimensional mismatch.
3. **Cloud safety:** randomized invalid floats, NaNs, duplicate samples, malformed point strides, wrong endianness, out-of-bounds field types and extreme coordinates fail cleanly with no hangs/overflow.
4. **Rigid registration:** rotated/translated overlapping asymmetric point sets recover metric transform; known rotation/translation tolerance recorded. Compare point-to-plane versus point-to-point and noisy robust fit.
5. **Negative registration:** parallel plane, symmetric room, near-zero overlap, moving object and strong outliers **refuse false high-confidence alignment**, even when a residual appears low. Record rotation/translation ambiguity.
6. **Fusion:** multi-view scans reduce noise on visible known surfaces while retaining unknown backface/occlusion masks. Confidence weighting impacts output predictably; same input seed/hash produces equivalent output.
7. **Coverage:** missed corners and transparent regions flagged unknown, not incorrectly filled; measured/inferred voxels survive mesh export receipt.
8. **Scale:** independent ruler/known distance check after registration/fusion; global scale errors caught even when rendered view seems right.
9. **Performance:** benchmark 10k, 100k, 1m points with CPU memory/runtime; optional GPU adapter separately verified with max budget and fallback.
10. **End-to-end:** capture/fixture→back-project→transform→register→fuse→mesh→GLB→independent Blender import/render, compare measured bounds and timestamps. Device-live physical metric acceptance only claimed after an actual hardware capture.
11. **Privacy:** captured human labels/photos blocked from public export unless authorized, rights tracked separately from coordinate correctness.

**Current honest conclusion:** This 16-field S14 research packet and native implementation blueprint are complete. **Production sensor integration, actual LiDAR measurements, physical room scanning and cross-device accuracy remain open implementation and verification tasks**; no fabricated progress percentages or verified hardware claims.
