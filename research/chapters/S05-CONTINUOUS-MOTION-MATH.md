# S05 — MGR Continuous Motion Mathematics

**Owner:** MGR 3D Forge · **Research date:** 2026-10-25 · **Evidence maturity:** SOURCED + code-read analysis of existing MGR motion primitives; **not** a complete external source-tree audit, solver benchmark, or physically verified full-body motion system.

**The practical answer:** A moving 3D object is a time-varying transform, not just coordinates at two endpoints. Professional movement quality depends on displacement, velocity, acceleration, angular speed, skeletal and contact constraints, timestep strategy, error bounds, and how simulation frames become displayed frames. A motion curve can look smooth yet violate collision, momentum, foot contacts, or camera comfort. MGR must differentiate authored cinematic motion from dynamically simulated motion, and must label the evaluation level accurately.

## 1. Definition and mathematical foundation

- Position trajectory `p(t) ∈ R³`; velocity `v(t) = dp/dt`; acceleration `a(t) = d²p/dt²`; jerk `j(t) = d³p/dt³`.
- Rotation is not an XYZ position: use valid SO(3) rotation representations, normalized quaternions or matrices; angular velocity is distinct from translational velocity. Quaternion interpolation should follow the short arc when appropriate, guard antipodal representation, and verify angular step limits.
- Animation sampling: a continuous function `p(t)` is evaluated at discrete frames `t_n = n/fps`. Time-step or frame-rate changes must preserve intended physical duration.
- Dynamics: `dx/dt = f(t,x)`, e.g. positions and velocities from forces. Solving requires an explicit numerical method, accuracy tolerance, integration interval, and stability evidence. A keyframe interpolation is **not** a physical solver.

## 2. Real production use

- Camera direction: authored start/end points plus ease curves, camera focus, focal length and subject/screen-space continuity; optional physically based camera rigs and motion blur.
- Character rigging: joint trajectories constrained by bone length, hierarchy, joint limits, foot contact, IK, collision, and source identity continuity.
- Game movement: fixed-rate physics simulation and interpolated rendered state to avoid jitter when display FPS differs from physics frequency. Teleports/reset events must prevent interpolating across discontinuities.
- FX/particles: emission paths, advection through force fields, deterministic seeds, substeps, collisions, cache and playback; analytical sparkle motion is not smoke/fluid simulation.
- Cloth/rigid/fluids: validated solver domains, collision geometry, physical units, timestep/substeps and convergence/performance measurements; higher polygon counts do not cure unstable dynamics.

## 3. Standards and interoperable contracts

- MGR canonical SI units: meters, seconds, radians, and frames/fps in receipts. Explicit display/render resolution and frame range.
- No universal animation solver file format; chosen destination dictates GLB animation, USD timeline, Alembic caches, or native `.blend` action/constraint transfer. Each must be independently reimported or played to verify time and transforms.
- Motion contract MUST record coordinate system, local/world space, frame rate, start/end timestamp, interpolation family, velocity/acceleration bounds, seed, solver/inference provenance, and runtime compatibility.
- Source/project/frame-of-reference identity is mandatory: asset identity across animations is distinct from perceptual similarity of frame images.

## 4. Applicable research and math fundamentals

- Smoothstep `e(t)=3t²−2t³` for normalized `t∈[0,1]` yields zero endpoint velocity; acceleration is not zero at endpoints.
- Smootherstep `e(t)=6t⁵−15t⁴+10t³` yields zero endpoint velocity and acceleration; it can still have nonzero jerk and must be constrained for comfortable camera moves.
- A path `p(t)=p0+(p1−p0)e(t)` has speed proportional to `|e′(t)|`; changing its duration changes speed and acceleration with inverse time powers. An animation that was safe at 4 seconds may exceed speed limits at 0.5 seconds.
- Explicit Euler is cheap but error accumulates and some stiff or highly oscillatory systems are unstable. Symplectic and higher-order solvers have different error/energy/stiffness tradeoffs. Adaptive RK methods are useful for nonstiff smooth ODEs; implicit Radau/BDF are often better choices for stiff systems. **No solver family is universally best**, especially around collisions/discontinuous constraints.
- Acceleration and jerk can be approximated numerically using finite differences, but one-sided endpoint formulas and nonuniform sample intervals need their own derivation/QA.

## 5. Open implementations and code lessons

| Candidate | Specific useful behavior | What MGR may learn | What is not verified here |
|---|---|---|---|
| Blender 5.2 FCurves and interpolation | Keyframe curves and evaluated channels; Actions/slots version changes | Art direction separate from sampled playback truth | Full Blender 5.2 source internals, export parity |
| SciPy `solve_ivp` | Multiple explicit/implicit ODE solvers, events, tolerances and dense output | Solver selection, local-error control, reference benchmarks | Installed in Forge; production runtime performance |
| Godot physics interpolation | Fixed-tick positions interpolated for render frames, teleport-reset cases | Runtime display vs simulation clock separation | Full runtime code history; MGR engine integration |
| Unity fixed updates and Rigidbody interpolation | Different physics tick and render rates; fixed update backlog / jitter | Evidence why FPS alone is insufficient | Unity licenses/engine integration beyond docs |
| Taichi simulation examples | Fluid and material-method numerical kernels | Field simulation and CPU/GPU acceleration candidate | Stable-fluid numerical comparison, exact code/license audit |

