# S20 — External provenance: relativity, quantum science, higher dimensions

**Inspected 2026-10-25.** These primary research/education sources inform the independently authored MGR Reality Boundary Lab. A browsed explanation is not proof of scientific simulation. No third-party code, media, dataset or model copied; no math/physics runtime benchmark carried out.

| Primary source | Sourced facts and practical value | Inspection level | MGR disposition and limit |
| --- | --- | --- | --- |
| [Einstein Online: Spacetime](https://www.einstein-online.info/en/spacetime/) | Physical spacetime, gravity/curvature and causal role of light propagation | Foundational institutional explanation reviewed | **STUDY** spacetime contract; pedagogical source, not full numerical GR solver. |
| [Einstein Online: Light cones](https://www.einstein-online.info/en/explandict/light-cone/) | Causal possible/impossible event influence regions | Reference reviewed | **ADAPT** scientific visualization/causality rules, not proof of FTL effects. |
| [Einstein Online: Light deflection](https://www.einstein-online.info/en/Light_deflection/) | Light traveling on geodesics in curved spacetime | Institutional explainer reviewed | **STUDY** ray-based lensing; robust metric/geodesic solver remains unbuilt. |
| [Einstein Online: Geodetic precession](https://www.einstein-online.info/en/spotlight/geodetic_precession/) | Four-dimensional spacetime curvature and observable precession context | Institutional article reviewed | **STUDY** distinguish real physical 4D spacetime from 4D Euclidean geometry. |
| [NASA Hubble gravitational lenses](https://science.nasa.gov/mission/hubble/science/science-behind-the-discoveries/hubble-gravitational-lenses/) | Actual gravitational lensing magnifies/distorts more distant objects | NASA explainer and images identified | **ADAPT** visual reference only; image licensing/credits checked before reuse. |
| [NASA gravitational lensing diagram](https://science.nasa.gov/asset/webb/gravitational-lensing-diagram/) | Ray-geometry interpretation of foreground mass/lens distortions | NASA illustration description reviewed | **STUDY** baseline for artistic lens shader, not exact numerical benchmark. |
| [NASA gravitational microlensing animation](https://svs.gsfc.nasa.gov/20242) | Educational visualization of lensing predicted from GR | NASA visualization catalog inspected | **STUDY**, not imported or licensed for redistribution. |
| [IBM Quantum basics](https://quantum.cloud.ibm.com/learning/en/courses/use-a-qc-today/quantum-mechanics-basics) | Quantum state amplitudes, superposition, gates, measurement and probability | Official educational lesson reviewed | **ADOPT scientific labeling**; quantum circuit ≠ ordinary geometry engine. |
| [IBM Quantum information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information) | Measurement yields classical outcomes, state amplitudes affect outcome probabilities | Official lesson reviewed | **STUDY** for toy quantum visualizations. |
| [IBM multi-system quantum information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/quantum-information) | Measured probability from amplitude magnitude squared | Official lesson reviewed | **ADOPT toy probability normalization test**; physical noise and full simulation excluded. |
| [Wolfram MathWorld: Hypercube](https://mathworld.wolfram.com/Hypercube.html) | n-dimensional cube and tesseract projection mathematical context | Reference reviewed | **ADOPT mathematical idea**, reimplement independently. |
| [Wolfram MathWorld: Hypersphere](https://mathworld.wolfram.com/Hypersphere.html) | 3-sphere embedded in four Euclidean dimensions | Reference reviewed | **ADOPT analytic fixture**, no source code to vendor. |
| [Wolfram MathWorld: Four-dimensional geometry](https://mathworld.wolfram.com/Four-DimensionalGeometry.html) | 2D/3D/4D shape relationships | Mathematical reference reviewed | **STUDY** space-dimension taxonomy. |
| [Wolfram MathWorld: Stereographic projection](https://mathworld.wolfram.com/StereographicProjection.html) | Mapping higher-dimensional spherical geometry into lower-dimensional coordinates, with projection singularity considerations | Reference reviewed | **STUDY** candidate projection method; exact 4D implementation must be derived/tested. |
| [Blender 5.2 Geometry Nodes manual](https://docs.blender.org/manual/en/5.2/modeling/geometry_nodes/index.html) | Geometry operation graph baseline, procedural effects | Official app documentation reviewed | **ADAPT** Blender execution adapter. No claim that Blender has native general 4D geometry support. |
| [Godot 4.4 spatial shaders](https://docs.godotengine.org/en/4.4/tutorials/shaders/shader_reference/spatial_shader.html) | Spatial shader vertex/world-space transforms | Official 4.4 docs reviewed | **ADAPT** fragment/vertex illusion presentation when runtime chosen. |
| [CERN Geant4 scope](https://geant4.web.cern.ch/about/) | Particle passage through matter, geometry and interactions | Official toolkit description reviewed | **STUDY ONLY**; not a 3D game world renderer. |
| [CERN Geant4 developer guide](https://geant4.web.cern.ch/documentation/pipelines/master/bftd_html/ForToolkitDeveloper/OOAnalysisDesign/Geometry/geometry.html) | Geometry hierarchy, navigation and transport calculations | Official source docs inspected | **STUDY** rigorous geometry correctness patterns; no Geant4 code adoption. |

## Key science-versus-creative boundaries

1. **4D Euclidean mathematics is well-defined and useful for visual art.** Its fourth coordinate `w` is another spatial parameter; rotation/projection is directly implementable with matrices. In a 3D projection, different source 4D states can collapse to identical visible shapes, so reverse projection is not uniquely solvable without more evidence.
2. **Relativity uses spacetime rather than one extra freely interchangeable spatial axis.** A black-hole lensing visual can imitate observable distortions but exact predictions require mass model, metric, numerical integration, frequency/redshift and observer conditions. A generic image warp is an **approximation** or **fantasy** effect.
3. **Quantum physics is real but misapplied easily.** Complex amplitudes, observables and measurement probabilities do not imply the universe can be reverse-engineered from a 2D image, nor that quantum computers remove graphics hardware needs. Classical sampling can illustrate quantum probabilities, with truth labels.
4. **String theory and additional spatial dimensions remain outside validated everyday rendering requirements.** Do not attach speculative physical claims to ordinary geometric projection or market MGR as discovering physical extra dimensions.
5. **Scientific geometry toolkits are not game engines.** CERN Geant4 is for particle-transport simulation; its robustness lessons can inform MGR spatial validation without transplanting its mission or code.

## Source risks and licensing

- Research explanations and mathematical statements can inform new implementation; exact photos, diagrams, animations and software may have rights notices and attribution requirements. Check each NASA/SVS media item and institutional figure before inclusion.
- Blender/Godot/CERN tooling licenses, sample code and third-party dependencies must be pinned and reviewed before code vendoring or redistribution. This research downloads none.
- Avoid including false claims of NASA/CERN/IBM partnership, experimental verification, high-accuracy scientific simulation or quantum speed advantage.
- Accessibility: dramatic perspective shifts, optical flow, flashes and portal motion can trigger discomfort or photosensitivity; enforce lower-motion settings and independent review.

## Independent calculations and honest acceptance protocol

**Initial pure mathematics:** Construct vertices `(±1,±1,±1,±1)` (16 combinations) and connect points differing in exactly one coordinate (32 edges). Apply a set of standard 4D Givens plane rotations. Assert `R.T @ R` approximately identity, `det(R)` approximately +1 and pairwise length preserved **before** projection. Orthographically map 4D to XYZ; expect multiple distinct source points to share projection where only `w` differs. For perspective 4D projection, reject/clip values close to its `d-w=0` singular plane.

**Physical approximations:** Zero-lens-strength input must preserve the original ray direction/image; lensing parameter changes should yield finite, monotonic deflection in the defined simplified model. If accuracy is claimed, test a documented physical approximation and numerical tolerance, not visual similarity alone. With quantum two-state fixture, ensure probabilities are nonnegative and sum to one and compare seeded sampling to binomial uncertainty.

**Playable world:** For portal connectivity, model graph edges of two scene sectors and verify coordinate/body orientation continuity on crossing, bounded recursive rendering, physics/camera agreement and deterministic return traversal. In VR, require comfort and reduced-effect mode.

**Not performed:** actual 4D kernel code, Blender render, NASA numerical-lensing calibration, Geant4 physics run, quantum hardware execution, user VR testing, source-binary audit, CPU/GPU benchmark or third-party media-rights clearance. These are executable gates for future build packets.

**Recommendation:** `MGR-NATIVE` 4D projection and portal effects; `STUDY` precise GR/quantum scientific engines; `REJECT` unsupported claims that quantum/higher-dimension ideas bypass classical 3D math or replace GPUs.
