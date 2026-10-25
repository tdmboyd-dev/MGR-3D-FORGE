# S04 — MGR Spatial Transform Intelligence

**Owner:** Money Grind Religion. **Research date:** 2026-10-25. **Maturity:** RESEARCHED at mathematics/contracts level; not yet an end-to-end executable third-party library audit, nor VERIFIED as an integrated cross-engine transform layer. External technical references live only in `research/external-provenance/S04-TRANSFORM-SOURCES.md`.

## Plain-English bottom line

Three-dimensional software cannot reliably agree on a character's location, camera direction, rotation, scale, pose, or reconstructed depth without a strict agreement on coordinate systems and transformations. Many apparent 3D failures are **not** mesh-generation failures: they are wrong axes, wrong handedness, a quaternion component ordering mistake, meters-versus-centimeters, inverted matrix composition, or poorly conditioned camera geometry. Forge needs a single MGR-native transform contract that validates and converts data at every importer/exporter and solver boundary.

## 1. Definition and exact mathematical contract

Let a 3D point be a column vector `p∈R³`. A rigid transform is `T=(R,t)∈SE(3)`, where `R∈SO(3)` (orthonormal, determinant +1) and `t∈R³`. It maps a source-frame point into a target frame: `p_target = R p_source + t`. Homogeneous form: `[[R,t],[0,0,0,1]] [p,1]ᵀ`. Composition with column vectors is `T_A←C = T_A←B · T_B←C`; inverse is `(Rᵀ,-Rᵀt)` for a true rigid transform. A reflection has determinant −1 and cannot be silently treated as a pure rotation.

Similarity transforms add a scale `s>0`: `p'=s R p + t` (Sim(3)). Nonuniform scales and shear are affine transforms, **not** rigid motions. They can distort skeletons, normals, physics and camera calibration. For camera coordinates `P_c=R_c←w P_w + t_c←w`, a pinhole image uses `u=f_x X_c/Z_c+c_x`, `v=f_y Y_c/Z_c+c_y` for positive visible `Z_c` in this *explicitly defined* camera convention. Undistortion and known camera intrinsics are separate prerequisites. A single image ray has unresolved distance.

Angles in radians. Serialization must declare units, axes, handedness, transform direction, matrix-vector convention, and quaternion component order. A bare array of sixteen numbers is **not** a sufficient production contract.

### Quaternion specifics

- Quaternion `q=(x,y,z,w)` by explicit MGR exchange convention, normalized to unit norm before use; `q` and `−q` represent the same 3D rotation and should not fail identity comparison.
- A zero, NaN or infinite quaternion is invalid. Normalization may repair minor floating drift only within a bounded tolerance, never an unknown transform.
- Quaternion interpolation must use shortest-arc handling for sign equivalence and stable SLERP or a justified near-angle linear approximation. Euler interpolation around ±π can spin the long way.
- Rotation multiplication order, local-vs-world orientation and right-vs-left multiplication need tests. A matrix-to-quaternion round trip should preserve rotated vectors even if the quaternion sign flips.

### A direct degeneracy proof for the reconstruction pipeline

The mapping `(X,Y,Z)→(fX/Z,fY/Z)` has the same output for `(kX,kY,kZ)` for any `k>0`. Stereo triangulation only resolves metric scale if camera baseline/poses are metric. Two rays that are parallel or nearly parallel have weak depth observability; depth error grows with distance and shrinks with baseline and parallax. Reprojection agreement by itself does not prove a unique or correct physical model if the rig, calibration or image correspondence is wrong.

## 2. Production usage

- Cameras: projection, view matrix, optics and lens distortion; moving shots need frame-consistent world transforms.
- Characters: bind pose, skeleton hierarchy, left/right bones, skinning matrices; no negative-scale mirrored bone assumptions.
- Animation: orientation interpolation, rig retargeting, character velocity and stable attachment poses.
- Worlds: floating origin for huge coordinates, chunk-relative transforms, reparenting and precision budgets.
- Reconstructing reality: solve relative camera poses, calibrated stereo, triangulation and bundle adjustment with outlier rejection.
- Export/import: Blender objects, glTF scenes, optional Unreal/Godot/USD; conversion is explicitly tested rather than inferred.

## 3. Standards and conventions

- The current native Forge `Mesh` coordinates are Y-up (ground X/Z), documented in `forge/geometry.py`. Its `forge/spatial_truth.py` pinhole proof separately defines camera +Z forward. Those are **different frames** and require explicit transformation when connected.
- glTF 2.0 is a right-handed, Y-up exchange format, with rotations serialized in xyzw quaternion order and transforms encoded as TRS or matrix. Document the specific local camera/asset conversion rather than silently swapping axes.
- Coordinate-metadata contract proposed: `{from_frame,to_frame,units_m,handedness,up_axis,forward_axis,matrix_layout,translation_m,rotation_xyzw,scale}`. Consumers must reject missing or contradictory fields. Do not infer Tevin's true physical height from arbitrary unitless pixels.
- Orthogonal matrices meet `RᵀR≈I` and `det(R)≈+1`; inverse and repeated composition should remain numerically bounded.

