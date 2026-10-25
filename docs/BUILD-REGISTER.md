# Native Capability and Build Register

Baseline 2026-10-25. Status sequence: DISCOVERED > QUEUED > SOURCED > READ > RESEARCHED > SPECIFIED > IMPLEMENTED > RUNNING > TESTED > VERIFIED > INTEGRATED > OWNER-ACCEPTED. Do not skip. Research state and actual product state are independent.

| ID | MGR-owned capability | Research state | Code state | Priority | Dependencies | Next evidence |
|---|---|---|---|---|---|---|
| F01 | Intent -> typed project & brief | SPECIFIED | PROTOTYPE TESTED | P0 | input schema | Limited count-only offline parser, not general intent |
| F02 | Scene/asset dependency graph | SPECIFIED | PARTIAL: tested DAG | P0 | F01 | Stable topo-sort/cycle checks; full scene graph pending |
| F03 | CPU procedural terrain/roads | SOURCED | PARTIAL: roads, TESTED | P0 | F02, Blender | Terrain, curves and engine import absent |
| F04 | Parametric buildings/rooms | SOURCED | PARTIAL: massing + two-room hypothesis TESTED | P0 | F03 | 1,000-lot test + interior GLB; real architecture/edits pending |
| F05 | Asset store and provenance | SPECIFIED | PROTOTYPE TESTED | P0 | asset schema | Hash/dedupe/tamper tests pass; durable transactional backend pending |
| F06 | GLB import/export + QA | SPECIFIED | PARTIAL: export, TESTED | P0 | Blender version | Internal structure test passes; independent import/export pending |
| F07 | Local model adapter contract | SPECIFIED | NOT STARTED | P0 | F02, license gates | Mock + two providers |
| F08 | CPU TripoSR prototype | SOURCED | NOT STARTED | P0 | runtime resources | Timed 3 asset benchmark |
| F09 | Character DNA measurements | SPECIFIED | PROTOTYPE TESTED | P0 | approved Tevin base | Synthetic proportion comparison only; Tevin not captured |
| F10 | Anatomy guardian | SPECIFIED | PROTOTYPE TESTED | P0 | F09 | Missing hand and symmetry checks; visual mesh checking pending |
| F11 | Garment/part separation | SOURCED | NOT STARTED | P1 | F09, permitted segmentation | Coat/chain boot suite |
| F12 | Automated rig/weights | SOURCED | NOT STARTED | P1 | clean mesh, rig type | T/A/walk deformation |
| F13 | Material/UV quality | SOURCED | NOT STARTED | P1 | F06 | PBR/export validation |
| F14 | Geometry repair/retopo | SOURCED | PARTIAL: triangle repair TESTED | P1 | F06 | Malformed triangle cleanup passed; retopo/manifold repair pending |
| F15 | Region/world graph | SPECIFIED | PARTIAL: road intersections TESTED | P0 | F02 | Region hierarchy and landmarks pending |
| F16 | World assembly | SPECIFIED | PARTIAL: static scene TESTED | P0 | F03-F05,F15 | Scene export works; graph and navigation pending |
| F17 | Scene navigation/collision | QUEUED | PARTIAL: grid pathfinding + box collision TESTED | P1 | F16, target engine | Navmesh and moving-agent engine traversal pending |
| F18 | LOD/instancing/streaming | QUEUED | PARTIAL: LOD1 + chunk manifest TESTED | P1 | F16 | LOD1 GLB and chunk coverage; runtime streaming/fps pending |
| F19 | Image/video scene reconstruction | SOURCED | NOT STARTED | P2 | licensed weights, GPU | Camera/depth benchmark |
| F20 | Persistent character/world memory | SPECIFIED | NOT STARTED | P1 | F05,F09,F15 | Cross-run continuity |
| F21 | Compute/resource cost router | SPECIFIED | PARTIAL: budget gate TESTED | P1 | benchmark data | Real hardware/provider estimates pending |
| F22 | Human approvals | SPECIFIED | PARTIAL: authorization TESTED | P0 | existing gateway integration | Fail-closed remote/spend test passes; identity and UI pending |
| F23 | Workflow resumes/retries | SPECIFIED | PARTIAL: local checkpoints TESTED | P1 | job store | Restart test passes; retries/concurrency pending |
| F24 | User-facing creation studio | DISCOVERED | PARTIAL: static SVG preview | P2 | stable engine | Actual editor, live preview and rehearsal UI absent |
| F25 | Creation OS integration | BLOCKED: repo audit | NOT STARTED | P1 | canonical ownership | Integration contract |
| F26 | Create Loco integration | BLOCKED: repo audit | NOT STARTED | P2 | consumer needs | Screenshot-to-scene |
| F27 | Tevin/MGR-ONE integration | BLOCKED: repo audit | NOT STARTED | P1 | canonical base | Owner-approved character |
| F28 | Cross-engine export pack | SPECIFIED | PARTIAL: OBJ/MTL + GLB exported | P1 | targets known | External Blender/Unity/Unreal import still unverified |
| F29 | License/provenance gate | SOURCED | PARTIAL: license ID gate TESTED | P0 | model legal review | Unknown-license approval enforced; legal clearance still open |
| F30 | Benchmark/quality ledger | SPECIFIED | PROTOTYPE TESTED | P0 | metric spec | Reproducible test/manifest; quality against Blender targets pending |
| F31 | Native World Flight (Scroll-World inspired) | SOURCED | PARTIAL: keyframe plan TESTED | P1 | F16,F17 | 3D camera paths exported; actual scroll player pending |
| F32 | Forge Model Dock (Pinokio inspired) | SOURCED | PARTIAL: recipe inspection TESTED | P1 | F07,F22,F29 | Fail-closed manifest; sandboxed installs and model launch pending |
| F33 | Spatial Eyes (God's Eye View inspired) | SOURCED | PARTIAL: geometry visibility TESTED | P1 | F16,F17,F20 | Known-object occlusion and evidence labels; HUD and external/reconstruction layers pending |

**Scope expansion:** 30 original tracked items plus F31 (World Flight), F32 (Model Dock) and F33 (Spatial Eyes) = **33**. Synapse is an unresolved research intake, **not** a counted capability until its upstream is verified. See `research/SCROLL-SYNAPSE-PINOKIO-INTAKE.md` and `research/GODS-EYE-VIEW-NATIVE-INTAKE.md`.

## Definition of production completeness

All critical capabilities must have checked-in code, reproducible runtime evidence, QA receipts, round-trip assets and actual consumer acceptance. A working README or API stub alone is not done. Keep partial status honest.

## Immediate build order

1. Obtain and verify source repos / Blender version / hardware, plus approved Tevin base privately.
2. Build F01/F02/F05/F06/F22/F29/F30 contracts and tests.
3. Build F03/F04/F15/F16 CPU world slice; verify no GPU.
4. Build F07/F08 baseline local generation with budget/quality receipts.
5. Build F09/F10 character validation; then F11/F12 production tests.
6. Expand world, reconstruction and studio only after narrow vertical slices pass.

## Blocking external decisions

Target runtime/game engine; production hardware; user-approved Tevin references in a private store; commercial license clearance for restricted models. These do not block independent CPU/procedural work.
