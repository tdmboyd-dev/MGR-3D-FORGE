# R15/R16 external provenance — CMU Robotics and Berkeley AI

**Date:** 2026-10-25. Official university primary academic publications, project pages and associated source-license indications. R15/R16 translate *ideas* into new MGR capability; no paper code, media, datasets or weights were copied. Pages primarily furnish abstracts/project summaries, **not complete implementation reading or reproduced experiments**. Exact project revision, dependency licenses, model/data rights and hardware should be verified before integration.

| ID | Verified research source | Primary URL | What is evidenced | Source/code/data caveat |
|---|---|---|---|---|
| C1 | CMU Robotics Institute, SplaTAM dense RGB-D SLAM | https://publications.ri.cmu.edu/splatam-splat-track-map-3d-gaussians-for-dense-rgb-d-slam | Camera tracking and dense scene representation with 3D Gaussians | Academic method description; no source/weight rights inferred |
| C2 | SplaTAM project source | https://github.com/spla-tam/SplaTAM | Public code exists for RGB-D Gaussian SLAM research | No exact current commit/license/admission verified; not copied or run |
| C3 | CMU spatio-temporal semantic SLAM | https://publications.ri.cmu.edu/toward-interactive-navigation-in-unknown-dynamic-environments | Semantic instance map and dynamic navigation/tracking | Publication only, independent implementation required |
| C4 | CMU CubeSLAM monocular object | https://publications.ri.cmu.edu/cubeslam-monocular-3d-object-detection-and-slam-without-prior-models | Object cuboid hypotheses plus multi-view SLAM | Single-image cuboid hypothesis not full reliable hidden shape |
| C5 | CMU lightweight 3D LiDAR mapping | https://publications.ri.cmu.edu/lightweight-3-d-localization-and-mapping-for-solid-state-lidar | Localization/mapping with solid-state LiDAR | Device and dataset unavailable here; no runtime claims |
| C6 | CMU point-cloud submap smoothing | https://publications.ri.cmu.edu/mapping-3d-underwater-environments-with-smoothed-submaps | ICP and locally aligned mapping submaps | Older environment-specific research, generalize cautiously |
| C7 | CMU segmented 3D volumetric SLAM | https://publications.ri.cmu.edu/segmented-slam-in-three-dimensional-environments | Volumetric submaps and flexible segmentation | Evidence historical; do not equate with modern runtime performance |
| C8 | CMU human pose OpenPose README | https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/README.md | Public human keypoint estimation implementation and research context | Project documentation flags free **noncommercial** use; commercial license gate |
| C9 | CMU OpenPose source/training | https://github.com/CMU-Perceptual-Computing-Lab/openpose_train | Training repo/research rather than generic commercial asset | Check exact model license/consent before any use |
| B1 | BAIR Manipulation By Feel | https://bair.berkeley.edu/blog/2019/03/21/tactile/ | High-res tactile RGB sensing and model-predictive tactile control from predicted observations | Sensor hardware/lab data needed for physical replication; no code imported |
| B2 | BAIR Whole-Body Conditioned Egocentric Video Prediction | https://bair.berkeley.edu/blog/2025/07/01/peva/ | Predict future first-person visual observations conditioned on whole-body motion | Video model weights/data not automatically licensed |
| B3 | BAIR Gradient-Based Planning for World Models | https://bair.berkeley.edu/blog/2026/04/20/grasp/ | Longer-horizon action optimization through predictive world states | Model validation and compute requirements unverified for MGR |
| B4 | Berkeley AUTOLab publication roster, Omni-Scan | https://autolab.berkeley.edu/publications.shtml | IROS 2025 fixed-camera bimanual Gaussian scanning and object inspection study listed | Public publication citation only; no actual robot assembly here |
| B5 | BAIR One-Shot Imitation | https://bair.berkeley.edu/blog/2018/06/28/daml/ | Demonstration-video imitation and meta-learning framing | Human demo data/model rights not included |
| B6 | Berkeley Robot Learning Lab publication list | https://rll.berkeley.edu/research.html | Broad robotic perception, grasping and manipulation research | Directory is context; not a standalone dataset/source license |

## Admission checks

1. Before using any outside model/code, resolve exact commit, SPDX/license file, transitive dependencies, pretraining dataset permissions and commercial deployment rights; study/use may have different legal scope.
2. University photographs, people, simulated agents and robot demonstration videos can have privacy, capture consent and copyright restrictions even when the article is publicly accessible.
3. A university method and its tested hardware do not guarantee an equivalent result on Time's Windows Blender machine or a consumer GPU; each MGR capability needs reproducible local evidence.
4. Pure CPU geometric methods, robotics control simulations, GPU Gaussian renderer and physical LiDAR/tactile instruments are distinct resource classes. Never flatten them into one budget claim.
5. Keep future external repo adapters isolated. Build MGR-owned `Reality Trail`, `Living Space Ledger`, `Contact Truth`, `Outcome Rollout Director` and `Capture Orbit Planner` through independent feature specs and validation gates.
