# MGR 3D Forge — Engineering Handbook

## Current owner Studio entry — November 1, 2026

`serve-studio` prints a private launch link with a fragment credential. Open that exact link locally; do not share or commit it. Bare localhost URLs show a public Unlock Studio shell with no world or token. The fragment is stripped before `/studio` is fetched with exactly one `X-MGR-Forge-Token`; tab session storage permits reload. A restarted server uses a fresh link. Query strings/cookies are not authentication. All private file and action clients use the same exact header. This supersedes older public-editor entry assumptions.

Current targeted proof: `evidence/studio-access-2026-11-01/verification.json`, real Chrome/Blender creature/world and human receipts. These replace the older “browser click not yet run” statement for these exact desktop paths only; mobile, permanent Tevin approval/execution/reopening, deployed OAuth, full product/neural/professional art acceptance remain open. Reproduce with `npm ci --ignore-scripts` in `scripts/browser-qa`, then `python scripts/verify_browser_ui.py --mode creature --out <new-private-directory>` and the separate `human` mode. The harness uses installed Chrome/Blender and refuses to overwrite an existing receipt before allocating jobs.

**Audited baseline:** GitHub main 310badac0661422fd1415b9d3baa52fed7127391, 2026-10-31. This handbook covers the **actual existing repository**. Subsequent changed code is tracked by the current docs/HANDOFF.md and docs/BUILD-REGISTER.md. It is NOT a new or separate Forge architecture.

## 1 — The read order and what counts as truth

1. `docs/HANDOFF.md`: one living operational status and resume point; newest proven work goes first. Do not create a competing handoff.
2. `docs/BUILD-REGISTER.md`: individual F01–F151 capabilities, code paths, prior proof and next acceptance. Some statuses remain historical and need reconciliation against current code/tests.
3. `evidence/audits/2026-10-31-baseline-static-inventory.json`: 405 tracked files with names, per-file SHA-256, sizes, classifications, declarations, imports and route mentions.
4. `docs/ACTUAL-FORGE-MODULE-MAP-2026-10-31.md`: **every existing Forge Python module** with source docstring and directly importing tests (test matching is heuristic).
5. `docs/MASTER-FORGE-PROGRAM-2026-10-31.md`: owner-approved target **roadmap**, not a replacement for source; do not implement an imaginary engine when a comparable implementation is present.
6. `research/external-provenance/BEAST-3D-RESEARCH-UNIVERSE-2026-10-31.json`: 187 source candidates (184 initial queued plus 3 newly sourced-only), **not** 187 installed/verified models or REA scans.
7. `docs/PROGRESS-LOG.md`, `evidence/`, `tests/`, `bridge/`: histories and acceptance evidence. README and WHAT-WE-HAVE contain dated older facts; reconcile first.

**Meaning of full:** this audit read, parsed or fingerprinted all **405 tracked Forge files** at the named commit; Python parsed with AST, JS/TS read statically. This is NOT proof every algorithm, Blender result, browser, external provider, licensing decision or deployment is right. Only a specific successful end-to-end test and inspected output establishes those claims.

## 2 — Product boundaries; stop duplicating code

Forge is a **standalone MGR-owned 3D creator**. Real model creation, world/camera/scene files, morphs, rigs, artifact rights metadata, quality receipts and job history live in this repo/Forge-controlled runtime.

Other independent clients: Forge Studio UI; MGR-ONE (Tevin); private ChatGPT Forge Creator; other authorized apps. Their shared remote bridge is the **existing MGR-API-MCP repository** at `../MGR-API-MCP/` (sibling checkout, not necessarily present on all machines). The word **local** only identifies verified tests run between Windows Python Forge Studio and Node MGR-API-MCP; it is NOT a second API/MCP project. The actual MGR-API-MCP includes hosted HTTP/MCP, OAuth/JWKS tools and application connections; a remote hosted Forge job and authenticated file return have NOT yet been demonstrated. MGR-CREATE-Os is an optional separate coordinator only when multiple creation factories are involved. REA is an optional licensed source/implementation inspector in existing MGR Beast X-Ray; no duplicate agent core.

