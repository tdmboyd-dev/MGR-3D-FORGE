# S19 — MGR Living Geometry and Nature Intelligence

**Owner:** Money Grind Religion. **Research date:** 2026-10-25. **Research state:** primary scientific literature and technical references reviewed. **Engineering state:** design/acceptance specified, **not built or verified** as a working biology simulator. External citations and licensing details are isolated in `research/external-provenance/S19-BIOLOGY-SOURCES.md` to protect MGR-native product canon.

## Plain-English verdict

Nature is not a random-object generator. A tree knows how to branch and compete for sunlight; a body grows with linked proportions and load constraints; a whole ecosystem changes as water, soil, weather and organisms interact. For Forge, we can build these principles into an original **MGR Living Geometry** engine that creates biologically *inspired* plants, bodies, animals, creatures, fungi/coral-like forms and evolving worlds. Every visual will be editable. Every simulation will distinguish “plausible art direction” from actual biological prediction. The fastest reliable track begins with deterministic CPU growth, measurable morphology, and staged ecosystem rules before claiming scientific realism or GPU-heavy dynamics.

## 1. Definition

Living geometry is shape constrained by growth rules, anatomical structure and environment through time. Key mechanisms: branching grammars (L-systems), differential elongation, allometry (body-part scaling changes with size/age), phyllotaxis (leaf/flower arrangements), tropisms (response to directional stimuli), self-organization, resource allocation, load-bearing/biomechanics, ecology and competition. **Morphology** is the observable form; **morphogenesis** is the process creating it; **simulation** must specify rules, units, inputs, time steps and limitations. A growth image is not an empirical scientific forecast by itself.

## 2. Production use

- Populate MGR worlds with forests, roots, vines, flowers, grasses, fungus-like structures, corals and fantastical hybrid ecosystems that evolve under time, terrain, sunlight and weather.
- Build creatures and character anatomy with plausible moving pivots, mass distribution, gradual changes over age, and intentional stylization without injury-like unnatural distortions.
- Create magical flora: growth/decay/rebirth can be cinematic, yet geometry remains spatially continuous, riggable and reversible.
- Teach/visualize environmental relationships and generate survival/interaction mechanics in future game worlds, while labeling models as simplified simulations.
- Produce repeatable worlds: seed plus recipe determines growth steps and geometry, with rich variations but no unexplained random changes.

## 3. Mathematical representations and standards

- Growth grammar: typed modules such as `Bud`, `Internode`, `Leaf`, `Root`, `Flower`, `Resource` with state (`age`, `length`, `radius`, `heading`, `vigor`) and rewrite rules, bounded generation count and deterministic pseudorandom seed. Brackets preserve branch state and a 3D turtle updates orientation/position.
- Geometry: generalized tubes along centerlines, tapered radii and leaf surfaces; branch junctions must maintain continuity, avoid degenerate triangles and preserve surface normal orientation. New meshes carry parent node IDs and generation IDs for evolution tracking.
- Growth laws: simple exponential/logistic/Gompertz or piecewise curves can be *art controls*, but never assert scientific prediction without species/calibration evidence. Units include meters, seconds/day, energy proxy units and terrain/environment coordinates.
- Biomass/mass proxies and branch radius relationships must be explicit: a tree-like visual with arbitrary widths is a design result, not a verified structural prediction.
- Environmental fields: sunlight vector/intensity, gravity vector, soil moisture, nutrient proxy, nearby-obstacle occupancy, wind and temperature, each spatially registered and time stamped.

## 4. Core science and governing caveats

Formal grammars explain repeated structural rules, but plant growth is also influenced by local environment and internal state. The 3D turtle must rotate frames correctly and preserve branch-stack balance; a grammar expansion can grow exponentially, so enforce depth, string length, geometry and runtime ceilings. Tropism can steer direction but must not cause discontinuous jumps. Phototropism, gravitropism and resource competition are modeled with simplified fields unless backed by species observations.

Animal/creature proportion scaling cannot assume geometric similarity over all body sizes: bones, muscles, gait and load can have size-dependent nonlinear behavior (allometry). For visual shape generation, use landmark-controlled skeletons and safe ranges; for locomotion claims, test center of mass, support polygon, foot clearance, joint limits, inertia and contact with S06 physics/S10 animation contracts. Extreme fantasy proportions can be deliberately stylized, but label biomechanics as nonphysical when violated.

Ecosystem plausibility is multiscale. A tree needs resources, neighboring plants shadow one another, water flows downhill and seasonal behavior changes. These interactions should run through separate growth/environment contracts, not be hard-coded into mesh generation. A deterministic forest at one moment is **not** evidence of long-term ecological stability or biodiversity accuracy.

## 5. Authoritative engineering/science insight

