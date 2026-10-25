# MGR Motion Truth & Reality Dynamics

**Scope:** S06 Physics and simulation: rigid bodies, deformables, cloth, fluids, collisions and conservation constraints. **Owner:** MGR. **Date:** 2026-10-25. **Research maturity:** inspected primary manuals, specifications, upstream repositories and published licenses; not an end-to-end code audit or physical validation. **Implementation maturity:** design and acceptance research only in this packet; do not mark an engine, solver or Blender integration complete without actual test receipts.

## Core finding and MGR-native direction

Convincing fantasy physics requires **two different contracts**: (1) measurable, stable simulated behavior for standard bodies and materials; and (2) deliberate artistic violations with declared causes, limits and continuity. A fireball may defy ordinary gravity, but it must not randomly teleport or penetrate the same wall in one shot and collide in the next unless the director authored that rule. MGR's opportunity is **MGR Motion Truth**, a layer that combines world rules, solver adapters, director intent, event traces, energy/momentum diagnostics, collision integrity and frame-by-frame visual QA.

**Build decision:** Do not rewrite an industrial-strength fluid, cloth and collision solver from scratch as the first move. Own the MGR simulation *contract*, canonical scene state, effect-rule graph, cache versioning, validators and creative-control layer. Drive Blender's established solvers for offline production and evaluate a permissively licensed real-time backend (Jolt/Bullet) through a replaceable adapter after hands-on benchmarks. An authored magical exception must be recorded, never concealed as ordinary physics.

## 16-field research contract

### 1. Definition

Simulation advances state (x(t)) using masses, velocities, forces, material parameters, constraints, collision geometry and numerical timesteps. Rigid bodies preserve shape, while cloth and soft bodies deform; fluid/gas fields require spatial discretization and pressure/transport modeling. *Plausible appearance* and *accurate physical quantities* are independent quality targets.

### 2. Production uses

- Tevin wardrobe: cloth drapes, coat tails, chain and accessory collisions, contact with articulated limbs.
- Character/world interaction: feet ground, doors and props respond, thrown objects follow trajectories, rubble and falling architecture resolve collisions.
- MGR fantasy: spells, gravity inversion, floating islands, portal entry and breakable materials with authored rule envelopes.
- Direction and camera: deterministic replays, effects choreography, contact-frame inspection, slow motion and continuity across cuts.
- Live game worlds: rate-limited collision and rigid-body simulation with game-appropriate stable fixed steps; selectively baked hero effects.

### 3. Mathematical contracts and standards

- Rigid motion: (m\mathbf{a}=\sum\mathbf F), and rotational dynamics around the center of mass use inertia tensor and applied torque. A simple isolated motion budget checks kinetic (\frac12 m\|v\|^2), gravitational potential (mgh), angular momentum and accounting for dissipation/impulses.
- Semi-implicit Euler example: `v += (force/mass)*dt; position += v*dt`; this is a minimal deterministic learning/reference integrator, **not** a replacement for contact solvers or proof of global energy conservation. Explicit schemes may destabilize at excessive `dt`.
- Collisions: broadphase candidate generation → narrowphase contact geometry → manifold/constraint solving → post-step contact diagnostics. Continuous collision detection (CCD) or substepping is needed for fast/small objects to mitigate tunneling.
- Cloth: mesh mass nodes and stretch/bend/shear constraints, pinned vertices, body-to-cloth and self-collision, friction and damping; measure interpenetration, over-stretch and temporal jitter.
- Fluid/gas: domain bounds, spatial/temporal resolution, mass/volume accounting, boundary/obstacle velocities and cache seeds; rendered smoke is not a guarantee of mass-conserving transport.
- Coordinate and interchange contract: meters, kilograms, seconds, handedness, frame rate/timecodes, rest transforms, collider scale and gravity vector explicit. Pixar OpenUSD Physics standardizes baseline rigid body representations, not cross-solver behavioral equivalence.

