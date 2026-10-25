# MGR Living World Fabric — Procedural Generation Intelligence

**Scope:** S11 procedural content generation: fractal/gradient/cellular noise, domain warps, L-systems, grammars, biomes and ecosystems, seed determinism, node-field graphs, instancing and chunk streaming. **Owner:** MGR. **Date:** 2026-10-25. **Evidence maturity:** primary manuals, original research textbook and upstream README/license inspected; no full dependency source audit or real hardware benchmark. **Build maturity:** specification and acceptance test plan, not proof that modules below are implemented.

## Native direction

The MGR differentiator is not random mountains. It is **a world that remembers its own laws and history**: a seed, region coordinate, lore/biome rules, ownership-approved edits and a typed graph produce a reproducible world. A character can cut a tree, a storm can move sediment, or a city can expand without regeneration overwriting approved assets. **MGR Living World Fabric** orchestrates native field graphs, tile-safe chunk generation, persistent authored overrides, ecological rules and visual/performance audits. AI may propose a scene brief but cannot silently change canonical geometry or ownership-approved character/landmark identity.

## 16-field contract

### 1. Definition

Procedural generation creates structured content from explicit algorithms, constraints, seeds and spatial/world inputs. Noise is a continuous or sampled scalar/vector field, not a complete terrain ecology. Grammars/L-systems generate recursively structured forms. Search-based PCG optimizes candidate outputs against target quality. A simulation ecosystem evolves over time and is distinct from a static random biome scatter.

### 2. Production use cases

- iKickItz and MGR world districts: traversable roads, terrain, landmarks, vegetation, caves, skies and fantasy realms with story constraints.
- Tevin shots: reproducible environment details, background crowds/props and weather variants while locking Tevin identity.
- Game exploration: deterministic regions/chunks, scalable LOD, colliders and navmeshes.
- Director tool: regenerate *only* a selected region or class of elements without moving canonical landmarks, approved art or quest dependencies.
- Cinematic production: high-density scattering and detailed geometry baked offline, with reusable low-cost runtime counterparts.

### 3. Mathematical/architectural contracts

- Scalar terrain sample: `height(x,z) = base + Σ amplitude_i * noise(frequency_i*x, frequency_i*z, stable_subseed_i)`; filtered/anti-aliased at distant LODs.
- Cellular partition: nearest feature points produces regions; distance combinations produce paths/ridges/cells; output ranges depend on algorithm and **must not be assumed universally within [-1,1]**.
- Recursive grammar: symbols expanded with bounded depth, replacement production rules and turtle state; constrain branching, thickness, self-intersection and total generated nodes.
- Seed function: stable documented `subseed = hash64(master_seed, world_id, generator_schema_version, chunk_xyz, feature_id)`; do not use Python's process-randomized `hash()` or one shared mutable RNG stream for all jobs. Choose and pin exact hash/PRNG algorithm for language-portable results.
- Chunk boundaries: sample **world coordinates** and deterministic halo/context, never restart an unrelated coordinate system at each tile; seam equality constraints on common vertices/normals/material splats.
- Graph: typed ports (`scalar_field`, `vector_field`, `point_set`, `mesh`, `mask`, `biome`, `nav_surface`), cycle prohibition except explicit bounded iterative/simulation zone, validation before evaluation, node-versioned outputs and cache hashes.
- Preserve deterministic result in a **declared tolerance** across CPU/GPU/engines; numerical floating-point variation may prevent bit-identical geometry unless fixed-point or rigorously controlled kernels are used.

### 4. Primary research and science

*Procedural Content Generation in Games* (Shaker, Togelius, Nelson, 2016) is a research overview: constructive/search-based methods, noise/fractals, grammars/L-systems, mixed-initiative design and evaluation. Official Blender Geometry Nodes manuals expose fields, noise/Voronoi/random nodes, instances, repeat and simulation zones; Godot documents FastNoiseLite's seed, frequency, fractal and domain-warp settings. The relevant biology/ecology literature (succession, nutrient flows, species distributions) and road/city planning publications require a separate scientific deep dive before claiming physically or ecologically accurate worlds.

### 5. Upstream implementation candidates and lessons