Foundational plant grammar research, university-authored visual botany papers, peer-reviewed mammalian allometry/biomechanics, a maintained plant image-analysis system, and species-occurrence data terms demonstrate what can be modeled and how to measure/reference it. Source/author links live in the S19 provenance ledger. None of the reference images, code or creature data has been copied into MGR.

## 6. Candidate AI/models

Image-to-3D and diffusion models may suggest novel species/creatures, but their outputs do not establish anatomy, taxonomic identity or ecosystem compatibility. A multimodal visual judge may flag leaf silhouette or gait artifacts but should not certify biological function. Keep learned inputs optional: MGR core procedural branch grammars, anatomy landmarks and seeded ecosystem updates can run on CPU. Future learned species classifiers/genetic algorithms are separate adapters requiring license, dataset provenance, benchmarks and out-of-distribution checks.

## 7. Datasets and evaluation

Start with **MGR-owned synthetic references**: exact grammar strings, turtle trajectories, self-similar branching fixtures, known phyllotaxis angles, trunk taper, leaf area counts, gravity-biased roots, directional sunlight, obstacle shadowing, growth time series and multi-species resource consumption. Real botanical photography and biodiversity records are governed by separate rights and may describe observations, **not** complete 3D growth rules. Capture private licensed plant scans with calibrated scale/metadata for validation. For anatomical references, use rights-cleared materials and consented subjects only; do not silently import human scans or protected species location metadata.

## 8. Licenses, ethics and environmental stewardship

Research papers can teach independent algorithms, but diagrams, figures, plant photos, anatomical scans, 3D meshes, animal captures and even biological occurrence records carry specific reuse/citation conditions. Check a dataset's own license and publisher citation before commercial use; not all public data are commercially reusable. Restrict precise endangered-species localities and personally identifying human/animal records where sensitive. Never market simulated morphology as medically/biologically validated. Avoid using “species authenticity” labels without taxonomic and morphometric evidence.

## 9. APIs/adapters

Core should have no required hosted API. Adapters can read simple JSON/CSV environmental grids and authored parameter recipes, optional geospatial distribution summaries, plant shape measurements and 3D scene exports. External ecological datasets/models are read through pinning/rights gates; plugins never change the canonical native `LivingRecipe` or `GrowthReceipt` without versioned migration. The same growth assets can output mesh/GLB for real-time, high-detail Blender/shot geometry and simplified collision geometry.

## 10. MGR native creation system — Living Geometry

1. **MGR BioBlueprint:** plain-English organism specification into a typed bounded recipe: `class`, `seed`, style, morphology, growth stage, dimensions, leaf/limb parameters, environment, degree of biological realism.
2. **MGR Growth Grammar:** sandboxed grammar rewriting with explicit budget, bounded recursion, bracket matching and reproducible pseudorandom choice.
3. **MGR Nature Turtle:** verified SO(3) branch frames, parent-child continuity, tubes, leaves and flowers without coordinate drift.
4. **MGR Flow of Life:** growth state machine and time stepping; energy/water/nutrient proxies with nonnegative conservation checks or declared source/sink terms.
5. **MGR Adaptive Branching:** obstacle avoidance, light and gravity tropisms, root/branch competition and neighbor exclusion with deterministic spatial fields.
6. **MGR Creature Frame:** segmented limbs/joints, anatomical landmark constraints and age-dependent scaling, separate from rigging and physical locomotion claims.
7. **MGR Living Terrain:** soil/water/light/temperature fields coordinate with world geometry; persist spatial/time coordinate metadata.
8. **MGR EcoWeave:** species density, resource consumption, competition/succession and simple predator/prey or pollination relationships as configurable, non-scientific-by-default models.
9. **MGR Fantasy Mutation:** intentional transformations (glowing veins, gravity inversion, branching crystals, regenerative appendages), each tagged as art physics and preserving recoverable pre-mutation source geometry.
10. **MGR Morphology Judge:** measured leaf count/angle/area, plant height/width, branch degree, silhouette, center of mass and deformation metrics; register observed reference conditions rather than comparing unrelated pictures.
11. **MGR Living LOD:** time-aware impostors/instancing, near/far branch simplification and animation-compatible structure IDs while preventing popping in interactive worlds.
12. **MGR Life Passport:** hash/seed/version/rules/environment, generation snapshots, species inspiration level, source rights, measurements, runtime costs, uncertainty and tests preserved with the scene asset.

## 11. Hardware and engine design

CPU-first rewriting, turtle geometry, spatial fields, collision approximations and small ecosystem time steps are realistic on ordinary laptops. GPU assists may accelerate millions of leaf instances, particles, volumetric effects, ecosystem grids and film-quality renders but are *not required to know branch grammar mathematics*. In practice the main resource hazard is combinatorial growth: worst-case branches double or more per iteration, raising O(b^n) work; enforce topology and memory quotas, chunk the world, instance repeated leaves, cull occluded canopies and profile the target GPU and CPU separately.