### 4. Original research and authoritative guides

Official Blender 5.2 manual covers rigid-body world/collisions, cloth caching and fluid gas/liquid domains. OpenUSD `UsdPhysics` describes rigid bodies, constraints and contact properties for portable scene descriptions. Upstream Bullet, Jolt and NVIDIA PhysX document different real-time collision/rigid solvers; Blender developer cache proposal explains sequential-time nature and cache invalidation needs. The physics subareas are broader than these inspected technical sources: full Navier–Stokes numerics and deformable-body convergence literature remain deep-research work.

### 5. Existing implementations and architecture lessons

| External implementation inspected | Strength useful to MGR | Limit / evidence depth |
|---|---|---|
| Blender physics and Mantaflow-backed domains | Integrated offline cloth/rigid/liquid/gas workflows, scene animation, caches and render output | Official manual and feature overview only; Windows execution/quality not run in this research packet |
| Jolt Physics | Multicore rigid-body collisions, game-focused C++ with optional JS/WASM bridge | Upstream README/license; behavior, speed and DLL builds not independently benchmarked |
| Bullet Physics | Real-time rigid collision and dynamics; C++ and Python ecosystem | Upstream README/LICENSE; API, solver determinism and current dependency tree not fully audited |
| NVIDIA PhysX | Mature broad real-time engine and extensions; CPU/GPU alternatives | Official docs/source license metadata; **component-specific licensing differs** and GPU path availability varies |
| Taichi | Python-accessible high-performance numerical kernels, cross-hardware potential | Upstream README/license; not a ready turnkey cloth/fluid studio replacement |
| OpenUSD Physics | Scene-level interchange for bodies, colliders and constraints | Schema specification, not a simulator or guarantee two engines replay identically |

### 6. Models and solver families

- Rigid: sequential impulses/constraint solvers, contact manifolds, CCD, convex hulls vs high-detail triangle colliders; never equate a visual mesh with a stable collision proxy.
- Cloth: mass-spring, position-based dynamics (PBD/XPBD), implicit integration; choose by stiffness, performance and numerical stability after testing.
- Liquids: grid/FLIP/PIC, volume/level-set style surfacing; expensive at high resolution. Smoke/gas: grid advection/pressure, buoyancy and temperature.
- Optional AI enhancement: learned motion prior can propose poses or parameter guesses; it cannot establish physically valid collisions or conserve energy by appearance alone.

### 7. Datasets and reproducible scenes

Canonical MGR-authored fixtures should be generated from geometry and typed state instead of downloaded copyrighted scenes: cube freefall onto plane; projectile into thin target; two-ball head-on collision with known masses/restitution; friction slide; thirty-cube stack; pendulum/chain; pinned hanging square cloth; draped coat-to-rig collision; fluid fill/drain boundary case; smoke plume with obstacle; portal/gravity inversion director rule. Save scene input/seed, solver version, frame state digest, expected invariants and video contact sheets. External benchmarks/scene assets need independent rights check before vendoring.

### 8. Licensing and commercial rights

- Blender source is GPL; using Blender as an independent content creation tool is different from embedding/relinking GPL source into a proprietary core. Packaging and program-derivative questions require review. The underlying `.blend` scene/assets have their own ownership and asset provenance.
- Jolt upstream declares **MIT**; Bullet upstream declares **zlib** with folder/third-party exceptions. Both are promising comparison engines, subject to pinned-version notice verification.
- PhysX repository root states **BSD-3-Clause**, while some nested PhysX documentation states **Apache-2.0** and GPU binaries have separate conditions. Treat exact component/revision rights as **unresolved**, not a universal license.
- Taichi upstream declares **Apache-2.0**. OpenUSD code and physics schema licensing must be audited by pinned revision before copying implementation. No upstream code is copied here.

### 9. APIs, integration and interchange