Unified route:

Person / Forge Studio / Tevin / ChatGPT -> MGR-API-MCP scopes + tenancy + audience -> **Forge's own job and artifact controller** -> existing native/procedural OR legally available external model -> Forge Vault/lineage -> independent Blender/Godot/QA -> verified output/revision to same caller.

No new geometry engine under a ChatGPT plugin. No separate 3D source catalog under Creation OS. Do not make proprietary source analysis or GPU rental prerequisites.

## 3 — What actually exists, by subsystem

| Actual MGR subsystem | Existing source ownership | Known proof | What is NOT fully proven |
|---|---|---|---|
| CPU World Forge | `forge/world.py`, `forge/geometry.py`, `forge/environment.py`, `forge/interiors.py`, `forge/world_editor.py`, `forge/scene_layers.py` | Tests, true world GLB/OBJ/LOD/camera/JSON, local editor, prior Blender and Godot receipts | Photoreal city, complex terrain/biomes, AI authored buildings, full collision/navmesh |
| Scene/game exports | `forge/engine_handoff.py`, `forge/web_runtime.py`, `viewer/runtime.js`, `viewer/template.html` | Godot project archive, offline WebGL2 world, edits and exports | Visual owner acceptance for latest scene, online multiplayer, engine import of every pack |
| Character/Human | `forge/character.py`, `forge/character_glb.py`, `forge/character_intake.py`, `forge/character_readiness.py`, `forge/wardrobe.py`, `forge/garment_fit.py`, `forge/reference_pack.py` | Generic mannequin with modular pieces, import/intake, fitted parts tests | Full morphable face, realistic skin options/locs, 52 visemes, true Tevin likeness |
| Original Creature Forge | `forge/imagination.py`, `forge/creature_jobs.py`, `forge/creature_rig_recipe.py`, `forge/morph_engine.py`, `forge/creature_rig.py` | Prompt + variation, real GLB, bounded length/height/width/twist, 19-bone exported rig and one action in prior Blender proof | Professional anatomy, arbitrary creature auto-rig, rich textures, uncanny motion |
| Animation/motion | `forge/animation.py`, `forge/character_motion.py`, `forge/motion_truth.py`, `forge/pose_guardian.py`, `bridge/blender_creature_skin.py` | Pose and motion guards, Blender rig/skin roundtrip | Phoneme-to-viseme/lip sync, arbitrary rig topology editing, 200+ verified movements |
| Shape and repair | `forge/marching.py`, `forge/smooth.py`, `forge/rectify.py`, `forge/repair.py`, `forge/meshqa.py`, `forge/surface_truth.py`, `forge/segmentation.py` | Bounded geometry/mesh checks and repairs | Production neural remeshing, arbitrary imported mesh morphology, full UV/topology pipeline |
| FX/materials/cinematic | `forge/fx.py`, `forge/fx_judge.py`, `forge/materials.py`, `forge/material_guardian.py`, `forge/cinematic.py`, `forge/shot_design.py` | Native effects, PBR recipes, camera/quality tests; older Blender proofs | High fidelity hair/fur/skin/cloth/VFX volumetrics and interactive lighting |
| Source/Asset Vault | `forge/assets.py`, `forge/asset_atlas.py`, `forge/pack_mirror.py`, `forge/ambientcg_source.py`, `forge/xray_kit.py` | 18 source directory families, 3 live metadata connections; pinned KayKit archive, license-scope, REA 302/302 file digests | All packs installed, universal commercial redistribution rights, multi-device backup/restore |
| Neural Shape Lab/GPU | `forge/generative_backends.py`, `forge/adapters.py`, `forge/gpu_packer.py`, `forge/gpu_rental.py`, `forge/hardware.py`, `forge/gpu_accounts.py`, `forge/gpu_lifecycle.py` | 14 candidate profiles with explicit rights; native CPU generator and dry-run planner | Permitted installed Pixal3D/TRELLIS.2 weights; actual GPU inference/billing acceptance |
| Studio/jobs/security | `forge/studio_server.py`, `forge/world_jobs.py`, `forge/creature_jobs.py`, `forge/durable_queue.py`, `forge/security/rambler.py` | Stable job IDs, replay/digest, no-spend native creation, local UI/static tests, unsigned release byte roster | Hosted multiuser jobs/zero-downtime, signed release, full browser UI test, owner approvals |
| Voice, design and intelligence | `forge/voice.py`, `forge/code_architect.py`, `forge/creation_memory.py`, `forge/director.py`, `forge/perception.py`, `forge/planner.py`, `forge/workflow.py` | Voice interface contracts, code-edit guards, memory/provenance and tests | Real mic/lip sync/phoneme recognition, continuously autonomous 3D art generator |
| Unclothe/segment visible parts | `forge/unclothe_3d.py`, `forge/segmentation.py`, `bridge/blender_character_intake.py` | Visible image/mask extraction and 3D silhouette proxy | Predicting unseen anatomy or perfect image-to-3D from masks |

