# All-path offline qualification and repairs — 2026-11-02

The follow-through added `retarget-motion` as CLI command 67. The positive CLI retry is in `retarget-cli-receipt.json`, and the independent positive and frozen-clip negative runs are in `../retarget-motion-2026-11-02/REPORT.md`. Godot imported two exported projects with its official 4.7.2 binary and verified actual imported geometry and basic runtime physics. See `godot-runtime-direct/godot-runtime.json`. The first console-wrapper run completed the empty-world fixture and timed out on the second import. The first retarget CLI run wrote its baked GLB and logged Blender shutdown, then hit the subprocess timeout. Those outcomes remain separate from the passing retries.

At the initial publication checkpoint, the completed matrices exercised 52 of 66 CLI declarations: 51 positive workflows, one rejection-only workflow and 14 then unrun. The completion pass below now covers all 66 declarations at scoped local/fixture level. This is related-path qualification, not completion of Forge or all F01–F156 requirements.

Reproduce from the repository:

```powershell
python scripts/verify_forge_path_matrix.py --out evidence/all-paths-2026-11-02/NEW-UNUSED-DIRECTORY --blender "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
```

The script creates original disposable fixtures, performs real subprocess CLI operations and retains results. Optional `--blender` performs actual two-process import/export/reimport, editable .blend reopen and a local render. Omit that option for the bounded CPU-only matrix; the composition command will remain unrun. No provider, model weights, purchases or network workflow occurs.

## Corrected behavior

- Bundle verification now checks that the declared main artifact and sidecars are actually in the verified inventory, including exact main SHA/size agreement and strict byte/hash types. Before repair a safe side.txt hash could falsely qualify a manifest naming missing.glb. This detects inconsistent bytes/metadata, not publisher identity or maliciously rewritten trusted rosters.
- Rambler rejects a roster destination within its release root before creating any directories or file. Previously the advertised external-output contract could produce a roster that failed its own unlisted-file verification. Signing remains absent.
- Zero-building worlds retain real authored ground/roads/parks and receive an overview camera. Empty interior and building-LOD assets are explicitly omitted. Fully occupied worlds similarly omit an empty park GLB while preserving its zero-park manifest. This avoids invalid zero-primitive GLBs and preserves the existing WorldSpec zero-building contract.
- World composition regenerates inventory and additional-artifact references for its actual new files. It no longer copies obsolete city hashes and uncopied sidecars into the combined bundle. The composed main GLB, editable scene, preview, independent proof and composition receipt all verify; original source identities remain separate.
- Godot source packaging now checks all eight box corners for each authored building plus the ground footprint against bounded transform-aware GLB world positions. Shifted collider metadata and changed ground dimensions fail before output. It reuses the static GLB reader from the original imported-morph owner. The two-millimeter corner witness is deliberately narrower than triangle/volume intersection or Godot physics acceptance.

## Actual results

`offline-matrix-initial/matrix.json` preserves the real initial zero-building failure. `offline-matrix-integrity-repaired/` preserves the subsequent state. `offline-matrix-final/matrix.json` contains 60 cases, zero failures and explicit expected rejections, including source tamper, missing declared artifacts, unknown asset acquisition, NaN FX radius, overwrite refusal, corrupt cell bytes, shifted Godot colliders and release tamper/unlisted-file refusal.

The final independent Blender composition reimported 204 city faces and 216 biome faces (420 total), reopened the editable .blend, rendered the retained preview and passed composed-bundle verification with six files. The preview was inspected: authored block city, roads and surrounding alien terrain are present. This is geometry/composition evidence; the image remains a simple prototype and is not owner art acceptance.

Source digests are retained before and after the run. Only creature_rig.py changed concurrently; this matrix does not execute rig-creature. Exercised owners were stable. This does not substitute for the parent serial regression and final source reconciliation.

Focused runs: 78 tests (integrity/Rambler/world-editor/image-relief compatibility), 63 tests (parity/cells/layers/engine/GPU/models/FX/materials/biome), 97 tests (zero/full occupancy and existing world/camera/engine paths), 13 tests (composition/jobs/integrity), and 20 tests (Godot corner and integrity regressions) passed. These runs overlap; their counts must not be added into a unique-test total. The parent owns final full-suite execution.

## Open acceptance

No Godot process was run. The package has authored colliders and a camera, not proven game physics/navigation. The corner witness does not prove closed collision volumes or arbitrary mesh surface coverage. Native source and bounded fixtures are not live-provider generation quality. Browsers, authenticated shared MCP, imported morph/rig/image workflows and other current command branches have separate owners/receipts; the 14 commands not run across completed matrices remain unassessed by these CLI receipts. Current native inventories map all 156 feature IDs to related cases where applicable and keep whole-feature acceptance open.

## Expanded CPU and independent Blender receiver matrix

`offline-matrix-extended-uv/matrix.json` passed 80 actual cases across 39 distinct CLI declarations. It adds real CPU image relief, calibrated orthographic mask fixtures and analytic scoring, planar rectification, imported static morph, original fully seamed/padded UV atlas, character source/readiness, source identity and raster comparisons, visible-part admission/extraction/proxy, native editing and pipeline. No model/texture generation or arbitrary photograph depth was inferred. It includes approved 16px cropped-part proxy output while keeping original source admission at 64px minimum.

The earlier extended matrix preserved two actual failures. `rectify-mask` sliced Pillow ImagingCore, and `compare-renders` referenced a branch-local import before binding. Both were repaired and re-executed. Rectification now samples consistent integer pixel centers and preserves foreground at the last row/column on identity. The crop defect was independently reproduced, fixed and exercised at 16px and 32px without relaxing original reference checks.

