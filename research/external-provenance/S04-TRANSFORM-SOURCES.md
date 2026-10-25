# S04 — External Technical Provenance (Not MGR Product Canon)

**Research date:** 2026-10-25. This ledger separates authoritative scientific/software sources from the MGR-native 3D Forge product contract in `research/chapters/S04-TRANSFORM-MATH.md`. Citing a source is not authorization to copy its implementation or redistribute its data.

## Primary sources and scope of inspection

| Primary source | Authoritative URL | Confirmed technical lesson | Inspection limit and required follow-up | MGR-native application |
|---|---|---|---|---|
| Khronos glTF 2.0 specification | https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc | Interchange uses right-handed coordinates, `+Y` up and quaternion components `[x,y,z,w]`; serialized transforms obey parent-child composition. | Specification consulted, not a full asset corpus validation. Pin revision and run golden GLB/JSON round-trip fixtures before claiming full compatibility. | MGR Coordinate Contract, strict importer/exporter conversion and receipt. |
| Eigen geometry official docs | https://eigen.tuxfamily.org/dox/group__TutorialGeometry.html | Affine/isometric transforms, translation, quaternion and composition types; distinguish rigid from general affine transformations. | API reference inspected, not numerical kernel audit; version/license audit required before vendoring. | Typed transform validation and composition tests. |
| OpenCV `calib3d` official reference | https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html | Pinhole intrinsics/extrinsics, distortion, reprojection, calibrated stereo and triangulation; camera conventions must be explicit. | Algorithmic API behavior reviewed, not validation of every solver path; pin OpenCV versions and test distortion, degenerate baselines and outlier correspondences. | MGR Camera Truth and two-view reconstruction adapter. |
| SciPy Rotation quaternion official docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_quat.html | Quaternion scalar-last ordering is default; scalar-first is an explicit option; a unit quaternion and its negative encode the same rotation. | Docs inspected, not library internals. Versions and tolerances need local verification. | Quaternion validation, canonical comparison and converter tests. |
| Sophus upstream | https://github.com/strasdat/Sophus/blob/main/README.md | SO(3), SE(3) and tangent-space updates are first-class geometry abstractions, useful in camera/pose optimization. | README and upstream APIs at discovery depth, not a full tagged-source or license/dependency review. | Inspired mathematical interface only; no copied implementation. |
| Ceres Solver official version history | https://ceres-solver.readthedocs.io/latest/version_history.html | Solver APIs evolve; manifold representations matter for constrained pose optimizations and older `LocalParameterization` examples may be stale. | Version-history check only. Need current official modeling/API docs and license review before implementing optional solver adapters. | MGR reprojection optimization backend contract with version pinning. |
| Blender official scene-unit docs | https://docs.blender.org/manual/en/4.0/scene_layout/scene/properties.html | Blender scene length/unit scale is configurable, so dimensions cannot be assumed invariant across `.blend` scenes and exports. | Blender 4.0 manual checked; verify installed Windows Blender version and export semantics experimentally. | Unit/axis manifest and Blender→GLB truth tests. |

## Mathematical caveats that must become negative tests

1. **Stereo parallax and conditioning.** For rectified pinhole stereo, approximate depth is `Z = f B / d`, with focal length `f` in pixels, baseline `B` in metric units and disparity `d` in pixels. The first-order sensitivity is `|∂Z/∂d| = fB/d² = Z²/(fB)`. Small disparity (far targets) therefore magnifies even tiny correspondence noise. Reject or label ill-conditioned geometry; do not accept a low reprojection error as proof of accurate depth.
2. **Nonparallel rotated cameras.** A horizontal baseline shortcut is valid only for a specifically rectified/parallel camera rig. General reconstruction must transform normalized rays with each camera's full rotation and center into a common world frame, solve closest approach/least-squares 3D intersection, check cheirality in **each** camera frame and reproject with each camera's own intrinsics/extrinsics. Do not apply the rectified disparity formula to unrectified images.
3. **Parallel and near-parallel ray gate.** If `a·b` approaches ±1, the two-ray normal equations become singular or ill-conditioned; use angular/condition-number thresholds and return explicit insufficient-parallax diagnostics, not fake precision.
4. **Scale ambiguity.** A monocular view cannot recover absolute depth or scale from perspective alone. A claimed metric stereo result requires a known metric baseline or another independent scale source.
5. **Lens distortion and calibration.** Ideal pinhole inverse rays are only valid for undistorted calibrated pixels. Distortion coefficients or model mismatch need explicit handling or an upfront refusal.
6. **SE(3) constraints.** Validate `RᵀR≈I`, `det(R)≈+1`, finite translations and correct frame composition. Shear and reflections must be tagged as affine transforms or rejected.
7. **Quaternions.** Normalize, disallow zero norm, handle antipodal `q/-q`, clamp dot products in interpolation and document `[x,y,z,w]` vs `[w,x,y,z]` conversion.
8. **Large worlds.** Prevent precision drift with floating origins or high-precision global coordinates paired with local render coordinates; test at large translations.

## Evidence integrity and licensing

The sources above support the research findings, not a claim that the native implementations are complete. Primary documentation and mathematical ideas may inform independent MGR implementation; code reuse requires an exact upstream commit, license, third-party notice review, tests, security evaluation and attribution where legally required. Further source-tree inspection should not overwrite MGR product naming or canon.

## Test trace requests

- Synthetic exact and noisy stereo at several baselines/depths, including parallel and 0.01°-parallax cases.
- Rectified and arbitrarily rotated rig pairs; independent principal points, focal lengths and lens distortion.
- Cheirality rejection, mirrored frame rejection, quaternion antipodal round-trips and chained 1000-pose drift checks.
- Blender and glTF unit/axis/bone attachment golden fixtures; large-world coordinate stress.
- Each result must record input calibration version, frame identity, residuals, thresholds and reason for rejection.
