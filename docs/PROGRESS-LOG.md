# MGR 3D Forge — Progress and Evidence Log

## 2026-10-25 — MGR Light Sculptor + Optical FX live Windows proof

- Implemented two physically instantiated Blender point lights and a separate neutral witness mesh, plus Blender 5.2 node-based `Fog Glow` optical compositor. This verifies **light interaction and image-space compositing**, not light-transport physics or atmospheric scattering.
- Repaired two actual Blender 5.2 API mismatches while executing on Windows: `Scene.node_tree` was removed and the old Composite node was replaced by the compositor group's `NodeGroupOutput`; Glare type is now a socket menu, not a node property. Added fail-closed CLI detection of missing render/report when Blender exits successfully despite an embedded Python exception.
- Real Windows Blender 5.2.2 CPU Cycles rendered a 600×600 PNG showing the native portal and visibly illuminated matte witness; JSON audit records **2 point lights**, `Fog Glow`, emitted materials and `PASS`. **140/140** Windows and Linux tests PASS. Evidence: `evidence/blender/windows-wave7-light-glow.png` and `evidence/blender/windows-wave7-light-glow.json`.

## 2026-10-25 — Windows fantasy effect acceptance (supersedes prior pending note)

- Synced MGR Fantasy Forge to user Windows device; **139/139 Python tests PASS** on Windows and Linux. Used Blender **5.2.2 LTS** CPU Cycles to render two 600×600 portal phases at 0.25 and 0.75. Both render receipts **PASS**, each showing three material emission colors.
- Independently inspected both actual Windows PNGs: cyan ring, purple orbit and moving orange particles. Actual Blender PNG pixel evaluation recorded mean absolute per-channel difference **0.00897953** across 360,000 pixels (normalized channels 0–1). The two actual images and machine report are kept under `evidence/blender/windows-wave6-*`.
- This proves imported emissive geometry, two different temporal states and real Blender visual output. It does **not** prove physically simulated portal phenomena, glow/bloom, raytraced volume scattering or film-grade FX.

## 2026-10-25 — Fantasy/VFX/Magic expansion wave

- Added F51–F67 MGR-native feature queue (now 67 tracked areas) for sophisticated lighting/shadow, volumes, particles, elemental physics, portals, magic, illusion, transformations, compositing, color, motion graphics, sound-response, destruction, continuity and FX judging. Kept public technical vendor study separate from MGR product truth.
- Authored full 16-field `research/MGR-FANTASY-CINEMA-CREATION-HOWTO.md` and external official provenance ledger. These provide the build curriculum and honest gaps, not completed film-studio capability.
- Implemented CPU `forge/fx.py`: real 3D portal/spell-orbit/aura beams and animated-phase seeded spark geometry, 3 layers, structured receipts, low per-job particle limits. Added standard glTF emissive-factor export and actual Blender emission-preview bridge/CLI.
- Five new quality tests plus Blender bridge negative, local suite now **139/139 PASS**. Blender FX actual Windows preview remains pending at this checkpoint.

## 2026-10-25 — Expanded multi-capability build wave

