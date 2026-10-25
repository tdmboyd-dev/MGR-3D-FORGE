# S08 — MGR Living World Runtime: real-time 3D at world scale

**Decision:** MGR Forge generates and validates engine-neutral worlds; a **separate living-world runtime adapter** turns approved worlds into playable environments. Do not rebuild an entire Unreal-class renderer before shipping the first believable explorable world. Build native scene contracts, streaming scheduler, truth/visibility validation, reproducible gameplay harness and exports first; connect available runtimes with clear licensing. “Fortnite-class” is a target for massive collaborative worlds, not a claim of equal production systems.

**Status — 2026-10-25:** full architecture research and implementation specification; not a verified MGR shipping game engine. External research ledger: [S08 sources](../external-provenance/S08-GAME-SOURCES.md). No third-party runtime source copied and no device/console benchmark measured in this research wave.

## 1. Definition: what makes a 3D scene a world?

A static render shows what a camera saw once. A **living world** preserves spatial truth, interactive rules, camera/player control, world persistence, collision, motion, events, streaming and optional shared online state as viewers move and interact. A believable castle must exist behind its facade; doors must connect traversable spaces and users must not fall through apparently solid floors. A photoreal frame is only one acceptance artifact.

## 2. Engine architecture and authoritative ownership

The runtime needs separate responsibilities: world store/scene graph, object/component identities, fixed-step physics/simulation, render view, audio, input/camera, animation, AI/navigation, resources/streaming, save/persistence, networking and instrumentation. Each component has an authoritative owner. Scene coordinates are meters, right-handed XYZ, Y-up per MGR geometry contract; adapters transform to a destination engine's axes, handedness and units. A network server determines gameplay outcomes; a client renders and predicts/interpolates local presentation. Forge's generator must never write directly into production multiplayer authoritative state.

## 3. Full interactive workflow

Prompt/story/world bible → deterministic authored **MGR World Anatomy** (regions, actors, interiors, paths, hierarchy) → geometric and visual truth QA → scene cells and asset content hashes → LOD/collision/navmesh/lighting baking → runtime packaging → continuous runtime cell streaming and camera traversal → object interactions/AI/physics → save or server replication → capture performance, correctness and visual evidence. Every generated asset should be traceable back to source design and exact revision.

## 4. Mathematics/graphics/physics foundations

World transforms, view/projection matrices, frustum checks, bounding volumes, spatial trees and occlusion are base geometry. Rendering uses visibility selection, draw-call/material batching, shader/material pipelines, texture residency, mesh LOD, light/shadow budgets, temporal stability and post-processing. Physics uses fixed time increments, robust collision broad phase/narrow phase and scene query integration; gameplay uses prediction and time-stamped events. Audio propagation and NPC perception also consume world geometry. A visible wall and its collider must agree.

## 5. Modern large-world design translated to MGR

| MGR-native subsystem | Purpose and original composition | Acceptance proof |
|---|---|---|
| **Realm Cells** | Divide geography into content-addressed cells with dependencies, staged load/activate/evict, optional indoor sectors | Fast camera travel loads assets before arrival without stale or missing geometry |
| **Horizon Truth** | Show distant forms using authored hierarchical proxy LODs with approved silhouette/material limits | LOD transition error bounded in pixels and no visible pops above threshold |
| **Perception Budgeter** | Choose geometric/material/FX/audio fidelity by screen-space relevance and platform budgets; not a copy of proprietary virtualized rendering | GPU and memory counters stay inside defined profile under stress |
| **Actor DNA** | Semantic object IDs, components, interactions, collisions, state, source assets, owners | Runtime can query every object and persist its state correctly |
| **World Continuity** | Stable time/weather/day-night/FX and world-wide rules across cells and transitions | No reset/weather seam when player returns to previous cell |
| **Portal Anatomy** | Indoor rooms, outdoor links, occlusion portals and navigation doors share a connectivity graph | Camera and agent can traverse valid routes, cannot pass closed doors |
| **Motion Clock** | Explicit simulation ticks, animation blending and visual interpolation | Repeated input seed replays deterministically within documented tolerance |
| **Population Fabric** | Proximity-aware NPC simulation LOD; far agents use coarse scheduled updates, near agents full behavior | Crowd state stable across unloaded regions and save/rejoin |
| **Live Presence** | Server-authoritative state with relevance subscription, rate-limited inputs, transport adapter | Two remote players agree on inventory/collision/events under latency and packet loss |
| **Director's World Eye** | Camera-inspection agent explores free orbit, noclip and player paths while recording occlusion/geometry faults | QA detects missing backside, non-traversable path or camera clipping |

