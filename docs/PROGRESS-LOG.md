# MGR 3D Forge - Progress and Evidence Log

## 2026-10-27 - F108 segmentation adapter contract

- Added `forge/segmentation.py`: runtime-checkable `SegmentationAdapter` protocol, `ManualMaskAdapter` (always available, never claims inference), `UnavailableAdapter` (honest refusal), `AdapterRegistry`, `build_default_registry()` (manual only), `describe_registry()`. No neural model shipped; `neural_adapter_installed` is False unless an inferred adapter is registered and available. 7 tests in `tests/test_segmentation.py`. Test count now 445 PASS.
- Open: SAM3 adapter behind a gated optional dependency with model version + licence record under `research/external-provenance/`.

## 2026-10-27 - F107 multi-view silhouette reconstruction (space carving)

- Added `forge/multiview.py`: measured orthographic silhouettes become a real triangle GLB/OBJ visual hull through CPU space carving. Back/right masks are mirrored before carving (they are seen from the far side); front/back and left/right scale/height consistency is checked; a voxel fit gate requires worst-view IoU >= 0.97 or the export is refused. Honesty fields are hard-coded `hidden_surface_inference=False`, `identity_verified=False`, `external_api_calls=0`. Export is byte-deterministic and writes `hull.glb`, `hull.obj`, `hull.mtl`, `reconstruction.json` with SHA receipts.
- Added `tests/test_multiview.py` (25 tests) covering cube/humanoid phantom recovery, mirror handling, scale/size/height rejection, empty/missing masks, threshold validation, determinism, CLI end-to-end, and `score_against_solid` against an analytic solid (exact cube = 1.0 IoU; T-shaped overfill case = 0.625 IoU; rejection of unusable solids).
- Added CLI actions `reconstruct-silhouette` and `reconstruct-score`, plus `scripts/make_phantom_silhouettes.py` (self-authored analytic box-humanoid phantom, no private references) and `scripts/hull_resolution_sweep.py`.
- Added `examples/multiview-phantom/` (front/back/left/right PNG masks + spec + truth). Independent accuracy: 0.8697 hull-vs-solid IoU at grid 64, 0.01393 m^3 overfill (12%), 0.00216 m^3 missed. Resolution sweep shows 0.847-0.878 IoU across grids 48-96 while triangles grow 14664 to 57088: the residual is view ambiguity, not voxel size. Grid 40 is refused by the fit gate.
- Live Blender 5.2.2 verification: imported `hull.glb` into an isolated collection, measured 1 mesh / 25744 triangles / 51488 vertices / bbox 0.6 x 0.265625 x 1.74375 m, then removed the collection and purged orphans; scene restored to 1143 objects and was not saved. Evidence: `evidence/blender/windows-wave25-multiview-hull.json` and `...-sweep.json`.
- Test count: 438 PASS (413 prior + 25 new F107 tests). No fabricated QA; every claim above is backed by a committed receipt or a reproducible command.
- Open next: neural segmentation adapters, oblique-view carving, marching-cubes smoothing, fitted textured full-volume mesh, identity likeness proof, engine import/play, owner-approved Tevin reconstruction.

## 2026-10-25 — F104 deforming animation export research and implementation

- Added a fixed Blender 5.2-compatible animated GLB export path that requires a real armature modifier, vertex groups and measurable skinned mesh movement across frames; new outputs only. Added independent Blender receiving-import script checking actual armature, skinned meshes and animation actions.
- Added guarded CLI actions `character-motion-export` and `character-motion-reimport`, SHA binding and seven denial/tamper/overwrite tests. Actual Windows Blender run was attempted but the remote desktop connector returned **user rejected MCP tool call**. Permission boundary respected; runtime status is **UNVERIFIED**, not FAIL or PASS.
- Research sources: Blender glTF export operators and Khronos glTF 2.0 animation/skins: `research/external-provenance/CHARACTER-MOTION-SOURCES-2026-10-25.md`. Game-engine receiving proof remains open.


## 2026-10-25 — F101/F102 character evidence and rig readiness

- Added original `character-readiness` report: source SHA, named mesh and primitive/material inventory, UV presence, per-primitive joint-weight signals and skin bindings.
- Added negative structural gates for unbound/broken skins and mismatched inverse-bind matrices. Mesh names do not automatically prove garment identity; structural rig data does not prove pose deformation or anatomical likeness.
- Blender intake now records every imported editable mesh object's materials, armature modifiers, vertex groups and shape keys. **Connected Windows 5.2.2 LTS passed** import/save and an independent fresh-process reopen with matching SHA. All **376/376 Windows Python tests PASS** (27.153s); Linux 376 PASS with 30 network skips. Exact receipt: `evidence/blender/windows-wave24-character-readiness.json`.
- Relevant original Khronos/Blender research and legal traceability: `research/external-provenance/CHARACTER-READINESS-SOURCES-2026-10-25.md`.

