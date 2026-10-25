# R23 — GDC Game-Production Research: MGR Forge Native Lessons

**Stage:** `SOURCED / selective session abstracts, one public PDF slide deck and separate official engine guidance`, checked 2026-10-25. No claim of full GDC-talk viewing or a verbatim transcript review. GDC Vault is reporting maintenance/access variability; many talk pages publicly expose abstracts while video/slides may require a session. Exact links/evidence depth in `research/external-provenance/R23-GDC-SOURCES.md`.

## Thesis: what belongs in native Forge

The production lessons worth owning are **multi-layer world generation**, **continuous scene-cell streaming**, **author-first constructive editing**, **budgeted rendering**, **procedural art support that preserves control**, **city life systems**, **repeatable quality tests**, and **non-destructive re-authoring**. The GDC examples provide design evidence, not source code or licensing to copy named games. The Forge canon stays MGR-native; only research attribution is external.

## Method 1 — Layered procedural world generator with explicit semantics

**Conference evidence:** GDC 2019 *End-to-End Procedural Generation in Caves of Qud* (Bucklew/Grinblat) describes interconnected history/culture/architecture/quest layers. Its publicly available **speaker PDF slides** expressly describe abstract-to-concrete, multi-stage village generation, defaults, and IO handoffs.

**MGR-native creation:** `MGR World Genesis` stage chain:

```text
World brief / theme / biome / civilization rules
  → semantic place plan → roads/room/block adjacency
  → construction grammar and terrain/mesh realization
  → material, light, ecology, populace and encounter population
  → contact/nav tests → world continuity receipts
```

Each stage emits typed source data/seed/version. It can regenerate just a street without changing approved character or unrelated neighborhood. Avoid inventing context when input is absent—use declared defaults with a visible trace.

**Tests:** same seed→same outputs/hash; artist override survives regenerate; invalid zoning/blocked roads; graph-connected routes; balanced building density; no duplicate asset IDs; predictable CPU time/RAM.

## Method 2 — Continuous world generation and geometry LOD

**Conference evidence:** GDC 2017 *Continuous World Generation in No Man's Sky* (McKendrick) officially describes a continuous pipeline from voxels to polygonization, texturing, population and simulation, with seamless transitions from space down to planets. Full technical slides/video were not inspected here.

**MGR-native creation:** streaming world shell with deterministic cell coordinates/seed, geometry chunk builder, mesh LOD tiers, material/texture pools, sector population and bounded memory. Separate player-visible presentation from canon geometry; cache/generated scenes may be evicted and recreated exactly. This informs iKickItz scale but does not mean arbitrary planetary fidelity comes for free.

**Tests:** long no-stop traversal, fastest camera/teleport transitions, cached vs regenerated chunk checksum, chunk-boundary seams, water/terrain normals, simultaneous agents, repeatable world population and p99 stutter/peak RAM.

## Method 3 — Hero-driven city asset/lighting streaming with populations

**Conference evidence:** GDC 2019 *Marvel's Spider-Man: A Technical Postmortem* (Ruskin, Insomniac) describes scaling asset count, rendering/streaming/lighting for a compact city, procedural Manhattan markup, pedestrians, traffic, street vignettes, random crime and pitfalls including pre-baked lightmaps. The accessible conference page is an abstract; detailed numeric techniques are **not verified** from full talk.

**MGR-native creation:** `MGR Living City Director`: city sector sources of truth; asset budget and streaming priority; region-specific material/lighting validation; NPC routines (idling, walking, traffic, encounters) feeding interaction triggers; cinematic Photo Mode scene cameras. Separate population narrative from core world geometry so player actions can change encounters without erasing architecture.

**Tests:** drive/walk across sector boundaries, traffic/pedestrian collision/route tests, stable lighting after day/night transition, save/reload NPC state, render-quality fallbacks, debug first-frame hitch and city asset package size.

## Method 4 — Player-speed construction with architectural freedom

**Conference evidence:** GDC 2013 *Under Construction: Crafting Fortnite's Building System* (Bramer, Epic) discusses rapid, accurate combat construction without blocking creative architecture, alongside iterative successes/failures. This is a public session description rather than a source/code walkthrough.

**MGR-native creation:** `MGR World Hand` gives one intent interface for grid snapping/structural support, collision-aware placement, rotation, undo/redo, blueprint sketches and freeform sculpting. Distinguish fast `live-build` from rich `studio-author` modes but use the same canonical asset graph. A fantasy construct may break realistic engineering rules if its world rules explicitly allow it; user needs previews and deterministic, recoverable edits.

**Tests:** under-100ms preview target is a **proposed target, not measured**; 100 rapid placements, supports, colliders, overlaps, invalid edit rejection, creative off-grid authoring, Undo 50 operations and idempotent save/load.

## Method 5 — Procedural artistic workflows must stay editable

**Conference evidence:** GDC 2024 *Marvel's Spider-Man 2: 10 Years of Procedural Content Creation* (Halperin, Insomniac) describes evolution of procedural content creation across multiple titles; session overview has no detailed method. GDC 2023 *Forza Motorsport: Non-Destructible Workflows* (Garzon) describes incremental adoption of procedural workflows into an established pipeline with lessons from failures. These are session abstracts, not full talk transcripts.