- Owner extended scope to full director, camera and motion capability research. Added F44–F50 MGR-native capability queue (total now 50), native 16-field `research/MGR-DIRECTORS-CAMERAS-MOTION-HOWTO.md` and isolated official-documentation provenance.
- Added `forge/director.py` with typed nonoverlapping shot cuts, hold frames, focal presets and smooth/linear sampled motion curves. Refactored Blender cinematic bridge to bind **separate cameras** to timeline markers with per-shot held keyframes rather than accidentally interpolating a single camera across supposed holds. Blender re-verification pending at this checkpoint.
- Verified actual Windows Blender 5.2.2: **3 independent cameras, 3 bound cut markers**, frames 1–48, 49–96, 97–144, CPU Cycles scene saved and rendered. Windows and Linux Python suites each **129/129 PASS** for this director baseline.
- Added `bridge/blender_director_inspect.py` for independent saved-project timeline verification; augmented camera tours with a small deterministic middle-shot dolly, sampled camera-path AABB guard and new movement tests. The latest local suite now **132/132 PASS**; live new dolly proof pending.
- Owner Windows Blender 5.2.2 accepted new 3-shot scene with **three actual camera objects, three distinct camera-bound markers, 1 moving shot (7.21726m planned camera displacement), 2 locked shots**, and CPU Cycles PNG. Independent reopened `.blend` audit passed camera cuts at frames 1/49/97 with `frame_end=144`. **132/132 Windows tests PASS**. Added further receipt measurement from evaluated per-frame camera positions so planned motion is not confused with actually evaluated motion.
- Ran the improved inspector against the actual saved `.blend` on Windows: **PASS**, measured frame 49→96 camera motion **7.21726m**, first and third camera motions **0.0m**, three cameras bound to three cut markers. Saved audit as `evidence/blender/windows-wave5-director-motion-audit.json`.
- Added low-sample Blender timeline renderer (`bridge/blender_director_frames.py`, CLI `blender-director-frames`) to output four real cut/motion sample PNGs and measure motion-frame pixel difference. Pure Python suite **133/133 PASS**; Windows render acceptance pending.
- Verified on Windows Blender 5.2.2 with **133/133 Windows tests PASS**. Actual saved multi-camera project rendered frames **1, 49, 96, 97** via 4-sample CPU Cycles at 320×180. Frame 49 vs frame 96 measured **RGB MAE 5.98669**, with both visually inspected and camera parallax confirmed. Saved all four PNGs and machine receipt under `evidence/blender/windows-wave5-frame-*.png` and `windows-wave5-director-frames.json`.

- Windows machine (Blender 5.2.2 LTS) accepted **123/123 tests**, actual skinned 20-part / 11-bone mannequin, **48 dual-weight elbow sleeve vertices**, joint gaps **0.0m** at both frames and hand travel **0.427002m**. This is a partial elbow-weight demonstration, not a smooth full character.
- Blender imported actual world PBR: **5 Principled materials**, inspected metallic/roughness/colors, **PASS**. CPU Cycles rendered a 3-shot golden-hour reel to an editable **100,058-byte `.blend`** and **229,289-byte PNG**, **PASS** on execution. Visual inspection caught a framing issue (roof nearly fills image), so we corrected the shot planner to place cameras above the highest authored building and added generated-world AABB collision clearance + negative test. **Corrected image must be rerendered before calling cinematic visuals accepted.**
- Additional camera-clearance negative regression brought local suite to **124/124 PASS**.
- Reran camera-corrected 3-shot scene on owner Windows Blender 5.2.2 LTS: **PASS**. Corrected image **252,649 bytes** and Blender project **100,097 bytes**, visible world building, streets and context instead of initial cut-off close-up. Actual Blender artifacts stored under `evidence/blender/`. Overall output is still deliberately blocky CPU-generated geometry and low-sample cinematic QA, not film-quality assets.

- F11/F38: added independently exported left/right trouser meshes and left/right elbow sleeve garment meshes; 20 editable mannequin parts total with MGR wardrobe classification, complete inventory and assignment checking. These remain generic proxies.
- F12/F37/F39: added 2-bone normalized weighting for elbow sleeve meshes, dual-bone weight counts and Blender-evaluated normalized-weight QA. Existing 11-bone mannequin anatomy remains unchanged. Smooth skin on an entire continuous body is **not** implemented.
- F13: authored native PBR material recipes, range-validated glTF metallic/roughness overrides, and Blender Principled-socket inspector with fail-closed material quality checks. Full texture/UV pipeline pending.
- F31/F41: added native shot-plan checks, daylight/golden-hour/moonlit recipes, CPU Cycles scene/lighting/camera creation and actual `.blend`/PNG receipt command. Renderer runtime verification pending publication to Windows at this checkpoint.
- Build now exports a lighting recipe alongside its camera tour and applies native PBR params. Added ten material, wardrobe and cinematic acceptance tests plus two sleeve-weight regression tests and material-guardian test; **123/123 local tests PASS**.
- Official interoperable format/weight-paint research preserved under `research/external-provenance/PBR-AND-SKINNING-2026-10-25.md` with no external code copied.

## 2026-10-25 — Next wave: MGR pose integrity gate

