# External spatial data/license reference ledger B — 2026-10-25

## Canonical source and rights

- Source: https://github.com/bilawalsidhu/gods-eye-view
- Official README: https://raw.githubusercontent.com/bilawalsidhu/gods-eye-view/main/README.md
- Official license: https://raw.githubusercontent.com/bilawalsidhu/gods-eye-view/main/LICENSE
- Code under MIT (copyright 2026 Bilawal Sidhu). **The MIT license expressly does not cover its bundled third-party datasets or runtime provider feeds.** Some bundled data is non-commercial (e.g., TeleGeography); commercial use needs separate audit and exclusion or license.
- The README distinguishes free/keyless base layers from photorealistic providers that may need Cesium or Google Maps keys and have usage rules or charges. Never assume "photorealistic free unlimited 3D Earth".

## What it actually is

An interactive 3D globe and spatial intelligence viewer combining visual terrain, camera modes, aircraft/ship/satellite/weather/earthquake/public-camera layers, inspection tools, HUD, voice control, scene direction and sourced public signals. Some data are live, some regularly refreshed, some simulated, and some geometry positions approximate. It is **not** a generator that reconstructs hidden rooms or whole 3D worlds from one photo.

## MGR-native decision: F33 — Spatial Eyes

This complements Forge's synthetic world and ultimately Creation OS and Tevin.

1. **Grounded scene awareness**: report which editable entities are present in a Forge-generated world, their center, approximate camera distance and what other known geometry blocks a center ray.
2. **Evidence and uncertainty layers**: clearly label generated, measured, inferred and externally sourced facts; never call AI guesses real measurements.
3. **Vision beyond a reference (future research)**: when an owner supplies multiple photographs and camera poses, match points, estimate depth, align a sparse 3D scene and create editable proxy geometry with uncertainty overlays. One picture does not reveal the unseen truth; generated backsides are hypotheses.
4. **Creator HUD (future)**: clickable objects, overview/follow/first-person camera modes, live route graph, debug occlusion, lighting/shading modes and a map-style editor.
5. **Optional real-world contextual layers (future)**: only from authorized providers with licensing, provenance, rate limits, freshness and location privacy boundaries; **not** a default external data feed or people-tracking service.

## Build receipt

- `forge/perception.py` implements a conservative first step: geometry-grounded building center visibility, occlusion blockers, distance and explicit real-world-not-verified tags.
- `forge/cli.py` exports `spatial_overview.json` with every generated world.
- Tests cover deterministic outputs, known occlusion and invalid camera input. No unseen world reconstruction, third-party tile usage, live sensors or voice interface implemented yet.
- This is **original Forge code inspired by capabilities**, not copied God's Eye View source or imagery. It costs no API credits and requires no GPU for its AABB ray checks.
- **Second proof increment:** `forge/interiors.py` creates a separate GLB mesh with two invented rooms per block building, doorway gaps and an `interiors.json` ledger. Every room is explicitly `MGR-procedural-hypothesis`, not observed and not owner approved. This makes geometry beyond an exterior silhouette editable in a standard 3D file, but does **not** establish the true interior of any photographed building.

## Native improvement proposal

Combine editable scene geometry, character DNA, model provenance, camera tours and observable evidence into a *Spatial Truth Graph*. Every object and inference carries source, confidence, license and mutation history. It would make inaccurate AI-generated geometry easier to detect and repair. This is proposed, not yet implemented or benchmarked.