## 2026-10-25 — F103 non-destructive character material part separation

- `character-separate` opens admitted character `.blend` in actual Windows Blender 5.2.2, splits selected mesh by material into a **new** `.blend`, preserves source, and emits each object's materials, triangle count, vertex group and armature modifier inventory. Original source is untouched.
- Windows proof: generic test mannequin went from **1 original mesh object** to **7 separately editable objects**, matching seven source material regions and **264/264 conserved triangles**. New file saved, then an independent Blender process reopened all **7** meshes and confirmed original GLB fingerprint. This enables selecting/removing/adjusting material regions, not verified semantic garment segmentation.
- Rig still absent on test source; human likeness, actual Tevin components, extreme pose deformation and runtime outfit swapping remain open.
- Final verification of the extended wave: **381/381 Windows Python tests PASS** in 27.608 seconds, no skips; **381/381 Linux PASS** with 30 loopback-dependent skips. Saved source, separation and reopened artifact were independently checked by installed Blender, with evidence `evidence/blender/windows-wave24-material-separation.json`.


## 2026-10-25 — First end-to-end interactive world program (F87)

- Replaced the checkpoint-only finish line for this slice with a user-openable **offline WebGL2 world**: actual Forge world GLB + metadata compile into one portable HTML with 3D triangles, direct movement, mouse look, bounds-based building collision and FPS telemetry. No CDN, paid API or server needed.
- Added original `viewer/runtime.js`, `viewer/template.html`, `forge/web_runtime.py`, `forge.cli world-flight`, `tests/test_web_runtime.py` and `demos/mgr-world-flight.html`. Generated a deterministic example from `examples/neighborhood.json` with **10 buildings, 372 triangles**, GLB SHA-256 `7c799190167d1255a5cbfbbb01fb4959a39b1441a8db78509365fcaa673c6cfa`. The packaged offline HTML contains the complete actual 3D geometry (46,592 bytes).
- Compiler guards: strict GLB receipt, model size cap, no overwrite, malformed world rejection. `node --check viewer/runtime.js` PASS; Python tests pass. **A browser/GPU visual test is required next** before declaring real-time playback verified. See `research/MGR-LIVE-WORLD-RUNTIME-CONTRACT.md` for honest limits.
- **Windows browser visual acceptance:** pulled commit `b0c0c64797f2b6e8cef261273d7659f603b12ba0`, opened `demos/mgr-world-flight.html` in real Chrome headless with ANGLE SwiftShader. Actual 1280×720 screenshot **shows the 3D city geometry, material colors, street network and HUD**; saved `evidence/browser/windows-wave13-world-flight.png` + JSON receipt. This proves browser rendering, not measured continuous FPS or physical keyboard input. Separately **216/216 Windows Python tests PASS** (exit 0; 3.265s test runtime) and Linux **216/216 PASS**.

## 2026-10-25 — Native asset transport, format parity and motion-contact wave

- **F83:** Built `forge/asset_parity.py`; validates independent counts of actual GLB and OBJ vertices/triangles, compares three-axis geometric bounds under a strict numeric tolerance, and detects tampering and invalid input. `forge.cli audit-export` emits a nonoverwriting JSON receipt. Actual generated six-building world passed the CLI parity audit. This does not demonstrate material or game-engine render parity.
- **F84:** Built `forge/cell_transport.py`; reads actual local GLB cell files, verifies SHA-256 and size, enforces a memory budget, tracks real disk reads, honors active-cell priority and returns missing/tampered-cell failures. `forge.cli load-cells` produces a receipt; still synchronous CPU disk data, not game GPU/network streaming.
- **F85:** Built `forge/dynamics.py` with continuous actor-segment contact against conservative expanded bounding rectangles to catch thin-wall tunneling. Positive/negative tests cover earliest-hit, ordering, motion rejection and invalid numbers. Not a complete rigid-body solver or skeleton physics binding.
- Added detailed 16-field native engineering packet `research/MGR-RUNTIME-FOUNDATIONS-WAVE.md`, mapping source study and explicit production acceptance for F82–F86. Original external rights remain separated.
- Added real CLI cell I/O and corrupt-cell receipt tests. `python3 -m unittest discover -q`: **212/212 tests PASS Linux**; separately pulled GitHub `main` commit `d48efabc3eabcccbf32a1b8890d28ea38ce934fd` to Time's Windows machine and ran `py -3 -m unittest discover -q -s <repo>\\tests -t <repo>`: **212/212 PASS Windows** (exit code 0, 2.291s unittest runtime). The integrity-negative fixture correctly emitted `PARTIAL_FAILURE` while the test passed. A second external game-engine import remains unverified.