## 12. Cost and fast-build strategy

No per-generation SaaS fee for native procedural growth. Build an independent deterministic parser/turtle first, then environmental steering, morphometric QA, Blender/GLB output and controlled scene ecosystem interaction. Every layer can be tested with synthetic truth before expensive artistic assets. Do not buy paid biological datasets or hardware until rights, measurable improvement and target use are clear. Time estimates require implementation inventory and benchmark measurements, not marketing comparisons.

## 13. Failure modes and mandatory guards

| Problem | Why it happens | Test/control |
|---|---|---|
| Runaway grammar | Recursive branching explosion | Maximum iterations/symbols/mesh vertices/runtime |
| Malformed branch stack | Unbalanced `[`/`]` | Syntax validation; never pop empty stack |
| Plant meshes self-intersect | Blind branch routing/thick tubular junctions | Geometric collision/proximity scan; declared overlap policy |
| Impossible anatomy | Unbounded limb proportions or scaling | Joint and landmark bounds; explicit fantasy override |
| Unrealistic ecosystem | Fixed fake abundances; no energy/water accounting | Track resources, extinctions and update invariants |
| Nondeterministic growth | Unseeded randomness or unstable ordering | Seed/hash repeatability, stable spatial traversal |
| Wrong physiology claim | A purely aesthetic equation sold as science | Distinguish artistic model and calibrated biological model |
| Explosive GPU/world draw | Too many triangles/leaves/fx | Instance/LOD/culling and memory budget telemetry |
| Rights exposure | Sensitive records/third-party photos | License and privacy gate before asset ingestion/export |

## 14. Metrics and acceptance thresholds

Track grammar length/symbol count per generation, expansion ratio, tree node count and depth, mesh triangles and instances, branch continuity displacement, radius/angle ranges, plant height/width, leaf count and distribution, per-stage biomass/energy proxy totals, growth monotonicity where specified, finite nutrient values, scene runtime/RAM/VRAM, render frames per second and polygon/texture budgets. For calibrated real plant comparisons report normalized shape error, leaf-area deviation, branch-angle distribution, height/width residual and species/reference validity. **Do not invent universal success thresholds:** define targets by asset scale, style and biological claims before testing; exact seed repeatability, syntactic validity, finite coordinates and budget adherence are hard gates.

## 15. Repo integration

Existing `forge/geometry.py` provides CPU mesh basics and scene coordinates, `forge/world.py` builds procedural environments, `forge/meshqa.py` checks basic mesh defects, and motion/fx/visual-judge modules can inspect outputs. These do not amount to a working growth/ecology simulator. Native additive targets: `forge/living_spec.py`, `forge/growth_grammar.py`, `forge/nature_turtle.py`, `forge/morphology_truth.py`, `forge/ecoweave.py`, `forge/living_export.py` with unit/visual/performance tests. S19 must interoperate with S03 geometry, S04 transforms, S06 physics, S09 modeling, S10 animation and S11 procedural worlds, without creating a second world engine or competing source-of-truth registry.

## 16. Executable tests and final proof gates

1. `A -> AB`, `B -> A` grammar produces exact expected generations by seed; malformed tokens/branch stacks rejected with typed errors.
2. Pathological `F -> FF[+F][-F]` grammar under high iterations triggers **budget refusal** before excess allocation; measure execution and memory.
3. Turtle turns preserve normalized orthogonal frames through 1000 seeded rotations, branch-state push/pop and trunk/leaf placement.
4. Generated 3D stems/branches have finite coordinates, consistent winding, no zero-area triangles and inspectable parent IDs; intentional crossing identified as allowed/rejected by recipe.
5. Tropism tests: directional light biases grown branches more toward light than neutral baseline; gravity biases roots downward; deterministic repeat with same seed.
6. Neighbor/resource tests: two plants compete for a bounded resource pool, never yielding negative inventory or uncontrolled net creation under conservative mode.
7. Biology claim tests: no unvalidated species name, medical anatomy claim, biomechanical guarantee or realistic ecosystem banner passes without qualified evidence.
8. Creature deformation: landmark completeness, limb/joint limits and center-of-mass bounds retained across a fixed motion test set; fantasy overrides remain labeled.
9. Growth snapshots: compare seed+recipe+time hashes, node IDs, sizes and memory across OS/runtime variants within declared numerical tolerances.
10. Export: create near/far mesh/GLB, open/render in actual Windows Blender and independently import into a viewer/game engine, verify instancing/LOD and material paths.
11. Validation against *owned/licensed* plant reference measurements reports numeric shape residual and uncertainty rather than a subjective percent-real score.

**Honest status:** This packet specifies independent MGR construction and hard acceptance gates. The engine and real-world biological calibration remain implementation work until tested with actual geometry, growth snapshots, Blender imports, and scientifically appropriate reference rights.
