# MGR 3D Forge — Progress and Evidence Log

## 2026-10-25 — User corrected Pinokio reference to God's Eye View

- Kept F32 Model Dock from Pinokio because it has separate native value for optional local model orchestration.
- Located canonical upstream `bilawalsidhu/gods-eye-view`; read official README/license. Code is MIT but third-party feeds and bundled assets are **not** blanket MIT and include commercial restrictions.
- Added F33 Spatial Eyes. Implemented `forge/perception.py` to report known-generated-building distances, camera visibility and blockers, with explicit evidence type and *not real-world verified* labels. CLI emits `spatial_overview.json`.
- Research-to-native contract in `research/GODS-EYE-VIEW-NATIVE-INTAKE.md`. Future camera/HUD, live evidence adapters and multi-photo reconstruction remain open.
- Expanded register to 33 areas. **47/47 tests passed** after new spatial visibility tests. No external data feeds, GPU inference or API charges.
- Owner clarified the goal is **native imaginative world creation**, not replicating God's Eye View. Added `forge/interiors.py` with original designed two-room interiors per building, real exportable `interiors.glb` and explicit `interiors.json` provenance. This is invented geometry, not a claim to know a building's unseen real interior. Test suite expanded to **49/49 passing**.

## 2026-10-25 — LOD, repair and two MGR-native research extensions

- Added coarse, **building-only** LOD1 mesh and deterministic world building chunk partition (`forge/streaming.py`), exported `world_lod1.glb` and `chunks.json`. This excludes terrain/roads and is preparation for streaming, **not a complete renderable LOD scene or live streamer**. Example 10-building LOD1: 120 triangles versus 372 triangles in the full original scene (different contents, so not an apples-to-apples optimization benchmark).
- Tightened `WorldSpec` against nonfinite dimensions.
- Added actual-3D-coordinate camera tour keyframes and interpolation (`forge/cinematic.py`, `camera_tour.json`) inspired by Scroll-World's flight concept but independent of its image/video pipeline.
- Added security-first model recipe schema and offline readiness assessment (`forge/recipes.py`), inspired by Pinokio's local launcher concept; no installation or execution yet.
- Added mesh triangle corruption/degeneracy inspection and conservative cleanup (`forge/meshqa.py`), not retopology.
- Reviewed primary upstream Scroll-World/Pinokio READMEs and licenses; researched the ambiguous Synapse name; documented exact native value and caveats in `research/SCROLL-SYNAPSE-PINOKIO-INTAKE.md`.
- Register expanded from 30 to **32** with F31/F32; Synapse is not counted until uniquely identified.
- **44/44 unit tests passed**. No GPU, model inference, unreviewed downloaded scripts or paid APIs used.

## 2026-10-25 — World graph and multi-export build increment

- Added deterministic intersections and symmetrical road adjacency, building-to-building shortest path and coarse AABB/circle collision (`forge/world.py`).
- Added CPU-only OBJ/MTL export (`forge/obj.py`) alongside native GLB; test checks triangle count parity across formats. OBJ diffuse colors approximate GLB PBR.
- Added static isometric SVG preview (`forge/preview.py`) and exported JSON navigation graph for human/consumer inspection. The SVG is generated from the scene manifest, **not imported and rendered from the GLB**.
- CLI now emits six related files: world.glb, world.obj, world.mtl, navigation.json, preview.svg and manifest.json.
- **33/33 Python tests pass**. Example spec generates 10 buildings, 372 triangles, QA PASS. External GLB/OBJ import, animated navigation and visual rendering acceptance are still pending.
- Updated the capability register for F15, F17, F24 and F28 as partial, not production finished.

## 2026-10-25 — First native code vertical slice

### Second native build increment — guarded workflows

- Added `forge/workflow.py`: deterministic dependency resolver, missing-step and cycle rejection; per-plan spend ceiling and mandatory explicit approval for paid, network or unapproved-license work.
- Added atomic local job checkpoints with process-restart recovery. **No actual provider API calls or multiworker production orchestration yet.**
- Expanded regression suite to **25/25 tests passing**; budget, license, dependency and restart tests included. Original 17-test claim below is preserved as an earlier checkpoint.