## 2026-10-25 — Open-system research expansion + MGR-native layered scenes

- Added 24 additional open-engine/physics/AI/world research families in `research/OPEN-SYSTEMS-RESEARCH-QUEUE.md`, separate from the 20 foundational domains and the 24 studio/academic source families. Inspected selected first-party source/rights pages; not every module, model, talk or paper. Tracked exact access/rights in `research/external-provenance/OPEN-SYSTEMS-SOURCES.md`.
- Implemented `forge/scene_layers.py` field-level scene layering, deterministic hashing and author attribution, explicit deletion and reintroduction, bounds/NaN/path validation, and five tests in `tests/test_scene_layers.py`. **A native authoring prototype; not OpenUSD implementation or film renderer.**
- New CLI `compose-scene --layers examples/layered-scene.json --out ...` accepts owner-authored JSON, generates an evidence receipt and refuses overwrite. Added real fixture and two more CLI tests.
- `python3 -m unittest discover -q`: **194/194 PASS Linux**. New Windows regression and cross-engine import remain unverified. Prior Windows Blender 5.2.2 real studio scene render is evidenced by `evidence/blender/windows-wave12-studio-witness.json`.
- Native register expanded F82–F86; only F82 is scoped CPU-implemented. F83–F86 queued with explicit independent runtime acceptance.

## 2026-10-25 — 24 external source families + ten studio-quality native test contracts

- Corrected research scope to **24** separate external source families (SIGGRAPH plus 23 numbered targets, with GDC distinct from Weta/ILM/DNEG), all tracked in `research/SOURCE-INTELLIGENCE-QUEUE.md`. R01–R10 each have technical source-audit chapters and five paired provenance ledgers; R11–R20 research in progress; R21–R24 next. These are selected paper/spec/source inspections, **not** claims of total institutional source mastery.
- Began independent studio-quality implementation alongside source reading: `forge/studio_quality.py` has ten bounded native validation/proof functions: material parameter check, camera-budgeted light plan, absorption reference, mesh-edge guard, strand motion consistency, pure scene layering + hash, chunk streaming plan, screen-space landmark drift, calibrated anatomical multiview reprojection, and atmosphere density continuity. Negative-case suite in `tests/test_studio_quality.py` and new `forge.cli studio-proof` materialize machine-readable receipts. Their limits are explicit; none replaces production physics, BRDF, full-body semantic vision, or a live engine.
- Local Linux suite after adding ten studio contracts: **186/186 PASS**, `python3 -m unittest discover -q`; `git diff --check` clean. Latest Windows verification for this new code is pending publication.
- Finished all **24/24 selected-technique source audit chapters** with 14 source provenance ledgers (ten paired and four individual); each marks inaccessible proprietary code, closed model weights, paper-only claims and legal rights explicitly. The exact source queue is `research/SOURCE-INTELLIGENCE-QUEUE.md`; these audits are not exhaustive catalogs, source-level parity or patent clearance.
- Added `bridge/blender_studio_witness.py` and `forge.cli blender-studio-witness`, an original editable `.blend` + CPU Cycles PNG fixture with three PBR/SSS materials, two actual point lights, a real Blender curve and low-density volume. Unit-tested typed outputs, nonoverwrite and script presence. Current Linux suite **187/187 PASS** and `compileall`/whitespace checks pass. Independent Windows render receipt is required before this real Blender witness is marked verified.

## 2026-10-25 — Five simultaneous foundations plus native validation

