# MGR 3D Forge - Full Living Handoff

**This file is the single source of truth for "where the build is."** It is updated in
the same commit as any feature change. If a claim here disagrees with
`docs/BUILD-REGISTER.md`, `docs/PROGRESS-LOG.md`, the test suite, or a committed
receipt, the receipt wins and this file must be corrected before anything else.

- **Repo:** MGR-3D-FORGE (sibling of MGR-ONE; the ONE WORK ORDER lives in MGR-ONE)
- **Branch:** `main`; inspected remote base `60c3a1317d77abe36f6e8ffa0c6db7dbcd308456` (2026-10-30 wave; publish SHA recorded in git after push)
- **Last verified:** 2026-10-30, Linux workspace and actual local HTTP bridge; Windows device receipts below are historical
- **Tests:** `python3 -m unittest discover -q` -> **543 executed, 540 passed, 3 skipped, 0 failed** with loopback enabled; 21 focused Source Atlas tests passed
- **Blender:** Historical Windows 5.2.2 independent witness is preserved; **not run with the new source atlas**
- **Owner:** tdmboyd-dev; no private weights/images/credentials committed

## Current recovery checkpoint — F118–F120, 2026-10-30 (supersedes outdated claims below)

| Outcome | Current fact | Independent proof / next closure |
|---|---|---|
| **F118 Source Atlas** | 17 categorized source families for faces, bodies, skin, animals, fantasy, props, kits, worlds, materials, animation and AI modeling; only 3DAssets.dev and Poly Haven have live read adapters. New Creation Chat Source Atlas panel, CLI and authenticated Studio read-only endpoints. | Live official dragon/rock/leather queries; local Forge Studio route tests, current full Python suite. **Actual Chrome click/visual acceptance still open.** |
| **F119 Forge Vault intake** | An explicitly selected 3DAssets.dev CC0-claimed small GLB can be fetched into the existing hashed vault, with URL, rights and container provenance; no automatic world use. | Actual 198,252-byte Western Dragon GLB / SHA `e6d97b12ff47d996025af6f75fa7bc1670d0747ae81b86a83ed6d4247f789172`, kept in disposable local quarantine; 6 mesh containers structurally parsed. **License adjudication, Blender visual QA and rig proof not done.** |
| **F120 MGR API/MCP source lookup** | Sibling `MGR-API-MCP` exposes conditional `mgr_forge_asset_discover` under the existing authenticated MCP route, source-only/read-only; never builds a competing router. | 55 API tests and actual Forge Studio HTTP ↔ API client + MCP read/tenant gate passed. **No live hosted Tevin client, creation worker, or paid action proven.** |
| **F110 missing-source discrepancy** | Previous 2026-10-27 handoff said GPU rental planner was implemented and 28 tests passed. On inspected GitHub `main`, `forge/gpu_packer.py`, `forge/gpu_rental.py` and their two tests are **missing**, and CLI `gpu-plan` imports a missing module. | **REOPENED/SOURCE GAP.** Recover verified source or rebuild and re-test. Do not quote its historical 28-test proof as current checkout success. |
| **Other previous proof** | The Windows SAM, Godot import, Chrome/WebGL and Blender outcomes below are retained as historical device receipts, not independently rerun in this workspace. | Reproduce current head on Time's PC before upgrading device/production acceptance. |

The required source ledger is `research/external-provenance/MGR-SOURCE-ATLAS-2026-10-30.md`; the machine receipt is `evidence/asset-atlas/2026-10-30-proof.json`. This handoff is the single resume file; `docs/BUILD-REGISTER.md` tracks detailed state and `docs/PROGRESS-LOG.md` tracks chronology. No second handoff file.

### Six concurrent Forge build lanes (next work, not claimed done)