| Inspected upstream | Useful contract | Limits |
|---|---|---|
| Blender Geometry Nodes | Author visual field graphs, scatter/instances, operations, baking and iteration | Offline/native Blender engine tied to version; node graph round-trip not verified |
| FastNoise Lite | Portable 2D/3D seeded gradient/cellular/fractal noises and warps in many languages | Upstream README/license inspected, not benchmarked locally; output parity needs tests by binding/version |
| Godot FastNoiseLite | Stable exposed seed/frequency/cellular/fractal/warp config; quick preview comparator | Engine-specific wrapper/settings; docs inspected only |
| Blender simulation nodes | Frame-to-frame state with explicit bake/cache | For evolving worlds, version-state design essential; no tests run |
| PCG academic textbook | Design/evaluation methods, constraints and mixed-initiative editing | Academic principles, not reusable source code or licensed commercial scene assets |

### 6. Algorithms/models

- Large forms: continental masks, multifractal terrain, ridges, domain warp, cellular boundaries, erosional postprocessing and protected landmark masks.
- Layout: Poisson-disk/blue-noise scatter to avoid clumps, rule-based spacing, weighted biome occupancy, grammar/L-system vegetation, graph-based streets/settlements, path constraints.
- Ecosystems: habitat suitability, carrying capacity, resources, weather/season, agent interactions; start with explicit deterministic rules and calibrate biological plausibility before complex agent-based claims.
- Experimental assistants: model-proposed constraints, masks, biome tags and semantic layout—not unreviewed asset geometry or autonomous changes to canonical maps.

### 7. Datasets and authored fixtures

Prefer MGR-created fixtures: 2×2/4×4 tile seam test, layered mountains with water and river route, procedural road intersecting a bridge, 100 seeded tree instances across zone borders, 24-season ecology cycle, 1000 seeds with constraint rejects, protected Tevin stage and approved landmark, city zoning with navmesh routes, storm/erosion evolution and multi-LOD inspection. External elevation/city datasets and model weights require provenance, license and geographic suitability reviews independently; no outside map data downloaded in this research pass.

### 8. Licensing

FastNoise Lite's upstream repository declares MIT and multiple language ports; use pinned revision, audit individual copied files and attribution before distribution. Blender source GPL and node graph artifact ownership require distinction; invoking an installed Blender executable as a tool differs from embedding GPL code into MGR proprietary runtime. Godot documentation is informative; using a Godot engine/module requires independent version and notice audit. Textbook contents are scholarly references, **not** a grant to copy chapter text, figures or example art wholesale. Procedural techniques/math can inform original MGR implementation without relabeling external source code.

### 9. APIs and interfaces

Proposed MGR `WorldRecipe` includes `schema_version`, `world_seed`, `units`, `world_bounds`, `tiles`, `field_graph`, `biome_rules`, `protected_assets`, `authored_overrides`, `generation_stage`, `quality_targets`, `rights_manifest`. `GenerateChunk(recipe, xyz, lod, prior_version)` returns geometry, collision and nav surfaces, instance references, receipts, border signatures and cache dependencies. A Blender adapter exports baked geometry/instances; lightweight runtime adapters receive game-ready mesh and collision products. Generated data must never implicitly require a provider key.

### 10. MGR-native inventions

1. **MGR World DNA:** fully versioned seed, graph, landmark registry, narrative/lore rules and rights manifest; a world can be reconstructed from its genetic recipe.
2. **MGR Seam Guardian:** cross-chunk tests for positions, normals, UV/material transitions, terrain height and navmesh continuity.
3. **MGR Biome Logic:** connects elevation, slope, moisture, sunlight, species compatibility, water and ecological succession with owner-directed fantasy overrides.
4. **MGR Regeneration Firewall:** records approved changes as immutable overrides; only authorized target regions can be regenerated and diffed before commit.
5. **MGR Time-Garden:** season/weather/history ticks evolve vegetation and settlements while maintaining explicit cause/effect ledger.
6. **MGR World Beyond Image:** infer a plausible navigable off-camera world from image evidence but label unseen generated regions as *authored hypotheses*, not surveyed fact.
7. **MGR Director's World Brush:** natural-language scene request compiles to a typed field graph, shows affected bounds, rule conflicts and cost before execution.

### 11. Hardware/runtime

Noise sampling, low-resolution tile mesh generation and grammar expansion are CPU-feasible. Large voxel worlds, photoreal scatter meshes, broad chunk streaming, ecological agents and high-resolution renders can exhaust RAM/VRAM, geometry bandwidth or storage; GPU not universally required. Runtime benchmark on the actual Windows CPU/GPU is required. Support instancing, tile LOD/culling, chunk budgets, cached immutable outputs and work queues. Distinguish generate-time FPS from in-game render FPS and load-time stutter.

### 12. Cost and scheduling

