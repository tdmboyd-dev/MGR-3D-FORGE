# S20 — MGR Reality Boundary: Higher-Dimensional Worlds & Scientific Illusions

**Status:** Sourced 16-field MGR-native research/specification packet (2026-10-25), **not implemented**. External source attributions and precise verification levels are segregated into `research/external-provenance/S20-PHYSICS-SOURCES.md`. This subject is scientifically useful for exotic world geometry and visual storytelling, but *most production 3D realism does not require quantum physics, relativity or string theory*.

## Executive decision

Build an **MGR Reality Boundary Lab** as an optional mathematically explicit effect authoring tool—not as the base scene engine. The early shippable slices are 4D-to-3D projection, topology-altering portals/world connectivity, curved-surface navigation, physically inspired gravitational lensing and controlled quantum-inspired visual motifs. Clearly label each work mode `scientific`, `approximate`, or `fantasy`. Claims like real quantum computation, true higher-dimensional physical worlds, or scientifically accurate black holes require deeper numerical physics and validation.

## 1. Definition

Four different objects must stay separate:

- **3D Euclidean game space**: ordinary x,y,z scene positions plus time-controlled animation.
- **4D mathematical Euclidean objects**: points `(x,y,z,w)`, rotations in coordinate planes, hypersurfaces like a 3-sphere, and 4D→3D projection/slicing for display.
- **3+1-dimensional spacetime**: physical 3-space plus time with Lorentzian metric, causal structure, and potentially curved spacetime. This is **not** the same as arbitrary four interchangeable spatial dimensions.
- **Quantum states**: complex vector amplitudes and probabilistic measurement outcomes; these are not intrinsically hidden 3D meshes, a free GPU shortcut, nor a way for a computer to “see beyond the image.”

For authored fantasy, dimensions and portals may be fictional and visually compelling; do not present them as measured reality.

## 2. Production use

MGR-world possibilities:

1. A visible tesseract rotates and is sliced; its apparent topology changes as the 4D object projects into the 3D scene.
2. The player passes through a room boundary and arrives in a space with non-Euclidean connectivity (connected interiors bigger than outside); implement multiple Euclidean scene chunks connected via portals rather than pretending a simple mesh is globally non-Euclidean geometry.
3. Black-hole-inspired screen-space gravitational lensing bends background appearance; exact astrophysical ray tracing optional.
4. Fantasy spell/illusion system controls geometric warps, time offsets, mirrored spaces, impossible stairs, dimensional echoes, higher-dimensional shadows and directed audiovisual cues.
5. An education/science explorer shows both mathematical 3D projection and actual physical assumptions, with uncertainty labels and interactive controls.

## 3. Standards and mathematical contracts

- Coordinates: units, handedness, transforms, projection convention, field-of-view, near singularity handling, time semantics and deterministic parameter seeds must be explicit.
- For Euclidean 4D positions `p4 ∈ R^4`, an orthographic projection is a 3×4 matrix `P`; `p3=P R4 p4` where `R4` is an orthogonal 4×4 rotation. A perspective-like 4D projection can use `p3=f * xyz/(d-w)` only outside a declared near-plane; division by zero is invalid.
- A 4D Euclidean rotation may occur independently in coordinate planes (XY, XZ, XW, YZ, YW, ZW); compose orthogonal transforms and test preservation of 4D distances preprojection.
- Physical spacetime intervals use a Lorentzian metric and consistent units/sign convention, e.g. with convention `(-,+,+,+)`, `ds²=-c²dt²+dx²+dy²+dz²`. A general-relativity geodesic requires a metric/connection and initial conditions, not arbitrary scene distortion.
- Scientific particle/quantum representations require state amplitudes, normalized probabilities, explicitly defined observables or validated Monte Carlo sampling. No equation is proof that an effect reproduces experimental physics unless benchmarked against accepted physical solutions.

## 4. Foundational research and algorithms

Applicable mathematics: projective geometry; matrix groups SO(4), SO(3,1); manifolds, charts, geodesics and metrics; differential geometry; numerical integration; optical ray tracing and lensing; stochastic simulation; probability amplitudes. Mathematical demonstrations have exact invariants, unlike pure artistic postprocess distortions. Relativity helps specialized science-fiction shots (redshift, time dilation, gravitational lensing), but does not govern ordinary character rigs or physically based materials. Quantum effects in visual narratives are typically artistic simulations; actual quantum hardware is neither needed nor established to improve polygon rendering.

## 5. Open implementations / study targets

