# MGR Forge — Asset Packs, REA X-Ray, Licensing and Durable Vault

**One truth:** docs/HANDOFF.md current, docs/BUILD-REGISTER.md capability status, full source list research/external-provenance/BEAST-3D-RESEARCH-UNIVERSE-2026-10-31.json. The register has 187 target records (184 originally queued and 3 newly sourced-only), NOT 187 acquired/installed kits.

## 1. Available tools (actual files)

`forge/asset_atlas.py` + `forge/data/asset_sources.json`: 18 source families, with actual live metadata adapters for 3DAssets.dev, Poly Haven, ambientCG (only three). `forge/assets.py`: local hash-addressed asset storage with source metadata and quarantined state. `forge/pack_mirror.py`: pinned allowlisted official KayKit snapshot/archive; byte inventory and nested license-scope claim receipt; no automatic distribution rights. `forge/xray_kit.py`: compare full REA static ZIP evidence against independent Forge Vault source manifest; fail on missing/hash-different file.

`MGR-API-MCP/integrations/rea-xray-plugin`: separate private plugin that can inspect **authorized local packages** when connected to the right host; it is NOT a universal secret model decoder or an already-connected ChatGPT/iOS file reader.

## 2. Source discovery and bounded intake

```powershell
python -m forge.cli asset-sources --category fantasy-creatures
python -m forge.cli asset-sources --category skin-materials
python -m forge.cli asset-search --catalog artifacts/source-atlas --provider polyhaven --kind models --query rock --live --limit 4
python -m forge.cli asset-search --catalog artifacts/source-atlas --provider ambientcg --kind textures --query leather --live --limit 2
python -m forge.cli asset-acquire --catalog artifacts/source-atlas --slug ACTUAL_DISCOVERED_SLUG --store artifacts/private-forge-vault
```

The last operation downloads one previously discovered model to quarantine; doesn't grant commercial rights or rigging. Do not run a public catalog crawl as a bulk raw library mirror.

For a pinned official KayKit repository where exact subtree/license was confirmed:

```powershell
python -m forge.cli kit-mirror --repo KayKit-Prototype-Bits-1.0 --commit bb159596f4f5106b663741d002c8eb45c80c0f41 --store artifacts/private-forge-vault
```

Example prior source proof: KayKit Prototype Bits commit `bb159596f4f5106b663741d002c8eb45c80c0f41`, original ZIP SHA-256 `17985aed180fe2f658c526e92dc300f2fde72db09494433153c7e808c6137afe`, 773,696 bytes, 302 ZIP files, including 72 glTF entries. CC0 was observed in its **nested Assets subtree**; that does not grant rights over future sibling folders or arbitrary mirrors. All admitted files still need art/engine acceptance.

## 3. REA package inspection is evidence, not permission

REA itself: official `rea-agents@6.8.0`, installed in a separate Windows runtime from Node global; snapshot license MIT for REA-authored code, third-party dependencies separate. Exact self-inspection report `research/external-provenance/REA-SELF-AUDIT-2026-10-31.md`; REA found 2,398 npm release files in a derived ZIP carrier. This does not prove how proprietary generators were trained.

When there is an **authorized** real full REA ZIP Evidence document and a previously stored Vault receipt, compare them:

```powershell
python -m forge.cli rea-kit-audit --rea-evidence path/to/full-rea-evidence.json --pack-receipt path/to/vault-pack.scope-v2.json --out artifacts/new-rea-crosscheck.json
```

Requires same archive SHA and each child hash/byte count to match, complete container evidence, no unsafe paths. A valid finding is INDEPENDENT_BYTES_MATCH_RIGHTS_AND_ART_REVIEW_PENDING; it does NOT make a restricted asset "MGR Native" through copying, recoloring, reskinning or conversion.

## 4. Exact rights-to-production checklist

1. Establish source owner/publisher (not just GitHub mirror title), original immutable version, actual archive/file URL, SHA-256.
2. Inspect code license separately from art/music/skin/scan models, weights, dataset, third-party dependencies and included nested folders. User "free" and MIT-root repository are NOT enough.
3. Record a specific action allowed: private download/backup, artwork inside a project, standalone raw redistribution, public asset-library distribution, model training, AI hosted usage. These are different legal rights.
4. Apply applicable platform terms (Quaternius QAL newer redistribution limits, MakeHuman community mixed terms, Hugging Face gated/restricted checkpoints, licensed human imagery/voice consent).
5. Admit only the permitted scope of source material, without auto-executing scripts or bundled executables. Keep original files/notice, edit copies separate and reproducible.
6. Test a representative glTF/FBX/OBJ/texture in actual Blender, reopen saved project and render; inspect rig/weights/animation, game engine roundtrip and visual use.
7. Mark production-accepted only after rights and quality gates independently passed with evidence. Otherwise keep quarantined.
8. Retain off-machine secure **owner-controlled** backup/restore and verify its hashes. The prior local Windows Vault is not proof of a working offsite backup.

## 5. MGR-native improvement process

REA maps permitted observable features -> original requirements. Forge's existing modeling algorithms, procedural worlds and morph/rig engines implement independently written behavior. Preserve license from third-party sources even when their concepts inspire improvement. Do not promise removing any restriction by reverse-engineering a purchased pack. Proprietary Meshy/Tripo/Higgsfield backend weights are not recoverable from output assets by REA.

## 6. Failures and recovery

- Source unavailable: inspect cached catalog/receipt; do not silently assume permission or invent a copy.
- Hash mismatch: quarantine the new file, retain old verified release and log version drift.
- ZIP incomplete: reject; avoid unsafe archive expansion and path traversal.
- Wrong license: do NOT reclassify as CC0 just because a neighboring folder has a license. Move to rights review or rebuild original MGR asset.
- Missing original Vault media: do NOT claim source Git contains the binary. Restore from verified backup or re-fetch exact publisher version where legally permitted.
- REA inspection unsupported target: store an accurate negative receipt, don't mark as passed. The official REA npm TGZ required a separately verified derived ZIP carrier; that is a format workaround, not upstream bytes.