These are proposed *MGR-owned designs*, not existing shipped component claims.

## 6. Repository and engine strategy

Use MGR-native procedural generation, validation and asset packaging regardless of chosen viewer. A permissive runtime adapter offers fast independent prototyping of camera/controller/physics/network use; a commercially licensed high-fidelity adapter can support cinematic features and complex production exports. Keep the canonical scene independent from the engine so one framework's proprietary internals do not become Forge's source of truth. Required adapter interface: `import_scene`, `mount_cells`, `set_camera`, `simulate_ticks`, `query_collision`, `query_navmesh`, `capture_frame`, `collect_metrics`, `export_playable`. Initially a headless test harness may stub display while exercising spatial contracts, but cannot pass visual QA by doing so.

## 7. Runtime algorithms and data structures

- Chunk region graph and quadtree/octree/BVH (choose by geometry); per-region content hashes, asset dependency DAG and stable actor IDs.
- Cell state machine: `UNSEEN → REQUESTED → FETCHING → DECODED → PREPARED → ACTIVE → COOLING → EVICTED` with bounded prefetch, memory, timeouts, cancellation and rollback; no active cell before its colliders/critical nav links are ready.
- Scheduling based on camera frustum, velocity predictive cone, player relevance, teleport destinations and deterministic priorities. Avoid asset I/O on render thread.
- Mesh HLOD/proxy generation, texture mip/virtual texture paging, impostors only when truthful to rendered view, material/shader instancing, GPU occlusion with fallback.
- Entity component or data-oriented storage for frequently processed systems, avoiding allocation and per-actor scripting overhead in mass populations.
- Multiple simulation fidelity tiers for AI, particles and distant physics, with exact state rehydration upon approach.

## 8. Models, datasets and generated assets

Models can propose a terrain plan, urban zoning, room layout, prop arrangements, animation clips, dialog or crowd trajectories. Deterministic validators confirm topology, scale, collision, navigation and licensing. Use synthetic scenes of increasing density and owned MGR assets for benchmarks: 1-room interior, 1-city block, 64-region countryside, 1,000 NPC actors, 1,000 simultaneous dynamic entities, teleport across opposite world ends, multi-user disagreement recovery. Public sample game assets are not assumed transferable to a commercial MGR project; every weight/asset/license needs an explicit admission record.

## 9. Graphics, camera, lighting and virtual production

Support perspective/orthographic camera, free orbit, third-person and first-person controls, cinematic rail/crane/dolly/lens controls, multi-camera cuts and physically plausible exposure/DOF/motion blur. HDR environment lighting, key/fill/rim, shadow maps or ray tracing based on profile, reflections, volumetric fog, particles, shader deformation, water and weather must have LOD/culling and temporal-stability gates. Magic/illusions/fantasy can *override appearance and physics* by explicit simulation rule with compositing passes; they must not silently corrupt collision, character identity or authored world continuity. Runtime camera QA must inspect unseen backsides, doors and environment interiors.

## 10. Gameplay, navigation and living systems

Define player controller, ground/air vehicle movement if needed, interaction ray/capsule query, triggers and game-state machine. Navmeshes and route graphs are baked per cell with dynamic updates for doors/hazards; stitch links across cell boundaries. NPC states persist in low-detail simulation even when not rendered. Animation rigs, root-motion integration, locomotion blending, IK foot placement, ragdoll/physics and contact normals need pose-specific safety tests. Each actor has an explicit behavior and authority policy, not just a floating visual model.

## 11. Networking, security and scale

Single-player local mode first, multiplayer via bounded transport/server adapter. Authoritative server validates speed, interaction distance, inventory/economy changes and game actions; clients interpolate/predict and reconcile. Interest management sends only relevant nearby cell actors, not the full world. Tick/payload caps, asset content hashes, encrypted authenticated transport, replay-safe commands, input rate limiting, state snapshots and persistence migrations matter as much as renderer fidelity. Tests must inject 50–250 ms latency, packet loss, out-of-order updates and reconnects. No remote code execution or arbitrary user scripts in shared worlds; optional scripting executes within the dedicated Forge workspace and capability policy.

## 12. Hardware and GPU truth

Creating a scene graph, procedural terrain geometry, navmesh proposals and validation can use CPU. Real-time rich 3D display needs a graphics pipeline; a robust quality target will benefit from a GPU, and path-traced scenes/high-density geometry can require substantial VRAM. Aim for selectable capability profiles (headless CPU validation, mobile-friendly raster, desktop high-fidelity, offline cinema). Console targets require vendor enrollment, SDK access, engine support, device certification and performance QA. We cannot honestly promise that a Windows Blender test equals a shipping PlayStation build.