## 4. Research and mathematical literature

Important themes: projective camera geometry, Lie groups SO(3)/SE(3), nonlinear least squares and sparse bundle adjustment, uncertainty propagation, robust stereo, numerical conditioning, large-world floating origins. Standard treatments include multiple-view geometry and optimization texts; no unreviewed source code or proprietary formulas are necessary to author the MGR contract. Specific technical sources and inspection depth are recorded in the companion provenance ledger.

## 5. Open implementations and engineering lessons

| Implementation family | Useful architecture lesson | Current review status | MGR disposition |
|---|---|---|---|
| Eigen Geometry | Distinguishes abstract rotations, quaternions, affine/projective transforms and type-aware composition | Official geometry reference inspected; library source/tests not fully audited | STUDY; build small native CPU validation first |
| OpenCV calib3d | Intrinsics/extrinsics, homogeneous triangulation, reprojection and calibrated stereo | Official API/reconstruction reference inspected; algorithms not reimplemented | ADAPT behind isolated reconstruction adapter when licensed |
| Ceres Solver | Optimization and rotation manifolds, local parameterization; robust least squares for bundle adjustment | Official version/API docs inspected; not installed or benchmarked | STUDY for future scalable calibration |
| Sophus | Lie group SO3/SE3 and tangent-space update semantics | Upstream README inspected; exact code/license/revision still requires audit | STUDY |
| SciPy Rotation | Quaternion scalar-first vs scalar-last flags and numerical utilities | Official API docs inspected; not required for native core | STUDY / optional validation oracle |

None of these libraries is currently asserted to be installed or integrated into the user's runtime for S04.

## 6. Models

**No neural model is required for exact rigid transform arithmetic.** Learned pose/depth estimators can propose orientations and geometry, but their outputs still require the same coordinate contracts and calibrated validation. Candidate neural estimator weights are outside the S04 core and must pass their own license/benchmark gates.

## 7. Datasets and synthetic evaluation data

Start with owned deterministic synthetic transforms and generated camera correspondences; they avoid ambiguous licensing and provide exact ground truth. Future real capture benchmarks can use approved calibrated multi-view photos, checkerboard camera data, and publicly documented SfM datasets only after reviewing dataset/subject/privacy rights. Required metadata: camera calibration, baseline, metric units, distortion, ground-truth transforms and error tolerances. No dataset downloaded in this pass.

## 8. Licensing

The MGR contract/math code can be independently authored and released under the repository's own applicable terms. Any imported Eigen/OpenCV/Ceres/Sophus/SciPy code, models, example assets or datasets needs an exact version/commit license and dependency audit. A GitHub README is insufficient commercial proof; see dedicated `research/LICENSE-RISK.md`. Current phase imports **no** external S04 source.

## 9. APIs/providers

Native CPU implementation of geometry and transforms is primary. Optional high-level solvers may use audited C++/Python libraries through a narrow adapter. A paid 3D-generation API is not necessary for rotation, projection or calibrated triangulation mathematics.

## 10. Native alternative — proposed build contract

`MGR Transform Guardian` (code module not yet created):

1. `RigidPose` with `(source,target,rotation_xyzw,translation_m)` and explicit handedness/axes.
2. `validate_transform`: finite checks, orthogonality, determinant, unit scale bounds, rejection of reflections/shear unless explicitly convertible.
3. `compose/invert/apply`: declared composition direction, round-trip loss bound, floating origin support.
4. `CameraCalibration`: `fx/fy/cx/cy`, image size, positive focal, distortion coefficients, version and confidence.
5. `triangulate_rays`: normalized calibrated rays in a common frame, closest-ray solution, angle/parallax threshold, positive-depth gate, reprojection residual and uncertainty/confidence receipt. Reject near-parallel rays or incompatible frames.
6. `scene_transform_audit`: compare bones, cameras, GLB/Blender/target engine and scene graph placements with measured landmark positions before accepting visual equivalence.
7. `world_origin_manager`: use double precision scene/global coordinates and camera-relative floating local transforms where applicable; prove round trips over large offsets.

No output that derives a 3D point from **one monocular ray** may be labeled a measured location without an external depth cue.

## 11. Hardware/runtime

Scalar/matrix operations, quaternion interpolation, validation and sparse camera triangulation are CPU-suitable and need no big GPU. Batch bundle adjustment on thousands/millions of correspondences benefits from optimized linear algebra, multi-core CPUs and possibly GPU but must be measured. Floating-point accuracy matters regardless of accelerator: single-precision large-world coordinates lose centimeter-level precision at sufficiently large offsets.