1. **Vault and rights:** add audited ambientCG, Kenney, MakeHuman and other source adapters only where upstream APIs/licensing permit; verify individual pack rights, size, completeness, duplicates and actual Blender imports.
2. **Creation / World Forge:** usable asset preview, semantic category/sizing, part sockets and transforms, procedural terrain/biomes, native snap kits, layered scene editing and exports.
3. **Human / Creature Forge:** configurable diverse face shapes, skin undertones/PBR textures, hair, nails, body proportions, clothes, real/fantasy animal morphs and rigs; use immutable identity/approval baselines and independent visual/pose verification.
4. **AI Shape / Motion / FX Lab:** optional gated text/photo/multiview-to-geometry and segmentation adapters, geometry cleanup/retopo/UV, rig retargeting, animation, lighting/FX; weigh local CPU vs rented GPU vs paid only after resource/license/cost proof.
5. **MGR API/MCP → Creation OS → Tevin:** authenticated tool discovery exists; next join actual Creation OS execution ownership, Tevin/ONE client calls, scoped approvals, job receipts and recovery without a second brain/router.
6. **Acceptance / cleanup:** independently test browser interaction and real Blender/Godot round-trips, ownership/license, security/auth negative cases, actual consumer acceptance; restore missing F110 source and update this file/ledger as code changes.

**Never call the entire program completed based on a catalog, a downloaded asset or a successful local bridge.** The earlier numbered sections contain preserved dated history; the table and build lanes above define current status.

## 1. Mission and naming

- Parent platform: **MGR 3D Forge** (repo name stays).
- Flagship product: **MGR Unclothed 3D** (character/asset separation).
- Workspace name: **The Forge**.
- Outside projects are inspiration only. MGR-native docs never credit a vendor as a
  defining feature. External research is segregated under `research/external-provenance/`.
- Owner-private Tevin reference images/models never enter the public repo.

## 2. How we build (rules that are not optional)

1. Never label researched ideas, prototypes, or CPU contracts as production-ready.
2. No fabricated QA. Every "PASS" must trace to a committed receipt or a reproducible command.
3. No 10x / photoreal / identity claims without a benchmark or a measured number.
4. An export is unverified until it is independently imported (Blender or engine).
5. Every 3D result states its evidence level: **MEASURED / INFERRED / INVENTED**.
   - `MEASURED_SILHOUETTE_HULL`, `MEASURED_HULL_VS_ANALYTIC_SOLID`, `MEASURED` (image relief), etc.
6. Hands-off building inside the approved Forge workspace is authorized. Hard stops only
   for: personal files outside scope, credentials, destructive actions, spending.
7. No expensive GitHub Actions for routine tests. Keep `main` current after local verification.
8. Update `docs/BUILD-REGISTER.md` + `docs/PROGRESS-LOG.md` alongside any tested implementation.
9. Update **this file** in the same commit.

## 3. DONE (shipped, tested, evidenced)

### F107 - MGR Multi-View Silhouette Reconstruction (space carving)  [NEW]
- Module: `forge/multiview.py`
  - `reconstruct(spec)` -> `(Mesh, manifest)`; `export_reconstruction(spec_path, out)` -> GLB/OBJ/MTL/JSON
  - `score_against_solid(spec, boxes)` -> hull-vs-analytic-solid accuracy
  - Space carving over measured orthographic silhouettes; back/right masks mirrored (far-side cameras)
  - Voxel fit gate: worst-view IoU >= 0.97 or export refused
  - Honesty fields hard-coded: `hidden_surface_inference=False`, `identity_verified=False`, `external_api_calls=0`
  - Byte-deterministic export with SHA receipts
- CLI: `reconstruct-silhouette --spec --out`, `reconstruct-score --spec --truth --out`
- Tests: `tests/test_multiview.py` - 25 tests (cube/humanoid phantom recovery, mirror handling,
  scale/size/height rejection, empty/missing masks, threshold validation, determinism,
  CLI end-to-end, scoring exact/overfill/rejection)
- Phantom harness: `scripts/make_phantom_silhouettes.py` (self-authored analytic box-humanoid,
  no private references), `scripts/hull_resolution_sweep.py`
- Example: `examples/multiview-phantom/` (front/back/left/right PNG + spec.json + truth.json)
- Evidence:
  - `evidence/blender/windows-wave25-multiview-hull.json` (manifest excerpt + accuracy + Blender facts)
  - `evidence/blender/windows-wave25-multiview-sweep.json` (resolution sweep, 7 grids)
