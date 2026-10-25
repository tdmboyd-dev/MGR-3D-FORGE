# MGR Forge — Open Systems Research Queue

2026-10-25. Owner: MGR. This is **additional** to the 20-domain scientific map and the 24-source studio/lab register; nothing is replaced. The vendor/project names in this document are **research labels only**, not MGR features. Original sources and rights are maintained in `research/external-provenance/OPEN-SYSTEMS-SOURCES.md`.

The first tranche inspected official public descriptions and selected documentation, **not every source module or complete talk archive**. `SOURCED` means real authoritative source links were checked; `SELECTED_DOCS_AUDITED` means a relevant technical entry was also examined. Each of these still needs an end-to-end repository/module audit before it can be declared research-complete. Never equate research status with production readiness.

| ID | Research family | MGR capability question | Present research level | Build and proof next |
|---|---|---|---|---|
| O01 | Godot | Scene graph, render path, animation, world runtime | SELECTED_DOCS_AUDITED | Export GLB, launch imported real scene, measure collision/fps |
| O02 | Google Filament | PBR, physically motivated material authoring, render QA | SELECTED_DOCS_AUDITED | Verify camera/light/material parity via reference images |
| O03 | bgfx | Graphics API portability and backend independence | SELECTED_DOCS_AUDITED | Renderer adapter spike and measured cross-backend output |
| O04 | OGRE | Rendering subsystem and resource abstraction | SOURCED | Versioned renderer/plugin source audit |
| O05 | Panda3D | Python-first runtime, scene controls, asset transport | SOURCED | Independent GLB actor/camera/navigation import |
| O06 | OpenSceneGraph | Large-world paged scene graphs | SOURCED | License/version audit before considering native patterns |
| O07 | Mesa | Open GPU implementation and software rendering | QUEUED | Shader/driver conformance, CPU fallback benchmark |
| O08 | OpenXR and Khronos runtime samples | Cross-device pose, camera, latency | SOURCED | Runtime headset/device smoke test |
| O09 | Vulkan samples | GPU queues, memory/synchronization, frame pacing | SELECTED_DOCS_AUDITED | Shader benchmark and validation-layer tests |
| O10 | Bullet | Rigid collision / simulation | SELECTED_DOCS_AUDITED | Collision determinism and source license exceptions |
| O11 | Jolt | Multi-core physics, moving actor contacts | SELECTED_DOCS_AUDITED | Character-contact/fixed-timestep acceptance |
| O12 | Box2D + ODE | 2D/gameplay simulation and articulated constraints | QUEUED | Source and exact license/version audits |
| O13 | OpenUSD | Composition, scene layers, assets and time samples | SELECTED_DOCS_AUDITED | Native scene-composition contract then true USD export/import |
| O14 | OpenStreetMap | Geospatial-world data origins and attribution | QUEUED | Dataset terms, attribution and offline ingestion |
| O15 | Cesium and 3D Tiles | Gigantic-world spatial tiling and streaming | SELECTED_DOCS_AUDITED | Real tile I/O, memory/fps budget, attribution |
| O16 | Blender Geometry Nodes | Procedural editable scene authoring | EXISTING SOURCE AUDIT R06 | Geometry Nodes native recipe with genuine Blender receipt |
| O17 | Gaussian Splatting | Novel-view image-to-space representation | SELECTED LICENSE RISK AUDITED | Study-only until code/model/data licenses cleared |
| O18 | Instant-NGP | Hash-encoded NeRF acceleration | SELECTED LICENSE RISK AUDITED | **Noncommercial** code; no commercial MGR vendoring |
| O19 | Nerfstudio | Multi-view capture/training/evaluation workflows | SELECTED_DOCS_AUDITED | Camera-calibrated dataset and GPU/cost benchmark |
| O20 | Neural/robotic world systems and Isaac Sim papers | Physics-grounded spatial sensors and AI world fidelity | QUEUED | Separate paper-level and simulator-license review |
| O21 | OpenGL / OpenUSD / OpenXR official specifications | Interchange, graphics and XR conformance | EXISTING SOURCE AUDITS R07/R13/O08 | Cross-runtime fidelity receipts |
| O22 | Motion capture and spatial photogrammetry | Skeletal motion, reconstruction and scan uncertainty | EXISTING 20-DOMAIN CHAPTERS | Captured footage and actual rig target tests |
| O23 | SIGGRAPH, GDC, Pixar, Disney, NVIDIA | Deep paper and talk library indexing | EXISTING R01–R04/R23 AUDITS | Full-authorized corpus indexing, reproducible benchmarks |
| O24 | Public research patents/technical blogs | Prior art, failure modes, algorithm design | EXISTING R22 AUDIT | Patent risk assessment by appropriate counsel |

## MGR-native synthesis from this tranche

**MGR Layered Reality Composition** (`forge/scene_layers.py`) is a tiny deterministic, purely owned authoring contract. Artists, world builders and the future director may stack a baseline world, a lighting pass and a character revision by stable scene paths. The stronger authored layer wins only on the fields it changes, with per-field origin receipts and a stable SHA-256. Deletion and reintroduction are explicit; bad input, nonfinite matrices and overlarge scenes are rejected. This is **not OpenUSD parity**; it is an immediate independently testable Forge primitive informed by open scene-composition concepts. Tests: `tests/test_scene_layers.py`.

Next implementation slots: F82 native scene composition; F83 import/export parity matrix; F84 real world-cell I/O+budget; F85 physics contact/animation binding; F86 rendering parity/performance lab. Each needs real engines/devices for production verification, not just CPU unit checks.

## Collection policy for the owner's suggested giant research vault

Index legally accessible titles, authors, URLs, release dates, abstracts, code entry points, version/hash, inspection depth, license and exact MGR use. Do **not** mirror all proprietary papers, talks, code, models or datasets. Public viewing does not imply permission to redistribute, retrain or commercialize. Record every inaccessible full paper/talk as `ACCESS_GATED`, and use author/open conference version if permitted. Research tracks must link learned algorithm → independent native spec → executable test → quality/latency benchmark; otherwise they remain study material.
