# MGR 3D Forge — Build and Acceptance Plan

Research is necessary but never a substitute for producing testable artifacts. This plan defines what to build, measure, repair and verify.

## Phase 0 — Baseline gates

- Verify GitHub repo tree/default branch and its existing user edits.
- Inspect Creation OS, Create Loco, Tevin Rain/MGR-ONE existing services before assigning integration ownership.
- Resolve Blender exact runtime version, OS/CPU/RAM/GPU/VRAM and disk.
- Decide reference privacy boundary. Public repo must not receive owner private character imagery.
- Review licenses before model downloads/distribution.
- Record source SHA and model versions for every experiment.

## Phase 1 — CPU-native vertical slice

Deliverable: prompt to deterministic `WorldSpec`, generate seeded terrain + roads + 10 buildings via Blender Python/Geometry Nodes, export GLB and `.blend`, reopen and verify counts/scale/landmarks/collision proxies. Run with no discrete GPU. Save screenshots and quality receipt.

Tests: same seed yields same scene graph; different seed varies intended aspects; room doors not blocked; negative scale/normals checked; no objects placed outside region bounds; export/import preserves dimensions; no paid API called.

## Phase 2 — Local single-object and character baseline

Deliverable: CPU TripoSR image-to-mesh test and controlled candidate alternatives on available hardware only with approved weights. Keep original Tevin model immutable. Add landmark/pose checkers before generation. Separate coat/shirt/pants/boots/hair/chains from base by whichever approved/manual/automatic path proves reliable. Rig-check and roundtrip.

Tests: left/right hand count; finger/limb landmarks; feet/boot and coat collision; correct torso/arm proportion bounds; no unbound mesh; T-pose, A-pose, idle/walk deformation preview; all parts named and independently selectable; original face unchanged within tolerance.

## Phase 3 — Large world

100 then 1,000 repeated buildings using instances and limited unique assets, constrained poly and texture budgets. Validate world-region memory, route connectivity, revisit landmark stability, editable export, LOD, streaming and import in selected runtime. No invented FPS target before hardware/engine baseline.

## Phase 4 — Quality and cost competition

Use same approved reference/prompt set across procedural+open-model MGR and optional paid vendor baseline. At least 30 comparable tasks for statistical stability; disclose failure/retry rates. Evaluate:
- per-accepted-asset total cost and time (P50/P95);
- mesh usability, topology, holes/non-manifold, UV/material pass;
- human-blind likeness/style quality for character;
- part separation / rig success / export reimport success;
- 3D world layout coherence and navigation tests;
- RAM/VRAM/GPU usage, model init and cold/warm inference.

A 10x result requires apples-to-apples baseline and confidence intervals or multiple robust repetitions. A feature-level 10x gain is not product-level 10x.

## Phase 5 — Integration and owner acceptance

Expose stable capability service through canonical MGR system (after source audit). Integrate with Tevin project and Creation OS without duplicating existing agents/approval queues. Owner approves canon and interactive world demonstrations. Provide rollback and cost telemetry.

## Model experiment matrix

| Trial | Input | Pass criteria | Known risk |
|---|---|---|---|
| C-01 | Tevin approved front/side/back and base mesh | preserves head/body and complete hands | private references, hands |
| C-02 | Coat + jewelry source | separate pieces and attachment sockets | thin geometry |
| C-03 | Humanoid rig | bend without catastrophic deformation | bad weights |
| P-01 | 1 building prompt | editability and correct measurements | procedural design |
| W-01 | city block with 10 buildings | street access, no overlaps | spatial layout |
| W-02 | same world reloaded | exact seed and landmarks | continuity |
| W-03 | 1,000 buildings | bounded memory and load time | mesh instancing |
| R-01 | authorized multi-image building capture | camera and geometry alignment | GPU and uncertainty |

## Status protocol

Each task records separate research status / implementation-test status / integration-owner status, exact executed command/version, exit/result and evidence links. If runtime unavailable, mark NOT RUN. A partial visual preview is not accepted production geometry.