- Five distinct 16-field sourced research packets and source ledgers now cover S01 vision, S02 optics, S03 geometry/slicing, S04 camera-transform algebra and S05 continuous motion/calculus. These are foundations, **not** full upstream audits or a claim S06–S20 are finished.
- Native checks expanded: calibrated parallel-camera stereo triangulation with depth/reprojection rejection; surface edge-incidence checks for open/degenerate/nonmanifold triangle meshes; sampled movement speed and acceleration guard. Full rotated cameras, oriented watertight meshes, robust correspondence and physically solved trajectories remain open.
- Complete-source CLI compilation/tail regression prevents the previous truncated GitHub upload defect. **168/168 local Linux tests PASS**. The last confirmed Windows run was 153/153; new Windows verification is pending publication.
- Next simultaneous research batch is S06 physics, S07 rendering, S08 game runtime, S09 sculpting/modeling and S10 skeletal motion, alongside production coding.
- **Windows first full foundation replay: 168/168 PASS** on Time's machine, fast-forwarded from published `main`; machine-produced proof `evidence/blender/windows-wave10-spatial-truth.json` independently confirms a calibrated parallel-view 3D point (0,1,4)m, zero reprojection error and box-edge counts. Subsequently added native **oriented** camera stereo with proper-rotation validation and additional negative tests; **170/170 Linux PASS**, Windows retest of oriented-camera addition still due.
- Finished five more research chapters S06–S10 in the same wave: physical solvers, graphics, playable worlds, production sculpt/garment pipelines and rigging/motion. Ten of twenty research domains now have individually sourced 16-field engineering packets; implementation gaps are explicit.
- Added **oriented two-camera** triangulation with proper right-handed matrix validation, source reprojection and negative tests. Hardened sampled motion against representational overflow. Added deterministic active/prefetch/evict **residency planner**, explicitly not a running game-streaming engine. **175/175 local Linux tests PASS**; post-addition Windows replay pending.
- S11–S15 dispatched as the third simultaneous research batch. No external runtime or model code copied into MGR implementation.
- S11–S15 **completed** as five additional 16-field source packets: procedural world DNA/seam controls, multi-camera observation truth, photogrammetry/metric scale, LiDAR/point-cloud registration, and GPU/console hardware admission. Fifteen of twenty research packets completed; fourth five S16–S20 launched in parallel. This is documentation/engineering research maturity, not feature/runtime acceptance completion.
- S16–S20 **completed**: neural generative 3D and license/hardware reality, headset presence, AR anchor/drift, biological growth/creature form, and mathematically bounded higher-dimensional/fantasy ideas. **20/20 scoped 16-field research packets and 20/20 external source ledgers written**. Not 20/20 production features, nor a claim that all papers/codebases are exhaustively audited.
- Owner challenged whether film/game studio technical sources were truly represented. Verified targeted primary research from film-studio papers/technical libraries, SIGGRAPH 2025 game-rendering courses, developer conferences and real engine documentation; separated provenance in `research/external-provenance/STUDIO-ENGINE-PRIMARY-SOURCES-2026-10-25.md` and translated findings into 10 original MGR-native experiments in `research/MGR-STUDIO-TO-NATIVE-ENGINE-LESSONS.md`. Full source-tree reading and quality parity tests remain open.
- **Published the twenty-packet foundation and MGR-native production overlay to GitHub `main` commit `32574c3cc4e8c16598d78fcb94d7fdee798743fd`.** Windows fast-forwarded to that same commit and passed **175/175 tests** (Linux also 175/175). A separate real Windows CLI proof reconstructed a fixture world point `(0,1,4)` meters from nonparallel cameras with 0-pixel reprojection errors, logged as `evidence/blender/windows-wave11-oriented-stereo.json`. These are calibrated fixture tests, not independent photo-correspondence discovery or Tevin likeness verification.

## 2026-10-25 — Reality-to-Space expansion beyond Blender

- Owner broadened 3D research to 20 scientific/computing domains plus physical 3D printing/slicers and console world architecture. Built the MGR-native 20-domain map `research/MGR-REALITY-TO-SPACE-MASTER-MAP.md`; isolated official literature/API/engine/slicer references in `research/external-provenance/REALITY-TO-SPACE-SOURCES-2026-10-25.md`. Current status is architectural decomposition + source review, not end-to-end mastery of 20 disciplines.
- Added F68–F71 to the MGR native build register (now **71** tracked areas). High-leverage discovery: monocular image pixels have no unique depth without additional evidence; printer slicers need an already-authored mesh, then section triangles into layers; console-scale worlds demand streamed/visible geometry budgets.
- Implemented `forge/spatial_truth.py` as deterministic CPU pinhole projection, camera-pixel unit ray, and capped Y-plane/triangle intersection producing XZ section segments. New `forge.cli spatial-proof` materializes an explicit two-depth/one-pixel example with 8 cross-section segments through a generated box. Seven positive/negative/reproducibility tests expanded both Windows and Linux to **153/153 PASS**. Windows proof: `evidence/blender/windows-wave9-spatial-truth.json`.
- Fixed a GitHub publication defect where a CLI file was uploaded only through line 450; compared the full published Git blob SHA against the local file and reran all tests plus actual spatial-proof on Windows. The full file and branch are now verified. No actual G-code printer path, image-to-3D reconstruction or console runtime claimed.

## 2026-10-25 — MGR FX Judge live acceptance

- Implemented `forge/fx_judge.py` and `forge.cli judge-atmosphere` to compare matched real PNGs with a configurable RGB MAE threshold. The control must declare volume density zero; the candidate must declare positive density and `ShaderNodeVolumePrincipled`. Different cameras, lights, emissive materials, render status, fake volume or unchanged pixels are rejected rather than called progress.
- Windows Blender rendered actual fixed-camera control and fog images; native `judge-atmosphere` reported **PASS**, **RGB MAE 22.37957/255** against a threshold of 3.0. On both Windows and Linux **146/146 tests PASS** including five new negative/positive judge cases. Exact machine receipt: `evidence/blender/windows-wave8-judge.json`.
- This visual gate proves scene difference under controlled renderer conditions, not artistic film-grade quality or physically measured atmospheric correctness.