- Measured results:
  - grid 64: worst_view_iou 0.9894, 25744 triangles, 51488 vertices, volume 0.121355 m^3
  - hull-vs-solid IoU 0.8697 (0.01393 m^3 overfill, 0.00216 m^3 missed)
  - Resolution sweep: 0.847-0.878 IoU across grids 48-96 while triangles grow 14664->57088
    => residual is view ambiguity, not voxel size. Grid 40 refused by the fit gate.
  - Blender 5.2.2 import: 1 mesh, 25744 triangles, bbox 0.6 x 0.265625 x 1.74375 m;
    scene restored to 1143 objects, not saved.
- Interpretation: visual hull bounds; does not invent. The 12% overfill is dominated by
  arm-depth ambiguity between 4 orthogonal views (arms carved with torso-depth z-extent).

### F110 - MGR GPU Rental Planner (historical log ONLY; source missing on current main)
- Previous Windows work recorded a pure-CPU packer, CLI and 28 passing tests. Those four source/test files were **not in the inspected 2026-10-30 checkout** and the CLI presently imports a missing module.
- Current outcome is **SOURCE GAP / REOPENED** until source recovery and reproducible checks; no live GPU spend is claimed.

### F109 - MGR SAM Segmentation Adapter (optional, gated, working)
- `forge/sam_adapter.py`, `scripts/sam_segment.py`, `tests/test_sam_adapter.py`
- SAM ViT-B (Apache 2.0) connected via Python 3.12 worker. Center mode segments a
  256x256 subject in seconds on CPU; auto mode works but slow. available() True.
- 8 tests (2 skip on env). Manual masks remain default.

### F108 - MGR Segmentation Adapter Contract
- `forge/segmentation.py`, `tests/test_segmentation.py`
- Protocol + registry for segmentation backends. Manual owner mask always available;
  never claims inference. Neural backends deliberately not registered; `available()`
  must be True on this machine and licence cleared before use. No model shipped.
- 7 tests PASS. Test count: 445.

### F106 - MGR Unclothe 3D Visible-Part Extraction
- `forge/unclothe_3d.py`, `unclothe-review`, `unclothe-extract`, `unclothe-proxy`
- Owner-reviewed semantic masks -> transparent isolated PNG parts, SHA-bound 3D job tickets
  and real separate GLB silhouette proxies sharing reference coordinate space
- 3-command CLI end-to-end checked; actual geometry independently parsed
- No neural mask inference, photoreal volume, deformation rig, or engine visual proof

### F105 - MGR Whole-Character Reference Batch
- `forge/reference_pack.py`, `character-reference-pack`
- Up to 128 bounded PNG entries, view/asset/variant provenance, hashes, missing-view jobs,
  distinct owner-approval status. Private owner-approved packet validated separately, never committed.

### F104 - MGR Portable Character Motion Gate
- `bridge/blender_motion_export.py`, `bridge/blender_motion_reimport.py`, `forge/character_motion.py`
- SOURCE IMPLEMENTED; local safety tests PASS. Windows Blender execution attempt DENIED by
  device permission. Runtime status UNVERIFIED (not FAIL, not PASS).

### F103 - MGR Recoverable Material-Part Separation
- Original 1-mesh model becomes 7 independently selectable objects, 264/264 triangles
  preserved in a NEW .blend; independent reopen PASS. 381 tests PASS at that time.

### F102 - MGR Character GLB Readiness Gate
- `forge/character_readiness.py`, `character-readiness`
- Audits independent GLB meshes, materials, structural skin readiness.

### F101 - MGR Character Material Separation
- `forge/character_intake.py` separate_character_materials
- Saves a NEW material-separated Blender character without rewriting the original.

### F100 - MGR Editable Character Handoff
- `forge/character_intake.py` create_character_blend / verify_character_blend
- Import an admitted model as an editable Blender project; independently verify saved .blend.

