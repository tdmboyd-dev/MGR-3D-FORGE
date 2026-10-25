# R15 — MGR interpretation of Carnegie Mellon robotics research

**Audit:** 2026-10-25, primary Carnegie Mellon Robotics Institute publication abstracts/pages and associated original repositories. **Scope:** robotic perception, 3D mapping, semantic world state, dynamic objects and human pose. This is research architecture, not execution of university research models. Verified citations/rights: [R15–R16 sources](../external-provenance/R15-R16-SOURCES.md). External names are confined here as scholarly attribution; implementation capability names stay MGR-native.

## Five methods with practical Forge translation

| Primary method | Evidence-based lesson | MGR native outcome | Input / compute / validation |
|---|---|---|---|
| Dense RGB-D SLAM with 3D Gaussians (SplaTAM) | Track camera while constructing image-renderable Gaussian geometry from depth/video | **Reality Trail**: synchronized camera path + multi-view appearance with confidence-labeled geometry | Calibrated RGB-D frames; GPU helpful/likely for learning/rendering, CPU geometric checks; loop trajectory error, held-out novel views, geometry/depth consistency |
| Semantic spatio-temporal SLAM for dynamic navigation | Joint geometry and semantic/instance-level tracking maps moving or changing objects | **Living Space Ledger**: split static wall/floor geometry from moving actors, per-ID temporal history | Camera/depth tracks and segmented detections; false-match/occlusion tests, identity precision/recall over time, dynamic collision truth |
| 3D monocular cuboid object SLAM (CubeSLAM) | Object cuboids and multi-view SLAM can help jointly explain 3D object placement, but one image alone is underconstrained | **Primitive Prior Solver**: labeled box/architectural primitive hypotheses corrected by camera multi-view observations | Monocular video, calibrated camera, category dimensions optional; reprojection, orientation/size error, explicit unknown scale |
| LiDAR-based lightweight localization / mapping | Geometry and odometry can work under conditions where RGB appearance is unreliable; computationally focused SLAM balances precision and runtime | **Sparse Geometry Atlas**: point-cloud+pose scene submaps with predictable computational budget | LiDAR point scans/trajectory; device needed for physical test, CPU ICP/registration plausible; trajectory drift, loop closure and scan alignment |
| Smoothed submap/ICP mapping and 3D volumetric segmented SLAM | Short-range registration plus map subregions reduces whole-world map management and error propagation | **Subrealm Mapping**: confidence-aware map cells, local registration and global correction without flattening provenance | RGB-D/LiDAR or synthetic point sets; ICP residual, loop-closure jump and preservation of actor/anchor IDs |

## Actual architecture

Scene evidence enters `ObservationLedger` (`sensor`, intrinsic/extrinsic, timestamp, calibration, rights). `PoseTrack` resolves device/camera path. `SpatialSubmap` carries point/volume/Gaussian or semantic objects in a coordinate frame. `MapFusion` proposes submap alignment; `DynamicMask` excludes movers from static walls. `WorldTruth` accepts/rejects proposed geometry using reprojection, multi-observation coverage and topology checks. Real-time render representations can be specialized and non-watertight; gameplay collision and printer solids require distinct conversion and acceptance.

## MGR applications

1. Tevin and other characters keep body/wardrobe semantic IDs through camera and scene motion; a model that re-identifies a coat as part of a wall must fail.
2. Captured rooms get physical traversal spaces instead of just a pleasant neural view; measured confidence differentiates floor from specular reflection.
3. Realm Cells store local maps, merge corrections and avoid forcing entire world resimulation after an extra captured view.
4. Director's camera can choose new viewpoints to reduce unseen surface gaps before committing to final geometry.

## Rights, data and hardware reality

- CMU publication abstracts are publicly readable research evidence, **not** blanket permission to copy paper figures, trained weights, source code or original scans. Projects vary in licenses.
- The OpenPose public repository contains explicit **non-commercial** notices/terms in project material. Do not silently embed a human-pose detector/weights from it into MGR's commercial default pipeline.
- GPU is not required for all camera geometry, spatial alignment or primitive hypotheses; dense learned RGB-D/gaussian scene reconstruction can be significantly GPU-intensive. Hardware and latency profiles are untested here.
- Real sensor datasets include potentially sensitive human body/movement and indoor imagery. Consent, rights, retention and access controls remain necessary.

## Required implementation acceptance

1. Synthetic static room + moving human generates stable static walls and a separate tracked actor; no ghost duplicate after occlusion.
2. Three overlapping RGB-D traversals, then loop back, trigger map correction without losing anchored object identities; metric pose and map error quantified.
3. Monocular image produces bounded cuboid hypothesis marked `INFERRED`, with scale `UNKNOWN` until anchored; wrong scale anchor deliberately fails.
4. Scan point-cloud submaps from different poses merge with logged residual and reject intentionally incorrect correspondences.
5. Sparse/lightweight scene map runs within named CPU/RAM budget; dense neural path benchmarked separately on named GPU, with no false real-time assertion.

**Status:** five source-supported independent MGR designs and repeatable gates. No university algorithm/code copied, trained or run. These are implementable decisions, not shipped components.
