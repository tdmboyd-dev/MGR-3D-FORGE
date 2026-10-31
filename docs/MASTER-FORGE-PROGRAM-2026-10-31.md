# MGR 3D Forge — Master Program, Integration Graph and Continuity Plan

Updated: 2026-10-31. Owner direction: independent, expandable, fully integrated MGR-native 3D creation platform, optional shared REA research, optional Tevin and ChatGPT controllers, not a fixed vendor asset selector.

**Authority**: MGR-3D-FORGE/docs/HANDOFF.md is the ONE live Forge resume record. This is the durable detailed build specification; MGR-3D-FORGE/docs/BUILD-REGISTER.md is the feature-level evidence tracker. No second handoff or brain, queue, approval engine, REA fork or vault is permitted. Checkpoint changes require updated tests and same-commit handoff sync.

## 1. Current observed baseline, separately from this plan

- Existing Forge GitHub main before this plan: 1d4c1235c79cce65acb6a1d75fa6a59bdfd46804 (current baseline, not this plan's future commit).
- Native CLI and CPU geometry: forge/cli.py, forge/imagination.py, forge/morph_engine.py, forge/creature_rig_recipe.py, forge/creature_rig.py; real prior Blender import/export/reimport: 19 bones, 3,840 weighted vertices, one animation action, but primitive art and nonproduction skinning. Source proof: evidence/rigging/2026-10-31-native-creature-rig.json.
- Existing Forge Studio and local jobs: forge/studio_server.py, forge/world_jobs.py, viewer/. Authenticated local creation and repeatable GLB digest exist; no finished hosted Tevin or phone-based creation flow.
- Vault and source engine: forge/assets.py, forge/asset_atlas.py, forge/pack_mirror.py, forge/data/asset_sources.json (18 families, only 3 live official metadata providers), forge/xray_kit.py, evidence/asset-atlas/2026-10-31-rea-official-kaykit-proof.json (302/302 file hashes matched; NOT license approval or 302 approved models).
- Compute: forge/gpu_packer.py, forge/gpu_rental.py dry-run, deliberately no paid instance launched; forge/data/generative_engines.json (14 profiles; only native procedural runnable). No high-fidelity open-weight model pilot yet.
- MGR API/MCP: sibling MGR-API-MCP/src/forge-mcp-tools.ts and src/forge-catalog-client.ts; source discovery and LOCAL durable world create/status use existing tools:read and tools:execute scopes, not a new router. Earlier suite: 62 tests PASS; current tests must be rerun for actual new work.
- MGR REA X-Ray: upstream morluto/rea 6.8.0 installed isolated on owner Windows; plugin account-private and source in MGR-API-MCP/integrations/rea-xray-plugin/. Local MCP static archive inspection demonstrated, but NOT a hosted iOS remote file reader.
- MGR-CREATE-Os remains an independent optional multi-factory coordinator; its media-factory false-success report was repaired. Creation OS is NOT mandatory between Tevin and Forge. Handoff: sibling MGR-CREATE-Os/HANDOFF.md.
- MGR-ONE / Tevin core client remains an independent owner. It must request Forge through shared MGR API/MCP; its ONE WORK ORDER governs Tevin, and this plan must not replace it. Tevin owner handoff: MGR-ONE/HANDOFF.md.
- Historic test results are evidence for those dated checkouts, not current certification or end-to-end launch. Pending current proof is logged in the register and this document.

## 2. The single integrated app, ownership and route

Standalone Forge Studio user, ChatGPT Forge Creator plugin, or Tevin/MGR-ONE
  -> MGR-API-MCP (verified actor, tenant, audience, tools:read or tools:execute, approval + limits)
  -> Forge's ONE job controller (stable request/variant IDs, cancel, recover, receipts)
  -> select creation method: native procedural / licensed pinned asset / permitted neural GPU backend
  -> Forge Vault (license/data/weight checkpoint), Human/Creature/World/Word/Creation/Material/Motion/FX engines
  -> Blender and target-engine QA + preview + saved revision + integrity/cost proof
  -> signed/scoped artifact access and ChatGPT/Tevin/Studio user revisions.

MGR REA X-Ray is an optional authorized public-source/owner-owned package investigation into the existing source-to-native gap tracker; it should NOT run on every creation request. Creation OS only orchestrates projects combining multiple creative factories. MGR Rambler is defense-in-depth for private releases; it should NOT obstruct MGR's own tests or normal authorized reverse engineering.

No duplicate artifacts, job history, source matrices, approval routers or model weights in plugins. The generator, file lineage, job state and quality receipts belong to Forge. The app/ChatGPT surfaces consume canonical job IDs and immutable saved artifacts from shared Forge contracts.

## 3. Creation lanes — every owner-approved system and exact code placement

| System | Repo authority / actual path | Already exists | Material open build targets |
|---|---|---|---|
| Forge Vault & Source Atlas | MGR-3D-FORGE/forge/assets.py, forge/asset_atlas.py, forge/pack_mirror.py, forge/data/asset_sources.json | Hash vault; 3 metadata adapters; pinned archive in owner private vault | Licensed categories, per-file admission, actual install/test, second backup, dedupe/usage rights, thumbnails |
| MGR Human Forge | forge/character.py, forge/character_intake.py, forge/garment_fit.py, forge/morph_engine.py | Generic character/part tests, not realistic identity | Faces, nose/lips/eyes/jaw, skin pigments and PBR, hairstyles/locs, body morphs, garment fit, facial blendshapes and independent identity QA |
| MGR Creature Forge | forge/imagination.py, forge/creature_rig_recipe.py, forge/creature_rig.py | Low-poly invented animals/hybrids + 19-bone Blender smoke | Species-specific topology/skeleton, believable wings/tails/fur/scales/feathers/claws and deformation, motion retarget, real movement |
| MGR Creation Forge | forge/cli.py, forge/studio_server.py, forge/world_jobs.py, viewer/ | CPU world/relief/GLB job interfaces and limited local UI | All methods in one creation director, prompt/variant/edit/revision/compare/undo, reliable receipts and UX |
| MGR Word Forge | No isolated production implementation confirmed; inspect existing Forge text/scene assets first | Owner-approved concept but NOT VERIFIED | Exact owner meaning to be specified; candidate lane covers artistic 3D typography, text geometry and creative brief/scene grammar. Do not invent a separate brain or unrelated tool. |
| MGR World Forge | forge/geometry.py, forge/environment.py, forge/world_editor.py, forge/engine_handoff.py | Roads, buildings, parks, CPU scene exports + earlier Godot check | Real terrain/biomes, interiors/architecture, asset instancing, navmesh, animated life, regions/world DNA, realtime streaming and multi-stop worlds |
| AI Shape Lab / Model Dock | forge/generative_backends.py, forge/data/generative_engines.json, forge/adapters.py | Candidate registry; no external backend installed | Exact checkpoint rights and costs, permitted neural inference, multiview, mesh repair, UV/PBR texture output and A/B benchmark |
| MGR MorphRig Continuity | forge/morph_engine.py, forge/creature_rig_recipe.py, bridge/blender_creature_skin.py | Shared mesh/bone deformation and first rig prototype | Arbitrary imported mesh morphology, semantic joint remap/weights, self-correction of clothing, hair and animation |
| Motion/Animation Forge | forge/animation.py, forge/character_motion.py, bridge/blender_creature_reimport.py | Basic poses and 1 actual creature animated action | 200+ animation target motion library, mocap retarget, facial animation, behavior/physics, deformation tests, clip licensing |
| Materials & FX | forge/materials.py, forge/fantasy.py, forge/environment.py (verify names before code) | Partial materials/VFX; full audit pending | Skin tones/pores, hair/fur, cloth, metals, terrain decals, water, smoke, portals and lighting |
| MGR Beast X-Ray / REA | MGR-3D-FORGE/forge/xray_kit.py and MGR-API-MCP/integrations/rea-xray-plugin/ | 302/302 independent package byte/size check | REA self-study of official source, 100+ research campaign, authorized documented feature-to-native comparisons, per-target evidence and tests |
| MGR Rambler | NEW planned code: MGR-3D-FORGE/forge/security/rambler/ | NOT BUILT | Signed manifest and hashes, scoped release packaging, server-only IP/weights, tamper alerts, threat-model tests, private build secrets |
| ChatGPT Forge Creator | NEW planned source: MGR-API-MCP/integrations/forge-creator-plugin/; execute via src/forge-mcp-tools.ts | Existing MCP world create only, not a dedicated complete ChatGPT Forge plugin | Plugin skills/tools, own artifact status/previews/download, image/reference inputs, native creation jobs, authenticated hosted remote relay |
| Tevin consumer | MGR-ONE/HANDOFF.md and shared MGR-API-MCP | No hosted end-to-end job acceptance | Use same approved Forge jobs from Tevin; preserve identity/world context, expenses and receipts |
| Creation OS orchestration | MGR-CREATE-Os/HANDOFF.md, src/factories/media-factory.ts | 12 registered factories, no actual 3D service integration | Join multiple real factory receipts when needed; no direct 3D detour or fake media succeeded |
| Independent Blender/Engine QA | bridge/blender_creature_reimport.py, forge/engine_handoff.py, tests/ | Several real local proofs | Every actual feature gets cross-process reopen, scene/morph/anatomy/rig/material checks and Godot interactive acceptance |

All paths beginning with forge/, docs/, viewer/, bridge/ and tests/ above are relative to MGR-3D-FORGE. Future paths are explicitly marked planned; check exact existence before claiming built.

## 4. REA self-study and the 100+ investigation campaign

Canonical queued dataset: research/external-provenance/BEAST-3D-RESEARCH-UNIVERSE-2026-10-31.json; human index: sibling .md. Seed has 184 investigation records across 177 distinct names (some categories intentionally overlap), NOT 184 proven distinct available assets or 184 completed analyses. It includes Kenney/KayKit/Quaternius, Poly Haven, ambientCG, MakeHuman, world tools, rigging, neural models, exact source atlas entries and neural registry profiles.

Execution order, no silent web/API downloads:
1. This plan and the 184-entry queue must be committed and fetched back from GitHub BEFORE first new REA investigation.
2. REA itself: official morluto/rea pinned source/release, MIT + third-party notices, code architecture, MCP envelopes, sandboxing, evidence integrity, unsupported targets and updater behavior. Inspect our legally acquired/authorized REA package and compare assertions with tests. Do not fork upstream REA or replace MGR Beast Pack.
3. Pilot 4-8 openly licensed pinned source archives (KayKit licensed Assets subtree, official Kenney packs, one permissible Blender addon) plus one prior REA file hash benchmark. Each study checks source existence, EXACT artifact and nested license, REA-supported operation, hazards and ownership before inspection. Quaternius QAL, CGAxis paid bundles, Tripo/Meshy/Higgsfield hosted engines and research-only weights = public documentation study unless separate rights.
4. Queue the remaining targets in low-cost, failure-tolerant waves; never claim all targets were analyzed if only names were assembled. Store detailed evidence in secure off-repo vault; commit immutable references, hashes, method, result and limitations; no private IP or paid binary uploads.
5. Compare observed principles and measured performance to Forge's current implementation. Build only verified missing capabilities in original source. No copy/translation of restricted meshes, private model weights or license-bypassing conversions.
6. Close targets only after code + negative/positive tests + Blender/Godot preview/reopen and appropriate rights. If research uncovers a better shared algorithm, repair existing Forge modules rather than adding a parallel factory.

Per-target fields: id, kind, exact URL/path/commit, claimed and checked license, authorization class, snapshot/hash, REA evidence ID/coverage, analysis limitations, adaptation decision, owner paths, issue/repair, tests, spend and acceptance. State lifecycle: QUEUED -> SOURCE_CHECKED -> LICENSE_CHECKED -> PERMITTED_REA_OBSERVED -> SPECIFIED -> BUILT -> TESTED -> INTEGRATED -> OWNER_ACCEPTED. NEVER infer from README or a file extension alone.

## 5. MGR Rambler (defense against copying, NOT mathematically impossible inspection)

Purpose: protect owner-controlled Forge value without preventing legitimate user files, independent inspection, security auditing or license attribution. Build toward: private server-side inference/algorithms/weights; client holds NO API secrets or signing keys; signed/verified release manifests; per-object hashes and authenticated time-limited artifact access; encrypted sensitive storage; tenant quotas and audited job access; production binary minimization/stripping when legally appropriate; reproducible outputs and rollback; secrets scanning and supply-chain SBOM; attack-surface and red-team testing using authorized REA self-inspection.

Do NOT claim impossible reverse engineering, embed secret decryption keys inside shipped clients, evade malware/security scanners, or block lawful auditing. Obfuscation alone only raises cost. Cryptography requires real key governance and signature verification in a separate trust boundary. Proposed files: forge/security/rambler/{manifest.py, verifier.py}, tests/test_rambler.py, protected deployment config in MGR-API-MCP; not built yet. Legal references: https://mas.owasp.org/MASVS/11-MASVS-RESILIENCE/ and https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html.

Acceptance: a signed build passes trusted verification; a single changed file is denied; no private keys or model weights appear in user-visible bundles; a legitimate MGR debugger retains debug symbols in a private escrow; security restrictions do not break offline Blender creation. First implement hash manifest + signature-ready contract with no invented keys, then real signing with secrets broker approval.

## 6. ChatGPT Forge Creator plugin as one more interface

MGR-3D-FORGE remains the one physical creation engine. API/MCP owns authentication, actor/tenant, exact-action scope, replay/cancel, approval and secure artifact URL. A separate ChatGPT plugin can expose:
- Discover licensed source models/materials, model capabilities, and preview actual generated results (read permission).
- Start original human/creature/world/relief/morph/rig/FX creation only through guarded tools:execute, size/time/cost controls and idempotency keys.
- Status/poll/cancel/retry-with-reconciliation, revisions, compare variants and download actual GLB/.blend/preview PNG with digest and scoped URLs.
- Creation Chat UI and optional on-device Blender workers; cloud/mobile access only once an authenticated remote MCP/worker endpoint and artifact storage are proven. A locally saved plugin is not automatic iOS access.
- Plugin source goes in MGR-API-MCP/integrations/forge-creator-plugin/, not an entirely separate backend. The first connected plugin may be private; no deceptive placeholder button/tool claiming to create files.
- No untrusted ChatGPT-generated Python executed blindly, no arbitrary desktop file path reader or public access to REA active reverse engineering tools.

MVP acceptance: in an authenticated consumer, request a creature, job ID created once, real file generated, SHA matches, preview visible, user revision saved with lineage, independent Blender/engine import. Route remains the same if the caller is Tevin, standalone Studio, or Creation OS's cross-factory orchestrator.

## 7. Full-app journey acceptance and incremental waves

Wave A — SOURCE OF TRUTH/PLAN (THIS WAVE): commit this master plan, target registry, handoff pointer, new tracked feature IDs to GitHub; fetch remote proof. No new 100+ REA scan before commit.
Wave B — REA SELF/HARDENED CORE: permitted official source/release analysis and evidence; run minimal archive/bytes demo, map capabilities/gaps and original improvements, keep upstream MIT notices and dependency scopes. Build Rambler first hash manifest and tests; no secrecy fantasies.
Wave C — FORGE CREATOR API: extend one existing Forge Studio job service and shared MCP tool set, not another server. ChatGPT local/remote private plugin spec, real job state, downloadable verified artifacts. Start with CPU creature/GLB + existing world; add high-quality models only after backend acceptance.
Wave D — STANDALONE STUDIO: user-facing one-screen create, visual compare, morph/rig/material edit, job history and recovery; real Chrome interaction, Blender/Godot open, license display, controls. Full product is NOT just API tests.
Wave E — 100+ LEGAL STUDY WAVES: prioritize categories/foundations per need; pinned source archives and REA evidence only with authorization; no blanket asset store dump.
Wave F — MASTER HUMAN/CREATURES/WORLDS: licensed morph/multiview model pilots, artistic surfaces, species anatomy and animation libraries, procedural worlds, materials, camera/lighting and meaningful effects. Every factory points to same job/vault/quality system.
Wave G — REAL COMPARISON: same brief/reference/budget against allowed Meshy/Tripo-style outputs; independent 4-view geometry/PBR/rig/quality/latency/cost and blind owner rankings. "100x" remains aspiration until metric proof.
Wave H — PRODUCT/SERVICE ACCEPTANCE: offline PC + authenticated hosted Tevin + ChatGPT remote plugin + standalone users; backups/restores, restart/queue/cancel, cost guard, tenant/privacy, package retention/rights, release signing and rollback. Production only after approvals.

## 8. Scope and cost discipline

- Review REA itself and public authorized packages; never fetch 100+ massive archives in one go. Start with publisher licensing and targeted bytes; keep Git history, binary assets and GPU weights separate from code Git.
- CPU/offline workflows have no per-request API credit but finite memory/storage/time. Models like TRELLIS.2/Pixal3D and paid cloud resources need checkpoint+license+hardware+cost proof and explicit approval before paid dispatch.
- No blanket statement "all packages embedded"; separate SOURCE FOUND, DOWNLOADED, QUARANTINED, VISUAL_TESTED, RIGHTS_CLEARED, PRODUCTION_ADMITTED.
- No automatic model training with legally questionable copyrighted materials.
- Preserve existing working behavior when improving; use known Python/test/Blender environment and no budget-heavy GitHub Actions.
- On 20+ waves, update both measured baseline and next shortfall to 100% for each area; overall product completion requires a verified denominator of accepted user journeys.

## 9. Required uninterrupted continuity and ownership contract

- Before any new feature: compare current GitHub main SHA, active branches/locks, current docs/HANDOFF.md, docs/BUILD-REGISTER.md, docs/PROGRESS-LOG.md, relevant tests, this master plan and source research JSON. Do not overwrite concurrent work or stale task claims.
- Each work item must log OWNER REPO / EXACT PATH / BEFORE STATUS / TESTS / ACTUAL PROOF / ERRORS + FIXES / OUTPUT LOCATION / LICENSE SOURCE / OPEN BLOCKERS / NEXT WORK. On acceptance update handoff, register and feature-specific docs in same commit, push to main safely, and fetch the published files back.
- Existing owner handoffs are authoritative per repo: MGR-3D-FORGE/docs/HANDOFF.md, MGR-API-MCP/HANDOFF.md, MGR-CREATE-Os/HANDOFF.md, MGR-ONE/HANDOFF.md. This master plan lives ONLY in Forge, with short pointers in the other repos. Do not create a rival ecosystem-wide "handoff" claiming status for Tevin.
- Where previous files have obsolete architecture (e.g., mandatory Creation OS in old Forge ARCHITECTURE.md or only two metadata adapters), mark dated history and update current design without deleting historical evidence. Real source/tests beat old prose.
- If this chat ends, the next engineer starts at Forge docs/HANDOFF.md and this master plan, follows source and evidence paths, and resumes the highest-priority OPEN item without asking the owner to repeat decisions. Local-only evidence always has a repository summary receipt and restoration pointer; PRIVATE binary/raw data is not published in public repo.

## 10. Current verification limits

This is PLANNING, not proof of 184 scans or a globally unbeatable platform. The initial commit of Wave A should be published independently before any new REA execution. Existing F01-F128 results are historical tested slices; F129+ programs begin as SPECIFIED or QUEUED until their exact implementation and live results are demonstrated.

## Wave B first verified slice (as of 2026-10-31)

The REA self-release was inspected with supported ZIP carrier after independent official npm TGZ hash check: 2,398 shipped files, complete container scope, source-level semantics not fully proven. MGR Rambler v0 unsigned roster and verification is real but public-key signing/not-inspectable claims are false. Exact code and evidence: forge/security/rambler.py, tests/test_rambler.py, evidence/security/2026-10-31-rambler-smoke.json, evidence/xray/2026-10-31-rea-self-static.json and docs/MGR-RAMBLER-SECURITY.md. Prior phases and unexecuted items remain OPEN.


## Wave C actual partial integration — native Creature Forge and shared ChatGPT workflow (2026-10-31)

One shared creation worker implemented under forge/creature_jobs.py + ForgeWorkstation: stable request IDs and replay, generated authentic original GLB, hash, status, token-controlled downloads; exposed through existing MGR-API-MCP (src/forge-catalog-client.ts / src/forge-mcp-tools.ts, tools:execute and tools:read). Local real cross-process test produced 114192-byte/1748-triangle GLB with SHA b019e661..., token-authenticated downloaded SHA identical; wrong tenant/scope/unauthenticated downloads rejected. Existing viewer/ Creation Chat now offers original creature creation and browser SHA-checked GLB downloads, but **interactive Chrome acceptance unverified**.

Private ChatGPT Forge Creator v0.1.0 skills-only source under MGR-API-MCP/integrations/forge-creator-plugin/ is an interface/workflow, NOT a hosted tool server. A working public ChatGPT/iOS authenticated creation action still needs real external OAuth/protected MCP and private artifact storage; no fake URLs. Detailed current proof in the single docs/HANDOFF.md, docs/BUILD-REGISTER.md F133/F134 and evidence/studio/2026-10-31-creature-bridge-local.json. Higher-quality neural 3D, full rig/edit/animation, Blender/Godot acceptance, world app UX remain open.
