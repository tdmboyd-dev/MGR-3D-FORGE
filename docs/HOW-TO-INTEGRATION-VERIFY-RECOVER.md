# Forge — How To Verify, Repair, Resume and Connect the Shared MGR API/MCP

**No duplicate backend:** MGR-3D-FORGE is the creator. MGR-API-MCP is the single shared service that governs actor/tenant/audience and tools:read/tools:execute. MGR-ONE/Tevin, Forge Studio, ChatGPT Forge Creator and optional Creation OS are clients with differing product responsibilities.

## Getting the source

Clone/checkout the existing real repos as siblings, keeping existing user work/dirty branches intact. Confirm Git main SHA with remote and read **both** current canonical handoffs before edits:

```powershell
git -C MGR-3D-FORGE status --short --branch
git -C MGR-API-MCP status --short --branch
git -C MGR-3D-FORGE rev-parse HEAD
git -C MGR-API-MCP rev-parse HEAD
```

Read Forge docs/HANDOFF.md, docs/BUILD-REGISTER.md and docs/FORGE-ENGINEERING-HANDBOOK.md. Read API-MCP/HANDOFF.md. Never replace a product's source-of-truth with a new plan.

## Local creator smoke — existing shared bridge, not new API repo

```powershell
cd MGR-3D-FORGE
python -m unittest discover -q
node --check viewer/runtime.js
python -m forge.cli build --spec examples/neighborhood.json --out artifacts/new-world
python -m forge.cli serve-studio --world artifacts/new-world --workspace artifacts/new-workspace --port 0

cd ../MGR-API-MCP
npm install --ignore-scripts --no-audit --no-fund --no-package-lock
npm run verify
python scripts/verify-forge-studio.py
```

The actual Python→Node bridge proof produces a source-fingerprinted edited world and a separate original CPU creature GLB, checks stored result SHA, stable replay and denies wrong tenant/missing execute scope/tokenless creature download. It is **not a hosted server** even though the source uses the real MGR API/MCP client code.

Client routes in MGR-API-MCP: `src/forge-catalog-client.ts` routes HTTP calls to Forge Studio; `src/forge-mcp-tools.ts` enforces permissions then registers `mgr_forge_asset_discover`, `mgr_forge_world_create/status`, `mgr_forge_creature_create/status`. `src/mcp-server.ts` and `src/http-server.ts` own real MCP service boundaries. There is no separate "local API/MCP repo."

Forge endpoints in `forge/studio_server.py`: `/api/asset-sources`, `/api/asset-search`, `/api/character`, `/api/relief`, `/api/world`, `/api/world-job`, `/api/world-job-status`, `/api/creature-create`, `/api/creature-status`, `/api/blender`, `/api/blender-status`, `/api/godot`. Endpoint existence doesn't mean hosted reachability or art quality.

## Artifact protection: why old direct links changed

Previously localhost Studio exposed some world/relief/character/Godot/Blender artifact GETs without the same authorization as creatures. In this audit, **all** `/files/` outputs require token header, local Host/Origin validation, bounded size and directory containment. Browser Creation Chat must fetch via authenticated same-origin requests and create a temporary Blob/download, never paste session tokens into URLs. A tokenless GET now correctly returns HTTP 403. Offline world HTML still works as a separate exported file.

## Failure troubleshooting

| Symptom | Check | Correct fix |
|---|---|---|
| 403 on private artifact | Session token, Host/Origin, current Studio session | Authenticated fetch through same Studio; do NOT disable token gate |
| HTTP 400 creation request | JSON schema, allowed keys, creature prompt 8–500, seed/variants, world building ID grammar | Fix caller contract; don't weaken validation |
| Request ID replay mismatch | Stable ID reused with changed input or source SHA | New request ID for genuinely different work, preserve previous files and lineage |
| CREATION_NEEDS_RECONCILIATION | interrupted operation / disk state | Inspect immutable job receipt/files/hash, repair state with evidence; don't blindly rerun |
| Job says done but GLB corrupt | Verify raw glTF header, byte length and SHA, inspect actual mesh | Mark failed/reconcile; never claim completion because job JSON says PASS |
| Blender import fails | Blender path/version, source GLB, rig/weight/units | Run bridge scripts on an authorized worker and second-process reimport |
| Browser UI blank | WebGL2 support, JS syntax, CSP, browser errors, actual Host | Use real Chrome/Edge acceptance not static HTML tests only |
| Node type errors | Existing TS exactOptionalPropertyTypes/contract types | Repair specific declared schema; do not disable compiler strictness |
| Model candidate unavailable | Model license/weight file/GPU and budget gates | No fake installed inference or spend; choose native fallback |
| GitHub stale docs | Compare master/README vs current source and test | Update handoff/register/progress in same commit with date + proof |

## Production/hosted acceptance still missing

The MGR-API-MCP repository contains real hosted HTTP/JWT/JWKS/OAuth code, but local Windows smoke is not proof that this deployed runtime is connected to Forge. It must be tested from the real remote Tevin/ChatGPT identity with correctly scoped OAuth token and tenant, approved worker relay, durable private artifact access, time-bounded signed/download URLs, cancellation, retries and re-opened GLB in Blender/Godot. The ChatGPT Forge Creator plugin's skills-only v0.1.0 private account release is not a remote 3D generator merely because it was created.

## Publish and handoff

Each safe build wave: record exact source/changed files -> reproduce tests -> actual result checksum -> user-facing checks -> docs/HANDOFF.md current entry -> docs/BUILD-REGISTER.md status -> docs/PROGRESS-LOG.md chronological evidence -> push existing main without force -> GitHub readback of source and handoff. Preserve existing old receipts under history instead of rewriting them as today's results.

## Actual new shared MCP typed files and Human/World jobs

In the existing sibling MGR-API-MCP use npm run verify and python scripts/verify-forge-creator-mcp.py to test the official Streamable HTTP client -> authorized shared edge -> Python Forge Studio. The current edge exposes guarded biome, human-lipsync create/status and artifact read with exact 24-hex job ID + SHA-256 + optional GLB binary resource, not a guessed public file URL. The local protocol test uses a fixture JWT verifier, not a deployed OIDC/JWKS issuer. Forge Studio owns real files; no duplicate Vault, no Creation OS middle hop. Missing real hosted worker/ChatGPT/Tevin and neural CUDA model acceptance are OPEN.