`blender-cli-inspections-final/matrix.json` passed 16 actual commands including independent Blender GLB import/facts/material sockets, editable candidate reopen, material separation, skinned mannequin pose measurements, deforming motion GLB export/reimport and editable-world Blender-to-native round trip. The initial trial used the wrong expected reopen SHA (.blend bytes instead of admitted original GLB); the receiver correctly rejected the harness mismatch. Original failure and corrected run are retained. No repeated Cycles render was part of this receiver matrix.

The checkpoint originally recorded asset acquisition rejection-only and 14 wrappers pending; the following table preserves that checkpoint. The completion pass below now records positive scoped evidence for those wrappers. The current JSON merges the finished receipts, and there is no blanket missing-hardware or missing-credential claim. Full provider generation, real Godot import/play, arbitrary scene reconstruction, production authoring and all feature-level acceptance remain open.

| Current CLI wrapper not run in these completed matrices | Next exact evidence |
|---|---|
| `blender-cinematic` | Existing Blender installed. Actual bounded multi-shot render invocation not yet in completed matrix. |
| `blender-director-audit` | Requires the saved cinematic .blend with real authored cuts. Not blocked by credentials or hardware. |
| `blender-director-frames` | Requires the saved director .blend and actual four-frame rendering; next bounded receiver run. |
| `blender-fx-render` | Requires actual paired CPU renders for atmosphere comparison; not a missing provider. |
| `blender-pose-render` | Requires rig .blend and independent renders; current matrix separately verified actual rig and motion without rendering pose pair. |
| `blender-render` | WorkBench receiver invocation not run in completed matrix; separate Blender composition render is a different command. |
| `blender-studio-witness` | Actual bounded CPU materials/light/strand/volume witness not run by completed CLI matrix. |
| `human-audio-motion` | Separate current native/Blender receiver proof exists. CLI wrapper still not run in completed matrix; use original PCM fixture. |
| `human-lipsync` | Separate current native/Blender receiver proof exists. CLI wrapper still not run in completed matrix; use original timed cues. |
| `judge-atmosphere` | Needs matched real control/candidate render and source receipts; no synthetic image may qualify a real render. |
| `kit-mirror` | Network archive transfer excluded from CPU matrix. Offline synthetic transport can exercise original handler without claiming live publisher archive or license. |
| `rea-kit-audit` | Needs exact matching archive/pack receipt and actual REA file evidence. Targeted own fixture run pending; historical publisher REA remains separate. |
| `rig-creature` | Separate current rig receiver evidence exists. CLI wrapper requires new original creature fixture and real Blender; no model download needed. |
| `serve-studio` | Current authenticated browser/HTTP proof separate. Actual CLI process startup/termination not in completed matrix. |

## Completion pass: all 66 current CLI declarations exercised

The updated `cli-command-coverage.json` records **64 actual local/receiver/REA workflows and two explicitly synthetic transport CLI contracts**. No command in this pinned set is wholly unrun. This supersedes the earlier 52-command checkpoint, while keeping its actual failures and bounds. It does not close every parameter branch, every client, or any whole F01–F156 requirement.

- `remaining-blender-cli/matrix.json`: all 17 actual command cases passed, including bounded World WorkBench rendering, cinematic camera .blend, independently audited timeline and four rendered frames, two actual matched portal/volume renders, measured atmosphere comparison, CPU light/material/hair witness, mannequin pose renders, timed and audio-driven Human CLI, and original creature rig CLI. Source before/after fingerprints are retained; separate newly added files are outside the captured original source list. The Blender bridge's existing fixed resolution/sample limits were used.
- `remaining-cli-support/serve-studio-cli.json`: original CLI `__main__` served on loopback in its own process, denied anonymous saved reads, authenticated the Studio UI, created exactly one original fixture creature, reopened saved status and verified exact native input, then exited zero with a test-only stdin graceful-stop shim. The ephemeral token was captured only in process memory and is not in evidence.
- `remaining-cli-support/kit-mirror-fixture.json`: actual CLI parser and original owner preserved the exact 2,150-byte original fixture ZIP through injected offline transport, retained two license-scope claims and one outside-scope file, and kept rights review false. This is not a live publisher acquisition or a rights determination.
- `remaining-cli-support/rea-kit-audit.json`: actual REA safe inventory record `ev_2d8249f3bdef7d99318267434cc74471789c8ebc56199310e9d4fc28210b4ca1` inspected the same own ZIP, and Forge CLI independently matched all 3 child SHA/size identities. The opened target was closed. This is ZIP-entry evidence only, not algorithm or provider inspection.
- `asset-acquire-cli-fixture/asset-acquire-fixture.json`: actual CLI parser and original catalog/acquisition owner inspected, quarantined and reopened an exact original 1,656-byte GLB through injected offline transport. The original undiscovered-slug rejection remains retained. No provider network transfer or rights/production acceptance occurred.

Reproduce the CPU/render phases with `scripts/verify_forge_path_matrix.py --extended`, `--blender-inspections-only`, or `--remaining-blender-only` as applicable, using a new output directory and the installed Blender binary for Blender phases. `scripts/verify_forge_kit_studio_cli.py` supplies `serve`, `asset`, and `kit` modes; kit mode emits the own ZIP/pack receipt in an ignored local fixture folder for independent REA `inventory_artifact` and subsequent `rea-kit-audit`.

The actual matched atmosphere run measured RGB MAE 28.029504 against threshold 3.0; that is a fixed-camera pixel difference, not smoke dynamics or artistic acceptance. Real Godot engine import/play, hosted OAuth/Tevin/mobile, live asset-provider transfer and neural generation remain separate open acceptance.
