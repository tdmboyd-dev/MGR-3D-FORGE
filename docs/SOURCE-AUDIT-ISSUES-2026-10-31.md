# MGR Forge — Real repo audit, bugs, corrected architecture and open integration

**Evidence class:** complete tracked-file baseline at 3 Git SHAs: Forge 405, real shared MGR API/MCP 169, Creation OS 365; read/AST/text static only. The exact hash list is in each repo's evidence/audits/2026-10-31-baseline-static-inventory.json. Different ongoing workers or current branches may have newer edits. Current truth and acceptance at docs/HANDOFF.md.

| Issue ID | Status | Owner source paths | Verified fact or gap |
|---|---|---|---|
| AUD-FG-001 | CLOSED_FIX_VERIFIED | forge/studio_server.py; viewer/runtime.js; tests/test_studio_server.py | Different private local Studio artifacts had inconsistent token gating; older world/relief/character/Blender/Godot artifact URLs could return on loopback without Studio token. |
| AUD-FG-002 | FIXED_IN_DOCS | docs/MASTER-FORGE-PROGRAM-2026-10-31.md; docs/FORGE-ENGINEERING-HANDBOOK.md | Master Plan falsely implied complete repo review and referenced nonexistent forge/fantasy.py. |
| AUD-FG-003 | FIXED_CURRENT_DOCS | README.md; docs/WHAT-WE-HAVE.md; docs/HANDOFF.md | October 30 17/2 source counts, 543 tests and broken F110 GPU summary remained visually prominent. |
| AUD-FG-004 | STATIC_COMPLETE_BEHAVIOR_OPEN | evidence/audits/2026-10-31-baseline-static-inventory.json; docs/ACTUAL-FORGE-MODULE-MAP-2026-10-31.md | Previous planning did not enumerate all current repo files. |
| AUD-MCP-005 | STATIC_COMPLETE_BEHAVIOR_OPEN | evidence/audits/2026-10-31-baseline-static-inventory.json; docs/API-MCP-ENGINEERING-HANDBOOK.md | Term local API/MCP led to potential duplicate-repo confusion. |
| AUD-CO-006 | STATIC_COMPLETE_BEHAVIOR_OPEN | evidence/audits/2026-10-31-baseline-static-inventory.json; docs/CREATION-OS-ENGINEERING-HANDBOOK.md | Creation OS was incorrectly treated as mandatory Forge router in older architecture. |
| AUD-FG-007 | OPEN_ART_CAPABILITY | forge/voice.py; forge/character_motion.py; docs/HOW-TO-MORPH-RIG-LIPSYNC.md | No verified audio-to-viseme/shape-key facial lip sync in current Forge code. |
| AUD-FG-008 | OPEN_ART_CAPABILITY | forge/morph_engine.py; forge/creature_rig.py; forge/creature_rig_recipe.py | Morph currently 4 bounded spatial controls and skeleton prototypes; arbitrary topology/weight/motion preservation unproven. |
| AUD-FG-009 | OPEN_SOURCE_GATES | research/external-provenance/BEAST-3D-RESEARCH-UNIVERSE-2026-10-31.json | 184 candidate queue counted as if exhaustive researched libs and possible installed assets. |
| AUD-FG-010 | OPEN_OWNER_UI | viewer/runtime.js; viewer/template.html; forge/studio_server.py | Static/HTTP UI verification isn't a real browser acceptance screenshot or tested previews. |
| AUD-FG-011 | OPEN_HOSTED_CONNECTION | src/http-server.ts; src/mcp-http.ts; src/forge-mcp-tools.ts | Local tests do not demonstrate hosted MGR API/MCP can invoke user workstation via secure authenticated relay. |
| AUD-FG-012 | OPEN_PROVIDER_AND_RIGHTS | forge/generative_backends.py; forge/data/generative_engines.json | Candidate neural model sources not installed; root code rights do not grant model/dataset permissions. |
| AUD-FG-013 | OPEN_OFFSITE_BACKUP | forge/assets.py; forge/pack_mirror.py | Preserved private asset archives local; independent offsite restore unproven. |
| AUD-FG-014 | RISK_HEURISTIC_NOT_DEFECT | forge/*.py; evidence/audits/2026-10-31-baseline-static-inventory.json | Static low-import modules may seem unused, but dynamic registration and CLI entrypoints can call them. |
| AUD-MCP-015 | FIXED_TESTED | MGR-API-MCP/docs/history/FORGE-SOURCE-CHECKPOINT-2026-10-30.md; WORK-STATE.md | Historical relative Markdown link fixed to real root file; 184 repository integrity checks PASS. |

## Root fix examples

AUD-FG-001: Fixed the old inconsistent localhost Studio file authorization in forge/studio_server.py, viewer/runtime.js, and tests/test_studio_server.py. Every private artifact now requires token, with foreign Host/Origin refusal. Existing Create Chat uses token-bound fetch and local blob download instead of naked /files/ links. Static and HTTP authorization passed; Chrome visual flow not independently accepted.

AUD-FG-002: The earlier 'Master Plan' wasn't a full source audit; correct it as an expansion roadmap. Reuse actual existing FX/motion modules instead of inventing forge/fantasy.py. Every proposed machine should map to the actual source and test before build.

AUD-FG-007/008: No evidence of an end-to-end audio lip sync engine or arbitrary topology-preserving morph-rig. Existing voice capture and rig prototype are genuine partial engines. Research source decisions and full how-to are in docs/HOW-TO-MORPH-RIG-LIPSYNC.md; do not count them done.

## No-work-lost protocol

On a new chat: read the one handoff first, the ACTUAL-FORGE-MODULE-MAP and source inventory, follow feature register and this gap ledger; verify the real Git HEAD and user changes before fixing. Open a specific receipt with exact file path, test commands, nonpassing evidence and next action for every issue. Do not erase earlier successful data or duplicate a component just because an older plan recommends it.

## 2026-10-31 new creation-wave audit issues and repairs

AUD-FG-016 FIXED: Real Blender import script failed after factory reset because sc.world was None. Bridge blender_biome_proof.py now creates World explicitly. Independent second-process reopen and render 864 faces in evidence/world/2026-10-31-native-biome-blender.json.

AUD-MCP-017 FIXED: src/mcp-server.ts claimed tools:write in system info while real execution uses tools:execute. Fixed and tested without inventing a second permission or server.

AUD-FG-018 OPEN ART: Real Human face animation currently uses supplied phoneme times and generic anonymous mannequin. Audio alignment, anatomy/jaw/tongue, film-grade identity, 200-plus animations and arbitrary topology retarget not accepted.

AUD-DEPLOY-019 OPEN HOSTED: Existing MGR-API-MCP HTTP/OAuth source is not proof of a deployed real OAuth endpoint reaching the owner computer or an actual cloud GPU. Separate secure worker/object store and real Tevin/ChatGPT session required.

AUD-FG-020 BROWSER QUALITY GATE: Real Chrome creature morph, biome and city editor passed. Human Studio browser worker had a genuine FAILED status; current worker now writes private human-error.json for diagnosis instead of swallowing exceptions. Until exact passing Chrome receipt exists, Human browser acceptance is OPEN.

## Follow-on November 1, 2026: recovery and new gaps

- AUD-FG-021 [REPAIRED] Current CLI expanded from 62 to 64 parser commands with new WAV-reactive Human Forge and one GLB World composition; docs/FORGE-ENGINEERING-HANDBOOK.md and tests/test_source_handbook.py updated from exact AST. 19 affected tests passed.
- AUD-FG-022 [NEW VERIFIED LIMITED] Real authorized synthetic PCM WAV -> bounded RMS-reactive jaw curves -> real Blender facial GLB and authenticated Studio passed; true phoneme/viseme recognition and human visual acceptance remain OPEN. Code forge/audio_motion.py, forge/human_lipsync.py, forge/human_jobs.py and evidence/human/2026-11-01-*.json.
- AUD-FG-023 [NEW VERIFIED LIMITED] City and native biome combined into independent Blender-reopened scene plus Godot project source. No actual Godot engine play/navmesh/collision acceptance. Source forge/world_composition.py, forge/world_composition_jobs.py and evidence/world/2026-11-01-*.json.
- AUD-FG-024 [REA SOURCE-ONLY] SkinTokens source ZIP contents fully statically inventoried; three targeted partial source bundles for Rhubarb, UniRig and Terrain3D. No deep algorithm, weights, model training/runtime, provider permissions or 187-target completion. Source evidence/xray/2026-11-01-*.json.
- AUD-FG-025 [OPEN HOSTED/NEURAL] Real remote OAuth/JWKS Forge worker+object store, ChatGPT/Tevin integration, licensed high-detail neural 3D/rigging and audio phoneme output still require verified provider capability, GPU budget, physical engine/owner acceptance.
