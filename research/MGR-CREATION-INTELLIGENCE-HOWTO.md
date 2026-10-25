# MGR Creation Intelligence — Native How-To Research and Acceptance Plan

**Owner:** MGR 3D Forge. **Date:** 2026-10-25. **Status:** researched implementation plan, not evidence of implemented features. **Canon:** `docs/MGR-NATIVE-CANON.md` and `docs/BUILD-REGISTER.md`.

This document describes **our** technical creation contracts. External documentation and licensing links are reference evidence, not MGR product names or architectural ownership. Keep provider dependencies interchangeable and preserve license notices in the isolated provenance ledger.

## Operating principle — autonomous but bounded

The target is **unattended work inside a specific approved project root**, not unconditional authority over the whole computer. MGR Code Architect may read/write/generate code and files, invoke installed Blender, run local tests, inspect render results, retry and roll back **within a designated job workspace** without checkpoint-by-checkpoint prompts. Human approval remains required for deleting unrelated personal data, writing outside approved roots, exposing secrets, changing authentication/permissions, buying compute, and running unreviewed network installers. All jobs carry immutable input receipts, an execution log, file diff, CPU/RAM/time budget, cancellation, checkpoint, rollback path and final tests. Policy denial is explicit; the engine must never reroute around it.

Do **not** grant blanket shell permission, recursive delete authority, or secret-store access merely because the AI generated the script. Prefer task-scoped Blender scripts launched headlessly; each code step must declare expected outputs. A private working copy plus selective promotion into the authoritative repo protects source of truth.

## Exact build cycle

1. **Understand:** parse user goal into typed objects, spatial relationships, constraints, style and target exports. Require a reference/approval for a protected likeness.
2. **Plan:** choose procedural CPU Blender actions first when precise editable geometry is available. Choose optional image-to-3D or vision worker only where measured gain outweighs cost, licensing, hardware and fidelity risks.
3. **Construct:** generate project-scoped Blender Python scripts or original mesh operations. Save editable `.blend` project, detachable elements and export GLB as separate artifacts.
4. **See:** collect object-level geometry, material slots, bone names, transforms, UVs, mesh topology and image renders from fixed camera angles. Keep structural facts separate from model-produced visual judgments.
5. **Judge:** compare against typed acceptance thresholds; emit measurable failures, screenshot artifacts and confidence-scoped observations. Missing hands and garment/body intersections are blocking defects.
6. **Repair:** generate a small patch, rerun Blender, compare before/after and revert if the candidate regresses. Limit attempts; report unresolved errors instead of claiming completion.
7. **Package:** validate mesh and semantic manifests, hash every artifact, independently open exports in Blender/game runtime, produce acceptance receipts and publish only approved results.

## F34 — MGR Scene Consciousness

- **How:** walk Blender's dependency graph and evaluated scene using `bpy.data`, `bpy.context`, evaluated meshes and object bounding boxes. Serialize stable object IDs, hierarchy, transforms, meshes, materials, armatures, semantic tags, portals and connections to `scene_facts.json`.
- **Reason:** a visual caption of an image cannot prove there is a walkable doorway. Geometry checks must be exact where possible; visual conclusions tagged `inferred`.
- **Tests:** create rooms, add/remove door, assert changed portal connectivity; test occlusion query, orphan assets, duplicate ID, impossible object dimensions, stable reload.
- **Acceptance:** all query answers link to source objects and measured data; no object hallucinated from a render.

## F35 — MGR Visual Judge

- **How:** Blender Workbench fixed-angle baseline first, plus Cycles/EEVEE beauty render variants. Store camera matrices, render resolution, color management, engine/version, object visibility and immutable PNG SHA. Compare geometry masks, silhouette occupancy, landmark locations and per-pixel metrics on identical settings. Add a separate multimodal vision evaluator behind a provider-neutral interface for qualitative defects.
- **Tests:** missing hand, hidden hand, shirt/coat intersection, wrong framing, flipped normals, intentionally moved eye/arm and changed lighting; assert expected failures detected. Blindly trusting a single visual model is prohibited.
- **Acceptance:** defects must be localized, evidenced and reproducible; zero false `PASS` cases in critical synthetic fixtures.

## F36 — MGR Code Architect

- **How:** planner produces a manifest of files/actions and allowed subprocesses; validator checks scope, paths and budgets; runner creates an isolated copy, applies patch, runs targeted Python/Blender tests, captures diffs, then promotes verified changes with authorization. Language adapters: Python/blender first; JavaScript/TypeScript, shader code and compiled native extensions only when a task requires them.
- **Tests:** enforce out-of-root writes rejection, symlink traversal rejection, network/secret access denial, timeout/CPU budgets, harmless multi-file changes without repeated prompts, failure rollback, resume after crash.
- **Acceptance:** routine approved multi-step builds run without interruption, but policy-denied operations remain blocked.

## F37 / F39 — MGR Anatomy Guardian Plus and Rig Intelligence