Use Blender Python (`bpy`) inside Blender for authored simulation jobs and cache baking. External MGR worker launches a project-local Blender background process with explicit file paths and deadline, then reads validated frame states and rendered contact sheets. Scene input carries typed `SimJob`, `WorldLaw`, `BodyState`, `MaterialPhysics`, `Collider`, `Constraint`, `EffectEvent`, `CacheManifest`, `QualityReceipt`; write adapter interfaces before selecting Bullet/Jolt/PhysX. OpenUSD physics schemas are a candidate exchange layer, with fallback to an MGR manifest when cloth/gas semantics do not round-trip.

### 10. MGR-native inventions

1. **MGR Motion Truth Ledger:** stores per-frame event causality, impulses, energy account and why each violation is allowed.
2. **MGR Fantasy Lawsmith:** a director can declare “gravity rotates for 36 frames inside this sphere,” with trigger, spatial boundary, priority, rollback and continuity rules.
3. **MGR Contact Guardian:** automatically detects interpenetration, tunneling, limb/garment collisions and improbable floating feet; blocks export or records owner override.
4. **MGR Simulation Twin:** runs budget CPU simplified world alongside a hero-quality offline bake and flags diverging silhouette/contact landmarks.
5. **MGR Chaos Rehearsal:** varies timesteps, masses, velocities, light/camera views and mesh resolution to expose brittle simulations before rendering expensive final frames.
6. **MGR Physics-to-FX Director:** converts impulses/collisions into authored dust, sparks, cloth motion, camera shake and sound with timing constraints; avoids duplicated effect triggers.

### 11. Hardware and runtimes

CPU handles compact rigid-body scenes, analytic trajectories and validation; larger collider counts, fluid grids, volumetrics and high-resolution cloth can become memory/compute heavy. GPU may accelerate particular solvers/renders but **is not required for every 3D simulation**. Some GPU solvers/compiled binaries require specific drivers. Validate Windows Blender version, CPU/GPU/RAM, per-scene frame counts, cache size, frame rate and average/P95 wall time; no benchmark or local machine inspection was performed in this research packet.

### 12. Cost and scheduling

No compulsory vendor API fee for a native deterministic test harness. Costs: developer time, licensed assets, labor on collision proxy authoring, hardware electricity, cache/storage, artist review, and render/simulation retries. Cost metric is **accepted shots/interactive scene minute**, including failed bakes. Model three tiers: `preview` low resolution + short horizon; `final` stable substeps and baked cache; `live` fixed time budget with budgeted body count and graceful degradation. Do not invent dollar or FPS estimates without running tests.

### 13. Failure modes and response

| Failure | Source | Required gate |
|---|---|---|
| Fast object tunnels through wall | Step too large, discrete collision only | CCD or finer substeps; swept path check |
| Contact stack explodes/jitters | Poor solver parameters, collider scale, contact margin | Solver convergence/stability receipt and stress test |
| Energy grows in isolated system | Numerical error/unmodeled actuation | Bounded energy drift or explicitly logged outside impulse |
| Cloth pierces Tevin's arm/coat | Rig collision proxies, thin fabric, timestep/self-collision | Multi-frame garment/body interpenetration judge |
| Smoke/liquid leaks container | Coarse voxels/incorrect boundaries | Mass/volume, boundary and topology validity diagnostics |
| Character/world size mismatch | cm/m or kg mismatch | Typed units, import-scale checks, invariants |
| Changing mesh with stale baked cache | Cache not invalidated | Hash input asset/material/solver config and invalidate dependent bake |
| Nonrepeatable shot/physics | Floating-point order, random seeds, GPU, variable timestep | Seed and binary versions; tolerance-defined replay; do not promise bit-exact cross-hardware behavior |
| Magic effect breaks continuity | Undeclared alternate world law | Explicit exception rule and before/after state transition |
| Simulated objects are visually plausible but physically wrong | Appearance-only judge | Numerical truth gate plus unseen-view render checks |

### 14. Evaluation metrics

