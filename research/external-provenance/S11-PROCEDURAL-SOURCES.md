# External evidence ledger — MGR Living World Fabric (S11)

**Inspected:** 2026-10-25. Primary manuals, original textbook website and upstream repository README/license. This is **not a full source-code audit, pinned-release reproducibility test, end-to-end PCG engine comparison or commercial data-license clearance**. External names are for attribution and evidence, not MGR feature branding.

| External source | Primary URL | Specific evidence inspected | Rights / adoption gate |
|---|---|---|---|
| Blender Geometry Nodes official manual | https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/ | Field/attribute, noise, Voronoi, random value, instance, repeat and simulation node family documented | Documentation-level architecture pattern; actual node availability may differ by installed Blender version |
| Blender Simulation Nodes manual | https://docs.blender.org/manual/en/latest/physics/simulation_nodes.html | Frame-dependent simulation zones, cache and disk bake | Sequential state needs versioned cache; no performance claim |
| Godot FastNoiseLite official reference | https://docs.godotengine.org/en/stable/classes/class_fastnoiselite.html | Explicit `seed`, frequency, fractal octave, cellular types, domain-warp options; cellular output can exceed `[-1,1]` | Official API docs inspected; compare exact Godot wrapper behavior only after pinned runtime test |
| FastNoise Lite upstream README | https://github.com/Auburn/FastNoiseLite | 2D/3D OpenSimplex2, cellular/Voronoi, Perlin, Value, fractal and domain warp algorithms; many language ports | Upstream declares MIT; inspect pinned file/license before vendoring or transpiling; no local benchmarking |
| FastNoise Lite upstream license | https://github.com/Auburn/FastNoiseLite/blob/master/LICENSE | Published MIT terms | Include notices for redistributed code, separately inspect ports and transitive code |
| Procedural Content Generation in Games | https://www.pcgbook.com/ | Original publisher-authored educational resource indexes search-based generation, fractals/noise, grammars/L-systems, mixed initiative, evaluations | Academic reference, not asset/source code license |
| Search-based PCG original chapter | https://www.pcgbook.com/chapter02.pdf | Research taxonomy of optimization over represented content against quality objective | Methodological source; do not copy lengthy chapter material or figures |

## Evidence boundaries

**Documented technical fact:** fields/instances/nodes exist in Blender docs; Godot FastNoiseLite exposes deterministic-seed inputs; upstream FastNoise Lite advertises multiple noise classes under an MIT codebase; PCG research encompasses constructive/search/mixed-initiative methods. **Design inference:** a versioned seed plus per-feature stable hash and coordinate-safe chunk graph should support replay and seam consistency. That inference requires implementation and tests—no such MGR module is attested as passing by this ledger.

## Version and license checklist

1. Record installed Blender version and the exact canonical node types/port names available there; benchmark background `bpy` execution separately.
2. Pin a FastNoise Lite release+commit, record algorithm numeric-output golden samples for JS/Python/C++ adapters, and verify bundled notices.
3. Use local MGR-generated terrain, tree and ecology fixtures first. Third-party maps (satellite imagery, DEM, open-city data), meshes, textures, and ecological datasets require an itemized source/license/redistribution audit.
4. Keep authored/world-approved layouts under native immutable overrides, and separate mathematical ideas from third-party code, art or trademark branding.
5. Check data dependency and world recipe graph schema upgrades through reproducible before/after snapshots; do not silently regenerate existing paid/user-created worlds.

## Required follow-up research and proof

- Research comparative derivatives/periodicity of Perlin/Simplex/OpenSimplex/cellular noise; test aliasing and coordinate precision at massive world scales.
- Inspect the actual `FastNoiseLite` per-language implementations and quantify cross-platform seed parity for pinned versions.
- Consult domain experts/peer-reviewed primary ecology and urban planning studies before claiming scientific biome or city realism.
- Implement and verify exact chunk border equality, LOD seams, feature-ID stability, a 1000-seed stress corpus and continuous collision/navmesh checks.
- Measure generated mesh quality, draw calls, memory, disk cache and runtime on target Windows Blender and gameplay machine.
