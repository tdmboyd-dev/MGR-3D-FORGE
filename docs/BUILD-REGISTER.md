# Native Capability and Build Register

Baseline 2026-10-25. Status sequence: DISCOVERED > QUEUED > SOURCED > READ > RESEARCHED > SPECIFIED > IMPLEMENTED > RUNNING > TESTED > VERIFIED > INTEGRATED > OWNER-ACCEPTED. Do not skip. Research state and actual product state are independent.

| ID | MGR-owned capability | Research state | Code state | Priority | Dependencies | Next evidence |
|---|---|---|---|---|---|---|
| F01 | Intent -> typed project & brief | SPECIFIED | PROTOTYPE TESTED | P0 | input schema | Limited count-only offline parser, not general intent |
| F02 | Scene/asset dependency graph | SPECIFIED | PARTIAL: tested DAG | P0 | F01 | Stable topo-sort/cycle checks; full scene graph pending |
| F03 | CPU procedural terrain/roads | SOURCED | PARTIAL: roads, TESTED | P0 | F02, Blender | Terrain, curves and engine import absent |
| F04 | Parametric buildings/rooms | SOURCED | PARTIAL: massing + two-room hypothesis TESTED | P0 | F03 | 1,000-lot test + interior GLB; real architecture/edits pending |
| F05 | Asset store and provenance | SPECIFIED | PROTOTYPE TESTED | P0 | asset schema | Hash/dedupe/tamper tests pass; durable transactional backend pending |
| F06 | GLB import/export + QA | SPECIFIED | PARTIAL: five Blender imports VERIFIED | P0 | Blender version | Windows 5.2.2 world/interiors/parks/T/A imported; edit/re-export/visual pending |
| F07 | Local model adapter contract | SPECIFIED | PARTIAL: local+unavailable adapter selection TESTED | P0 | F02, license gates | CPU adapter runs; remote approval simulated, real models absent |
| F08 | CPU TripoSR prototype | SOURCED | NOT STARTED | P0 | runtime resources | Timed 3 asset benchmark |
| F09 | Character DNA measurements | SPECIFIED | PROTOTYPE TESTED | P0 | approved Tevin base | Synthetic proportion comparison only; Tevin not captured |
| F10 | Anatomy guardian | SPECIFIED | PROTOTYPE TESTED | P0 | F09 | Missing hand and symmetry checks; visual mesh checking pending |
| F11 | Garment/part separation | SOURCED | PARTIAL: 20 independently exported mannequin parts Windows Blender VERIFIED | P1 | F09, permitted segmentation | Left/right trousers, two elbow sleeves and 16 prior parts; real Tevin segmentation absent |
| F12 | Automated rig/weights | SOURCED | PARTIAL: 20 skinned parts, 48 dual-weight sleeve vertices Windows VERIFIED | P1 | clean mesh, rig type | Actual Blender .blend proof; full-body smooth skin still pending |
| F13 | Material/UV quality | RESEARCHED | PARTIAL: glTF PBR imported as 5 Principled materials Windows VERIFIED | P1 | F06 | Real Blender roughness/metallic socket check passed; textures/UV remain |
| F14 | Geometry repair/retopo | SOURCED | PARTIAL: triangle repair TESTED | P1 | F06 | Malformed triangle cleanup passed; retopo/manifold repair pending |
| F15 | Region/world graph | SPECIFIED | PARTIAL: road intersections TESTED | P0 | F02 | Region hierarchy and landmarks pending |
| F16 | World assembly | SPECIFIED | PARTIAL: static scene TESTED | P0 | F03-F05,F15 | Scene export works; graph and navigation pending |
| F17 | Scene navigation/collision | QUEUED | PARTIAL: grid pathfinding + box collision TESTED | P1 | F16, target engine | Navmesh and moving-agent engine traversal pending |
| F18 | LOD/instancing/streaming | QUEUED | PARTIAL: LOD1 + chunk manifest TESTED | P1 | F16 | LOD1 GLB and chunk coverage; runtime streaming/fps pending |
| F19 | Image/video scene reconstruction | SOURCED | NOT STARTED | P2 | licensed weights, GPU | Camera/depth benchmark |
| F20 | Persistent character/world memory | SPECIFIED | NOT STARTED | P1 | F05,F09,F15 | Cross-run continuity |
| F21 | Compute/resource cost router | SPECIFIED | PARTIAL: budget + conservative local model admission TESTED | P1 | benchmark data | Owner PC hardware inventoried; per-model inference benchmarks/cloud pricing pending |
| F22 | Human approvals | SPECIFIED | PARTIAL: authorization TESTED | P0 | existing gateway integration | Fail-closed remote/spend test passes; identity and UI pending |
| F23 | Workflow resumes/retries | SPECIFIED | PARTIAL: local checkpoints TESTED | P1 | job store | Restart test passes; retries/concurrency pending |
| F24 | User-facing creation studio | DISCOVERED | PARTIAL: static SVG preview | P2 | stable engine | Actual editor, live preview and rehearsal UI absent |
| F25 | Creation OS integration | BLOCKED: repo audit | NOT STARTED | P1 | canonical ownership | Integration contract |
| F26 | Create Loco integration | BLOCKED: repo audit | NOT STARTED | P2 | consumer needs | Screenshot-to-scene |
| F27 | Tevin/MGR-ONE integration | BLOCKED: repo audit | NOT STARTED | P1 | canonical base | Owner-approved character |
| F28 | Cross-engine export pack | SPECIFIED | PARTIAL: GLB Blender import VERIFIED | P1 | targets known | GLB Blender 5.2.2 PASS; OBJ and other engines unverified |
| F29 | License/provenance gate | SOURCED | PARTIAL: license ID gate TESTED | P0 | model legal review | Unknown-license approval enforced; legal clearance still open |
| F30 | Benchmark/quality ledger | SPECIFIED | PARTIAL: measured CPU + integrity ledger TESTED | P0 | metric spec | 10/100/1000 benchmark and all-file SHA; GPU/Blender comparisons pending |
| F31 | MGR World Flight | SPECIFIED | PARTIAL: 3-shot camera reel and clearance-corrected Blender rendering VERIFIED | P1 | F16,F17 | Frames 1/49/97 real keyframes, edited camera visibly reveals surroundings; runtime camera player pending |
| F32 | MGR Model Dock | SPECIFIED | PARTIAL: recipe inspection TESTED | P1 | F07,F22,F29 | MGR model manifest; sandboxed installs and model launch pending |
| F33 | MGR Spatial Eyes | SPECIFIED | PARTIAL: geometry visibility TESTED | P1 | F16,F17,F20 | MGR-authored world occlusion and evidence labels; HUD and reconstruction pending |
| F34 | MGR Scene Consciousness | SPECIFIED | PARTIAL: generated-world facts/qualified routes TESTED | P0 | F02,F05,F16,F33 | `forge/consciousness.py` emitted in world bundles; Blender object inspection pending machine test; semantic door portals absent |
| F35 | MGR Visual Judge | SPECIFIED | PARTIAL: pixel/translation/quarter-turn/alpha-aware silhouettes TESTED | P0 | F06,F30,F34 | Real transparent Blender pose images foreground QA; arbitrary 3D pose identity and semantic evaluator pending |
| F36 | MGR Code Architect | SPECIFIED | PARTIAL: typed workspace file edits and rollback TESTED | P0 | F22,F23,F29 | `forge/code_architect.py`; isolated arbitrary-code executor, policy enforcement, consent UI pending |
| F37 | MGR Anatomy Guardian Plus | SPECIFIED | PARTIAL: 2-frame bone/joint and dual-weight QA Windows VERIFIED | P0 | F09,F10,F35 | New 20 parts, 11 bones, 0m joint gaps, 0.427m hand travel; skin seam and anatomy realism pending |
| F38 | MGR Fabric Intelligence | SPECIFIED | PARTIAL: 8 detachable garment pieces and metadata TESTED | P1 | F11,F12,F13 | `forge/wardrobe.py` catches missing/misbonded clothing; real tailored fit, cloth physics and intersections open |
| F39 | MGR Rig Intelligence | SPECIFIED | PARTIAL: 20-part modular rig and 48 blended elbow-weight vertices Windows VERIFIED | P0 | F09,F12,F37 | 11-bone rig pose QA passed on actual 20-part project; full-body smooth skin pending |
| F40 | MGR World Logic | SPECIFIED | PARTIAL: collision-checked road-centerline rehearsal TESTED | P1 | F15,F17,F34 | `forge/traversal.py`; actual navmesh/doors/stairs/dynamic agent game runtime pending |
| F41 | MGR Cinematic Director | SPECIFIED | PARTIAL: 3-shot Windows CPU Cycles and 3-camera/3-cut Blender VERIFIED, dolly CODED | P1 | F13,F31,F35 | Multi-camera scenes saved; moving-path render/audit pending; cinematic quality far from finished |
| F42 | MGR Creation Memory | SPECIFIED | PARTIAL: integrity-chained JSON revisions and locks TESTED | P0 | F05,F20,F34 | `forge/creation_memory.py`; concurrent DB, actual owner identity and cross-app replay pending |
| F43 | MGR Self-Repair Studio | SPECIFIED | PARTIAL: bounded file repair + build→Blender→render receipt pipeline TESTED (CPU stage) | P1 | F23,F30,F35,F36 | `forge/repair.py`, `forge/pipeline.py`; full Blender integrated run and semantic repair pending |
| F44 | MGR Narrative Director | SOURCED | QUEUED | P1 | F01,F34,F41 | Beats, subject intent, continuity, human approval and directed scene assembly |
| F45 | MGR Camera Intelligence | SOURCED | PARTIAL: camera AABB clearance and 5-sample moving-path checks TESTED | P0 | F31,F35,F41 | Subject framing score, full swept collision, lenses, focus and tracking |
| F46 | MGR Motion Director | SOURCED | PARTIAL: measured 7.21726m dolly + 3-cut Blender 5.2.2 VERIFIED; `forge/motion_truth.py` bounded sampled speed and acceleration negative tests | P0 | F12,F31,F39 | Reopened .blend measured shot 2 movement, shots 1/3 stayed 0.0m; bone retarget, foot plants, between-sample behavior and general library open |
| F47 | MGR Lighting Director | SOURCED | PARTIAL: 3 mood recipes + Windows CPU Cycles key/ambient TESTED | P1 | F13,F41 | Key/fill/rim, continuity, cinematographer controls, physical light calibration |
| F48 | MGR Scene Continuity Director | SOURCED | PARTIAL: identity and revision primitives only | P0 | F35,F42,F44 | Shot-level costume, props, screen direction and position continuity tests |
| F49 | MGR Cinematic Judge | SOURCED | PARTIAL: 4-frame Blender timeline render + moving-shot pixel difference Windows VERIFIED | P0 | F35,F41,F45 | Four 320x180 PNGs, middle-shot RGB MAE 5.98669; semantic framing, DOF, clipping, intershot composition open |
| F50 | MGR Editorial Director | SOURCED | QUEUED | P1 | F41,F44,F46 | Native edit decision list, timeline, clips, audio sync and final media assembly |
| F51 | MGR Light Sculptor | SOURCED | PARTIAL: 2 actual point lights and illuminated witness verified in Windows Blender 5.2.2 | P0 | F13,F41,F47 | Production light rigs, interactive worlds, physically measured setups open |
| F52 | MGR Shadow Intelligence | SOURCED | QUEUED | P1 | F51,F16 | Contact, soft, volumetric and dynamic-world shadow quality |
| F53 | MGR Atmosphere Field | SOURCED | PARTIAL: bounded 0..0.25 density, Cycles Principled Volume + uniform/noise-cloud field, Windows renders verified | P1 | F51,F56 | Soft boundary falloff, animated smoke, authored OpenVDB and runtime scattering open |
| F54 | MGR Particle Architect | SOURCED | PARTIAL: seeded budgeted CPU particle geometry TESTED | P0 | F03,F13 | `forge/fx.py` stable particles; emitters, forces, GPU/runtime/LOD still open |
| F55 | MGR Elemental Simulator | SOURCED | QUEUED | P1 | F53,F54 | Smoke, fire, water, wind, fluids and deterministic simulation caches |
| F56 | MGR Portal Intelligence | SOURCED | PARTIAL: 3D ring + emissive GLB, two-phase Windows Cycles renders and light/volume scene proof | P0 | F54,F59 | Traversal, interior dimension and parallax open |
| F57 | MGR Energy Weave | SOURCED | PARTIAL: animated phase arc/aura geometry TESTED | P0 | F54,F59 | Beams, shields, electric forces, character spell choreography and glow QA |
| F58 | MGR Illusion Architect | SOURCED | QUEUED | P1 | F33,F35,F56 | Depth/parallax, refraction, impossible-space portals and cross-view validity |
| F59 | MGR Shader Alchemist | SOURCED | PARTIAL: glTF emission and PBR tested; Windows Blender Emission sockets + procedural Noise→Density volume graph verified | P0 | F13,F56 | Rich authored layered materials, texture baking and MaterialX support |
| F60 | MGR Metamorphosis Director | SOURCED | QUEUED | P1 | F39,F42,F57 | Safe shape/material transformation with face/identity locks |
| F61 | MGR Compositor | SOURCED | PARTIAL: Blender 5.2 node-group Fog Glow real Cycles render verified | P1 | F35,F41,F57 | Layer passes, distortion, HDR/OCIO grade and cinematic optical QA open |
| F62 | MGR Color Master | SOURCED | QUEUED | P1 | F13,F41,F61 | ACES/OCIO scene-referred grade, display transforms and tone mapping |
| F63 | MGR Motion Graphics | SOURCED | QUEUED | P1 | F41,F50,F61 | Kinetic typography, 3D HUD, animation timing and web export |
| F64 | MGR Sound-Reactive FX | SOURCED | QUEUED | P2 | F46,F54,F63 | Beat/envelope/event-driven light, particles and scene animation |
| F65 | MGR Destruction Director | SOURCED | QUEUED | P1 | F55,F16 | Fracture, collision/physics, debris, cache and restoration |
| F66 | MGR Spell Continuity Brain | SOURCED | QUEUED | P0 | F42,F48,F56 | Stable spell/world states, owner approvals and cross-shot replay |
| F67 | MGR FX Judge | SOURCED | PARTIAL: `forge/fx_judge.py` rejects unmatched cameras, fake volume and static pixels; Windows real 22.37957 RGB MAE PASS | P0 | F35,F49,F54 | Perceptual semantics, volume artifacts and cross-view cinematic scoring open |
| F68 | MGR Spatial Truth | SOURCED | PARTIAL: CPU pinhole/ray ambiguity plus calibrated **parallel** stereo triangulation and reprojection/cheirality negative tests | P0 | F30,F35 | Rotated-camera extrinsics, correspondence, confidence intervals, uncertainty-labeled reconstruction |
| F69 | MGR Geometric Cross-Section | SOURCED | PARTIAL: bounded Y-plane/triangle sections plus `forge/surface_truth.py` edge-incidence/degeneracy audit and negative tests | P1 | F03,F16,F68 | Oriented watertightness, closed loops, self-intersections, repair, 3MF/STL and independent slicer verification |
| F70 | MGR Perception Inference Guardian | SOURCED | RESEARCHED CONCEPT / QUEUED | P0 | F35,F68 | Distinguish observed pixels, inferred depth, generated hidden surfaces and owner approval on every asset |
| F71 | MGR World Residency Intelligence | SOURCED | PARTIAL: deterministic CPU `forge/streaming.py` camera-distance active/prefetch/evict **plan**, bounded tests | P1 | F24,F40,F68 | Actual streamed asset I/O, visibility/occlusion and collision continuity, console/game-engine live FPS/VRAM evidence |
| F72 | MGR Material Reality Witness | AUDIT IN PROGRESS | PARTIAL: bounded PBR authoring checks in `forge/studio_quality.py`, TESTED | P0 | F13,F47,F59 | Measured scene-linear BRDF, UV, energy and varied camera render parity |
| F73 | MGR Adaptive Light Orchestra | AUDIT IN PROGRESS | PARTIAL: deterministic camera-distance light-budget ranking, TESTED | P1 | F47,F51 | Actual many-light path, shadows, physical luminance, frame-time/variance benchmarks |
| F74 | MGR Flesh & Translucence Lab | AUDIT IN PROGRESS | PARTIAL: Beer–Lambert attenuation reference, TESTED | P1 | F13,F59 | Skin/wax/material spectral/multiple-scatter reference and real Cycles parity |
| F75 | MGR Surface Anatomy Guardian | AUDIT IN PROGRESS | PARTIAL: mesh edge/incidence interface, TESTED | P0 | F14,F37,F69 | Deforming sculpt, UV/subdivision, true anatomy and self-intersection evidence |
| F76 | MGR Living Hair Director | AUDIT IN PROGRESS | PARTIAL: stable strand-root/stretch track guard, TESTED | P0 | F39,F46,F55 | Blender actual hair curves/physics, contact, hair shading and independent cloth QA |
| F77 | MGR Layered World DNA | AUDIT IN PROGRESS | PARTIAL: immutable overlay composition + scene SHA, TESTED | P0 | F42,F48 | OpenUSD-style layering, concurrency/permissions, actual character clothing/shot relink |
| F78 | MGR Horizon Truth Streaming | AUDIT IN PROGRESS | PARTIAL: CPU residency budget plan, TESTED | P1 | F18,F71 | Real live cell loads, collision continuity, memory and measured frame p99 |
| F79 | MGR Visual Surface Reconciler | AUDIT IN PROGRESS | PARTIAL: corresponded projected landmark pixel drift guard, TESTED | P0 | F35,F69 | Multi-camera silhouette mesh LOD/render comparisons and animated edge seam QA |
| F80 | MGR Cross-View Reality Judge | AUDIT IN PROGRESS | PARTIAL: calibrated pose+anatomy landmark reprojection with missing-hand gates, TESTED | P0 | F09,F35,F68 | Semantic identity, visibility/occlusion and actual multi-angle Tevin reference acceptance |
| F81 | MGR Atmosphere Memory | AUDIT IN PROGRESS | PARTIAL: bounded indexed volume temporal consistency guard, TESTED | P1 | F53,F61,F67 | Physically rendered volumetric temporal shots, flow/smoke sim and measured runtime proof |