## 2026-10-25 — MGR Atmosphere Field Windows volume acceptance

- Built `--volume-density` (strict finite `0..0.25`, 0 disables medium) and `--volume-style uniform|cloud` in the Blender FX command. Windows Blender 5.2.2 Cycles accepted a real `ShaderNodeVolumePrincipled` participating medium, anisotropy and point-light illumination. Cloud mode adds a bounded procedural noise-driven density material in an ellipsoidal volume proxy.
- Actual matched 600×600 Windows renders: no-volume control, uniform atmosphere, and cloud-style atmosphere. Visual inspection showed distinct blue/warm scattering through the authored portal scene; uniform cube had a hard rectangular edge, while cloud was curved but still clearly bounded. Blender image comparison: uniform vs control **0.06582227** normalized RGBA MAE, with **156,410 / 360,000 pixels** differing by more than .05 in an RGB channel; cloud vs uniform **0.02924215** normalized RGBA MAE.
- **141/141** Windows and Linux tests PASS, including negative density and style validation. Actual images and JSON scene receipts are under `evidence/blender/windows-wave8-*`. This is real volume light scattering in Cycles, **not** simulated smoke dynamics, soft volumetric boundaries, physically authored weather or playable real-time atmospheric lighting.

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
## 2026-10-25 — Editable world to actual 3D re-export (F88)

- Delivered the **MGR Live World Editor** in `viewer/runtime.js`, `viewer/template.html`, and self-contained `demos/mgr-world-editor.html`: choose a building, move it along X/Z, adjust its height and material (brick, stone, blue, gold, emerald), reset, save/reload JSON, and preserve current edits locally where browser storage allows.
- Delivered `forge/world_editor.py` and `forge.cli apply-world-edits`. Exported browser JSON is checked against original SHA-256 and strict building identity/size bounds, then CPU rebuilds genuine geometry and new GLB/OBJ/MTL/SVG, a complete artifact inventory and new offline WebGL2 page. No paid API or AI inference. Input world is not changed and target directory must be new.
- Extended OBJ custom material support and SVG palettes. Seven new unit tests cover the generated-file loop, deterministic exports, tamper rejection, invalid geometry/identity, oversized input, non-overwrite and original immutability. **223/223 tests PASS on Linux and Time's Windows device**. Chrome headless ANGLE SwiftShader rendered the 3D world with visible editor controls; screenshot and truth limits in `evidence/browser/windows-wave14-world-editor.json`. **Windows CDP automated interaction PASS:** edited a real building, checked saved localStorage JSON, verified a real downloaded edit JSON file, re-imported the original and reset successfully (`tests/browser_editor_smoke.mjs`). Manual physical UI interaction remains untested.
- Scope honesty: this creates editable cuboid buildings and material presets, not arbitrary sculpting, photoreal effects, animation editing or studio parity.

## 2026-10-25 — Spatial object selection and recoverable editing (F89)

- Added real browser-screen ray/AABB picking against authored 3D world geometry; click a building to select it without searching its ID in a form. Camera drag still rotates and is distinguished from a click via a five-pixel movement threshold.
- Added recoverable edit history with bounded 80-entry undo stack, redo stack, Ctrl/Cmd+Z, Ctrl/Cmd+Y, Shift+Ctrl/Cmd+Z and disabled-button state. Changes, resets and imported edits participate; no-op edits do not create false checkpoints.
- Rebuilt the canonical offline `demos/mgr-world-editor.html` with new controls while preserving its old published version in Git history. Windows Chrome now passes **ten real editor checks**: real building edits, history travel, local persistence, downloaded JSON, import, reset, 3D ray selection, canvas mouse click selection and actual KeyW camera navigation. Screenshot + receipt: `evidence/browser/windows-wave15-spatial-editor.json`. **223/223 Python tests PASS on Linux and Windows.**

## 2026-10-25 — MGR Creation Director, text-to-real geometry (F90–F93)

