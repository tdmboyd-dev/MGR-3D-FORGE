# MGR Reality-to-Space Intelligence — Native Master Research Map

Date: 2026-10-25. Owner: MGR. **Status: all TWENTY 16-field technical research packets and TWENTY isolated source ledgers written, plus native CPU proofs; NOT complete implementation, full upstream source-code audit, or scientific mastery.** This map governs research alongside implementation. External sources stay in the provenance ledger.

## Central design finding

The word *3D* refers to different things in different systems. A camera measures projected light; a brain infers depth from clues; a GPU projects author-specified geometry into pixels; a printer receives geometry and converts it to physical layer paths; a scanner measures surfaces; a generative model proposes missing geometry using learned prior knowledge. **None of these conversions supplies all missing scene truth by itself.** MGR must track which dimension came from measurement, a physical constraint, a template, a model hypothesis, or the owner's creative approval.

In a pinhole camera, image x = fx * X/Z + cx, image y = fy * Y/Z + cy. The 3D points (X,Y,Z) and (kX,kY,kZ), for positive k, land on the same pixel. So **one pixel cannot determine depth uniquely**. Stereo, motion, LiDAR, known shape, shading, learned priors or user instructions add constraints—not a universal certainty guarantee. MGR `forge/spatial_truth.py` now proves the ambiguity with tests and exposes a camera ray instead of inventing distance.

A 3D printer's slicer intersects an *existing* watertight/repairable mesh with layer planes, converts the resulting 2D contours to toolpaths, infill and machine motions, then produces hardware-specific G-code. This is not an image-to-3D miracle, but the slicing and mesh-repair mathematics can strengthen MGR sectioning, garment fit, cross-section checking and world collision. Our first bounded triangle/plane section prototype produces contour **segments**, not closed printable layers or instructions for hardware.

Console game worlds are a **runtime systems** challenge: content streaming, occlusion, visibility-dependent geometry/detail, shaders, texture and memory residency, CPU/GPU timing, input-to-photon latency, physics and network state. Not all features of a high-end rendering path can run on CPU alone; the asset creation and validation phases can often use CPU.

## All 20 interdisciplinary tracks — research → native outcome

| ID | Domain | What matters underneath | Native MGR translation / proof needed | Evidence maturity |
|---|---|---|---|---|
| S01 | Human vision | Stereo disparity, monocular perspective, occlusion, motion parallax, convergence, retinal/cortical limits | MGR Perception Judge: multi-cue depth/conflict detector; compare viewpoint motion, not one still | 16-field packet; stereo proof; perceptual study open |
| S02 | Optics and light | Reflection, refraction, lens focus, diffraction, BRDF/light transport | MGR Light Witness: calibrated source-object-camera observations and glare/volume separation | 16-field packet; Blender render proof; calibrated EXR measurements open |
| S03 | Geometry | Coordinates, surfaces, topology, intersections, volume representation | MGR Spatial Truth: ray, plane, shell, manifold and cross-section operators | 16-field packet; edge topology proof; self-intersections open |
| S04 | Linear algebra | Matrices, camera calibration, transforms, quaternion stability | MGR Transform Guardian: right/left-handed, scale and inverse-transform invariants | 16-field packet; parallel **and oriented** calibrated stereo proofs; distortion and uncertainty open |
| S05 | Calculus | Continuous motion and differential physics | MGR Continuous Motion: bounded velocity, acceleration, derivatives and smooth interpolation | 16-field packet; sampled speed/acceleration guard; continuous solver open |
| S06 | Physics | Rigid constraints, collision, cloth, smoke and fluids | MGR Simulation Reality Gate: solver vs fake effect, cache, conservation/energy checks | 16-field packet; prototype volumes; actual dynamics solver open |
| S07 | Computer graphics | Visibility, rasterization, PBR, ray tracing, shading and time budgets | MGR Renderer Independence: CPU reference image, Blender render, future GPU parity | 16-field packet; reference-vs-preview comparison open |
| S08 | Game architecture | World cells, streaming, visibility, virtualized geometry, networking | MGR World Residency: measurable chunks, occlusion sets and runtime budgets | 16-field packet; CPU camera-distance residency **plan** tested; live engine open |
| S09 | Modeling | Shape semantics, edge flow, UVs, rig-friendly topology | MGR Geometry Anatomy: silhouette + deformation + print-slice/section checks | 16-field packet; generic mannequin; real sculpt/retopo open |
| S10 | Animation | Kinematics, pose graph, capture, retarget, physically plausible motion | MGR Motion Director: skeleton + constraints + render evaluation | 16-field packet; verified prototype poses; live retarget open |
| S11 | Procedural generation | Noise, grammars, growth, constrained randomness, field operations | MGR Field Composer: world, cloud, biology and branching rules | 16-field packet; CPU world/noise prototypes; seed-seam stress open |
| S12 | Computer vision | Calibration, feature tracks, optical flow, SLAM, ambiguity | MGR Observation Solver: observed rays/depth with confidence and missing geometry flags | 16-field packet; projection/stereo proofs; real SLAM/reconstruction open |
| S13 | Photogrammetry | Multi-view correspondences, SfM/MVS, mesh/texture synthesis | MGR Reality Reconstruction: capture plan, camera solve and confidence mask | 16-field packet; real multiview SfM/MVS acceptance open |
| S14 | LiDAR & scanners | Time-of-flight, structured light, calibration, point clouds | MGR Measured Geometry: import registered scans with uncertainty and units | 16-field packet; sensor data/ICP fusion acceptance open |
| S15 | GPU/console hardware | Shader stages, depth buffer, cache, bandwidth, frame budgets | MGR Runtime Admission: hardware-aware compute and detail gate | 16-field packet; CPU admission prototype; GPU render runtime open |
| S16 | AI & neural 3D | 3D priors, implicit fields, splats, generative meshes and data rights | MGR Model Dock: swappable licensed inference, cost and geometry verification | 16-field packet; commercial model rights and heavy GPU runtime open |
| S17 | VR presence | Six-degree pose, stereo rendering, frame timing, locomotion sickness | MGR Presence Judge: near-field scale, stereo/parallax and latency tests | 16-field packet; actual headset/comfort acceptance open |
| S18 | AR & mixed reality | Visual-inertial odometry, anchors, physical-world mesh alignment | MGR World Anchors: tracked local-to-world transforms and drift QA | 16-field packet; real tracked-device drift/occlusion acceptance open |
| S19 | Biology & nature | Morphogenesis, anatomy, growth constraints and ecosystems | MGR Living Geometry: anatomical and environmental generative constraints | 16-field packet; actual biome/anatomy solver acceptance open |
| S20 | Fundamental physics | Relativity/quantum questions vs practical metric spatial representations | MGR Scientific Boundary: speculative ideas stay research; ship only measurable applicable transforms | 16-field packet; optional 4D projection/portal demos open, no quantum simulation claim |

