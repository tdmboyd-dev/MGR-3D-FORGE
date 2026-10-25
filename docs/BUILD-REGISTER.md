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
| F11 | Garment/part separation | SOURCED | PARTIAL: synthetic detachable parts TESTED | P1 | F09, permitted segmentation | Generic 16-part mannequin; real Tevin segmentation absent |
| F12 | Automated rig/weights | SOURCED | PARTIAL: rigid + 1.0-weight skinned armature Blender VERIFIED | P1 | clean mesh, rig type | 16 modifiers, 11 bones, hand mesh moved 0.428m, 2 render frames; smooth joint weights/full animation remain |
| F13 | Material/UV quality | SOURCED | NOT STARTED | P1 | F06 | PBR/export validation |
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
| F31 | MGR World Flight | SPECIFIED | PARTIAL: keyframe plan TESTED | P1 | F16,F17 | MGR 3D camera paths exported; actual camera player pending |
| F32 | MGR Model Dock | SPECIFIED | PARTIAL: recipe inspection TESTED | P1 | F07,F22,F29 | MGR model manifest; sandboxed installs and model launch pending |
| F33 | MGR Spatial Eyes | SPECIFIED | PARTIAL: geometry visibility TESTED | P1 | F16,F17,F20 | MGR-authored world occlusion and evidence labels; HUD and reconstruction pending |
| F34 | MGR Scene Consciousness | SPECIFIED | PARTIAL: generated-world facts/qualified routes TESTED | P0 | F02,F05,F16,F33 | `forge/consciousness.py` emitted in world bundles; Blender object inspection pending machine test; semantic door portals absent |
| F35 | MGR Visual Judge | SPECIFIED | PARTIAL: pixel/translation/quarter-turn/alpha-aware silhouettes TESTED | P0 | F06,F30,F34 | Real transparent Blender pose images foreground QA; arbitrary 3D pose identity and semantic evaluator pending |
| F36 | MGR Code Architect | SPECIFIED | PARTIAL: typed workspace file edits and rollback TESTED | P0 | F22,F23,F29 | `forge/code_architect.py`; isolated arbitrary-code executor, policy enforcement, consent UI pending |
| F37 | MGR Anatomy Guardian Plus | SPECIFIED | PARTIAL: multi-frame bone and joint QA TESTED (pure Python) | P0 | F09,F10,F35 | `forge/pose_guardian.py` rejects missing bones, changed bone lengths, joint gaps, weightless mesh parts and frozen hand motion; live Blender bridge acceptance still pending |
| F38 | MGR Fabric Intelligence | QUEUED | NOT STARTED | P1 | F11,F12,F13 | Separable fitted garments, intersections and motion QA |
| F39 | MGR Rig Intelligence | SPECIFIED | PARTIAL: modular deform modifiers, 1.0 bone weights, keyframes Blender VERIFIED; pose inspector CODED | P0 | F09,F12,F37 | `bridge/blender_pose_inspect.py` observes two evaluated frames and full skin coverage; live Windows pose audit, smooth weights and production animation remain |
| F40 | MGR World Logic | SPECIFIED | PARTIAL: collision-checked road-centerline rehearsal TESTED | P1 | F15,F17,F34 | `forge/traversal.py`; actual navmesh/doors/stairs/dynamic agent game runtime pending |
| F41 | MGR Cinematic Director | QUEUED | NOT STARTED | P1 | F13,F31,F35 | Reproducible cameras, lighting, material and shot recipes |
| F42 | MGR Creation Memory | SPECIFIED | PARTIAL: integrity-chained JSON revisions and locks TESTED | P0 | F05,F20,F34 | `forge/creation_memory.py`; concurrent DB, actual owner identity and cross-app replay pending |
| F43 | MGR Self-Repair Studio | SPECIFIED | PARTIAL: bounded file repair + build→Blender→render receipt pipeline TESTED (CPU stage) | P1 | F23,F30,F35,F36 | `forge/repair.py`, `forge/pipeline.py`; full Blender integrated run and semantic repair pending |

**Scope:** 43 MGR-native areas: original 33 plus F34–F43 approved for the implementation queue on 2026-10-25. Queued is **not** implemented. Technical research is organized by MGR functions in `research/MGR-CREATION-INTELLIGENCE-HOWTO.md`; necessary external provenance stays under `research/external-provenance/`.

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