- Blender Geometry Nodes and `mathutils` for deterministic projection meshes, fields, deformation and rendered evidence.
- Godot spatial shader/vertex transforms and depth-buffer postprocessing for world illusions and portal compositor candidates.
- Geant4 for **scientific particle transport in matter** and rigorous geometry modeling, not a production substitute for games rendering; deep integration unwarranted for routine magic FX.
- Mathematical software and scientific papers for SO(4), geodesic and lensing reference equations; choose independently coded small reference fixtures first.
- Ordinary game engine scene/portal rendering for navigable world transitions, with explicit collider and acoustic continuity tests.

## 6. Models

No trained AI model is required for deterministic 4D projection, portals, topological illusions or simplified lensing. Optional neural video/world models may inspire art but cannot prove scientific validity; their output often lacks coherent persistent 3D geometry. Actual quantum circuit simulators and quantum processors solve different problems, with significant noise and sampling constraints. Treat these as education/science visual inputs only, not required 3D-generation backends.

## 7. Data, fixtures and research corpora

MGR-owned analytic fixtures: hypercube with 16 vertices/32 edges, 3-sphere points on `x²+y²+z²+w²=R²`, 4D planar rotations, projection near-plane crossing, known sphere great-circle paths, ray-bending toy lens, graph/portal adjacency maps, controlled shader lensing grids, normalized two-state quantum toy probability table. External NASA lens imagery and CERN examples are educational comparisons only until media reuse rights/attribution are checked. Real astrophysics comparisons need source parameters, numerical methods and uncertainty; do not claim physical fidelity by eye.

## 8. Rights/ethics/scientific truth

Mathematical formulas are general scientific knowledge, but illustrations, NASA media, lab research code, visualization assets, brands and third-party datasets have their own terms. Use an explicit `scientific`, `approximation`, `fantasy` claim label in all native artifacts. Ensure accessibility (photosensitivity, motion sickness, disorientation, VR comfort, rapid pulsing) and user controls. Do not present quantum healing, paranormal claims, faster-than-light travel or higher dimensions as experimentally established.

## 9. APIs and providers

No paid API, GPU provider, quantum service or scientific simulation backend is required for the introductory effects. Local Python geometry+Blender/Godot shader can produce small demonstrations. Optional compute workers for high-resolution gravitational lensing/geodesics must be provider-swappable and cost-gated with reproducible input/receipt. Quantum/cloud backend costs are unscoped; do not claim they improve ordinary 3D renders.

## 10. Native design

Proposed additive engine capabilities (paths provisional):

```python
# Native design contract only; these symbols are not implemented yet.
effect = RealityEffect(
    kind="four_space_projection", mode="mathematical",
    inputs={"vertices4": hypercube(), "rotation_planes": {"xw": 0.4}},
    projection={"type": "orthographic", "matrix": "default_xyz"},
    seed=8964,
)
result = RealityBoundary.evaluate(effect)
proof = RealityJudge.check(result, invariants=["4d_length", "finite_3d", "topology"])
```

**MGR Reality Boundary Lab** parts: dimension-typed node graph; 4D geometry/projection kernel; portal/topology scene routing; lensing/screen warp shader adapter; explicit scientific assumption manifest; Reality Judge for mathematical invariants, perceptual quality and navigation safety; VR comfort/accessible reduced-effects preset; exportable evidence receipts. World canon stays 3D; higher-dimensional coordinates are stored as specialized mathematical source values and evaluated to ordinary 3D geometry/shaders. No canonical scene conflict.

Novel features to benchmark, not advertise as proven: **Dimensional Truth Lens** (toggle source 4D structure versus observed 3D projection and reveal depth/occlusion), **Reality Rules Editor** (artist changes spatial topology/metric under declared constraints), **Impossible Space Director** (camera/blocking-aware portal traversal choreography), **Causality Lock** (scientific preset checks time/order and fantasy preset marks rule exceptions), **Illusion Honesty Meter** (math/science/art levels and evidence for each effect).

## 11. Hardware/runtime

Small 4D projection and portal graph math is easily targeted at ordinary CPU workloads, while rendering and VR can need GPU acceleration. High-resolution geodesic path tracing/volumetric accretion disks or particle transport is much heavier; specific CPU/GPU and memory numbers require real benchmarks. A separate 4D spatial coordinate does not create free rendering capability. Numerically unstable metrics or near-projection singularities may produce extreme geometry; bound work and handle nonfinite values.

## 12. Cost and implementation order

