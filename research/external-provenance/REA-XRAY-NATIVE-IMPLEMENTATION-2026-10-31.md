# REA X-Ray → original MGR 3D Forge engineering (2026-10-31)

**Document class: source/evidence and architecture reference, NOT a second handoff or blanket legal clearance.** The one current Forge handoff is `docs/HANDOFF.md`. The active feature register is `docs/BUILD-REGISTER.md` (F128).

## Identity and installation that were actually proven

- Official upstream: https://github.com/morluto/rea (REA, Reverse Engineer Anything); observed Git main `6e9ee97a69cb16c7150d8b550e705cba055ee4f0`. This observed SHA does **not** assert that the npm release was built at the identical commit.
- Official npm: `rea-agents@6.8.0`, release SHA-512 integrity `sha512-9QDeRnGqEDzABZyr04eLnBXBv/c6I9/TWu/6M0MD4pEfkySI/BIgwTODIbAReX3C1x6hjw9+Jlx4A2yUSPZ9ww==`. REA-authored code MIT, preserve upstream notices and independently licensed dependencies. Runtime Node 24 requires >=24.22.1. Owner PC global Node was 24.21.0 (too old); a portable **official SHA256-verified Node 24.22.1** installed under `%USERPROFILE%\.mgr-tools\rea\node\node.exe` without changing global Node. Node publisher ZIP SHA-256 `d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5`.
- Isolated official npm package installed under `%USERPROFILE%\.mgr-tools\rea\runtime`, package scripts disabled. `rea --version --json` verified `rea-agents 6.8.0` on Node 24.22.1; a real `inspect-artifact` call succeeded. Not installed in Forge's core Python interpreter or its 3D generation runtime. No money spent.
- Private account plugin **MGR REA X-Ray** version 0.1.0: https://chatgpt.com/plugins/plugins_6ae674d617d881919da938edf6e018d4 ; source in sibling `MGR-API-MCP/integrations/rea-xray-plugin/`. Plugin uses a minimal local stdio MCP wrapper around one read-only REA static command; it is not REA's unrestricted full MCP surface. The exact saved plugin archive was fetched back, started locally, listed its tool, denied a file outside its allowlisted workspace and inspected the same pinned ZIP. Account installation alone does **not** make local files available to mobile ChatGPT; a compatible local host/connected execution environment remains necessary.

## Actual evidence-to-Forge end-to-end pilot

Target was owner-preserved official `KayKit-Prototype-Bits-1.0` pinned source commit `bb159596f4f5106b663741d002c8eb45c80c0f41`, ZIP SHA256 `17985aed180fe2f658c526e92dc300f2fde72db09494433153c7e808c6137afe` (773,696 bytes). A copy was staged under `~/.mgr-tools/rea/workspace/packs`; original Forge Vault bytes remained untouched.

1. REA static `inspect-artifact --detail summary --evidence_output <scoped-file> --json` required **both** summary and complete Evidence. First invocation without `--evidence_output` failed `invalid_request`; fixed before integration. Full authoritative Evidence was retained locally (718,948 JSON bytes) as REA's application bundle. Not checked into Git because it carries unnecessary local absolute paths; public output is redacted to hashes/results.
2. REA full bundle's `records[0].normalized_result.coverage` reports `{scope:container-entries,status:complete}`. 310 occurrences included the root ZIP and seven directories; 302 independent child files matched the Forge receipt's **302 sha256 hashes and byte sizes**. REA identified 232 unique content nodes, which is not the number of distinct models. The Forge receipt catalogs 72 glTF candidates; those are not proven animated characters or 72 distinct usable character rigs.
3. Added **optional REA Evidence Bridge** `forge/xray_kit.py` and `rea-kit-audit` CLI. It reads the full REA Evidence bundle and pinned Forge Vault receipt, rejects archive digest drift, incomplete REA coverage, unsafe/duplicate ZIP names and any changed/missing child byte hash. It emits `mgr.forge.xray-kit-audit.v1` with observed extension types and five actionable original MGR build-target areas. No third-party code, images, vertex geometry or restricted model weights are copied.
4. Real crosscheck output: `evidence/asset-atlas/2026-10-31-rea-official-kaykit-proof.json` status `INDEPENDENT_BYTES_MATCH_RIGHTS_AND_ART_REVIEW_PENDING`, `source_file_sha256_matched:302`, `rights_reviewed:false`, `safe_to_redistribute:false`. The original KayKit `Assets/LICENSE.txt` scope was recorded in the Vault. This is an independent **byte/inventory verification**, not a grant for raw model distribution, an original creation technology, or proof of missing code from a binary.

## Can REA help us make MGR totally original?

**Yes for studying features and identifying technical principles; not by copying proprietary expression or waiving licensing.** Using a self-authored mesh generator, our own shader implementations, geometry rules, authored rigs/skin weights, fresh artwork, and legally reusable source/code/weights can reduce dependence on kit vendors. A copy or translated version of a restricted mesh remains subject to its own legal and contractual constraints. Reverse engineering may also be limited by contracts, patents, trade secrets and privacy, so flag scoped legal review for restricted sources rather than claiming magic unrestricted rights.

REA's ZIP inspection cannot reveal the training data, underlying Tripo/Meshy/Higgsfield weights, proprietary sculpting tools, artistic design process, or how a model was originally generated. A glTF file reveals geometry and material/rig structure **if separately parsed**, not the original authoring algorithm. For independent *shape generation*, continue Forge Native Imagination, `morph_engine`, `creature_rig`, lawful Pixal3D/TRELLIS.2 checkpoints and real Blender/Godot acceptances.

## Actual independent product wiring

- **MGR BEAST X-Ray:** repeatable source/asset investigation, rights evidence, comparison; no competing agent brain.
- **MGR API/MCP:** owns shared assistant authorization and transport. The dedicated local REA plugin is optional read-only tool access and remains intentionally narrower than a full REA MCP. No remote REA file-inspection HTTP endpoint exposed.
- **MGR 3D Forge:** owns `forge/xray_kit.py` optional evidence normalization, the current Forge Vault/Source Atlas, original geometry/rigger/world toolchains and their single feature register. No REA dependency for ordinary user world creation.
- **MGR Creation OS:** optional for cross-factory projects; must never become a mandatory middleman for Forge or another vault/queue.

**Minimum full user journey** (still OPEN as a clickable UI): From standalone Forge Studio / Tevin client, select a licensed source package or original generation brief → source/rights admission → REA static inspection only when useful → existing Forge Vault snapshot → original shape/rig/world job → SHA receipt → Blender render → target engine play → user revision/reopen → recorded progress. Currently a reproducible **local CLI evidence pipeline**, not a hosted on-click end-to-end product.

## Next measures to beat proprietary generators

- Benchmark same prompts, images and target engines for original shape detail, shape invariants, PBR textures, UV, rig/animation quality, world complexity, editability, latency, compute price and human judgment. One REA pass never proves quality superiority.
- Build native semantic mesh/skin/rig morphing, procedural scenery, truly original appearance generation, cloth/hair/facial deformation and reversible editing. Store evidence from 3D acceptance, not only static ZIP inventories.
- Add scoped X-Ray browse/preview in Forge Studio only after local permission paths, UI/tenant binding and browser QA. Do not expose arbitrary REA file paths or shell commands from an untrusted browser.
- Use pinned permissive libraries/weights in isolated environments; third-party-license matrices are already in `NEXT-GEN-MORPH-RIGGING-2026-10-31.md`. No blanket claims about "unlimited" APIs, storage or GPUs.