- Added collapsible MGR Creation Director sidecar. Typed prompts compile into allowlisted actual scene changes; optional browser speech transcribes into a **reviewable** command, never arbitrary Python. Photo uploads preview as local references only; no image-to-mesh model claim.
- Expanded scene editor to create, duplicate and remove independent buildings and to resize width/depth. `forge/world_editor.py` accepts tightly bounded `mgr-created-####` IDs and deleted/reordered base buildings, with source SHA and dimensional checks, then emits genuine GLB/OBJ/MTL/SVG/HTML.
- Added research specification `research/MGR-CREATION-DIRECTOR-CONTRACT.md` and segregated Web Speech/File API standards provenance. F92 real picture reconstruction and F93 spoken Python execution remain separate research gates, NOT BUILT.
- **Verified on Time's Windows machine:** real Chrome headless WebGL2 passed all **16/16 browser checks**, including live text creation/change, collapsible chat, arbitrary-code rejection, duplicate/delete and pixel-sampled image-to-material editing. **227/227 Python tests PASS** on both Linux and Windows; Windows full command exited 0. See `evidence/browser/windows-wave16-creation-director.json`. The source HTML and geometry exporter are genuine, but these tests do not prove arbitrary image-to-3D reconstruction or microphone dictation accuracy.
- Image preview has an optional material sampler: it downsamples a locally loaded PNG/JPEG/WebP, averages visible pixels, and applies the nearest native material preset to the selected real building. This change participates in edit history and the JSON-to-GLB rebuild. It does **not** fabricate geometry from the picture.

## 2026-10-25 — MGR Editable Blender World Handoff (F94)

- Added `forge/live_blender.py` to inspect edited-world geometry fingerprints, reject altered/malformed source, cap input sizes, protect existing outputs and run a fixed Blender script instead of executing user-authored Python.
- Added `bridge/blender_live_scene.py`: independently selectable building meshes preserve MGR IDs, dimensions and materials. Native Blender scene gains ground, lighting, camera and saves to a new `.blend` file alongside a JSON receipt.
- Added CLI `blender-live-scene --world EDITED_BUNDLE --blend NEW.blend --report NEW.json --binary BLENDER_PATH`.
- Five new adversarial tests cover source fingerprint mismatch, absent edit provenance, output overwrite and missing executable. **232/232 local Python tests PASS**; live Blender verification is a separate gate.
- **Actual Windows Blender 5.2.2 LTS verification PASS:** native 102,983-byte `.blend` created with five independently editable ID-bearing buildings including `mgr-created-0001`; a fresh Blender process reopened it and verified the five object IDs and live camera. Another Blender process rendered a real 640×400 PNG. Fixed a Blender 5.2 EEVEE enum incompatibility and a Blender false-zero-exit without a receipt; added regression, bringing **233/233 tests PASS on Windows**. See `evidence/blender/windows-wave17-live-creation-scene.json` and rendered image.

## 2026-10-25 — Larger connected creation wave, source pixels and Blender roundtrip (F95–F96)

- Built `forge/image_relief.py`: strict bounded PNG parser (CRC, 8-bit grayscale/RGB/RGBA, no interlace, all five standard PNG row filters), reproducible real mesh columns proportional to actual image luminance, independent GLB inspection, OBJ/MTL output, source fingerprint and inventory receipts. This is image-derived **2.5D** geometry; hidden surfaces are **not inferred**.
- Built two-way fixed-script Blender bridge: Forge world edits → `.blend` with embedded source provenance → edit native buildings in Blender → `blender-to-forge` transforms → SHA-validated original JSON contract → new world GLB. Custom arbitrary Python from text or voice remains forbidden.
- Added a 59-case generated filter/bounds/corruption PNG regression set plus roundtrip negative tests and separate end-to-end Blender smoke scripts. **Actual Windows Blender 5.2.2 verified both** a 192-triangle pixel-derived GLB import and a full real `.blend` edit→Forge export→SHA-validated rebuilt five-building GLB. Native building transform changed to X=1.25 and height=19.0 during the independent roundtrip.

## 2026-10-25 — MGR Local Creation Workstation (F97)

- Connected the previously separate browser and CPU tools with a loopback-only HTTP Studio in `forge/studio_server.py`. A per-session random token, exact JSON routes, origin check, bounded requests and separate per-job storage guard against unrelated personal-file access.
- Browser Creation Chat now exposes optional `Create 3D Relief (PNG)`, `Build Edited World`, and `Open in Blender Project` actions **when served from the local workstation**. Offline self-contained HTML still works without a server; advanced buttons remain disabled there.
- Added `python -m forge.cli serve-studio --world WORLD_FOLDER --workspace NEW_FORGE_WORKSPACE --port 0 --blender BLENDER_EXE`, which prints an OS-assigned loopback URL. Generated GLB/Blender outputs are downloadable through job-scoped URLs; no paid API, no arbitrary user script execution.
- Added 19 HTTP authorization, path, PNG download, async Blender-job lifecycle and duplicate-submission tests. Local Linux runner forbids localhost sockets: **317 local tests PASS, 19 skipped** there. **317/317 Python tests passed on Windows in 29.183 seconds, zero skips; process exited 0.**
- **Windows creation proof:** Chrome submitted a 16×16 PNG and a browser-edited world via the actual localhost service. Both real GLB download links appeared. Blender generated an actual editable 10-building `.blend` within the same job. The initial browser acceptance capped the wait too tightly, so Studio now starts a background Blender job and the real-browser acceptance waits up to three minutes; full download-button verification is being rechecked.
- **Final connected browser proof PASS:** The revised real Chrome CDP chain completed with exit code 0 in **106.29 seconds**. All six checks passed, including actual HTTP GET/200 of the Blender `.blend`, relief `.glb`, edited world `.glb` and editor `.html`. Reproducible evidence: `evidence/browser/windows-wave20-local-studio.json`. This is a native Windows loopback workflow, not a hosted public studio.