**A critical correction:** there is no `forge/fantasy.py` in the audited current repository; fantasy FX functionality is spread over existing `forge/fx.py`, `forge/fx_judge.py`, `forge/materials.py` and relevant source files. Any old master-plan reference to the nonexistent path has to be repaired, not built into a duplicate module.

For **all** 89 tracked Python modules under `forge/`, see the actual module map; for **all 405 files** see the hashed inventory. No important subsystem may be labeled missing merely because it has low static import mentions or its work is recorded under another name.

## 4 — Run, build and verify what exists

Start in the actual Forge root, with Python installed and Windows Blender optional:

```powershell
python -m unittest discover -q
node --check viewer/runtime.js
python -m forge.cli build --spec examples/neighborhood.json --out artifacts/neighborhood-new
python -m forge.cli inspect artifacts/neighborhood-new/world.glb
python -m forge.cli world-flight --world artifacts/neighborhood-new --out artifacts/neighborhood-flight.html
python -m forge.cli serve-studio --world artifacts/neighborhood-new --workspace artifacts/forge-workspace --port 0 --blender "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
```

The Studio prints its loopback URL. It binds to 127.0.0.1, has its own session token, and is **not** a hosted remote MCP server. Open its UI in a browser on that machine. Creation Chat can edit existing buildings, find source metadata, upload small GLBs, create relief, export worlds and request original CPU creature meshes. Browser network access is not implied merely by serving the page.

**Actual tracked CLI commands, all extracted from forge/cli.py:** see section below. Test command availability with `python -m forge.cli --help`. Every listed command must have documented inputs/output schema and error behavior before release.

## 5 — Actual CLI actions from source (current implementation)

**64 actual CLI actions**, extracted from current Python argparse AST on 2026-11-01. Previous 60/62 counts are historical.