| F82 | MGR Layered Reality Composition | SELECTED OPEN-SYSTEMS RESEARCH | PARTIAL: deterministic field overrides, provenance and hashing; 5 CPU tests PASS | P1 | F18,F78 | Real USD authoring, scene references, time samples and engine roundtrip |
| F83 | MGR Runtime Parity Lab | SELECTED RESEARCH | PARTIAL: actual GLB/OBJ independent geometry count and bound cross-check; TESTED | P1 | F82,F79 | Independently import/render in two engines, animation and material fidelity, measured FPS |
| F84 | MGR Cell Transport | SELECTED RESEARCH | PARTIAL: actual disk GLB cell reads, SHA-256, bounded active/prefetch RAM cache; TESTED | P1 | F78,F82 | Live game/GPU residency, asynchronous transfers, collision continuity, recovery and FPS |
| F85 | MGR Dynamics Binding | SELECTED RESEARCH | PARTIAL: conservative swept actor segment vs obstacle contact; TESTED | P1 | F39,F40 | Physics-engine capsule, stairs/slopes, rig contact, impulses and deterministic replay |
| F86 | MGR Render Truth Lab | RESEARCH QUEUED | NOT BUILT | P1 | F72,F73,F74 | Real engine lighting/material parity and performance |
| F87 | MGR World Flight Runtime | SELECTED WEBGL/GLB SPEC RESEARCH | IMPLEMENTED and Windows BROWSER RENDER VERIFIED: self-contained WebGL2 city, actual GLB meshes, screenshot receipt; input/FPS still UNVERIFIED | P0 | F04,F18,F40,F83 | Keyboard/collision/fps telemetry acceptance, independent second backend, full asset/animation/rendering |
| F88 | MGR Live World Editor + Export Roundtrip | MGR AUTHORED EDITING CONTRACT | IMPLEMENTED AND WINDOWS BROWSER VERIFIED: position, height, material editing with browser persistence, actual downloaded/imported JSON, CPU GLB/OBJ/MTL/SVG re-export and standalone WebGL editor | P0 | F87,F04,F83 | Third-party GLB import, full scene graph, non-box modeling |
| F89 | MGR Spatial Selection + Recoverable Edit History | MGR WORLD-EDIT TRANSACTION CONTRACT | IMPLEMENTED AND WINDOWS BROWSER VERIFIED: real canvas clicks, ray-selected nearest bounding box, Ctrl+Z/Y plus buttons, bounded 80-history checkpoint, restored states and WASD camera movement | P0 | F88,F68 | Precise triangle picking, multi-select, gizmos, quantitative browser performance |

