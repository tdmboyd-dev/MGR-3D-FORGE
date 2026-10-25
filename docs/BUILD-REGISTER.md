# Native Capability and Build Register

Baseline 2026-10-25. Status sequence: DISCOVERED > QUEUED > SOURCED > READ > RESEARCHED > SPECIFIED > IMPLEMENTED > RUNNING > TESTED > VERIFIED > INTEGRATED > OWNER-ACCEPTED. Do not skip. Research state and actual product state are independent.

| ID | MGR-owned capability | Research state | Code state | Priority | Dependencies | Next evidence |
|---|---|---|---|---|---|---|
| F01 | Intent -> typed project & brief | SPECIFIED | PROTOTYPE TESTED | P0 | input schema | Limited count-only offline parser, not general intent |
| F02 | Scene/asset dependency graph | SPECIFIED | NOT STARTED | P0 | F01 | Deterministic plan diff |
| F03 | CPU procedural terrain/roads | SOURCED | PARTIAL: roads, TESTED | P0 | F02, Blender | Terrain, curves and engine import absent |
| F04 | Parametric buildings/rooms | SOURCED | PARTIAL: massing, TESTED | P0 | F03 | 1,000-lot test passes; rooms absent |
| F05 | Asset store and provenance | SPECIFIED | PROTOTYPE TESTED | P0 | asset schema | Hash/dedupe/tamper tests pass; durable transactional backend pending |
| F06 | GLB import/export + QA | SPECIFIED | PARTIAL: export, TESTED | P0 | Blender version | Internal structure test passes; independent import/export pending |
| F07 | Local model adapter contract | SPECIFIED | NOT STARTED | P0 | F02, license gates | Mock + two providers |
| F08 | CPU TripoSR prototype | SOURCED | NOT STARTED | P0 | runtime resources | Timed 3 asset benchmark |
| F09 | Character DNA measurements | SPECIFIED | PROTOTYPE TESTED | P0 | approved Tevin base | Synthetic proportion comparison only; Tevin not captured |
| F10 | Anatomy guardian | SPECIFIED | PROTOTYPE TESTED | P0 | F09 | Missing hand and symmetry checks; visual mesh checking pending |
| F11 | Garment/part separation | SOURCED | NOT STARTED | P1 | F09, permitted segmentation | Coat/chain boot suite |
| F12 | Automated rig/weights | SOURCED | NOT STARTED | P1 | clean mesh, rig type | T/A/walk deformation |
| F13 | Material/UV quality | SOURCED | NOT STARTED | P1 | F06 | PBR/export validation |
| F14 | Geometry repair/retopo | SOURCED | NOT STARTED | P1 | F06 | Broken mesh fixtures |
| F15 | Region/world graph | SPECIFIED | NOT STARTED | P0 | F02 | Stable landmarks |
| F16 | World assembly | SPECIFIED | PARTIAL: static scene TESTED | P0 | F03-F05,F15 | Scene export works; graph and navigation pending |
| F17 | Scene navigation/collision | QUEUED | NOT STARTED | P1 | F16, target engine | Agent traversal |
| F18 | LOD/instancing/streaming | QUEUED | NOT STARTED | P1 | F16 | Load times, fps |
| F19 | Image/video scene reconstruction | SOURCED | NOT STARTED | P2 | licensed weights, GPU | Camera/depth benchmark |
| F20 | Persistent character/world memory | SPECIFIED | NOT STARTED | P1 | F05,F09,F15 | Cross-run continuity |
| F21 | Compute/resource cost router | SPECIFIED | NOT STARTED | P1 | benchmark data | Budget cap tests |
| F22 | Human approvals | SPECIFIED | NOT STARTED | P0 | existing gateway integration | Denied spend/upload test |
| F23 | Workflow resumes/retries | SPECIFIED | NOT STARTED | P1 | job store | Restart midflight |
| F24 | User-facing creation studio | DISCOVERED | NOT STARTED | P2 | stable engine | Rehearsal UI |
| F25 | Creation OS integration | BLOCKED: repo audit | NOT STARTED | P1 | canonical ownership | Integration contract |
| F26 | Create Loco integration | BLOCKED: repo audit | NOT STARTED | P2 | consumer needs | Screenshot-to-scene |
| F27 | Tevin/MGR-ONE integration | BLOCKED: repo audit | NOT STARTED | P1 | canonical base | Owner-approved character |
| F28 | Cross-engine export pack | SPECIFIED | NOT STARTED | P1 | targets known | Target engine import |
| F29 | License/provenance gate | SOURCED | NOT STARTED | P0 | model legal review | Block unapproved weights |
| F30 | Benchmark/quality ledger | SPECIFIED | PROTOTYPE TESTED | P0 | metric spec | Reproducible test/manifest; quality against Blender targets pending |

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