## 12. Cost and timeline

No API charges for the native core. Main costs are engineering/tests and calibrated capture quality. A small typed pose/calibration implementation and synthetic test suite are much cheaper than acquiring a new neural GPU pipeline. Commercial solve budgets should be measured using points/cameras/iterations/time/memory, not marketing claims. No dollar estimate is credible until target data size and hardware are fixed.

## 13. Failure modes and controls

| Failure | Symptom | Mandatory control |
|---|---|---|
| Axis swap / hand mismatch | Facing backwards, wrong gravity, mirrored normals | Typed frame contract + test basis vectors |
| Wrong transform direction | Camera/character moves in reverse or off-screen | Inverse/compose/point round-trip tests |
| Invalid quaternion or order | Twisted wrists, 180° flips | Explicit xyzw order, normalize, sign-equivalence |
| Negative scale/reflection | Bad skin or face culling | Determinant gate, separate reflection transform |
| Degenerate stereo baseline | Huge unstable depth or NaNs | Minimum angle, positive depth, residual/uncertainty receipt |
| Calibration/units mismatch | 100× room or misaligned objects | Metric units, focal/principal validity, reprojection |
| Large-world float precision | Shaking vertices or characters | Double global + local origin, camera-relative transforms |
| Normal transform under nonuniform scale | Incorrect light shading | Inverse-transpose normals / renormalization |
| Euler gimbal singularity | Sudden motion jumps | Quaternion/SO3 plus retarget/continuity checks |

## 14. Evaluation and metrics

Use: rotation geodesic angle error (degrees), translation absolute/relative error (meters), orthogonality residual (`||RᵀR−I||`), determinant deviation, point transform round-trip, reprojection RMS/max pixels, ray convergence angle, line-to-line closest approach distance, 3D reconstruction absolute error on synthetic ground truth, chirality/pass-positive-depth fraction, and numerical stability at scene distances from centimeters to kilometers. Report device/runtime, input units, solver version, degeneracy count and confidence separately.

## 15. Placement and integration

Canonical source of truth in `docs/MGR-NATIVE-CANON.md` and `docs/BUILD-REGISTER.md`. Own math/validation under `forge/` with stable typed interface. `forge/spatial_truth.py` already proves perspective nonuniqueness; `forge/perception.py`, `forge/director.py`, `forge/cinematic.py`, `forge/animation.py`, `forge/character.py` and `forge/blender_bridge.py` must share the new transform contract, not independently guess conventions. External engines consume outputs through adapters with round-trip receipts. Keep training/inference separate from measured calibration.

## 16. Required acceptance tests, including adversarial cases

- Identity, translation-only, 90° rotation, 180° rotation, nontrivial quaternion; compose/inverse/apply around all three basis axes.
- `q` and `−q` identical outputs; near-zero quaternion rejected; near-180° SLERP does not flip unexpectedly.
- Mixed centimeters/meters, mirrored determinant, shear and changed-handedness matrices fail closed unless explicit conversion requested.
- Known camera intrinsics/extrinsics project known 3D points to exact pixels. Reprojection/inversion estimates must stay within set thresholds.
- Two distinct 3D depths on one camera ray are **both valid**; no false monocular depth claim.
- Two calibrated cameras with known metric baseline recover multiple synthetic 3D targets. Triangulation rejects parallel/near-parallel rays and points behind a camera, tracks pixel noise and extrinsics uncertainty.
- Camera-space→world→camera-space coordinates reproduce source within tolerance; compare Y-up world against camera +Z local conventions.
- Large-coordinate translation preserves sub-meter accuracy through double/global and relative local coordinate paths.
- Bone attachment poses remain consistent between Blender render and GLB export, including mirrored left/right parts.
- Benchmark 10, 100, 10,000 camera correspondences with CPU time and memory, deterministic precision and no silent invalid entries.

### Current evidence vs completion

Existing `forge/spatial_truth.py` has a pinhole project function and pixel-to-unit-ray proof. `tests/test_spatial_truth.py` asserts one-pixel/two-depth ambiguity, finite validation and reproducible sectioning; actual Windows tests have already passed in the parent wave. **Concurrent implementation note:** the main builder reports a newly implemented calibrated **parallel-camera** two-ray triangulation and reprojection guard; this research agent has not independently run or verified those additions. That is a useful narrowly scoped first solver, **not** evidence that arbitrary rotated cameras, lens distortion, full SE(3), camera-pose uncertainty, depth conditioning or production stereo reconstruction are solved. For rectified stereo `Z=fB/d`, and disparity uncertainty `σ_d` induces approximately `σ_Z≈Z²σ_d/(fB)`; therefore tiny disparity can yield wildly uncertain depth even when reprojection seems convincing. Extend rays to a shared world frame through full rotations and translations, then test parallax, both-camera positive depth, independently calibrated reprojection and uncertainty receipts before generalizing claims.