| Real CLI action | Existing source-described effect |
|---|---|
| `apply-world-edits` | materialize saved browser world edits into genuine GLB/OBJ/preview and viewer |
| `asset-acquire` | explicitly fetch one discovered CC0 GLB into local rights/quality quarantine |
| `asset-search` | search cached models or explicitly fetch fresh CC0 source metadata |
| `asset-sources` | browse rights-labeled 3D kits, creators and tool sources without network |
| `audit-export` | compare geometry counts and bounds in Forge GLB and OBJ exports |
| `blender-cinematic` | materialize a 3D camera reel, lights, editable .blend and real CPU render |
| `blender-director-audit` | audit actual saved Blender timeline cameras/cuts |
| `blender-director-frames` | render four actual timeline frames and compare dolly output |
| `blender-facts` | inspect real Blender GLB object facts |
| `blender-fx-render` | actually render CPU-native 3D fantasy effect in Blender |
| `blender-live-scene` | turn verified edited world into an actual individually editable Blender project |
| `blender-material-audit` | check actual imported Blender PBR material sockets |
| `blender-pose-audit` | measure animated rig bones, joints and skin coverage inside Blender |
| `blender-pose-render` | render two animated Blender keyframes with transparent background |
| `blender-render` | render real Blender workbench QA PNG |
| `blender-rig` | assemble modular T mannequin as Blender armature project |
| `blender-studio-witness` | render real Blender CPU material/strand/light/volume witness |
| `blender-to-forge` | export validated Blender building edits back to Forge JSON |
| `blender-verify` | run actual Blender GLB import verification if installed |
| `build` | generate real GLB geometry + manifest |
| `character` | export generic detachable mannequin T/A pose |
| `character-blender` | import an admitted model as an editable Blender project |
| `character-intake` | inspect and preserve a real GLB character candidate |
| `character-motion-export` | export an existing deforming Blender rig to animated GLB |
| `character-motion-reimport` | independently import animated GLB in Blender |
| `character-readiness` | audit independent GLB meshes, materials and structural skin readiness |
| `character-reference-pack` | admit many private character/outfit images as one coordinated asset batch |
| `character-reopen` | independently verify saved character .blend in fresh Blender |
| `character-separate` | save a NEW material-separated Blender character without rewriting the original |
| `compare-asset-identity` | compare trusted asset and neutral-mesh SHA receipts |
| `compare-renders` | compare fixed-camera RGB PNG frames |
| `compare-views` | translation/quarter-turn aware appearance check; not identity proof |
| `compose-scene` | compose owned MGR scene layers into a deterministic receipt |
| `fantasy-effect` | generate native animated-time magic geometry with emissive GLB |
| `godot-handoff` | package verified Forge world for Godot 4 with collision bodies and camera |
| `gpu-plan` | dry-run cost plan for renting a GPU (no money spent) |
| `human-audio-motion` | animate original Human Forge jaw from approved PCM WAV loudness; NOT speech/phoneme alignment |
| `human-lipsync` | add real Blender 3D facial shapes and animation to existing Human Forge mannequin; requires timed phonemes |
| `image-relief` | build real image-derived relief 3D geometry from PNG pixels, not hallucinated full mesh |
| `imagine-creature` | create procedural creature mesh and design DNA; not neural inference |
| `inspect` | check a GLB for structural validity |
| `judge-atmosphere` | compare real matched Blender volume/control renders |
| `kit-mirror` | preserve a pinned official KayKit CC0 archive in quarantined local vault; no extraction |
| `load-cells` | apply a residency plan to integrity-checked local GLB cells |
| `model-engines` | show verified native vs uninstalled optional AI 3D engines and license gates |
| `pipeline` | build world and optionally verify/render in real Blender |
| `rambler-seal` | write an unsigned, SHA-256 release byte-integrity roster; NO anti-inspection claim |
| `rambler-verify` | verify file bytes and roster completeness against supplied manifest |
| `rea-kit-audit` | crosscheck archived kit file hashes with real REA Evidence; no rights promotion |
| `reconstruct-score` | measure a carved hull against an analytic solid at voxel resolution |
| `reconstruct-silhouette` | carve real measured triangle geometry from multi-view silhouette masks |
| `rectify-mask` | rectify a perspective mask to orthographic using 4-point correspondences |
| `rehearse-walk` | simulate collision-checked road-centerline traversal |
| `rig-creature` | fit DNA skeleton, weighted skin and test real animation in independent Blender processes |
| `serve-studio` | start private localhost Forge creation workstation |
| `spatial-proof` | prove 2D/3D perspective ambiguity and mesh slicing |
| `studio-proof` | run ten native studio-quality validation contracts; not a film render |
| `unclothe-extract` | isolate only owner-approved visible pixels for separate 3D jobs |
| `unclothe-proxy` | make independent real GLB silhouette proxies from approved extracted parts |
| `unclothe-review` | inspect a proposed multi-part segmentation without extracting |
| `verify-bundle` | verify artifact hashes in world build folder |
| `world-biome` | make a real original biome ring as an optional GLB layer around an unchanged authored MGR city |
| `world-compose` | combine the same original MGR World GLB + pinned native biome in one real Blender-reopened editable world |
| `world-flight` | package a generated world into an offline interactive 3D HTML world |

## 6 — How the specific workflows operate