**Internal source reality:** `forge/director.py` implements `ease_fraction(linear|smoothstep|smootherstep)` and samples 3D camera positions with bounded input count; `forge/animation.py` generates T↔A landmark clips using a deterministic arm-angle formula and guards some bone lengths. Camera movement and arm movement were independently observed in Blender evidence. These are currently a **kinematic starter**, not physical trajectories with velocity/acceleration/foot-lock/force validation.

## 6. Models and learned motion

- Deterministic interpolation/IK/physics do not require a neural model.
- Learned motion generation/retargeting may help realistic gait and choreography, but models need exact weights/license/data rights, skeleton conventions, speed/VRAM benchmarks, and contact/penetration evaluation. None have been selected, installed or verified for S05.
- Motion-capture footage, pose estimation, biomechanical priors and multi-sensor fusion are possible sources; all derived character identity/rights must stay separate from technical evaluation.

## 7. Datasets and reference scenes

- **MGR-native synthetic reference suite (recommended first):** constant-speed line, sinusoid, ballistic free fall, undamped harmonic oscillator, damped oscillator, 90° turn with quaternion orientation, character stance/foot plant, camera teleport and two interacting bodies. These can be authored, versioned and reproduced without external data rights.
- External human motion datasets (AMASS, Human3.6M, LaFAN1 and others) are **candidates only**. Their individual capture, redistribution, commercial use and subject privacy conditions must be checked before import; no unverified assumption of free commercial use.
- For fluid/smoke, analytically solvable fields and controlled benchmark meshes should precede expensive reference simulation datasets.

## 8. Licensing and provenance

- MGR-authored mathematical formulas, contracts and reference fixtures are independent code; mathematical principles are not exclusive proprietary product code.
- Dependencies must keep their own project licenses. Blender/Godot/SciPy/Taichi/Unity/other source terms differ. Do not paste external engine implementation into public Forge without checking the exact repository version, dependency license, redistribution obligations and asset/model licenses.
- Avoid publishing owner's private Tevin motion reference imagery, biometric traces or motion datasets into a public repository.

## 9. APIs/providers

- Start with local CPU math and Blender Python scene evaluation. Treat native game runtimes and physically based simulators as replaceable validation/execution backends.
- Optional learned motion/mocap providers are separate cost-approved adapters; **none** are bound into current S05 code.

## 10. Native MGR synthesis: Continuous Motion Guardian

**Contract (proposed):**

```json
{
  "schema": "mgr.forge.motion-guardian.v1",
  "asset_id": "approved-stable-asset-id",
  "space": "world_meters",
  "fps": 24,
  "motion_kind": "authored-kinematic",
  "samples": [
    {"time_s": 0, "position_m": [0, 0, 0], "rotation_xyzw": [0, 0, 0, 1]}
  ],
  "limits": {"max_speed_mps": 4, "max_acceleration_mps2": 8},
  "checks": {"finite": false, "duration": false, "kinematic_bounds": false,
             "bone_lengths": null, "collision": null, "foot_contact": null},
  "provenance": {"generated_or_measured": "generated", "solver": null},
  "status": "UNVERIFIED"
}
```

- Tier 1: pure CPU derivative/continuity validator consuming existing MGR camera/pose samples, strict finite values and monotonic times, max distance/speed/acceleration thresholds, normalized quaternion checks, unit labels.
- Tier 2: constrained procedural timeline with endpoint/hold, nonoverlapping cuts, velocity/acceleration limits and angle interpolation guard.
- Tier 3: contact/IK/collision and physically simulated backend with solver/caching receipts, per-scene budgets and a rollback strategy.
- Tier 4: render two independent viewpoints, test visual continuity, measure animation export/reimport, seek owner acceptance.

## 11. Hardware and runtime

- CPU-only interpolation, finite differences, quaternions and modest ODE fixtures are appropriate; no GPU prerequisite.
- Higher-detail cloth, fluid, neural motion and render evaluation may demand specialized CPU/GPU memory/performance. Benchmarks must separate simulation time, rendering time, number of degrees of freedom and scene complexity.
- Browser/game runtime requires frame budgeting. Deterministic fixed simulation ticks plus interpolation for display avoid coupling result quality to monitor FPS, but precise network sync is another domain.

## 12. Cost model