- **How:** establish T/A neutral poses, real body scale, distinct hand/foot geometry and shoulder/elbow/wrist/hip/knee/ankle landmarks. Create armatures with named parenting hierarchy, joint limits, IK/FK where needed, normalized vertex-group weights and exportable deform bones. Blender skinning and Rigify workflows provide implementation evidence for the mechanics.
- **Tests:** all hands/fingers inside camera frustum in turnarounds; pose shoulders, elbows, hips and knees across motion range; check disappearing faces, skin weight normalization, joint volume loss, self-intersection, rest/pose transform round trip, GLB animation reimport.
- **Acceptance:** moving **mesh** follows bones in Blender; metadata-only pose tracks do not pass.

## F38 — MGR Fabric Intelligence

- **How:** create separately named detachable coat, shirt, pants, footwear, hair and jewelry with material/rig bindings; fit garments to the actual body using offset surfaces or designed pattern meshes; resolve intersections at rest and during animation; optional cloth simulation for secondary motion.
- **Tests:** hide each garment independently, replace coat without altering body mesh, animate full pose range, test garment skin penetration from multiple camera angles, asset bundle reimport.
- **Acceptance:** garments remain separate, modifiable components and do not intersect in required motion tests.

## F40 — MGR World Logic

- **How:** represent buildings, rooms, doors, streets, stairs and elevators as a typed portal graph; produce traversable floor geometry and navigation meshes; route actual agents through geometry in a runtime. Keep route A* graph validity distinct from walkable navmesh validity. Bake navmesh off the interactive frame when possible.
- **Tests:** blocked door breaks route; stair connects floors; agent walks street→door→room; no solid wall shortcuts; dynamic obstacle avoidance; route replanning.
- **Acceptance:** recorded agent traversal and collision-rejection proof, not just a JSON path.

## F41 — MGR Cinematic Director

- **How:** reproducible camera rigs (focal length, depth of field, orientation, keyframes), lighting presets, HDRI/area-light setups and consistent material rendering. Track shot assets and camera coverage; preserve look across re-renders.
- **Tests:** exact pose/shot keyframes, subject fully inside frame, no accidental clipping, reproducible exposure and shot continuity at fixed settings.
- **Acceptance:** actual rendered footage and per-shot coverage receipts.

## F42 — MGR Creation Memory

- **How:** keep approved asset hashes, canonical semantic IDs, versioned character and world contracts, ownership flags, fixed dimensions, provenance and approval history. Store style preferences as explicit constraints, not hardcoded model prompt lore.
- **Tests:** regenerate with new seed without violating locked character identity; inspect diff; merge authorized updates only; restore history; detect unauthorized replaced asset.
- **Acceptance:** original approved properties survive edits, exports and consumer handoffs.

## F43 — MGR Self-Repair Studio

- **How:** bounded loop `observe → classify → propose minimal diff → run checks → compare → promote or revert`. Never use image similarity alone for anatomy, licensing or safety. Stop after configurable failed attempts or budget exhaustion.
- **Tests:** intentional overlapping jacket, missing hand and corrupt GLB fixtures; verify successful repairs improve measured checks and regressions are automatically rejected.
- **Acceptance:** repair receipt includes original defect, change, new render, test scores, rollback availability.

## Model acceleration and hardware decisions

- Procedural generation, metadata checks, graph reasoning, GLB assembly, basic Blender rendering and many geometry tests run on CPU. The Windows Blender 5.2.2 owner-machine receipts already prove some of this.
- Heavy neural image-to-3D / texturing is a **separate optional worker** with model-dependent GPU memory. Never claim GPU-free advanced neural inference without a measured run on the target machine.
- Candidate adapters must record model weights, dependencies, exact license, commercial terms, VRAM/RAM, model-download size, speed, fidelity, riggability and re-export QA before enabling.
- Public code licenses and model-weight licenses can differ. Do not copy repository implementation or weights without review; a documented algorithmic concept can inform an independently built MGR capability while preserving mandatory notices.

## Research coverage still required before claiming 'complete how-to'

For **each** F34–F43 and existing F03/F04/F06/F09–F19/F24/F28, add version-pinned source documentation, exact scripts, inputs/outputs, failure taxonomy, performance baselines on Time's PC, at least one positive/negative test fixture, third-party license review and a working Blender receipt. Specific gaps: real production topology/retopology, UV unwrapping, PBR material validation, skeleton/weights, corrective shapes, face rig, cloth simulation, dynamic world collision, navmesh runtime, visual evaluator calibration, neural model hardware feasibility, and interactive studio acceptance.

### Technical reference evidence (not MGR product identities)

- Blender 5.2 armature deformation: https://docs.blender.org/manual/en/latest/animation/armatures/skinning/parenting.html
- Blender 5.2 skinning: https://docs.blender.org/manual/en/latest/animation/armatures/skinning/index.html
- Blender Python API: https://docs.blender.org/api/current/
- Blender BMesh geometry API: https://docs.blender.org/api/current/bmesh.html
- Godot navigation implementation: https://docs.godotengine.org/en/stable/classes/class_navigationregion3d.html
- Microsoft image-to-3D code and dependency/license caveats: https://github.com/microsoft/TRELLIS.2
- Tencent 3D memory and separate weight license review: https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1

**Source-of-truth rule:** Product-facing docs describe MGR functionality and evidence. References above are purely technical validation. Any reused code, weights or assets must retain legally required credit/license notices in provenance and distributions.