## Four cross-domain bridges that previous research underweighted

| ID | Bridge | Why it is high leverage | First build | Next acceptance |
|---|---|---|---|---|
| B01 | Printer/slicer/CAD → game and character geometry | 3D shape quality is not only a screenshot: section integrity, thickness and watertightness matter | Triangle/plane cross-sections and bounded edge-incidence tests in `forge/spatial_truth.py`, `forge/surface_truth.py` | Closed contours, oriented manifold proof, self-intersection and independent slicer verification before print-ready claims |
| B02 | Human visual inference → image-to-3D truth | Pixels underdetermine depth; the model must label unseen areas as hypotheses | Pixel ray plus parallel calibrated two-view triangulation with depth and reprojection guards | General rotated/intrinsic cameras, robust correspondence search, uncertainty propagation and multiview reconstruction |
| B03 | Console runtime → MGR persistent world | Gigantic scenes need visibility/streaming and fixed budgets, not blindly higher mesh counts | Existing MGR chunk/LOD paths as starting point | Measure camera-driven residency, draw counts, collisions and memory at 60 FPS in an actual target runtime |
| B04 | Scientific field representations → fantasy creation | One field can drive volume density, terrain, growth, particles, and material masks | Noise-modulated volume plus CPU procedural geometry | Portable typed field graph, physically informed sampling and visual/failure receipts |

## Research-to-build gate for these tracks

**Parallel packet ledger:** S01 [`chapters/S01-HUMAN-VISION.md`](chapters/S01-HUMAN-VISION.md), S02 [`chapters/S02-OPTICS-LIGHT.md`](chapters/S02-OPTICS-LIGHT.md), S03 [`chapters/S03-GEOMETRY-SLICING.md`](chapters/S03-GEOMETRY-SLICING.md), S04 [`chapters/S04-TRANSFORM-MATH.md`](chapters/S04-TRANSFORM-MATH.md), S05 [`chapters/S05-CONTINUOUS-MOTION-MATH.md`](chapters/S05-CONTINUOUS-MOTION-MATH.md), S06 [`chapters/S06-PHYSICS-SIMULATION.md`](chapters/S06-PHYSICS-SIMULATION.md), S07 [`chapters/S07-COMPUTER-GRAPHICS.md`](chapters/S07-COMPUTER-GRAPHICS.md), S08 [`chapters/S08-GAME-RUNTIME.md`](chapters/S08-GAME-RUNTIME.md), S09 [`chapters/S09-MODELING-SCULPT.md`](chapters/S09-MODELING-SCULPT.md), S10 [`chapters/S10-ANIMATION-RIGGING.md`](chapters/S10-ANIMATION-RIGGING.md). Each has a corresponding S01–S10 source ledger under `research/external-provenance/`. These are actionable sourced packets, **not** claims that every linked upstream repository, research method or scientific field has been fully reverse engineered.