## 13. Performance budget economics

At 60 FPS the full frame budget is ~16.67 ms; at 30 FPS ~33.33 ms. That covers simulation, scene scheduling, rendering and presentation—not merely mesh drawing. Allocate budgets per profile for CPU main/game thread, render/GPU, audio, streaming I/O, memory/VRAM, shader compilation stalls, network bandwidth, save time and peak scene transition. Compile real measured baseline tables only after a device run; the budget numbers here are target arithmetic, not benchmarks. Frame-time percentiles (p50/p95/p99) matter more than average FPS, especially for camera teleport and crowds.

## 14. Major failure modes and evidence

- Cell pop-in, unloaded floors/colliders, actor duplication, wrong network relevance, memory leak on repeated travel.
- Far-from-origin coordinate jitter; automatic double precision is not free; world origin shift can desync replicated actors.
- Giant/high-detail assets blocking the render thread, shader compilation hitch, texture/geometry residency thrash, wrong camera frustum/LOD popping.
- False photorealism with empty backsides/interiors, player camera clipping geometry, broken transitions, inaccurate colliders or navmesh.
- Rigs, capes/hair/FX clipping during animation; effects covering needed UI or obscuring multiplayer gameplay.
- Non-authoritative clients cheating, replayed input, state corruption across reconnects, crashing cells from malformed downloaded assets.

## 15. Integration placement and test surfaces

Forge owns world generation, geometric and semantic truth, materials, lighting direction, actor and room IDs, asset export and reproducible QA. **Runtime adapter** owns frame loop, input, graphics backend, audio device, physics world, synchronization and profiler captures. On import, all cells/actors preserve original MGR IDs and units. Wire to existing spatial truth and mesh QA checks, world director/camera capabilities, animation, FX and motion-clock packages. Maintain one canonical feature registry and one build/evidence register: add each runtime gate when code and reproducible test evidence land, not when a document names it.

## 16. Acceptance matrix — production gates

| Gate | Fixture | Pass/fail signal | State |
|---|---|---|---|
| R1 | Free-camera 3D room | Walk/orbit/look up/down, collision and input responsive, frame capture with known camera | OPEN |
| R2 | Four adjacent streamed cells | Prefetch, activation and eviction work with no missing floor at seam | OPEN |
| R3 | Teleport across 64-region world | No crash/duplicate actors, bounded peak RAM/VRAM and measured cold/warm transition time | OPEN |
| R4 | Far camera with 3 detail ranges | Quantified silhouette/texture changes and no noticeable popping threshold violation | OPEN |
| R5 | Fully enterable building | Camera, collision, NPC path and actual internal geometry agree | OPEN |
| R6 | Ten poses with garments/FX | Character/wardrobe separation survives motion, shadows and camera orbit | OPEN |
| R7 | Day/night + weather + fantasy event | State continues during travel/unload, no visual discontinuity or gameplay rules violation | OPEN |
| R8 | 1,000 moving actors | Measured p50/p95/p99 frame time, simulation counts and memory by hardware profile | OPEN |
| R9 | Two clients + authoritative server | Reconcile latency/loss/disconnect; reject invalid movement and repeated transactions | OPEN |
| R10 | Save and reload 100 world objects | Identical IDs, placement, inventory, trigger and NPC state | OPEN |
| R11 | 30-minute reproducible traversal | No resource leaks, unexpected actor duplication, game-thread/asset stalls, lost interactions | OPEN |
| R12 | Low-end/mobile + desktop + headless | Same semantic/collision content; presentation scales to device, failures reported | OPEN |
| R13 | Native/target engine import-export | Scene coordinates, transforms, skins, materials, animations and IDs preserved | OPEN |
| R14 | Console readiness | Actual approved SDK/device and certification/perf evidence | BLOCKED UNTIL PLATFORM AUTHORIZATION |

**Build sequencing:** ship R1 and R13 together, then R2/R3/R4 streaming/LOD, then R5–R7 scene/world/FX truth, then R8/R11 optimization, then R9/R10 authoritative multiplayer, then R12 portability. Console release stays separately gated. Every step captures scene version, input seed, machine/GPU, settings, FPS/frame time, screenshots/video and test result. Don't claim any gate complete from architecture research alone.

**Bottom line:** the power move is a truthful, fully editable MGR world description and a measured living-world runtime—not dependence on one engine's marketing label. An engine adapter gets a playable experience into Time's hands early, while original geometry, characters, physics rules and assets remain MGR-native.