- Built Python-standard-library GPU-free 3D neighborhood mesh generation, material grouping, GLB 2.0 binary writing and internal structural inspection (`forge/geometry.py`, `forge/glb.py`).
- Added seed-based reproducibility, bounded typed world specs and an explicitly limited English-count prompt planner (`forge/spec.py`, `forge/planner.py`).
- Added synthetic character landmarks, missing-hand and limb-symmetry tests, relative-proportion drift checks (`forge/quality.py`). These **do not** create a Tevin 3D character or rig.
- Added a content-addressed asset registry with ownership/license metadata and integrity detection (`forge/assets.py`). This is an early local store, not a production database.
- `python3 -m unittest discover -v`: **17/17 pass**. Initial test fixture for anatomy identity was invalid; corrected to plausible symmetric landmarks and reran green.
- `python3 -m forge.cli build --prompt "Create 25 buildings and streets" --out artifacts/prompt-25`: **25 buildings, 756 triangles, QA PASS**, real GLB output, no external APIs/model inference. SHA-256 `46738a68b153bc8c1e168fb1ea047c294c73db67fcf40a136d4ff705ee16e81d`.
- `python3 -m forge.cli inspect artifacts/prompt-25/world.glb`: internal inspection **valid=true**, one mesh, six primitives, 1,512 vertices, 756 triangles, six materials.
- CLI, tests and manifest are reproducible. No Blender, external GLB importer, target game engine, approved Tevin base or GPU model runtime available for integration proof; those gates remain open.

**Proof classification:** local CPU prototype and unit tests verified; independent application import, visual appearance, interactive worlds, advanced text-to-3D, character production, licenses and cross-repo integration **not verified**.

## 2026-10-25 — GitHub repository designated

- Owner supplied https://github.com/tdmboyd-dev/MGR-3D-FORGE and requested everything preserved with full research, native inventory and exact build needs.
- GitHub connector verified repo exists, public, default branch `main`, and current access includes push. Repository size was 0 (empty baseline).
- Added README, Product Bible, Architecture, Decisions, Research Register, Hardware & Cost, License Risk, Build Register and Acceptance Plan.
- Research foundations: official repositories and papers for TripoSR, TripoSG, TRELLIS.2, Hunyuan3D 2.1, Hunyuan3D-Part, HY-World 2.0, WorldClaw, WorldGen, UniForge3D and Blender; plus 2026 mesh research.
- Discovered important nuance: public Tencent releases have additional license restrictions and not all are safe for commercial reuse.
- Architecture conclusion: world planning + CPU procedural geometry + reusable asset memory + optionally GPU neural detail appears most promising for MGR. Benchmark pending.
- **No code for a working 3D engine written. No local models installed or benchmarked. No repo consumer integrations tested. No expenses incurred.**
- External source tree audits, full candidate code inspection, 16-field packets, actual hardware test, model licenses and owner acceptance remain OPEN.

## Status snapshot (honest categorical, not percentages)

| Domain | Evidence | Status |
|---|---|---|
| Repo ownership | GitHub get_repo | VERIFIED |
| Vision and native capability description | GitHub docs | DOCUMENTED |
| Architectural direction | source-linked research | SPECIFIED, NOT BUILT |
| Candidate research | official docs/repo/papers | SOURCED; not exhaustive |
| CPU-only world prototype | generator + GLB + 17-test suite | WORKING PROTOTYPE, internally tested |
| Character preservation | synthetic landmark suite, no Tevin base | PARTIAL; production NOT STARTED |
| Model runtime proof | no compute | NOT STARTED |
| Blender bridge | no runtime | NOT STARTED |
| Creation OS / Tevin integrations | repos not inspected | NOT STARTED |
| Commercial license clearance | preliminary warnings | BLOCKED pending exact review |
| Owner approval | absent | PENDING |

## Next action

Audit target runtime and connected owner repos, then implement the smallest CPU-only scene production vertical slice and gather measured evidence. Add research receipts without silently upgrading implementation status.