**World:** `forge/cli.py build` uses typed WorldSpec and `forge/world.py`, `forge/geometry.py` and current output bundle. `world-flight` uses `forge/web_runtime.py` and bundled WebGL viewer. Local Studio `/api/world` or durable `/api/world-job` stores edited GLB; `/api/world-job-status` looks up immutable job ID. Older `/api/world` has different replay semantics; do not assume it is identical to durable route.

**Original creature:** `forge/imagination.py` builds seeded original procedural geometry and DNA; `forge/morph_engine.py` deforms geometry using shared bounds; `forge/creature_jobs.py` owns restart-safe local `/api/creature-create` and `/api/creature-status`, with model SHA and bytes; `forge/creature_rig_recipe.py` produces skeleton plan, `forge/creature_rig.py` invokes actual Blender processes for weighted skinning and independent GLB re-import. A generated GLB is **not** automatically rigged, or photo-realistic.

**References and existing models:** `character-intake` preserves a GLB candidate and provenance without invented identity. Additional Blender import/part separation and motion export are separate commands, with an independent second-process acceptance when supported.

**MCP:** real bridge repo `MGR-API-MCP` has `src/forge-catalog-client.ts` and `src/forge-mcp-tools.ts`. Existing `tools:read` and `tools:execute` scopes, actor/tenant/audience and accepted job receipts, with no mandatory Creation OS. **Local** in old receipts means the Windows processes reached each other; hosted Tevin or mobile file delivery still needs real remote deployment evidence.

**REA and source kits:** `asset-sources`, `asset-search`, `asset-acquire`, `kit-mirror`, `rea-kit-audit` distinguish discovery, downloaded/hashed/quarantined files, exact folder license, and visual/art approval. The 187-entry universe (184 original queued + 3 newly sourced) remains a research list, not installed 184 kits.

**Rambler:** `rambler-seal` and `rambler-verify` detect changed release bytes with an **unsigned** SHA-256 roster; no guarantee of impossible inspection or real publisher signature.

**GPU:** `gpu-plan` uses a caller-supplied dated quote for a dry-run or returns UNPRICED; does not rent GPUs. Different external model/checkpoint rights may limit future deployment.

## 7 — Fix and update protocol: no dirt in the repo

Before a change: fetch the current GitHub main, inspect any dirty workspace and other worker branches, read this handbook and the canonical HANDOFF, reproduce the actual failing command; identify source owner and expected contract. Never overwrite somebody else's changes or confuse research docs with running code.

Build on the original component and its neighbors, add tests for actual failure, invalid input, unauthorized calls, tampered artifacts, retries and restarts; run the focused tests then full suite; where UI/Blender/Godot involved, run the real receiver and inspect screenshot/mesh/rig geometry. Record exact failures and corrections.

After passing: update docs/HANDOFF.md, BUILD-REGISTER.md and PROGRESS-LOG.md, add a safe evidence file with SHA/size/runtime/limitations, correct stale current documentation, commit **those same source/docs/tests**, push without force, fetch published file fingerprints back. If a test or acceptance didn't run, state OPEN. No invented numerical feature percentage.

## 8 — Exact security issue found in this audit

Before this audit, some localhost Studio GET artifact routes allowed tokenless reads, unlike recent creature files. The new security fix requires the same Studio token for relief, world, candidate GLB, report, Blender and Godot artifacts; validates local Host/Origin; bounds file size; and changes the existing Creation Chat download helper to fetch with the token rather than expose it in URLs. A broken tokenless download is a correct 403, **not** an app outage. Full regression, actual consumer click and background renderer tests are separate acceptance.

## 9 — Priority research: expressive rigs, lip sync and arbitrary morphs