## 2026-10-25 — Persistent Blender job receipts and interruption recovery (F97 follow-on)

- Blender job transitions now write bounded atomic `blender-state.json` receipts inside their job directory. A newly started local Studio can recover success/failure receipts, and reports any orphaned `RUNNING` record as an interrupted job instead of claiming that a vanished worker is still running.
- A Blender subprocess timeout now produces a visible failed-job result. Repeated clicks within the live process continue to share one worker, rather than launching duplicate conversions.
- Four additional HTTP-backed tests exercise recovered failure, interrupted-worker recovery, invalid receipt isolation and atomic file replacement. **321 local unit tests PASS** (23 network/socket tests skipped under Linux sandbox restrictions). **All 321/321 tests also PASS on Time's Windows machine in 27.641 seconds with zero skips; process exit 0.**
- This addresses process-restart truthfulness; it does **not** make Blender jobs independently resumable after process termination. Full durable background worker orchestration remains open.

## 2026-10-25 — Engine-target handoff (F98)

- Added `forge/engine_handoff.py`, `godot-handoff` CLI and Studio `/api/godot` export. A SHA-verified MGR authored world becomes a genuine Godot 4 source project: `project.godot`, `world.tscn`, original GLB under `assets/`, per-building collision body preserving authored MGR identity, ground collider, preview camera, and directional light. The Studio delivers the files as a project ZIP.
- Added independent contract tests for complete package, original GLB identity, collider counts, scene entry, nonoverwrite, corrupted GLB, invalid manifest, duplicate identity, nonfinite collision bounds, CLI and Studio endpoints. **335 local tests PASS; 26 HTTP tests skipped because the Linux sandbox forbids loopback binds.** Connected Windows acceptance and real Godot 4 runtime import remain separate proof gates.
- Project intentionally records `engine_import_verified=false` until a real Godot execution can prove import, rendering, collision, and material results. No game-engine installation, credentials, or paid API used.
- **Actual Windows verification PASS:** 335/335 Python tests completed in **142.775 seconds**, process exit 0, no skips. Chrome CDP completed the extended **7/7 connected creation checks**, including actual download of the generated Godot ZIP, revised world GLB and editable Blender `.blend`, process exit 0 in **144.94 seconds**. See `evidence/browser/windows-wave21-godot-handoff.json`. Tests ran concurrently on the same device, increasing wall time relative to isolated earlier suites. The Godot receiving engine is not installed in the accessible Windows PATH, so no import/play claim is made.

## 2026-10-25 — Character candidate admission and editable Blender handoff (F99–F100)

