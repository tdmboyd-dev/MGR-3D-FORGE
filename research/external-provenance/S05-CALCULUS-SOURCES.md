# S05 — External source provenance: calculus and continuous motion

**Purpose:** Keep all borrowed facts, interfaces, and open-source evaluation outside the MGR-native design contract. The production feature is **MGR Continuous Motion Guardian**, not a rebranded external product. Checked 2026-10-25. Links are primary documentation and source repositories; verification levels are explicitly distinguished from execution.

| Primary source | Inspected capability / relevance | Verification level | Native use, limitation, or follow-up |
| --- | --- | --- | --- |
| [SciPy `solve_ivp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) | IVP ODE integrators, RK23/RK45/DOP853 for non-stiff systems and Radau/BDF for stiff systems; dense output and error tolerance concepts | Official API documentation reviewed; no runtime benchmark | Base analytic solver comparison and configurable numerical error gate. Stiff/nonstiff classification and performance require workload-specific tests. |
| [SciPy `Slerp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Slerp.html) | Quaternion rotation interpolation with constant angular velocity along shortest path | Official API documentation reviewed; not executed | Reference for camera/joint rotation tests; cannot infer contact or anatomical correctness from quaternion continuity. |
| [Blender FCurve API](https://docs.blender.org/api/5.2/bpy.types.FCurve.html) | Keyframe curve evaluation and native animation curve handling | Official versioned API reviewed; Windows Blender evaluation not executed in this research packet | Sample evaluated camera/bone transforms and compare with Forge contract. Bezier behavior must be tested, especially overshoot. |
| [Blender keyframe introduction](https://docs.blender.org/manual/en/5.2/animation/keyframes/introduction.html) | Keyframe interpolation and animation process | Official manual reviewed | Documentation bridge; not evidence of complete animation rigs. |
| [Blender animation editors](https://docs.blender.org/manual/en/5.2/animation/animation_editors.html) | Timeline and graph editing workflows | Official manual reviewed | Human-review workflow for rejected motion. |
| [Godot 4.4 physics interpolation](https://docs.godotengine.org/en/4.4/tutorials/physics/interpolation/physics_interpolation_introduction.html) | Separates fixed physics ticks from visible interpolated transforms | Official engine documentation reviewed | Support dual clocks and interpolation receipts; Godot-specific semantics must not be copied as a cross-engine guarantee. |
| [Godot 3.5 physics interpolation](https://docs.godotengine.org/en/3.5/tutorials/physics/interpolation/using_physics_interpolation.html) | Older implementation guidance on smoothing physics/render updates | Official historical documentation inspected | Historical comparison only; do not use stale API calls on Godot 4.4. |
| [Unity 6 fixed updates](https://docs.unity3d.com/6000.1/Documentation/Manual/fixed-updates.html) | Different schedules for rendering updates and fixed physics updates | Official manual reviewed | Independent confirmation of the fixed-tick design concern, not evidence of identical engine behavior. |
| [Unity Rigidbody interpolation](https://docs.unity3d.com/6000.0/Documentation/Manual/rigidbody-interpolation.html) | Interpolation/extrapolation and smoothing of physics body visibility | Official manual reviewed | Negative tests for teleport, lagged frame presentation and collision/render mismatch. |
| [Taichi stable-fluid example](https://github.com/taichi-dev/taichi/blob/master/python/taichi/examples/simulation/stable_fluid.py) | Public implementation example for grid-based fluid numerical simulation | Source path identified; **not audited, executed, or licensed independently** | Possible experiment fixture for numerical diffusion/performance; no source vendoring until dependency and asset licenses verified. |
| [Taichi MPM example](https://github.com/taichi-dev/taichi/blob/master/python/taichi/examples/simulation/mpm128.py) | Public material-point-method example | Source path identified; **not audited or executed** | Optional deformable-material experiment, not needed for camera/rig MVP. |

## Direct mathematical principles to verify in Forge

1. **Derivative-aware trajectory:** positions sampled as a function of timestamps; finite-difference velocity and acceleration need explicit endpoint schemes and uneven-timestep support. Sampled derivatives are estimates, not proof of true curve derivatives.
2. **Interpolation:** a linear segment gives constant velocity but abrupt joins; `smoothstep(u)=3u²−2u³` makes endpoint velocity zero; `smootherstep(u)=6u⁵−15u⁴+10u³` also makes endpoint acceleration zero. These functions do **not** impose physical speed, acceleration, jerk or obstacle clearance limits by themselves.
3. **ODE integration:** explicit Euler is low cost but can drift badly; semi-implicit/symplectic Euler often improves boundedness for simple mechanical systems; adaptive higher-order Runge–Kutta improves local truncation error for smooth nonstiff systems; stiff motion may demand implicit methods. Solver choice must be empirically verified for each simulation class.
4. **Rotations:** use shortest-path normalized quaternion interpolation and explicit angular rates, while retaining handedness, units and world/local transforms; a visually smooth rotation can still clip scenery.
5. **Fixed-tick simulation:** store previous and current physical states and interpolate presentation state. Do not advance canonical physical state by arbitrary display frame durations; set rules for cuts, teleports and resets.
6. **Render timing:** shutter interval and motion blur require samples across exposure time, not only a single center-frame pose; motion blur should not hide discontinuity errors.

## Rights and scope boundary

- Underlying calculus identities are general mathematical knowledge; implementation choices remain MGR-native. External source code or datasets are **not** transplanted into Forge by this research.
- Blender, SciPy, Godot, Unity and Taichi have distinct software terms. Documentation visibility does not authorize unrestricted copying. Before importing any source implementation, inspect exact repo revision, license, notices, transitive dependencies and commercial redistribution terms. In particular, engine source availability is not equivalent to open-source permission.
- Public motion datasets such as AMASS, Human3.6M and LaFAN1 are only candidate leads. No dataset rights, consent, subject likeness use, or commercial fitness has been verified; keep them blocked until rights review.
- There are no sourced measured prices, elapsed generation times, GPU memory budgets, or physical quality benchmarks here. For simple kinematics and sampling, CPU execution is technically plausible; expensive cloth/fluid/particle scales need measured CPU/GPU tests before making a GPU-free claim.

## Evidence needed before acceptance

- Version-pin each dependency and environment (Blender build, Python/SciPy versions, GPU/CPU hardware), collect reproducible fixture files and original command logs.
- Compare analytical linear, ballistic and harmonic trajectories against implemented numerical methods over decreasing timesteps, reporting convergence, positional error and mechanical energy drift.
- Test camera cut/teleport, 180° quaternion turn, zero-duration movement, NaN/Inf data, duplicate timestamps, variable FPS, non-uniform key spacing, extreme scene scale and rotation wrapping.
- Independently inspect Blender-evaluated transforms and real rendered frames from several viewpoints. Identical-image matching does not establish 3D geometry/pose continuity.
- Record runtime percentiles, memory, platform costs, exit codes and measured export/reimport differences. Mark unsupported features **unknown**, never passed.

## References by intended engineering area

- **MGR timing and motion source:** `forge/director.py` (`ease_fraction`, `sample_motion`) and `forge/animation.py` (pose/arm proportional guards). Their present functionality is a deterministic geometry baseline, not an all-purpose physics solver.
- **Planned native consumer:** `forge/motion_guardian.py`, additive contract proposed in `research/chapters/S05-CONTINUOUS-MOTION-MATH.md`.
- **Primary mathematical tests:** smoothstep analytic derivatives, quaternion orientation metrics, timestep convergence, collision/contact assertions, shutter sampling and numerical stability.

**Provenance confidence:** high for linked documentation descriptions; moderate for design inferences until built; unknown for third-party data rights, benchmark performance, actual Forge integrations and project-wide production readiness.