**Scope:** 89 MGR-native areas: original 33, F34–F43, director/camera/motion F44–F50, fantasy/VFX F51–F67, reality-to-space F68–F71, ten studio-quality CPU contracts F72–F81, open-systems F82–F86, offline interactive World Flight F87, bounded live editor/export roundtrip F88, and spatial selection/history F89. Queued is **not** implemented. Detailed MGR-native research remains in `research/` and external attribution/rights under `research/external-provenance/`.

## Definition of production completeness

All critical capabilities must have checked-in code, reproducible runtime evidence, QA receipts, round-trip assets and actual consumer acceptance. A working README or API stub alone is not done. Keep partial status honest.

## Immediate build order

1. Use the verified Windows Blender 5.2.2 installation; obtain full hardware inventory and approved Tevin base privately.
2. Build F01/F02/F05/F06/F22/F29/F30 contracts and tests.
3. Build F03/F04/F15/F16 CPU world slice; verify no GPU.
4. Build F07/F08 baseline local generation with budget/quality receipts.
5. Build F09/F10 character validation; then F11/F12 production tests.
6. Build F34/F35 scene queries and visual QA on reproducible, small Blender renders, then F36 scoped coding jobs.
7. Build F39 deforming rig, F38 separable clothing and F37 full-pose anatomical checks on generic models before Tevin.
8. Build F40 world navigation, F41 cinematic controls, F42 continuity memory and F43 bounded repair loops; verify every consumer integration separately.

## Blocking external decisions

Target runtime/game engine; production hardware; user-approved Tevin references in a private store; commercial license clearance for restricted models. These do not block independent CPU/procedural work.