Existing `forge/morph_engine.py` offers 4 bounded spatial transforms. Existing `forge/character_motion.py`, `forge/animation.py` and `forge/creature_rig.py` provide partial motion/Blender proofs. They do **not** constitute complete facial lip sync or changing an arbitrary animal into a fully stable unseen creature. Build and verify more than marketing concepts:
- Human faces: landmark/semantic controls and production shape keys for eyes/nose/jaw/mouth, skin layers, hair, clothing identity locks.
- Audio-driven face: transcript/phonemes and their aligned timestamps, viseme blendshapes, jaw/tongue/teeth, emotion and eye controls, animation constraints, per-language evaluation; explicit source/audio consent/rights.
- Rig morph: edit bone geometry, regenerate weights and inverse-bind transforms, retarget motion, preserve foot/hand contacts, correct skin folds, cap clip deformation and rerender.
- Creatures: biped/quadruped/bird/serpent/aquatic/multi-leg/anatomically novel skeletons with pose-dependent corrective shapes, capable of original movement not simply importing Mixamo.
- Assets/worlds: high quality PBR/UV, procedural grammar, terrain, articulated fauna, motion and effects, **reversible** non-destructive edit recipes.
- Neural generation: isolate actually permitted checkpoints; test output quality, memory, dependencies, costs. A discovered model profile or bundled README is not an installed inference engine.

See docs/HOW-TO-MORPH-RIG-LIPSYNC.md for exact stage gates, and docs/MASTER-FORGE-PROGRAM-2026-10-31.md for roadmap. User ambition is top-tier, but no verified world-best metric or 100x performance claim exists.

## 10 — What this handbook still cannot certify

Not certified: full browser end-to-end click with download after the new security fix; hosted MGR API/MCP and Tevin roundtrip; every external kit legally approved/Blender-imported; multiuser private artifact store and offsite restore; 200+ actual animation clips; true LipSync/viseme and anatomically stable arbitrary morph engine; photoreal original mesh generation; production render/model benchmark vs Tripo/Meshy/Higgsfield; actual permanent signing keys. Track each with a concrete acceptance test and file owner; do not mark success by document creation.

## New 2026-10-31 native creation lanes

Original Forge extensions: human_lipsync.py + lipsync.py plus Blender face scripts, biome_jobs.py and original environment.py terrain layer, the original morph_engine.py extended to bend/taper, and Studio Creation Chat code in existing viewer. Actual Chrome receipt evidence/browser/2026-10-31-morph-biome-world-real-chrome.json and original face/biome independent Blender evidence under evidence/human/ and evidence/world/. MCP client/authorization ownership is still the sibling MGR-API-MCP/src/forge-mcp-tools.ts, not a new direct local API. Static inventory and module maps must be reindexed after release before claiming a new full-tracked audit.

## Exact original-request readback

`mgr_forge_request_verify` is read-only, same actor/tenant and `tools:read`. Input is `{kind,input}` with kind `world|creature|biome|human|composed` and the exact original typed creation input (including original requestId). It calls the native authenticated `/api/request-verify` with native field names. The native creator owns normalization/hashes; no JavaScript imitation of Python float/Unicode/morph defaults. `accepted:true/status:NATIVE_REQUEST_INPUT_VERIFIED` proves original input identity only: inspect `nativeStatus` and `nativeResult` for actual readiness/hash/bytes. RUNNING/FAILED/NEEDS_RECONCILIATION are never completion. NOT_FOUND or mismatch creates no job and must not authorize automatic retry. Persist the verified original command/job/artifact linkage through the existing consumer store and grants. The older ID-only status alone cannot settle a newly approved action. Full shared tools now13; CLI count stays64. Original twelve schemas are unchanged.

## Native preallocation world validation and owner preparation

`world_editor.validate_world_edits` is the read-only original editor validation shared by `apply_world_edits` and `world_jobs._binding`. The latter validates the exact serialized JSON snapshot before a job/ledger is allocated; valid fingerprints remain unchanged. `/api/request-verify` now rejects a new invalid world request rather than returning NOT_FOUND before checking native source/schema/material/identity/ground/dimension validity. Shared `mgr_department_prepare` consumes this read under departments:read, exact principal/workspace and command binding; ONE requires it before consuming an approval. It creates no job/authority/artifact and cannot authorize unknown-effect retries. Same13direct Forge MCP tools/64CLI/F01-F156; permanent worker/launcher and whole-product acceptance remain open. Root-relative evidence/forge-preparation-2026-11-01/REPORT.md retains real workflow and failed-before/passing-after proof.
