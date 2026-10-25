# S12 — External Provenance for MGR Spatial Sight

**As researched:** 2026-10-25 · **Inspection:** Selected primary documentation, maintainers' repository notes and academic authors' papers. Not an exhaustive source-code/license audit or reproduced benchmark. Native feature specifications remain separate in `research/chapters/S12-COMPUTER-VISION.md`.

| Primary authority | Source | Supported finding | MGR use and diligence |
|---|---|---|---|
| OpenCV maintainers | [Camera calibration tutorial](https://docs.opencv.org/5.0/tutorials/calib3d/camera_calibration/camera_calibration.html); [calibration/reference functions](https://docs.opencv.org/4.7.0/d9/d0c/group__calib3d.html) | Camera intrinsics and distortion are estimated from known 3D↔2D correspondences; `solvePnP`, essential geometry and pose recovery are available. | Build camera witness and pose tests. Record installed OpenCV version and numerical limits; do not confuse projection match with unique hidden geometry. |
| OpenCV maintainers | [OpenCV 5 optical flow tutorial](https://docs.opencv.org/5.0/tutorials/others/optical_flow.html) | Sparse Lucas–Kanade and dense Farnebäck optical flow estimate image displacement between frames. | Track motion and measure residuals. Flow is not automatically metric 3D motion; occlusion and brightness consistency matter. |
| OpenCV maintainers | [4→5 migration notes](https://github.com/opencv/opencv/wiki/OpenCV-4-to-5-migration) | Some calibration and geometry APIs move between modules in OpenCV 5. | Avoid hardcoded import/header assumptions. Integration must detect installed version. |
| COLMAP project maintainers | [Official overview](https://colmap.github.io/); [tutorial](https://colmap.github.io/tutorial.html); [FAQ](https://colmap.github.io/faq.html) | SfM estimates registered camera poses/sparse points; MVS computes depth/normal maps and can fuse dense point clouds/surfaces. | Study reproducible CLI flow, image overlap and camera suitability. Verify scene/input ownership and precise binary/library licensing. |
| COLMAP maintainers | [Maintainers' tutorial source](https://github.com/colmap/colmap/blob/main/doc/tutorial.rst) | Workflow has explicit feature matching, camera models, sparse SfM and dense MVS stages. | Make each MGR stage inspectable, resumable and auditable; independent validation required. |
| Campos et al. (original authors) | [ORB-SLAM3 research paper](https://arxiv.org/abs/2007.11898); [author-maintained repo](https://github.com/UZ-SLAMLab/ORB_SLAM3) | Visual, visual-inertial and multimap SLAM support monocular, stereo and RGB-D with pinhole/fisheye models. | Inspiration for trajectory/map status and loop-closure proof. Review third-party code license and dependencies before any incorporation; do not imply license-free proprietary reuse. |

## Scientific restrictions and unresolved claims

- Single-perspective images cannot determine a uniquely correct full 3D body or scene. Missing occluded features are unknown without extra views, strong priors or measured data. Hypotheses need explicit confidence labels.
- Monocular SfM ordinarily has scale ambiguity absent measurements, stereo baseline, depth sensor or inertial/gravity constraints. Poses can also be wrong under insufficient parallax, mostly planar scenes and camera rotation without translation.
- Reprojection fit alone is necessary but insufficient: overfit distortion/intrinsics, degeneracy and low baseline can yield low error but poor geometry.
- Optical flow can arise from moving camera, moving object, illumination, occlusions or frame interpolation. It is not a 3D mesh/rig detector.
- Open-source library use does not automatically license the authors' third-party test videos, images, datasets or camera calibration captures for commercial distribution.

## Reproducibility and acceptance recipe

1. Write an MGR-owned Blender scene with ground-truth camera trajectory, known `K`, distortion perturbation, depths, optical flow and multiple occluders.
2. Split sequences by feature richness, pure camera rotation, planar geometry, translation baseline, moving objects and repeated backgrounds.
3. Execute OpenCV calibration, matched-feature rejection, flow and robust pose estimation. Record version, precision, seed when applicable, inlier masks, camera frames and reprojection residuals.
4. Run COLMAP sparse reconstruction on sequence with adequate overlap; compare recovered poses and points against known synthetic truth after appropriate gauge/scale alignment.
5. Explicitly mark unseen regions and insufficient-parallax cases as uncertain; compare novel-view depth and silhouette in held-out frames.
6. Report CPU time/RAM and failure states before considering live video or GPU optimization.

**Assessment:** These sources justify a buildable, testable vision pipeline and truthful confidence gates; they do not prove any existing MGR feature currently satisfies them. Do not present a generated character turntable as true same-character geometry until camera and model evidence support it.
