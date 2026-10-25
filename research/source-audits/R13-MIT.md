# R13 — MIT OpenCourseWare: MGR Math-to-3D Research Audit

**Research:** 2026-10-25 · **Access depth:** MIT OCW course descriptions, syllabi, lecture-topic inventories and selected resource summaries. This is an instructional-method audit, **not** a full download/review of every lecture/video, nor a source-code audit. Primary references and restrictive content license recorded in `research/external-provenance/R13-R14-SOURCES.md`.

## Mission-critical finding

University math is useful only when converted into **pass/fail geometry and image tests**. MGR should derive its own equations/code and create owned example scenes, while preserving the course-material license boundary. Four educational threads unlock immediate fixes to character pose, mirror/scale errors, camera consistency and numerical drift.

## M1 — Coordinate transformations and matrix chains

**Source family:** MIT 18.06 linear transformations; MIT 6.837 coordinate transformations.

**Mathematics:** In homogeneous coordinates, a point transforms by `p_world = T_parent × R_joint × S_local × p_local`, after careful convention selection. The order is **not commutative** (`AB ≠ BA`). For a surface normal under a general transform `M`, use normalized `n' ∝ (M^{-1})^T n`; multiplying normals by arbitrary nonuniform scale `M` can be wrong. Composition must explicitly carry units and handedness.

**MGR-native use:** **Pose Axis Oracle**: flags parent-space/child-space errors in arms, hands, apparel attachments and cinematic cameras before rendering. Makes TEVIN full-body rotation and missing/short-limb poses mathematically inspectable.

**Proof:** Transform one test triangle and its normal under translation + quaternion rotation + nonuniform scale; compare dot product normal/tangent≈0 across poses. Draw known wrist/hand attachments and check bone transforms in T-pose, A-pose, fist and full camera orbit.

## M2 — Numerical stability, least squares and eigenvectors

**Source family:** MIT 18.06 matrix rank, singular values, least-squares, eigenanalysis.

**Mathematics:** For overdetermined measurements `Ax≈b`, minimize `||Ax-b||²`; rank deficiency or tiny singular values expose underconstrained reconstructions. PCA covariance eigenvectors suggest dominant geometric axes, but near-equal eigenvalues make axes unstable and can flip sign. Prefer QR/SVD over naive normal-equation inversion where condition number is problematic.

**MGR-native use:** **Rank Truth Judge**: rejects false confident camera/shape solutions when viewpoints are near-identical, features are coplanar or measurements do not constrain depth.

**Proof:** Use well-conditioned 3D landmark cloud versus planar card and pure-rotation frames; compare singular spectrum, residual, recovered pose and scale ambiguity. Perturb data slightly and require uncertainty/rejection for ill-conditioned fits.

## M3 — Ray casting, raster/depth and light visibility

**Source family:** MIT 6.837 graphics pipeline, ray casting/tracing and global illumination lectures.

**Mathematics:** A primary ray is `r(t)=o+t d`; triangle intersections require valid barycentric weights (`u≥0`, `v≥0`, `u+v≤1`) and nearest positive `t`. Visibility from surface point `p` to source `L` is blocked if any geometry intersects segment before `L`. In projection, z-buffer holds closest sampled surface, not every hidden object.

**MGR-native use:** **Visibility Prosecutor**: explains when Tevin's hand is physically absent versus merely hidden behind arm or coat, and distinguishes shadows from painted dark regions.

**Proof:** MGR-owned overlapping planes, fingers in front/behind body, partly occluded jewelry and point light shadow-caster; validate object-ID/depth AOV, analytical intersections and no missed occluder at grazing angles.

## M4 — Skinning, envelopes and motion continuity

**Source family:** MIT 6.837 introductory computer-animation/skinning lecture inventory.

**Mathematics:** Linear-blend skinning commonly evaluates vertex `v' = Σ_j w_j (M_j B_j^{-1}) v`, with weights nonnegative and summing to one. Quaternion-aware or dual-quaternion alternatives can mitigate twist volume loss; no single skinning method repairs unsuitable bone placement, topology or clothing collision.

**MGR-native use:** **Skeleton Integrity Witness**: tests joint count, hand completeness, limb lengths, deformation around shoulder/elbow/wrist and garment separation across multiple motions.

**Proof:** Locked bind-pose mesh, 60°/120° elbow flex, forearm twist and raised-arm animation; enforce joint attachment residuals, weight-sum tolerance, named-bone presence and mesh self-intersection reports.

## M5 — Camera optics, flow and recoverable depth

**Source family:** MIT 6.801 Machine Vision pinhole projection, optical flow and motion-field lecture material.

**Mathematics:** `u=fx X/Z+cx`, `v=fy Y/Z+cy` under undistorted pinhole assumptions. Pixel velocity depends on camera translation/rotation, object depth and independent object motion; an optical-flow vector is not a unique 3D displacement. Small baseline results in poorly conditioned depth.

**MGR-native use:** **Parallax Integrity Switch**: reject confident arbitrary-angle reconstruction from one view and request physically useful additional references when necessary.

**Proof:** Track known 3D checker points during camera translation versus pure rotation; compare reprojection and depth errors; mark hidden and near-infinite-depth geometry uncertain.

## How to implement without training a giant GPU model

1. Add pure math tests for coordinate transforms, normal matrices, quaternion rotations and world-to-camera inversion (CPU-only).
2. Generate small synthetic Blender scenes and export depth/object IDs, bind pose and camera transforms.
3. Add rank/conditioning metrics to any 3D-from-image/camera solve.
4. Use standard ray intersections or Blender BVH to distinguish occluded versus absent parts.
5. Run full TEVIN rig and outfit pose matrix before relying on Visual Judge pixel-score claims.

### Research/license risks and acceptance

MIT OCW explicitly uses **CC BY-NC-SA 4.0** with conditions. **Do not** copy lecture images, PDFs, code or derived instructional content into commercial MGR training/product packaging without separately evaluating permission and licensing. Mathematical formulas and independently coded standard algorithms are distinct from reproducing protected course content. Course outlines were read; selected linked lecture resources were identified, **not** every PDF and course exercise executed. Accept this as scoped research; only mark features engineered after deterministic witness tests, benchmarks and native source ownership. No result is proved by this document alone.