- Added `character-intake` CLI to take an existing real `.glb` candidate, inspect independent geometry/hierarchy/skin/animation/morph evidence, record the original SHA and preserve original bytes in a new dedicated output folder. It never generates a likeness, fabricates skin weights, or claims clothing/hair are separate when the source is merged.
- Added `character-blender` fixed-script CLI and `bridge/blender_character_intake.py` for actual Blender import → editable original-mesh project `.blend` → evidence receipt, with source-SHA verification, no arbitrary user Python and no overwrite.
- Added 13 negative/adversarial tests for corrupt files, missing source, fake identity, unrigged warning, expected bounds, size caps, tampering, nonexistent Blender, suffix validation, CLI and preservation. **348 Python tests PASS locally**, with 26 HTTP tests skipped by socket-restricted Linux. Actual connected Windows Blender acceptance required before labeling F100 VERIFIED.
- **Connected Windows Blender 5.2.2 proof PASS:** `character-intake` preserved the SHA-bound generic T mannequin; `character-blender` saved a real editable `.blend` with **one mesh object, 264 triangles, zero armatures and source SHA `90a98b906c865c64e185ea90505b2a7a67c5e5b390800436288b3aa1a0e20e1f`**. This is correct candidate admission, **not** human likeness acceptance or skinning. Added `character-reopen` for independent fresh-process verification, four extra negative tests; **352 local tests PASS**, 26 skipped for restricted HTTP sockets. Reopen and latest Windows suite remain pending.
- **Independent Windows reopen PASS:** fresh Blender 5.2.2 process loaded the persisted `.blend`, found 1 mesh and 264 triangles, and matched source SHA on the scene and mesh. Final **352/352 Windows Python tests PASS**, 0 skipped, **23.211 seconds**, process exit 0. Consolidated proof at `evidence/blender/windows-wave22-character-intake.json`.
- Connected the candidate intake to local Creation Chat: choose a real `.glb` file (currently up to 900 KB in-browser), click **Inspect / Preserve 3D Model**, download an unchanged source and evidence JSON. This does not reconstruct a character from photographs or pretend a world mesh is human. Added 4 HTTP tests and a real-browser GLB-upload step, making **356 local tests PASS** (30 HTTP tests skipped only in the restricted Linux environment); Windows verification pending.
- Backwards audit found the older Forge-only `inspect_glb` validator rejected normal external glTF data such as `TEXCOORD_0` VEC2 UVs and 16-bit unsigned-short indices. Added independent `forge/character_glb.py` with bounded standard component/type handling, accessor offsets/strides, index range verification, and explicit rejection for sparse/compressed geometries that need a separate decoder. Added 8 more positive/adversarial tests, bringing **364 local Python tests PASS** (30 socket tests skipped). Windows full suite and browser admission QA pending.
- Refreshed canonical self-contained `demos/mgr-world-editor.html` from the current source UI and runtime with `scripts/refresh_offline_demo.mjs`. Preserved the prior embedded world's exact SHA-256 and geometry. Offline Chat now visibly contains the new model-upload and game-engine controls, which correctly remain disabled without a localhost workstation. The refresh tool stops on a missing/mismatched original fingerprint.
- **Windows browser acceptance PASS:** 8/8 CDP checks completed, including real GLB file upload and downloading an untouched `candidate.glb` plus inspection JSON, along with edited world, Godot project and Blender `.blend`. Process exited 0 in **32.78 seconds**. Windows regression first reported one `WinError 10053` socket-abort in a tokenless-upload test; a complete independent rerun passed **364/364** tests in **25.625 seconds**, exit 0, zero skips. The intermittent failure is retained in `evidence/browser/windows-wave23-model-admission.json` rather than concealed.

## 2026-10-25 — F105 private multiview character references

- Added a single-batch PNG reference intake with separate jobs for the body, face, feet and outfit parts; no private image files are checked into this repository.
- Owner approval is recorded independently of geometric/identity verification. Approval proves the owner selected the visual reference; it does **not** prove orthographic geometry, mesh generation, rigging or an engine import.
- Validated one private 18-entry, 16-distinct-PNG owner-approved reference batch and produced a SHA-bound local JSON receipt. Six new owner-approved body/face/feet sheets are included, along with prior outfit component sheets. Sheets still require per-view extraction and actual 3D modeling.
- `python3 -m unittest discover -q` **397 tests OK**, **30 skipped** because of restricted sockets; Blender proof is not newly claimed.

## 2026-10-25 — F106 Unclothe 3D native approval/separation boundary

- Selected primary research into Meta SAM3/SAM2, Microsoft TRELLIS.2 and Tencent Hunyuan3D. Model inference, exact code/weights licenses, local GPU feasibility and actual quality are not yet verified; see `research/external-provenance/UNCLOTHE-3D-SOURCES-2026-10-25.md`.
- Implemented a real, reversible production-admission boundary: semantic asset mask proposal review, explicit per-part owner approval/rejection, fully transparent per-part RGBA PNG isolation with actual bounds, independent hashes and named downstream 3D reconstruction job tickets. No network call or unaudited Python execution.
- Explicitly left occluded geometry, 3D generation, rig binding, texture reconstruction and game-engine import **OPEN**. Owner approval of full-body references is distinct from approval of AI-suggested masks on a dressed image.
- 11 new tests for real mask extraction, missing approval, rejection, invalid kinds/paths, duplicate IDs, mismatched dimensions, empty masks, overwrite and schema errors. **408/408 tests OK (30 environment skips)** using `python3 -m unittest discover -q`.
- Continued the same wave with a deterministic `unclothe-proxy` step: converts actual approved alpha silhouettes to bounded watertight-style front/back/sides thickness geometry with shared source-image coordinates, exports each part as a separate standard GLB, checks it with the independent GLB parser, saves SHA receipts. No synthetic depth claim. 4 more real geometry/tamper/no-overwrite tests: **412 tests OK, 30 environment skips**.
- Added an independent executable CLI three-step smoke test (review → approved 2D extraction → GLB proxy materialization), raising the total to **413 tests OK (30 environment skips)**.