- Implemented `forge/pose_guardian.py`: strict two-frame joint-continuity, non-stretching bones, all required bones, mesh skin coverage and real hand motion checks, with structured failure receipts. Explicitly **not** identity proof or smooth-skin acceptance.
- Implemented `bridge/blender_pose_inspect.py` and CLI `blender-pose-audit` to extract Blender-evaluated bone endpoints and mesh vertex-group coverage at frames 1 and 12. **Executed on the authorized Windows Blender 5.2.2 LTS device: PASS**. All 11 bones, 16 weighted mesh parts, 0.0m measured arm-joint gaps, 0.427002m hand motion; see `evidence/blender/windows-2026-10-25-pose-guardian.json`.
- Added seven positive/negative checks including missing hand, separated elbow, stretched bones, missing weights, frozen animation and NaN coordinates. **Local 110/110 and Windows 110/110 PASS**.

**This is a historical sequence, not the current status page.** The canonical current status is `docs/WHAT-WE-HAVE.md` plus `docs/IMPLEMENTATION-EVIDENCE.md`. Superseded historical claims are retained only as dated checkpoints.

## 2026-10-25 — First actual weighted Blender pose proof

- Extended modular armature bridge with optional `SKIN`: each detachable part gets a vertex group with 1.0 bone weights and a real Armature modifier. Added left/right upper-arm quaternion keyframes 1→12 and measured evaluated geometry, **0.428282m maximum left-hand vertex motion**. **This is rigid-segment skin weighting, not smooth production skin**.
- Blender 5.2.2 actually generated/reopened a **124,099-byte** skinned `.blend` with 16 mesh objects, 11 bones and 16 armature modifiers.
- Rendered both keyframes from a fixed Blender Workbench camera. Visual inspection confirmed changed arm positions; raw decoded RGB MAE **0.671411**. First QA incorrectly classified the whole image as foreground because of a gradient background; repaired render path to transparent RGBA and QA to use alpha. Corrected foreground: **40,564 / 39,265 pixels**; separate subject bounding boxes recorded.
- Added two negative/alpha-positive tests. Local Python suite **99/99 PASS**; latest Windows rerun of new source pending at this checkpoint.
- Pulled published commit `35f1b9c` onto Time's Windows machine. **99/99 Windows tests PASS**. Used `forge.cli blender-rig --skin` end to end with installed Blender 5.2.2: **PASS** 16 separate parts/11 bones; used `forge.cli blender-pose-render`: **PASS**, two PNG frames, RGB MAE **0.671411** and visibly different arm poses. This verifies the public CLI workflow, not just ad hoc scripts.
- Saved actual skinned Blender project and frame PNGs to `evidence/blender/`; full trace is in `evidence/blender/windows-2026-10-25-skinning.json`.
- Inspected owner PC without changing Windows settings: **Intel Iris Xe**, reported GPU AdapterRAM ~2 GiB (not assumed dedicated VRAM), physical RAM ~15.73 GiB. Added `forge/hardware.py` conservative local-model admission policy and four tests; heavy CUDA/VRAM jobs fail closed pending optional reviewed compute. Research receipt `research/MGR-COMPUTE-ADMISSION-2026-10-25.md`. Local suite **103/103 PASS**; Windows current-code retest pending.
- After publishing `966cace`, pulled latest source onto the owner Windows device and reran **103/103 tests PASS**. Source, hardware-admission tests, Blender pose outputs and evidence are all preserved on GitHub `main`.

## 2026-10-25 — Cross-view honesty and integrated creation pipeline