Low-cost early path: independent Python linear algebra, Blender mesh export, a small deterministic tesseract scene with multiple views, and a separate portal room proof. High-cost later path: physically constrained relativistic lensing, real-time large-world portals with recursive renders, VR interactions and scientifically validated particle simulation. Research time includes choosing simplified versus exact equations, numerical integration accuracy, render budget and visual acceptance. No purchased datasets or providers assumed.

## 13. Failure modes

Confusing fourth space coordinate with time; invalid metric signature; superluminal mislabel; transformation matrix not orthogonal; 4D rotation changes lengths; projection division by zero; topology lost at singular perspective; self-intersecting projected geometry mistaken for original collision; portal physics/camera disagreement; infinite recursive portal renders; seam flicker; broken occlusion/lighting/sound; local player teleported with wrong orientation; incorrect energy/units in physical lensing; unstable geodesic solver; lensing shader called scientifically accurate without mass metric; quantum probability sums not equal one; claims that consciousness creates dimensions; VR nausea or flashing-sensitive exposure.

## 14. Evaluation

**Mathematical:** 4D rotation orthogonality `RᵀR≈I`, determinant ≈+1, distance invariant; projection has finite coordinates, reproducible output and known topology/connectivity; inverse/reprojection checks where defined. Scientific relativity mode checks metric and geodesic residuals against analytic simple solutions; simplified optical lens mode checked against declared approximation.

**Playable:** portal transition occupancy/pose preservation, no discontinuous collider or bad camera clip, recursive depth budgets, navmesh transitions, audio consistency, 24/30/60 presentation stability. **Visual:** multiple camera views, lensing grids and known identity silhouettes, clear differentiation of altered screen image versus actual geometry. **Safety:** motion comfort options, reduced flashing, opt-out and bounded transform speeds. Record CPU/GPU performance and quality independently.

## 15. Forge placement

Add-on world and FX layer, not a replacement for existing character, sculpting, illumination, S03 geometry, S04 transforms, S05 dynamics or S15 hardware admission. Input source geometry/material/world state remains canonical. A projection/portal effect emits ordinary 3D scene transforms, visuals and explicit collision/navigation adaptation with a trace. Director chooses shots; Renderer executes visual mapping; Visual Judge and Reality Judge independently verify math and perceptual output.

## 16. Acceptance tests

1. Generate canonical 4D hypercube topology (16 vertices, 32 edges); test graph degrees, boundary connectivity and deterministic source hash.
2. Rotate through all six coordinate planes; check orthogonality, determinant and 4D pairwise distance preservation, including random seed cases.
3. Orthographic 4D→3D projection and perspective mode: compare analytic fixtures; reject singular denominator or NaN/Inf; clip instead of blowing up world bounds.
4. Vary fourth coordinate and prove multiple distinct 4D sources can share identical 3D projection (non-invertible information loss); never hallucinate missing higher-dimensional data.
5. Render multi-angle Blender 4D projection sequence; verify exported mesh, editable scene and camera-space continuity.
6. Walk player/camera through portal room and back with preserved expected pose, velocity and reference scene identity; test recursive depth cap, occlusion and collisions.
7. Compare simplified lens shader with known straight-ray zero-mass/zero-strength baseline; parameter monotonicity, finite image coordinates and no shader crash.
8. Where physical relativity mode is claimed, compare against at least one analytic flat-spacetime case and a documented lensing approximation, log method, tolerance and uncertainty.
9. Quantum toy display: normalized state, total outcome probability approximately one, deterministic seeded simulation, sampled distribution within statistical confidence and explicit label not actual quantum computation.
10. Negative tests reject mistaken spacetime metric/type, non-orthogonal 4D rotation when orthogonality required, unstable geodesic, impossible lossless inverse projection and inconsistent scene/physics portal transforms.
11. Record real CPU/GPU performance, VR comfort access, reduced-effects and flashing behavior; prohibit claims on platforms not tested.
12. Independent render + scene export + human review for fantasy quality; classify all claims `scientific`, `approximate`, or `fantasy` in receipts.

### Recommendation

**Green-light geometry-based 4D projection and a portal-world prototype**, since both have clear mathematical contracts, easy synthetic fixtures and direct creator value. Build relativistic lensing as clearly labeled artistic approximation first, then scientific accuracy only if source model and target quality require it. Defer quantum hardware, speculative string dimensions and full general-relativistic simulation: no evidence they would improve the current MGR character/world pipeline enough to justify complexity.
