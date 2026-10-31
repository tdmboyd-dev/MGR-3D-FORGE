# MGR 3D Forge — direct creation + kit preservation (2026-10-31)

This is the architectural decision record. **`docs/HANDOFF.md` remains the sole current Forge resume authority.** This file is a technical reference, not a second status database.

## Product boundaries

MGR 3D Forge is a standalone character, creature, asset, environment, animation and 3D world creation engine. People use it directly via its Studio/CLI, and assistants/apps use it through the shared MGR-API-MCP edge. Tevin/MGR-ONE is a client, not its sole reason for existing.

MGR-API-MCP owns authentication, permissions, tenant identity and external MCP transport. It must not own another asset vault, geometry worker or shared creative database. Forge owns its own geometry/asset/job files, history, safety QA, license receipts, worker recovery and rendering.

MGR-CREATE-Os is an **independent optional coordinating product**. It provides multi-factory workflows for campaigns, film, apps and media involving several specialized systems. A plain Forge creation request **must not depend on Creation OS**. Creation OS may call Forge via the same governed API/MCP route. Its existing MediaFactory does not produce 3D geometry; "SUCCEEDED" requires a real referenced verified artifact.

## Proven local flows and boundaries

- Forge Studio supports authenticated read-only source search and real world edits via /api/world. New owner world jobs: /api/world-job accepts an immutable request_id and source-fingerprinted edit document, persists job outcomes and file digests; /api/world-job-status reconciles/reopens. Duplicate ID with changed input fails; uncertain interruption never silently repeats.
- The shared MGR API/MCP routes source discovery, world create and world status through its existing authenticated MCP server. Write requires the **existing** `tools:execute` scope, correct verified tenant/audience, and an exact bounded edit document. Read requires `tools:read`.
- Local actual Forge Studio HTTP → Node adapter + MCP-policy function has produced one 13,964-byte world GLB with SHA-256 `89144125aa7e9ac42d755a10eabdd283d6271cb2fb5f2af948d84e45fb0198ac`, repeated the request with exactly the same artifact, and denied wrong tenant/missing execute scope. This is local process proof, **not live hosted MCP protocol, Tevin launch, user review, or independent Blender acceptance of that specific world**.
- The older 2026-10-30 device proof on Time's Windows Blender 5.2.2 independently imported, saved, reopened and rendered the 3DAssets.dev dragon and a Kenney mirror GLB. Both remain rights/visual/animation unapproved. That test does not confer rights.

## Three distinct types of assets

1. **Source directory/catalog entries:** can be searched, not installed. Existing Atlas has 18 source families; live adapters now 3DAssets.dev, Poly Haven and official ambientCG v3. All other entries are research/discovery until tested.
2. **Quarantined copies:** exact archive/model is downloaded to private content-addressed storage, source commit, SHA-256, license text/scope and file manifest recorded. No automatic insertion into user worlds, training, public distribution or third-party export.
3. **Accepted production assets:** separate per-file license/rights review (including embedded media, trademarks, personalities, provenance), mesh/texture/rig/render checks and the applicable target-engine round trip. A successful ZIP download never implies acceptance.

## Selective preservation policy

Mirror selected **official pinned commits and rights-reviewed packs**, not indiscriminate sites or all Hugging Face datasets. This protects availability if a website disappears while keeping legal obligations. Official release assets and mirror repositories have different trust levels; never assume the parent repo license applies to every file.

Pilot: KayKit-Game-Assets/KayKit-Prototype-Bits-1.0 commit `bb159596f4f5106b663741d002c8eb45c80c0f41`; archive 773,696 bytes, SHA-256 `17985aed180fe2f658c526e92dc300f2fde72db09494433153c7e808c6137afe`, 302 archived files, preserved locally under `%USERPROFILE%\Documents\MGR-Forge-Vault`. The CC0 notice was discovered in `addons/kaykit_prototype_bits/Assets/LICENSE.txt`; therefore the **whole repo is NOT automatically CC0 cleared**. The receipt holds the license scope, file hashes and rights-review pending. No archive committed to source Git.

Priorities: curated CC0 Kenney packs, selected KayKit asset subtrees, ambientCG materials, Poly Haven models/HDRIs, MakeHuman core data (separate GPL/copyleft software concerns). Mixed rights: Quaternius, community MakeHuman packs, Sketchfab, OpenGameArt, Objaverse and public GitHub/Hugging Face repositories **must be reviewed per asset**. Do not mirror their full catalog without rights clearance.

## Portability & backups

GitHub contains code, recipes, provider adapters, non-sensitive license manifests, contracts and tests—not hundreds of gigabytes of binaries. Keep master ZIPs/GLBs/textures in private Forge Vault with an immutable object digest and source/commit/version; replicate vetted snapshots to a second secure off-device backup when a destination and credentials are approved. Test restore hashes, do not rely solely on a single Windows PC. No remote backup is claimed done.

## GPU planner

Recovered **behavior** rather than the old missing source bytes: `gpu-plan --jobs ... --out ...` now runs locally. Uses deterministic first-fit decreasing paid time blocks plus shadow-only backfill; no extra billed block created for shadow work. Without fresh caller-supplied provider quotes, returns `UNPRICED`. With dated HTTPS-source quotes, computes a **dry-run** estimate, excluding cold starts/egress/storage/taxes. Does not start, stop or purchase any GPU. Original historical implementation's other provider features were not recovered and remain unverified.

## Next acceptance gates

- Reopen the official KayKit archive and import at least one **license-scoped** included GLB/FBX into actual Blender and game engine; inspect materials visually; document source file hash, no automatic acceptance.
- Add more official pinned pack categories with independent license scopes, duplicate detection, legal review queue and restore verification. Extend official ambientCG download+material map and Poly Haven export only after tests.
- Build Human/Creature Forge creators using character DNA, skin/morph, shape-key, species rigs, anim retargeting and 200+ targeted motions; test real face likeness/rig deformation, do not count source listings as functionality.
- Recreate human-facing Forge Studio browse-to-create-to-preview-to-edit journey; run real Windows Chrome, Blender and target-engine checks on current source.
- Test actual MGR-ONE/Tevin authenticated hosted MCP client and permissioned Forge job, service restart, error reconciliation, job cancellation and remote bearer credential setup; no extra router or mandatory Creation OS detour.
