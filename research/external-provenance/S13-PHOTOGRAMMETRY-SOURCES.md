# S13 external provenance — photogrammetry and camera solving

Capture 2026-10-25. Source-specific facts, rights and inspection depth live here; MGR-native authority lives at `research/chapters/S13-PHOTOGRAMMETRY.md`. These are official source/docs and research datasets **not installed, copied, trained or benchmarked here**. Verify exact release/dependency/license before shipping any adapter.

| Primary source | URL | Verified technical evidence | Rights/inspection boundary |
|---|---|---|---|
| COLMAP official guide | https://colmap.github.io/ | SfM estimates camera poses and sparse reconstruction; MVS fills dense geometry. Incremental and pose-prior workflows exist. | OFFICIAL_DOC; code BSD/new BSD, dependencies separate; not executed. |
| COLMAP tutorial | https://colmap.github.io/tutorial.html | Traditional input photographs → camera pose/sparse 3D → dense multi-view stereo, fused points and optional surface stage. | OFFICIAL_DOC; output correctness depends on image coverage/calibration. |
| COLMAP camera/feature data | https://colmap.github.io/database.html | Shared camera intrinsics (focal, principal point, distortion) and per-image extrinsics (pose); geometric correspondence/track data. | OFFICIAL_DOC; database format version must be pinned. |
| COLMAP FAQ | https://colmap.github.io/faq.html | Pose priors, GPS/geo-registration and axis alignment are distinct steps; support fixed camera intrinsics and known-pose workflows. | OFFICIAL_DOC; GPS/EXIF alone not proof of metric accuracy. |
| COLMAP source rights | https://github.com/colmap/colmap/blob/main/doc/license.rst | Project new BSD license independent of third-party dependencies. | SOURCE_LICENSE; full dependency audit necessary. |
| COLMAP hardware/install | https://colmap.github.io/install.html | GPU acceleration available for feature extraction/matching and dense stereo; exact backend support varies by release. | OFFICIAL_DOC; no MGR hardware benchmark. |
| openMVG SfM | https://github.com/openMVG/openMVG and https://openmvg.readthedocs.io/en/latest/ | Camera models, feature matching/tracks, robust geometric estimation and triangulation/bundle-adjustment pipelines. | MPL-2.0; repo/doc inspection, not executed. |
| openMVS | https://github.com/cdcseacave/openMVS | Dense points, mesh refinement and textured mesh stage; memory-aware subscene processing exists. | AGPL-3.0 in upstream repo. Important commercial/copyleft review; no code imported. |
| AliceVision/Meshroom | https://alicevision.org/ and https://github.com/alicevision/meshroom | Node-based SfM/MVS/scanning workflow exposes modular stage DAG, image processing and mesh texture outputs. | MPL-2.0 framework; plugin/dependency model and GPU needs version-specific. |
| OpenCV calibrated geometry | https://github.com/opencv/opencv/blob/5.x/modules/geometry/doc/solvePnP.markdown | Camera intrinsic matrix/distortion plus 3D-2D correspondences allow camera pose estimation; refinement available. | Versioned source doc (5.x); check API compatibility. |
| OpenCV license | https://opencv.org/license/ | OpenCV versions 4.5.0+ use Apache License 2.0. | OFFICIAL_LICENSE; third-party algorithms/data rights distinct. |
| ETH3D benchmarks | https://eth3d.ethz.ch/ and https://www.eth3d.net/documentation | High-res stereo/multi-view benchmark, ground-truth/reference geometry and evaluation tools. | Dataset CC BY-NC-SA 4.0; **not blanket commercial training/shipping authorization**. |

## Critical distinctions

1. **Metric scale ambiguity:** monocular/unconstrained image-only SfM recovers shape only up to similarity transform without a measured anchor (camera baseline, coded target, surveyed object, reliable depth/LiDAR or known length). GPS/EXIF priors are neither universal nor perfect.
2. **Occluded regions are unknown:** inferred back-of-head/underside/inside is `INFERRED`, not a measured reconstruction, regardless of beauty of the texture.
3. **GPU truth:** CPU calibrated camera geometry and sparse solving is feasible; dense high-resolution MVS can be computationally heavy and often accelerated by GPU. No universal “no GPU needed” promise.
4. **Rights:** photos themselves may contain personal faces, proprietary interiors and copyrighted marks. Subject consent, capture access, asset licenses, retention policy and privacy review apply independently of open-source library license.
5. **Coverage:** a single stylized/concept image may make an attractive invented mesh, but cannot supply the triangulation baseline or accurate unseen surface required by multi-view photogrammetry.
