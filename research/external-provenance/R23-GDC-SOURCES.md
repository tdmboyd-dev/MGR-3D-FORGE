# R23 — GDC public technical source provenance

Research date 2026-10-25. No videos, recordings, media files, game-source repositories or privileged GDC Vault assets copied/downloaded. **Levels:** `ABSTRACT` = official session landing text and speaker/title metadata inspected; `SLIDES` = public speaker PDF inspected via retrieved selected text, not page-by-page full deck; `ENGINE-DOC` = official vendor technical docs consulted as supporting evidence, **not a talk transcript**. There is no `FULL-TALK`, full transcript or runtime implementation audit in this wave.

| Primary source | Public evidence actually inspected | Level | Usable MGR lesson, what remains unknown |
| --- | --- | --- | --- |
| [GDC 2019: End-to-End Procedural Generation in Caves of Qud](https://www.gdcvault.com/play/1025914/Math-for-Game-Developers-End) | Official title, speakers Brian Bucklew/Jason Grinblat, systems linking histories/cultures/architecture/NPC/quests | ABSTRACT | Multi-stage semantic world construction, no code or full video reviewed. |
| [Caves of Qud GDC speaker PDF slides](https://media.gdcvault.com/gdc2019/presentations/Grinblat_Jason_End-to-End_Procedural_Generation.pdf) | Selected extracted slide text: abstract facet models, staged reification to concrete, IO plumbing, defaults when inputs absent | SLIDES (selected text; no full visual page audit) | Strongest concrete method: typed stage chain and defaults. Full talk commentary not claimed. |
| [GDC 2017: Continuous World Generation in No Man's Sky](https://www.gdcvault.com/play/1024265/Continuous_World_Generation_in__No_Man_s_Sky_) | Official speaker Innes McKendrick (Hello Games), voxel generation→polygonization→texturing→population/simulation and seamless travel topic | ABSTRACT | Continuous sector generator and LOD test concept; real algorithms/performance numbers not examined. |
| [GDC 2019: Marvel's Spider-Man technical postmortem](https://www.gdcvault.com/play/1026496) | Official speaker Elan Ruskin (Insomniac), asset counts, rendering/streaming/lighting, Manhattan procedural markup, living-city NPCs and failures | ABSTRACT | Source-of-truth city streaming/life architecture; numerical budgets remain unknown. |
| [GDC 2013: Under Construction: Crafting Fortnite's Building System](https://www.gdcvault.com/play/1017937/Under-Construction-Crafting-Fortnite-s) | Official speaker Billy Bramer (Epic), accurate rapid construction without restricting architectural creativity; iteration successes/failures | ABSTRACT | Native live-build vs studio-build interface and undo tests; no Fortnite source or gameplay timings inspected. |
| [GDC 2024: Marvel's Spider-Man 2: 10 Years of Procedural Content Creation](https://gdcvault.com/play/1034369/) | Official speaker Xray Halperin (Insomniac), evolution of procedural workflows over multiple games | ABSTRACT | Artist override and lineage is a **design inference**, not a method demonstrated in accessible abstract. |
| [GDC 2023: Forza Motorsport: Non-Destructible Workflows](https://gdcvault.com/play/1029329/Technical-Artist-Summit-Non-Destructible) | Official speaker Diego Garzon (Microsoft), adoption and lessons from procedural, non-destructive workflows in existing pipeline | ABSTRACT | Versioned edits/incremental adoption/rollback; detailed tooling, success metrics and sample assets unavailable here. |
| [GDC Vault free GDC 2017 catalog](https://gdcvault.com/free/gdc-17/) | Conference archive identifies relevant talk under free catalog | CATALOG | Catalog listing does not prove unrestricted direct video access. |
| [GDC Vault free GDC 2019 catalog](https://gdcvault.com/free/gdc-19/) | 2019 topical listings | CATALOG | Session availability and media rights vary. |

## Supporting official engine documents — NOT GDC session transcripts

| Primary source | Inspected fact / connection | Level |
| --- | --- | --- |
| [Epic PCG Framework documentation](https://dev.epicgames.com/documentation/unreal-engine/procedural-content-generation-framework-in-unreal-engine) | Authoring PCG graphs, biomes/buildings, runtime/GPU execution and official GDC 2023 demonstration references | ENGINE-DOC; not full 2023 presentation. |
| [Epic Unreal 5.4 release notes](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5.4-release-notes?application_version=5.4) | Partition 3D grids, server streaming, HLOD, asynchronous landscape rebuild and water scalability descriptions | ENGINE-DOC version 5.4; no engine source/runtime tested. |
| [Epic UE5 performance talks context](https://dev.epicgames.com/community/learning/talks-and-demos/Vpv2/unreal-engine-optimizing-ue5-rethinking-performance-paradigms-for-high-quality-visuals-part-1-nanite-and-lumen-unreal-fest-2023) | Topic coverage Nanite/Lumen quality and performance | TALK-LANDING (Unreal Fest, **not GDC**); not video transcript. |
| [Epic Lumen technical documentation](https://dev.epicgames.com/documentation/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine) | Dynamic GI/reflections, software tracing modes, detail resolution tradeoffs and emissive noise caveat | ENGINE-DOC; no shader/source audit. |

## MGR-native synthesis without source copying

1. `World Genesis`: semantic graph → terrain/architecture realization → population/quests; primary grounding: Caves of Qud speaker slides + session metadata.
2. `Continuous World Shell`: chunk reconstruction/LOD/asset stream; conference topic from No Man's Sky + separately verified partition concepts in Epic docs. The precise No Man's Sky algorithm was **not** examined.
3. `Living City Director`: streaming city sources, lighting, pedestrians/traffic, interaction timelines; GDC Spider-Man session abstract. Implementation details unknown.
4. `World Hand`: quick accurate freeform building/undo; GDC Fortnite design talk abstract. No engine code used.
5. `Authoring Lineage`: non-destructive procedural edit contracts; Forza session abstract and separate procedural art evolution topic. Exact studio approach unknown.
6. `Generation X-Ray`: visible stage timings/errors, CPU/GPU checks; Epic official documentation rather than speaker transcript.
7. `Light Reality Budget`: scene/render quality tradeoffs, GI/reflection truth; Epic Lumen tech docs rather than an inferred GDC full-talk finding.
8. `World Memory`: semantics-to-architecture/encounters and replayable NPC state; GDC Caves of Qud and Spider-Man abstracts.

## Legal, technology and source-depth limits

- Conference presentations, videos, diagrams, sample slides and game assets carry copyrights/license and GDC access terms. Public search metadata and slides are educational research; do not embed source deck or substantial speaker text in MGR code or public artifacts without rights review.
- Vault site showed a maintenance message in at least one public search retrieval. Some sessions are listed free, others member-gated; exact media access was not validated by successful playback. No bypass attempted.
- Epic Unreal source/documentation and GDC publisher/presenter rights are separate. Public UE technical docs do not grant rights to relabel engine source, Fortnite mechanics assets, Spider-Man code/characters, or No Man's Sky assets as MGR-native.
- No full presentation transcript, downloadable speaker code sample, animation runtime or proprietary AAA performance trace was collected. Inferences are explicitly labeled and require native test execution.

## Native test harness and acceptance evidence needed

- Generate 10 seeded neighborhoods with canonical semantic outputs and artist edits; regeneration preserves approved changes and detects invalid road/navigation graph.
- Populate one multi-sector city with NPC routes/traffic; traverse forward/back/fast teleport, measure p95/p99 streaming stutter, memory and deterministic sector hashes.
- Stress live-building with rapid placement/collision/undo and a creative off-grid variant; compare authoritative world mesh and renderer state.
- Run director camera paths through day/night reflections, emissive surfaces and volumetric effects with reference images and different quality budgets.
- Test incremental procedural edit and rollback without corrupting source scenes; exact commit/asset receipt required.
- Revisit public videos/slides only through legitimate access; if whole talk can be inspected, expand source evidence and revise tentative attributions before architecture locks.

**Confidence:** high that the named talks/topics exist and public metadata says what is recorded above; moderate for general MGR design relevance; **unverified** specific secret production algorithms, per-frame timings, rendering internals and transfer performance. No "studio hidden knowledge uncovered" overclaim.