- First native math validators: no inference/API charge; CPU processing proportional to track sample count and joints/objects. Cost is developer/test effort and asset capture when needed.
- Physically simulated cloth/particles: cost grows with number of samples, constraints, collision checks and solver iterations/substeps. Capture cost and cached storage can dominate; benchmark actual target hardware.
- Never claim a universal 10× advantage from writing a different integrator. Measure duration, max error, quality/contact violations, runtime memory and target FPS against approved baselines.

## 13. Failure modes and risk controls

| Failure | Cause | Gate |
|---|---|---|
| Sudden camera/character jump | Wrong time units, key mismatch, timeline cut treated as interpolation | Segment shots and detect discontinuity; allow declared cuts only |
| Foot sliding / limbs stretching | Landmarks interpolated without contact and IK constraints | Bone lengths, contact intervals, joint limits and render checks |
| Energy explosion | Too-large timestep, explicit integration of stiff force | Bounded dt/substeps, stable integrator selection, numerical reference test |
| Collision tunneling | Motion travels farther than obstacle thickness between ticks | Swept/continuous collision or smaller dt; test high-speed negatives |
| Quaternion flip | Unnormalized, antipodal representation, Euler discontinuity | Unit quaternion checks, short-arc interpolation and angular continuity |
| Frame-dependent behavior | Physics updated at variable display FPS | Fixed-step simulation, timestamp interpolation, frame-rate invariance |
| Motion blur mismatch | Render shutter/time samples not aligned with track | Sample actual evaluated transforms and camera shutter settings |
| Hidden source/rights issue | Unverified motion dataset/captured body data | Provenance + commercial/privacy gate before training or distribution |

## 14. Evaluation and benchmarks

Metrics: (a) endpoint and timestamp error, (b) max/rms speed/acceleration/jerk, (c) bone length/foot contact violations, (d) angular speed spikes, (e) collision penetrations, (f) numerical trajectory error versus analytic/high-accuracy solution, (g) determinism/replay hash, (h) actual CPU wall time and memory, (i) user-visible frame judder, and (j) export-reimport animation drift.

Benchmark tracks at 24, 30, 60 and 120 FPS should describe the **same physical duration and trajectory**, not silently speed up the animation. Compare render samples and fixed simulation ticks separately. Errors should scale predictably under timestep refinement.

## 15. Placement and integration dependencies

- Native source: `forge/director.py` and `forge/animation.py` remain producers; new validator should be an additive `forge/motion_guardian.py` consumer, not an incompatible competing motion system.
- Cinematic Blender bridge should report actual evaluated frame transforms; existing receipt patterns can be extended with derivative stats.
- `forge/world.py` collision/proximity checks and existing geometry/character locks provide only partial constraints; do not claim physics unless a solver executes.
- World runtime needs fixed timestep, interpolation state, deterministic seeds and replayable cache separate from render FPS.
- F46 Motion Director, F39 rig/pose, F48 continuity, F55 elemental simulation, F67 FX Judge and S04 transform math depend on these contracts.

## 16. Acceptance tests required BEFORE production completion

1. Strict rejection for NaN/infinite/nonmonotonic timestamps; bool masquerading as numeric; zero/negative durations; impossible axis/unit metadata.
2. Constant-speed analytic line: exact position and derivative within tolerance; reparameterized sample counts produce same time-indexed samples.
3. Smoothstep and smootherstep: endpoint/velocity/acceleration continuity checked numerically or analytically with precise tolerances; limits still enforced at interior peaks.
4. Ballistic free fall and harmonic oscillator: validate against analytic positions/energies over increasing time spans and decreasing dt; record drift.
5. A sharp 90° camera change: detect overspeed/acceleration, expected smoothing, screen-space subject tracking and collision clearance.
6. Rig: lengths preserved across full reference pose suite, joint bounds, hand/finger coverage, foot contact, and no wardrobe intersections; report unknown without a full rig.
7. Interpolation across a declared cut or teleport **must be blocked** unless explicitly permitted; fixed-tick reset tested.
8. Blender 5.2.2: evaluate project animation at exact frames, compare to native sample receipt, render two or more independent viewpoints and preserve editable `.blend`.
9. GLB/USD/Alembic receiving systems: reimport and measure frame/rotation/world scale/pose fidelity before marking interoperable.
10. Benchmarks at multiple fixed physics ticks and variable rendered FPS, CPU/GPU resource budgets, rollback/retry and deterministic receipt.

### Research status / next move

**Completed this packet:** decomposed S05 into 16 decisions, inspected existing Forge motion modules and sourced primary Blender/Godot/Unity/SciPy documentation; identified test gates and MGR-native module contract. **Not completed:** production code, real dynamics solver, complete external source audits, motion datasets rights inspection, GPU/CPU hardware performance, full-body/cloth/FX simulation and target-game-engine acceptance.

**Immediate integration recommendation:** implement additive `forge/motion_guardian.py` validating time series and derivative thresholds, then test existing camera and pose tracks. This yields actionable correctness before costly simulation experiments, without blocking the concurrent S01–S04 mathematics/perception research.
