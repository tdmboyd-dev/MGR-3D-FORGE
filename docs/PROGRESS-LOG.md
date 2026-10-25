# MGR 3D Forge — Progress and Evidence Log

**This is a historical sequence, not the current status page.** The canonical current status is `docs/WHAT-WE-HAVE.md` plus `docs/IMPLEMENTATION-EVIDENCE.md`. Superseded historical claims are retained only as dated checkpoints.

## 2026-10-25 — Owner autonomy lock, ten-capability extension and F34 starter

- Locked approved **hands-off within Forge workspace** policy in MGR Native Canon and `AGENTS.md`; other personal files, credentials, destructive actions and spending remain authorization boundaries. The complete policy-enforcing task runner (F36) is not built yet.
- Extended native implementation register F34–F43 and wrote functional how-to/negative-test/acceptance plan `research/MGR-CREATION-INTELLIGENCE-HOWTO.md` with source evidence segregated from product identity.
- Built starter MGR Scene Consciousness `forge/consciousness.py`: reproducible scene facts grounded in authored world geometry, exact IDs/dimensions/entrance heuristics and honest road-route limitation labels. Added four tests covering determinism, route qualification, nonexistent objects and invalid dimensions.
- Local automated suite **71/71 PASS**. Scene metadata intelligence is partial; no visual AI model, autonomous code runner, real rig, or complete world-interaction system is represented as finished.

## 2026-10-25 — MGR-native canon and Windows Blender import proof

- Centralized MGR naming/ownership in `docs/MGR-NATIVE-CANON.md`. External technical reference details segregated under `research/external-provenance/`, not used as MGR feature names or product definitions.
- On Time's connected Windows PC: Blender **5.2.2 LTS** verified; Python **3.14.8**; Git **2.56.0**. Cloned the latest Forge main commit to a unique temporary validation folder, with no existing user files replaced.
- Windows native test suite: **64/64 pass**.
- Windows Forge generated world and generic T/A mannequins with **16 modular parts** each; both anatomy checks pass.
- Real Blender 5.2.2 headless GLB imports: `world.glb` **372 triangles PASS**, `interiors.glb` **1,200 PASS**, `parks.glb` **504 PASS**, T mannequin **204 PASS**, A mannequin **204 PASS**; every receipt written on Windows.
- These prove real Blender import and geometry presence, **not** rendered image quality, skin weights, morphs, animation deformability, likeness approval or game-engine acceptance.

### Actual Blender image render and visual correction

- Added `bridge/blender_render.py` and `blender-render` CLI command to frame GLB content and render PNG with Blender's Workbench engine, creating a JSON receipt.
- Ran real Blender 5.2.2 Windows Workbench renders: procedural world preview **PASS** (285,421-byte PNG), T-pose modular mannequin **PASS** (initial 261,030-byte PNG).
- Visual inspection spotted unwanted center overlap in the mannequin coat. Changed the MGR coat mesh to two independent front panels and regenerated the character. **Fixed T-pose render PASS** (261,975-byte PNG); visually inspected: hands in frame, both forearms present, coat no longer obscures center shirt.
- The mannequin is a deliberately basic geometric test subject, **not Tevin's likeness**. Rendering proves the pipeline and exposed a correctable defect, not character-art acceptance.

## 2026-10-25 — Larger connected build cycle: character, adapters, Blender probe, greenery

- Locked MGR creative sovereignty in `docs/MGR-NATIVE-CANON.md` and `AGENTS.md`: all Forge capability identities are owned MGR creation contracts.
- Added generic fully enclosed 3D proxy mannequin, left/right arms, visible hands, hair, detachable coat, shirt, chain, pants/legs and boots (`forge/character.py`), 16 independent parts, T and A poses. **Not Tevin's approved identity.** Actual CLI T/A builds both passed.
- Added `forge/animation.py`: bone-length-preserving T→A→T landmark samples, currently **metadata only, no rig weights or deforming mesh**.
- Added `forge/adapters.py`: swappable contract, functioning CPU-world adapter and explicit not-installed neural adapter. Mock remote choice tested against budget+approval. **No real neural model integrated**.
- Added optional Blender import verifier (`bridge/blender_probe.py`, `forge/blender_bridge.py`). `blender` executable absent in runner; **not independently executed yet**.
- Added deterministic trees/parks on unoccupied lots (`forge/environment.py`), distinct GLB and provenance manifest. Six parks/18 trees in default world test.
- Added 13-file artifact SHA manifest (`forge/receipt.py`) and `verify-bundle` CLI; tamper rejection test passes.
- Tightened workflow cost validation against NaN inputs.
- Benchmarked procedural scene generation + GLB export: 10 buildings 0.006222s; 100 at 0.043213s; 1,000 at 0.310850s on CPython 3.12.14 x86_64. Baselines are **local CPU prototypes** and not compared to competitors.
- Suite **64/64 pass**. No GitHub Actions run, no paid APIs, GPU inference or networked third-party script execution.
- Remaining gates: real Blender import/render, approved Tevin body/face, skinning, exact asset separation, neural model runtime + licensing, interactive studio, external Creation OS/MGR-ONE consumer integration, game-engine benchmarks and owner acceptance.

## 2026-10-25 — MGR Spatial Eyes and Beyond Imagery

- Retained F32 MGR Model Dock because local-model sovereignty is a native creative requirement.
- External data/license restrictions were recorded in the separate provenance ledger; no outside spatial dataset copied into Forge.
- Added F33 Spatial Eyes. Implemented `forge/perception.py` to report known-generated-building distances, camera visibility and blockers, with explicit evidence type and *not real-world verified* labels. CLI emits `spatial_overview.json`.
- MGR Spatial Eyes research and build contract are tracked as F33; future camera/HUD and multi-photo reconstruction remain open.
- Expanded register to 33 areas. **47/47 tests passed** after new spatial visibility tests. No external data feeds, GPU inference or API charges.
- Owner clarified the goal is **MGR-native imaginative world creation**. Added `forge/interiors.py` with original two-room designs per building and an explicit uncertainty ledger. Test suite expanded to **49/49 passing**.

## 2026-10-25 — LOD, repair and two MGR-native research extensions

- Added coarse, **building-only** LOD1 mesh and deterministic world building chunk partition (`forge/streaming.py`), exported `world_lod1.glb` and `chunks.json`. This excludes terrain/roads and is preparation for streaming, **not a complete renderable LOD scene or live streamer**. Example 10-building LOD1: 120 triangles versus 372 triangles in the full original scene (different contents, so not an apples-to-apples optimization benchmark).
- Tightened `WorldSpec` against nonfinite dimensions.
- Added MGR World Flight 3D-coordinate camera keyframes and interpolation (`forge/cinematic.py`, `camera_tour.json`).
- Added MGR Model Dock security-first recipe schema and offline readiness assessment (`forge/recipes.py`); no installation or execution yet.
- Added mesh triangle corruption/degeneracy inspection and conservative cleanup (`forge/meshqa.py`), not retopology.
- External licensing evidence was isolated to `research/external-provenance/`. Original 30 MGR areas expanded to 32 at this checkpoint.
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
- At that earlier checkpoint, only internal GLB tests had been run. The subsequent Windows Blender import verification is recorded at the top of this log.

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

The initial historical snapshot has been superseded by the current live inventory in `docs/WHAT-WE-HAVE.md`; Git history preserves its original wording if needed for audit.