No mandatory paid API for deterministic PCG. Cost is implementation/maintenance, CPU/GPU time, asset sculpting, QA, world storage, streaming, collision/navmesh cooking and owner review. Measure cost per *accepted traversable square kilometer and cinematic shot*, not per random mesh. Proposal tiers: seed preview on CPU; detailed local area; authored/quality-checked final render; game-ready optimized stream. Quantitative dollars and timings are **not measured** in this packet.

### 13. Failure modes

| Risk | Mechanism | Native defense |
|---|---|---|
| Visible tile cracks | Local-coordinate noise or incompatible LOD edge verts | World coordinate sampling, shared border signature + skirts only if justified |
| Saved world changes on rerun | RNG call order, thread scheduling, version changes | Counter/subseed per element and pinned graph schema; replay digest |
| Identical repetitive vegetation | Unvarying rules/random distributions | Environmental constraints, species mix and structure metrics |
| Objects float or collide | Scatter ignores ground normals/colliders | Contact/clearance check in actual collision world |
| Roads end in cliffs | Independent generation layers | Constraint ordering: infrastructure first or negotiated graph solve |
| Biomes nonsensical | Noise alone used as ecology | Ecology suitability constraints and ecological tests |
| Huge mesh/VRAM blowup | Unbounded recursion/scatter/density | Hard production budgets and geometry simplification |
| Old map edits erased | Regeneration overwrites stored state | Approved asset lock and layered authored override ledger |
| Visual terrain but unplayable | No navmesh/collision/streaming | Traversal and physics acceptance independent of render |
| Data rights conflicts | Imported proprietary terrain/assets | Explicit rights manifest and external asset quarantine |

### 14. Evaluation metrics

Record 100% deterministic per-chunk digest under pinned toolchain, exact edge vertex agreement/toleranced normal match, no gap in path traversal, count/density by biome, species overlap score, landmark preservation, collision penetration/clearance, 100% approved override preservation, topology validity, triangle and instance counts, draw calls, peak RAM/VRAM, generation latency P50/P95 and data footprint. Aesthetic evaluation uses multi-camera contact sheets and a human owner gate; visual beauty scores cannot replace correctness. Proposed thresholds require measurement, not claimed product success.

### 15. MGR Forge placement

MGR living-world recipe and output receipts belong in canonical native Forge source; graph runtime, noise field evaluator, topology/biome validation, persistence and Blender exporter should be cleanly separated. World assets remain shareable across Creation OS and game consumers through versioned interfaces. Preserve continuity of iKickItz-approved content and Tevin character locks. Check existing paths/interfaces before creating new source modules to avoid conflicting source-of-truth copies.

### 16. Acceptance tests before production labels

1. Same recipe/seed/tile/version twice produces identical stable serialization/digest on same runtime; rerun shuffled tile order and concurrency and verify identical outputs.
2. Adjacent tiles agree on shared height vertices and tangent/material/normal continuity within declared tolerance; compare near/far LOD boundaries.
3. Changing one feature sub-seed preserves unrelated region/landmark hashes and approved objects; validate region diff.
4. Sweep 1000 seeds for NaN, infinite recursion, invalid mesh, road blockage, impossible building placement and triangle/time budgets.
5. Validate all proposed world props have physically plausible surface attachment, collision clearance, and reachable game navmesh where required.
6. Run an L-system tree at depth 0..max and prove strict bounded geometry/branch counts, monotone safety budgets and stable feature IDs.
7. Check biome outputs against authored water/sun/slope suitability and ecology conservation/turnover rules; document fantasy exceptions.
8. Validate long-running seasonal evolution replay with checkpoints; modifications outside target region must remain unchanged.
9. Export representative terrain+instances through Blender, render at least four camera perspectives, and import in target runtime with coordinate/material/nav contracts intact.
10. Benchmark CPU/GPU time and peak memory on Time's installed Windows Blender hardware; do not claim verified measurements before receipt exists.

## Concrete build order

Start with a CPU-friendly **MGR World DNA + chunk border proof + per-feature deterministic RNG + immutable approved-asset overlay**. Then layered field graphs, scatter/grammars, biome constraints, nav/collision and Blender bake adapters. Add time-evolving ecology and director's brush once static continuity and replay pass. This yields the most reusable foundation without committing to one commercial PCG system.

## Explicit research gaps

- Version-pinned source-level study and algorithm comparison for gradient/cellular noise and FastNoise Lite ports; seed parity across Python/JS/C++.
- Authoritative ecology/urban planning/river hydrology studies, climate data bounds and biological realism QA.
- Large open-world streaming/LOD/navmesh implementations and cross-engine asset performance testing.
- Fully measured Windows Blender/interactive platform outputs, audited third-party terrain asset licenses and generated content rights.