### F99 - MGR Character Intake
- `forge/character_intake.py` admit_candidate
- Inspect and preserve a real GLB character candidate.

### F98 - MGR Godot Handoff
- `forge/engine_handoff.py` export_godot_project
- Package verified Forge world for Godot 4 with collision bodies and camera.
- **Historical 2026-10-27 Windows Godot 4.3 portable headless import/scene-quit receipt passed**; actual current-world interactive play/visual/collision proof remains open. Portable binary is not bundled in Git.

### F97 - MGR Local Studio
- `forge/studio_server.py` serve-studio
- Private localhost creation workstation: PNG -> GLB -> Blender -> downloads.

### F96 - MGR Blender Roundtrip
- `forge/blender_roundtrip.py` blender-to-forge
- Export validated Blender building edits back to Forge JSON.

### F95 - MGR Image Relief
- `forge/image_relief.py` image-relief
- Real image-derived relief 3D geometry from PNG pixels (not hallucinated full mesh).

### F94 - MGR Blender Scene Handoff
- `forge/live_blender_scene.py` blender-live-scene
- Turn verified edited world into an actual individually editable Blender project.

### F87-F93 - World Flight, World Editor, Creation Interfaces, Blender scene handoff
- `forge/world_flight.py`, `forge/world_editor.py`, `forge/creation_memory.py`, etc.
- Offline interactive 3D HTML world, materialized edits, creation chat/voice/image color.

### F82-F86 - Open systems / layered scenes / cell transport / asset parity / motion contact
- `forge/scene_layers.py`, `forge/cell_transport.py`, `forge/asset_parity.py`,
  `forge/spatial_truth.py`

### F72-F81 - Studio-quality CPU contracts
- `forge/studio_quality.py`, `forge.cli studio-proof`

### F68-F71 - Reality-to-space
- Camera rays, triangle-plane cross-sections, materialized JSON proof.

### F51-F67 - Fantasy/VFX/magic expansion
- FX, judge, atmosphere, light sculptor, optical FX.

### F44-F50 - Director/camera/motion
- Camera tours, LOD, interiors, navigation.

### F01-F43 - World builder foundation
- Procedural CPU GLB world builder, navigation, OBJ/SVG, modular mannequin/wardrobe.

## 4. NOT DONE (honest open gaps)

### Reconstruction (F107 follow-ups)
- Neural segmentation adapters: historical device-proven SAM ViT-B (F109) and prompted part-level F111; SAM2/SAM3 upgrade, native correction and full hair/skin/clothes pipeline still open
- Oblique/perspective view carving (currently orthographic only)
- Surface Nets smoothing is implemented as F113; full marching-cubes path / adaptive resolution / visual and topology acceptance remain open
- Fitted textured full-volume mesh assembly
- Identity likeness proof (silhouettes never prove identity)
- F112 four-point rectification exists; real consistent-camera multiview calibration and likeness proof remain open

### Character (F99-F106)
- Smooth multi-bone skinning (current: 0.428 m hand travel measured, but full pose suite open)
- Fitted garments (current: material separation only)
- Real voice mic proof (creation interfaces unproven on mic)
- SAM3/TRELLIS.2/Hunyuan adapters
- Full-pose anatomical checks on generic models before Tevin
- Rigged-source deformation check

### Engine
- Historical Windows Godot 4.3 headless import and scene-quit passed; latest full viewer/play-mode acceptance remains open
- Engine-level visual verification open
- No measured on-device real-time game-world play/collision proof for this build

### Runtime / platform
- F114 file-backed durable queue exists and F97 runs locally; authenticated hosted durable concurrent Studio worker orchestration remains open
- Real Tevin 3D reconstruction blocked on owner-approved masks/references
  (exist only in the old ChatGPT sandbox, not on this PC, must not enter the repo)
- Tevin private references must stay out of GitHub