**Third parallel packet ledger:** S11 [`chapters/S11-PROCEDURAL-GENERATION.md`](chapters/S11-PROCEDURAL-GENERATION.md), S12 [`chapters/S12-COMPUTER-VISION.md`](chapters/S12-COMPUTER-VISION.md), S13 [`chapters/S13-PHOTOGRAMMETRY.md`](chapters/S13-PHOTOGRAMMETRY.md), S14 [`chapters/S14-SCANNING-LIDAR.md`](chapters/S14-SCANNING-LIDAR.md), S15 [`chapters/S15-GPU-HARDWARE.md`](chapters/S15-GPU-HARDWARE.md). Each has its corresponding S11–S15 source ledger. These distinguish authoring/estimated representations from sensor-measured truth and specify real performance/license gates.

**Fourth parallel packet ledger:** S16 [`chapters/S16-AI-NEURAL-3D.md`](chapters/S16-AI-NEURAL-3D.md), S17 [`chapters/S17-VR-PRESENCE.md`](chapters/S17-VR-PRESENCE.md), S18 [`chapters/S18-AR-ANCHORS.md`](chapters/S18-AR-ANCHORS.md), S19 [`chapters/S19-LIVING-GEOMETRY.md`](chapters/S19-LIVING-GEOMETRY.md), S20 [`chapters/S20-REALITY-BOUNDARY.md`](chapters/S20-REALITY-BOUNDARY.md). Each has its corresponding S16–S20 source ledger. These explain the boundaries of neural weights, licensed datasets, real XR hardware, organic growth models and speculative physics rather than selling them as finished capabilities.

**Production-research overlay:** [`MGR-STUDIO-TO-NATIVE-ENGINE-LESSONS.md`](MGR-STUDIO-TO-NATIVE-ENGINE-LESSONS.md) now explicitly translates the useful production lessons from primary studio papers, SIGGRAPH real-time courses, technical engine documentation and conference sessions into ten **MGR-native** quality systems and their fail/pass experiments. The actual external technical citations, rights and inspection limits remain isolated in `external-provenance/STUDIO-ENGINE-PRIMARY-SOURCES-2026-10-25.md`. Reading a source catalog is **not** claiming we inspected every engine source file or reproduced a feature-film pipeline.

**All four five-at-once technical packet batches are documented. Next priority:** cross-domain implementation, deep pinned source-code audits only for selected real dependencies, real-world camera/scan calibration, game runtime and visual-quality benchmarking. Research and negative tests continue alongside builds; no research-only completion label substitutes for a working proof.

Each track must recursively collect (1) definition, (2) production usage, (3) standards, (4) current research, (5) code architecture, (6) applicable models, (7) datasets, (8) code/model/data rights, (9) APIs, (10) native alternative, (11) CPU/GPU/runtime, (12) cost, (13) failure modes, (14) evaluation, (15) MGR integration owner, (16) acceptance tests. **SOURCED** means a useful official reference exists; it does not mean those 16 fields are complete. Track source-tree/read depth and experiment outcomes separately.

## No-fake-certainty acceptance rules

1. A photo is measured 2D appearance, not automatically ground-truth unseen 3D shape.
2. A cross-section only explains geometry already present; it is not a complete 3D-print file or G-code toolpath.
3. A view-dependent splat or radiance field may look photorealistic but not give a collision-ready mesh.
4. A GPU renderer may hide geometric errors; section tests, different views, anatomy and physics checks must complement images.
5. A scientific field equation has no production advantage until an actual quality/performance comparison demonstrates it.
6. Game-engine features like virtualized geometry imply target runtime/hardware requirements; a source-code idea does not prove portable console support.

## Immediate work order

1. Complete camera ray and plane/triangle section primitive **(first coded proof)**.
2. Parallel-camera triangulation and reprojection **now coded**; extend to rotated cameras, robust correspondences, uncertainty, incomplete geometry and outlier rejection.
3. Edge-incidence checks **now coded**, not watertightness certification; add mesh section closure, self-intersections, physical volume validation and optional STL/3MF export after rights/unit QA.
4. Camera-driven geometry residency/LOD and actual browser or game-runtime walkthrough.
5. Reuse field graphs for volume, particles, terrain and procedural anatomy, with repeatable visual comparisons.
6. Return to full rig, modular clothing and approved Tevin likeness; research should help assets reach owner acceptance, not become a permanent research detour.