**MGR-native creation:** `MGR Authoring Lineage`: procedural node graph per prop/terrain/wardrobe with dependency capture and a human override layer. Re-running a generator must not discard material edits, owner-approved face assets or scene dressing. Source changes produce diff and retest list. The same graph operates through Blender authoring scripts and runtime exporters.

**Tests:** regenerate on 100 edited props and compare edit persistence, linked dependency invalidation, split source-vs-hand-edited provenance, undo/recovery, multi-user concurrent edits and asset license receipts.

## Method 6 — Procedural Generation Debugger and GPU routing

**Conference-linked evidence:** Epic's official Unreal PCG documentation references the GDC 2023 PCG demonstration and current PCG concepts: graphs, biomes, runtime generation, GPU processing and debugging. **Caveat:** those docs are not a transcript of the GDC presentation, and API/version specifics change.

**MGR-native creation:** `MGR Generation X-Ray`: graph inspector showing input/output asset counts, seed, step cost, CPU/GPU route, provenance, geometry failures, cell-level run status and artifact. Deterministic CPU pipeline remains a baseline; optional GPU execution based on S15 hardware admission and measured advantage. Bad graph edits fail locally, preserving previous committed world.

**Tests:** reproduce error by seed, step-by-step rerun, intentionally invalid graph edge, GPU capability missing, memory pressure, seed collision, mass asset population and stage timing regression. Compare CPU reference to accelerated candidate geometry/visual output.

## Method 7 — Dynamic lighting/render cost under frame deadlines

**Conference-linked evidence:** Epic's official optimizing UE5 talks discuss Lumen/Nanite quality-performance choices; Lumen technical documentation describes global illumination, reflections, far/near detail and reduced-resolution indirect-light evaluation, with known noisy emissive and material/lighting limitations. **This is vendor documentation/talk-page context**, not inspection of Lumen internals.

**MGR-native creation:** `MGR Light Reality Budget` assigns a shot/region quality tier, lighting dependency graph, high-value hero GI/reflection resources, distant fallbacks and objective exposure/continuity tests. Material and light-source truth must not silently diverge between story frames. Do not claim MGR built Lumen or Nanite; start with Blender Cycles/EEVEE supported paths and improve only after measured needs.

**Tests:** indoor/outdoor, moving emission, reflective/rain surfaces, colored light bleed, transparent FX, sudden camera shift, 24/30/60FPS target where interactive, offline image noise and color matching; p95/p99 GPU memory and render time with reference image receipts.

## Method 8 — Story-driven population, authored meaning and repeatability

**Conference evidence:** GDC 2019 *Caves of Qud* and *Spider-Man* session descriptions connect world structure to cultures/histories/NPCs/encounters. The explicit slides are available for *Caves of Qud* only.

**MGR-native creation:** `MGR World Memory` stores who lives where, histories, schedules and interactable city records independent of visual mesh generation. A world change triggers only affected NPC navigation/story region. Artists can lock narrative canon and place life behaviors by rules. No AI-language dependency is needed for deterministic baseline events; optional writer/provider must preserve schema and avoid hallucinating confirmed canon.

**Tests:** deterministic quest/local event routes, no orphaned home assignments, NPC graph reachability, temporal causality, replay/restart state continuity, 100-population stress, independent visual scene ownership and approval lock persistence.

## Recommended Forge integration wave

1. Native graph contracts for geometry, stage receipts and dependency lineage; implement CPU first.
2. One procedural street with 10 edit-preserved props, road adjacency, playable nav route and multi-camera render proofs.
3. Cell-based runtime streaming with density/LOD/asset memory admission and failure recovery.
4. Live author placement and 50-step undo/redo with collision/construction validation.
5. Living city state/NPC routines, procedural dressing and time-of-day/lighting stress scenes.
6. Optional high-performance GPU acceleration only after objective frame/memory/visual benchmark and rights review.

## Access, source-code and truth boundary

- GDC session titles and official abstracts are useful first-party testimony about *topics*, not full technical disclosures. Only the *Caves of Qud* public slides were inspected at meaningful below-abstract depth in this wave (selected slide-extracted details); no full video transcripts watched. GDC Vault maintenance/access can affect video and downloadable decks.
- Video/slides may have separate public, member or paid rights. No access barrier was bypassed, and no archived/private media or game source was copied.
- Unreal engine documentation is official technical corroboration and **not** an unviewed GDC speaker transcript. Unreal code/runtime and GDC speaker slide rights are distinct; learn concepts and independently implement only MGR authored systems.
- These examples do not prove MGR already matches Fortnite, Spider-Man, No Man's Sky or Hollywood. Every claim must be backed by our own actual scene, export, performance and gameplay tests.

**Verdict:** 8 concrete native candidates and executable test designs are now specified. Highest near-term leverage is layered procedural world generation plus non-destructive authoring/streaming—more direct creator value than attempting to reconstruct proprietary AAA renderer internals from conference summaries.