### Verification
- F104 Windows Blender motion run was permission-denied (UNVERIFIED)
- Voice mic test unproven
- Historical SAM ViT-B installed on Time's device; availability on this Linux checkout is **unverified/unavailable without device-specific model worker/weights**
- Source Atlas browser panel real Chrome interaction and accepted-art Blender import remain open
- F110 GPU planner source gap: imported by CLI but missing from current Git checkout

## 5. Knowledge and decisions (do not re-litigate without new evidence)

- Cost verdict: Tripo cheaper for automation (~$0.10-0.30/asset); Hyper3D Rodin premium
  (~$0.75/asset, $120/mo business API). Recommendation: Tripo API + Blender, Hyper3D optional,
  and own the creation engine natively. Do not depend on any single vendor.
- Architecture: own the platform/workflow/asset library; use open models optionally;
  procedural CPU generation first, neural models as optional gated adapters.
- Tiered evidence rule: every 3D result states measured / inferred / invented.
- Repo name stays "MGR 3D Forge"; "MGR Unclothed 3D" is the flagship product; "The Forge" is the workspace.
- Superhuman build is intentional (extra muscle approved); bald T-pose set; face and foot anatomy
  sheets approved; feet/toes must be perfect.
- Never credit outside projects as defining features.

## 6. Workflows and commands

### Test
```
python3 -m unittest discover -q
```
Latest witnessed 2026-10-30 Linux execution with local sockets enabled: **543 run / 540 passed / 3 skipped / 0 failed**. The old 438 Python 3.14.8 Windows count was historical and not current coverage.

### Reconstruct (F107)
```
python -m forge.cli reconstruct-silhouette --spec examples/multiview-phantom/spec.json --out build/hull
python -m forge.cli reconstruct-score --spec examples/multiview-phantom/spec.json --truth examples/multiview-phantom/truth.json --out build/accuracy.json
python scripts/hull_resolution_sweep.py --example examples/multiview-phantom --out evidence/blender/windows-wave25-multiview-sweep.json
```

### Phantom regeneration
```
python scripts/make_phantom_silhouettes.py --out examples/multiview-phantom
```

### Blender verification (headless, isolated collection, restore scene)
Use the blender MCP `execute_blender` with a script that imports into a new collection,
measures, then removes the collection and purges orphans. Never save the scene.

### Git
```
git status --short
git add <files>
git commit -m "..."
git push origin main
```
No force push. No large binary artifacts unless justified (artifacts/ is gitignored).

## 7. Blockers (external decisions needed)

- Target shipping runtime/game engine and quality bar; Godot 4.3 portable *historical import proof* exists, not approved interactive runtime acceptance
- Production hardware inventory
- User-approved Tevin references in a private store (never committed)
- Commercial license clearance for restricted models
- Explicitly authorized Blender 5.2.2 run for F104 motion (permission-denied last time)

## 8. Next build order (continue from here)

Use the six concurrent, owner-approved lanes in the **current recovery checkpoint** at the top of this file. Concrete next acceptance targets: source-to-approved-kit and Blender import; face/skin/creature part libraries; source-to-scene placement and visual acceptance; F104 animation export/reimport; real Godot play; authorized hosted MGR API/Tevin; and F110 source recovery. Keep owner-private Tevin references outside public Git.

## 9. Update protocol

When you finish a unit of work:
1. Run `python -m unittest discover -s tests`. All must pass.
2. Update `docs/BUILD-REGISTER.md` (feature row + scope count).
3. Append to `docs/PROGRESS-LOG.md`.
4. Update this file (sections 3, 4, 8 at minimum; measured numbers, not opinions).
5. Commit and push to `main`.
6. Only then move to the next task. Do not stop at checkpoints to report small milestones.

## 10. Provenance and evidence index

- Conversation readback source: `C:\Users\cool\AppData\Local\Temp\opencode\assistant-text.txt`
  (245 assistant narrative messages), `user-messages.txt` (57 user messages),
  `commands.txt` (793 deduped container commands).
- MGR-ONE repo contains the ONE WORK ORDER and the ai-bridge coordination notes.
- External research segregated under `research/external-provenance/`.
- All receipts under `evidence/` are JSON; Blender receipts under `evidence/blender/`.