Track: collision penetration depth/fraction, missed CCD contacts, solver crashes/NaNs, kinetic + potential energy drift when applicable, linear/angular momentum before/after isolated impacts, drift over fixed replay, cloth stretch percent and contacts per frame, fluid total mass/volume error when method supports it, voxel resolution, sample/substep count, memory, bake size, throughput FPS (sim-only vs rendered), visual silhouette temporal consistency and owner approval. Thresholds below are **MGR test targets**, not scientific certification: analytic gravity trajectory within 1% over 120 fixed steps, zero observed wall tunneling in thin-target stress set, no NaN/inf, stable 30-body pile for 10 seconds, all declared magic effects have event log, 100% cache dependency invalidation after a material/body change. Physics engine tolerances and contact thresholds must be calibrated by case.

### 15. MGR Forge placement and dependency boundaries

Canonical state sits in `forge` native domain contracts (future `simulation/` modules by owner architecture review) while Blender adapters, real-time backends and optional accelerated kernels stay separate. `WorldLaw` cannot overwrite base units or scene identity. Visual Judge may check camera/appearance; numerical physics authority comes from per-step records and ground truth. The director authoring interface may request cinematic impossibilities but every override is versioned and testable. Existing source paths should be inspected before creating files to avoid duplicate/conflicting registries.

### 16. Acceptance tests needed before verified delivery

1. **Analytical gravity:** fixed `dt`, no drag, finite-mass body, compare position and velocity against closed-form (p(t)=p_0+v_0t+\tfrac12gt^2); log integrator and error tolerance.
2. **Collision/restitution:** equal masses, near-elastic head-on, compare momentum and total kinetic-energy budget within method tolerances; perfectly inelastic loses kinetic energy appropriately.
3. **CCD:** fast sphere must not pass through thin collider for documented permitted speed/step size; prevent post-step deep penetration.
4. **Rotational invariants:** fixed rigid transforms retain orthonormal basis/unit quaternion norm within tolerance; zero-force angular behavior interpreted with inertia.
5. **Cloth:** pin corners, drop over animated proxy, check pin drift, max stretch, body penetration and self-collision over whole shot.
6. **Fluids:** unit-scaled domain, obstacle, controlled inflow/outflow; evaluate leakage, mass/volume and divergence with method limitations recorded.
7. **Replay:** run identical seed+inputs twice and compare numeric trajectories within documented tolerance; fail cache when collider topology/physics config changes.
8. **Magic:** authored gravity inversion has explicit start/stop, affected body set, causality record and repeatable return to ordinary gravity; no silent global side effects.
9. **Visual check:** render 4+ cameras over temporal sequence and inspect contact clipping/silhouette; never treat one good frame as a pass.
10. **Budget:** record CPU/GPU/RAM/cache bytes and wall time on Time's Windows Blender rig; mark benchmark pending until machine-run receipt exists.

## Next-build directive, with no false completion claim

Extend the current geometry/visual checks through a **MGR Motion Truth** analytical fixture suite and a typed adapter contract. Then wire Blender background-cache orchestration, collision+cloth verification, deterministic replay and MGR Fantasy Lawsmith event application. Benchmark Bullet/Jolt only where needed for interactive scenes; keep cinematic liquid/gas in offline baking until performance proves a live path. This avoids rebuilding complex physics solvers while still producing an MGR-owned product layer.

## Remaining research depth (explicit open items)

- Full code-level examination and pinned releases of Blender's actual cloth, rigid-body and gas/liquid solvers; instrument cache invalidation on Windows.
- Peer-reviewed comparison of fluid algorithms, PBD/XPBD/implicit cloth error bounds and conservations across solver families.
- License matrix by specific PhysX submodule/binary, Bullet optional extras and dataset asset rights.
- Runtime benchmarking and numerical-vs-render fidelity across different frame rates and scene complexities.
- Cross-engine round-trip conformance test of MGR state manifest and OpenUSD collision/constraint semantics.