- Added `forge/view_identity.py`: cryptographic identity comparison for approved canonical/rest-mesh assets across different recorded camera/pose states, carefully distinguishing same verified **source asset** from merely matching filenames or appearances.
- Added image comparison tolerant of translation/scale and optional 90° **image-plane** rotation, with explicit `identity_proven=false` for silhouette similarity. Rotation of a 3D camera, altered 3D body pose and different models of one person remain unproven from images alone.
- Added `forge/pipeline.py` and CLI: build a new native world in an empty directory, optionally run actual Blender GLB import/render, record stage evidence, and optionally compare a fixed-camera baseline. No overwriting existing job output.
- Fixed a half-pixel mask normalization issue caught by new rotation tests. Local suite **93/93 PASS**. The actual Windows pipeline integration test remains pending at this checkpoint.
- On Time's actual Windows PC, pulled GitHub commit `5e05be7` and verified **93/93 unit tests PASS**. Ran two independent end-to-end CLI pipeline jobs: 10 buildings / 372 triangles / GLB import PASS / Blender render PASS. Second job compared rendered RGB against the first: **MAE 0.0 PASS** even though PNG file SHA differed (nondeterministic metadata/encoding). This establishes stable visible pixel output under the tested render settings, not semantic equality across different poses.
- Added pose-neutral template hashes to generic T/A mannequin export manifests; shared base confirms **same procedural source template** despite different pose, not an approved real person. New local suite **94/94 PASS**.
- Added `bridge/blender_rig.py`: 16 independently imported mannequin parts rigidly attached to an 11-bone armature, saved as editable `.blend` with machine-readable assignment receipt. Blender runtime acceptance pending. Rigid parenting is explicitly **not normalized vertex skin weights**.
- Windows reality check after GitHub commit `cf8b9a2`: **94/94 tests PASS**; Blender 5.2.2 imported all 16 separate GLB parts, built an 11-bone armature, saved a **120,608-byte** editable `.blend`, then reopened it successfully with **16 meshes and one armature**. Actual project preserved in `evidence/blender/modular-rig-example.blend`; proof receipt in `evidence/blender/windows-2026-10-25-rig.json`. This is an early rigid assembly, not deformable skinning.
- Added F40 MGR World Logic starter `forge/traversal.py`: sampled agent movement along known road graph, building contact rejection and explicit time/sample budgets; CLI emits an offline traversal receipt. **97/97 local tests PASS**. This is not an engine navmesh or real character gameplay.
- Pulled the exact GitHub `c0db6fe` onto Time's PC. **97/97 Windows Python tests PASS.** CLI road travel from `building-000-001` to `building-003-003`: **120 meters**, **321 sample frames**, zero building intersections in generated geometry. Evidence: `evidence/windows-2026-10-25-traversal.json`.

## 2026-10-25 — Larger build wave: scene facts, visual pixels, recoverable jobs, continuity

- Built MGR Code Architect starter (`forge/code_architect.py`): preview scoped multi-file text edits, enforce old-file SHA preconditions, block traversal/symlink paths, size/file budgets, atomic replacement and collision-aware rollback. **Not an OS sandbox or arbitrary Python/shell code runner.**
- Built MGR Visual Judge deterministic PNG engine (`forge/visualqa.py`): RGB/RGBA PNG decode with filter/CRC validation, exact RGB mean-absolute difference, foreground bounds and occupancy; strict camera/render-setting equivalence remains caller responsibility. **Not a semantic image model**.
- Built MGR Creation Memory starter (`forge/creation_memory.py`): SHA-chained JSON revisions, approved property locks, stale-head rejection, tamper detection. No authenticated owner identity or concurrent backing store yet.
- Integrated MGR Scene Consciousness facts into generated world bundles (`scene_facts.json` plus integrity manifest), added Blender scene-object inspection script and CLI entrypoint (real Windows Blender validation pending).
- Built `forge/repair.py` bounded trusted-callback repair loop: failed candidate automatically reverts, successful candidate persists, budgeted attempts stop. No untrusted callback execution or model-driven diagnosis.
- Reproduced on Time's actual Windows Blender **5.2.2 LTS**: CLI-generated world GLB imported into new scene-facts inspector, `status=PASS` and `objects=1` (GLB combines 3D scene into one mesh). Windows visual judge processed a real fixed-mannequin PNG: self-comparison RGB MAE **0.0 PASS**, comparison to a world PNG MAE **7.153049 FAIL** as expected; silhouette bounds reported. The visual judge cannot semantically identify missing anatomy.
- Initial Windows suite on commit `da3f6a9` ran 82 tests with one **test-harness error**: Windows symlink creation privilege (`WinError 1314`) prevented the symlink fixture. Fixed the fixture to handle unavailable symlink creation privilege without skipping traversal tests. **Re-ran on Windows after GitHub commit `7133476`: 85/85 PASS**.
- Expanded negative regression tests; local **85/85 PASS** and owner's Windows **85/85 PASS** at this checkpoint. This is functional early groundwork, not production acceptance.

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
