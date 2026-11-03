# MGR 3D Forge — How to Use It

## Make a measured image hull or revise an uploaded static model

In the running authenticated Studio, open **Creation Chat**. To revise a model, choose its GLB in the existing model upload control, open **Morph the uploaded static model**, set the six shape controls and create the revision. The original upload remains saved. Length, height and width are multipliers; bend and twist are degrees. Repeating exactly the same upload/settings reopens the same job. Changing settings makes a new recoverable revision.

This path accepts a bounded self-contained static GLB up to 900,000 bytes in Studio. It preserves original parts, scene transforms, UVs, embedded images, material definitions and indices. It refuses skinned or animated models, existing blend shapes, compressed geometry and external dependencies rather than silently dropping them. The CLI supports a larger native static subset:

```powershell
python -m forge.cli morph-model --source artifacts/owned-static.glb --morph examples/owned-morph.json --out artifacts/owned-static-revision-01
```

Create your own recipe JSON, for example `{"length":1.3,"height":1.0,"width":0.9,"bend_degrees":8,"twist_degrees":10,"taper":0.9}`. The example recipe filename above is user supplied, not a bundled asset. Output includes `original.glb`, `morphed.glb` and `morph-receipt.json`. Use a new destination; overwriting is refused.

To construct a measured hull, open **Build measured 3D from two silhouette images**. Upload a front PNG mask and a side PNG mask, with white subject on black background, captured orthographically and aligned to the same physical dimensions. Use images no larger than 256 pixels per axis, supply width/height/depth in meters, choose detail 8–64 and create. Smooth mode rounds the voxel hull; voxel mode retains cell edges. This reconstructs the intersection of silhouette volumes. It does not infer hidden concavities, textures, likeness or perspective calibration from an arbitrary photograph.

Both paths save into the existing Studio workspace and appear in **Saved Creations**. Reopen checks original source, request, receipt and model hashes; it starts no new creation. Protected GLB downloads check the saved hash again. The saved asset preview shows actual static geometry and material colors: drag to orbit and scroll to zoom. Texture/animation rendering is not included in this preview. Larger than 100,000 triangles can be saved within native limits but are refused by this bounded browser preview.

The whole product also includes worlds, terrain, creatures, human animation, scene composition, materials, cameras, assets, exports and engine handoffs. These two workflows are additions to those paths. The [active all-path scorecard](full-build/SCORECARD.md) distinguishes exercised paths from work still open.

Use this guide to start the existing local creator, make a world or creature, use Blender-dependent workflows and understand the shared API/MCP connection. Commands below were checked against the current CLI source; this document itself is not a fresh execution receipt. See the [living handoff](HANDOFF.md) for actual source-specific test results and [Owner Handbook](FORGE-OWNER-HANDBOOK.md) for the completed-product target.

## Create a padded UV atlas for an untextured static model

For models with flat surfaces, add `--layout planar-pairs` to the CLI command below. Forge joins neighboring, consistently wound triangles on the same plane into pairs. Each pair shares UV coordinates along the common edge and occupies one padded atlas cell. The default layout gives each triangle its own cell. Compare `chart_count` and `atlas_coverage_fraction` in the receipts using the same resolution and padding.

Choose an original GLB in Studio's existing model upload control, open **Author UV coordinates for the uploaded static model** and select **Create Native UV Atlas**. This accepts an untextured model with no existing UV layout. Studio binds the selected bytes to their SHA-256 identity and uses the original saved-job journal: repeating the same source/settings reopens that revision; changed settings create separate work. The Studio upload limit is 900,000 bytes, with additional native geometry and saved-receipt budgets checked before allocation. The CLI supports larger original files inside the native limits:

```powershell
$sourceSha = (Get-FileHash -LiteralPath artifacts/owned-untextured.glb -Algorithm SHA256).Hash.ToLowerInvariant()
python -m forge.cli uv-atlas --source artifacts/owned-untextured.glb --expected-sha256 $sourceSha --atlas-size 2048 --padding 2 --out artifacts/owned-uv-revision-01
```

Output contains `original.glb`, `uv-mapped.glb`, `uv-receipt.json` and `diagnostic-checker.png`. The source stays intact, and an existing output directory refuses overwrite. Open `uv-mapped.glb` in Blender to edit the actual UV layer. The diagnostic checker is a QA image; assigning it in Blender can expose seams and coordinate problems. The saved Studio preview shows static geometry/material colors and does not establish checker-texture rendering.

The default layout gives each triangle its own padded island. It keeps the original triangle positions/order, material assignments, parts and hierarchy, while duplicating vertices and remapping active indices to create seams. This deliberately changes the active vertex/index representation; exact original bytes remain saved separately and as an unchanged prefix of the derived GLB's binary data. Normals and vertex colors follow their source vertices, and existing tangents are recalculated for the new UV coordinates.

Use atlas sizes 256, 512, 1024, 2048 or 4096 and padding from one to sixteen pixels. The native cap is 16,384 triangles, with additional checks that the resolution fits the padded cells and that float32 UV islands do not collapse. Existing UVs, textures, skinning, animation, blend shapes, compressed geometry and external dependencies refuse. The default layout has triangle seams. Planar pairing removes the shared UV seam within each pair. It does not paint texture art, bake materials, merge semantic charts, optimize texel density or establish artistic/engine acceptance. An [actual separate Blender import and checker render](../evidence/uv-authoring-2026-11-02/REPORT.md) verifies the tested original fixture.

## Transfer one original animation to a different rig

Use a source GLB with one original skeletal animation and a target GLB with a single skinned rig in its neutral bind pose and no earlier animation. Both must be owned or authorized for this use. Align the rigs' up and forward directions first. Make a `motion-map.json` naming the source and corresponding target bones. The bone names can differ; mapped parent relationships must agree.

```json
{
  "schema": "mgr.forge.motion-retarget-map.v1",
  "bone_map": { "source_root": "target_base", "source_arm": "target_tip" },
  "start_frame": 1,
  "end_frame": 16,
  "fps": 24,
  "root_motion": "in_place"
}
```

Use the actual bone names from your originals and a frame range present in the source clip at your chosen FPS. Then run the local CLI with both original identities and a new output folder:

```powershell
$sourceSha = (Get-FileHash -LiteralPath artifacts/source-rig.glb -Algorithm SHA256).Hash.ToLowerInvariant()
$targetSha = (Get-FileHash -LiteralPath artifacts/target-rig.glb -Algorithm SHA256).Hash.ToLowerInvariant()
python -m forge.cli retarget-motion --source artifacts/source-rig.glb --target artifacts/target-rig.glb --mapping artifacts/motion-map.json --source-sha256 $sourceSha --target-sha256 $targetSha --blender 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --out artifacts/target-motion-revision-01
```

Open `retargeted.blend` to edit the baked clip or `retargeted.glb` to use the new interchange model. The folder keeps `source-original.glb` and `target-original.glb` as exact copies and includes `retarget-receipt.json`, a separate `retarget-blender-proof.json` and before/after rendered images. A second Blender process must measure actual deformation after import before the native command returns success.

The current local path transfers explicit mapped rotations in place. It accepts 2–240 sampled frames at 12–60 FPS, bounded single-skin GLBs and bounded embedded PNG textures. It refuses existing target clips, shape keys, external/compressed assets, incompatible maps and unsupported translation/scale motion. It does not guess anatomy, transfer root travel, solve foot contacts or certify game-engine playback. See the [actual local retarget proof](../evidence/retarget-motion-2026-11-02/REPORT.md) for tested bounds and original fixture details.

## Start Forge Studio on this computer

Open PowerShell in the repository. Use new output names for each example run; many Forge commands deliberately refuse to overwrite existing results.

```powershell
Set-Location 'C:\Users\cool\Documents\Codex\Projects\MGR-3D-FORGE'
python -m forge.cli --help
python -m forge.cli build --spec examples/neighborhood.json --out artifacts/owner-world-01
python -m forge.cli inspect artifacts/owner-world-01/world.glb
python -m forge.cli verify-bundle artifacts/owner-world-01
python -m forge.cli serve-studio --world artifacts/owner-world-01 --workspace artifacts/owner-studio-01 --port 0
```

Keep that terminal running. Open the exact private launch link printed by Studio. It uses a temporary fragment credential; the page removes the fragment and uses a private header for subsequent requests. Do not share or save that link in Git. A bare localhost URL shows the unlock shell. After restarting the server, use its new launch link. The same dedicated workspace is how you retain that workstation's existing jobs; a new workspace starts a separate set of local records.

Blender is optional for the basic CPU world and creature steps. To enable workflows that actually launch Blender, add its installed executable to the Studio command:

```powershell
python -m forge.cli serve-studio --world artifacts/owner-world-01 --workspace artifacts/owner-studio-01 --port 0 --blender 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
```

Use the actual installed path on another machine. The local server binds to this computer's loopback interface; it does not publish Forge to the internet.

## Edit and save a world

Use **WORLD EDITOR** to select a building and change its position, dimensions or material. **Undo**, **Redo**, **Duplicate** and **Delete** edit the current browser scene. **Download World** saves the edit JSON; **Load a saved world (.json)** loads that edit document. This saved JSON is separate from the generated GLB geometry.

Open **Creation Chat**, then use **Create / Change** for supported building instructions such as `create a gold building height 15`. This is a bounded native command parser. Use **Build Edited World** to materialize geometry, then use the resulting private download controls. **Open in Blender Project** runs a background conversion when Blender is configured; **Download Game Engine Project** packages the supported Godot project. Check the displayed result/error before treating the action as complete.

For a separate offline world viewer:

```powershell
python -m forge.cli world-flight --world artifacts/owner-world-01 --out artifacts/owner-world-flight-01.html
```

The offline viewer can navigate/edit its embedded scene. Native creation buttons require the authenticated running Studio. Keyboard navigation is W/S forward/back, A/D strafe, E/Q vertical, arrows turn, drag to look and Shift for faster movement.

## Create an original procedural creature

In Creation Chat, scroll to **MGR CREATURE FORGE**. Enter a prompt of 8–500 characters, choose the design seed and 1–12 variants, optionally adjust **Advanced MorphRig — shape changes**, then choose **Create Original 3D Creature**. The seed makes a design reproducible; changing a prompt or morph is a new creative request. **Check Last Creature** checks the remembered request. Use the result's authenticated download control for the GLB.

The CLI offers the same native creation method:

```powershell
python -m forge.cli imagine-creature --prompt 'Invent a horned winged forest animal with a long tail' --seed 21 --variants 4 --out artifacts/owner-creature-01
python -m forge.cli inspect artifacts/owner-creature-01/creature.glb
```

The current bounded anatomy parser respects explicit supported counts and exclusions such as `four legged`, `eight eyes`, `wingless` and `tailless` across variants. It rejects contradictory/unsupported explicit anatomy instead of silently substituting a different design. This remains a bounded native parser; inspect the resulting manifest and mesh against your brief.

Keep `creature.json` with the GLB: it records DNA, variants, artifact identity and limitations. This is original stylized CPU geometry. Explicit anatomy now supports exclusions such as `wingless`, `without wings or horns`, `tailless` and `unarmored`, plus supported counts: 0/2/4/8 legs, 0–8 eyes, 0–6 horns and zero/two wings. For example, `a four-legged creature with eight eyes and two horns, without wings` keeps those constraints across all variants. Unsupported or conflicting explicit anatomy returns an error before a native job is allocated. This is bounded English syntax; arbitrary creative prose is still richer than the generator's understanding.

Newly generated limbs use authored knees shared with their rig, tapered radial appendages and smoothed organic normals. The result remains separate overlapping components rather than a seamless anatomical surface. Old saved outputs retain their original bytes; the new construction method applies to new jobs. To run the existing prototype rig/skin/independent Blender reimport workflow:

```powershell
python -m forge.cli rig-creature --source artifacts/owner-creature-01 --out artifacts/owner-creature-rig-01 --blender 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
```

Inspect the rigged GLB, editable Blender project and proof files. Successful execution is technical evidence for that result; professional anatomy, natural motion and owner art approval remain separate. See [Morph, rig and lip-sync details](HOW-TO-MORPH-RIG-LIPSYNC.md).

The [November 2 surface/rig witness](../evidence/native-creature-quality-2026-11-02/REPORT.md) records actual fixed-camera before/after Blender renders, smooth organic surfaces, tapered radial appendages, common mesh/rig limb joints and separate receiving-process rig proofs. Explicit tailless/wingless creatures use existing leg or head bones for the bounded deformation preview. The creature remains a procedural prototype with separate overlapping body components.

## Add terrain and compose a Blender world

In Studio choose a biome under **MGR WORLD BIOME FORGE**, set seed/detail, then **Generate 3D Terrain Layer**. The terrain is a separate source-pinned layer around the original world. **Combine Original City + Terrain (Blender)** creates a combined editable project from the original city and generated layer. Unsaved or separately materialized building edits do not automatically become that original source.

Equivalent CLI workflow:

```powershell
python -m forge.cli world-biome --world artifacts/owner-world-01 --biome forest --seed 42 --resolution 28 --out artifacts/owner-biome-01
python -m forge.cli world-compose --world artifacts/owner-world-01 --biome artifacts/owner-biome-01 --out artifacts/owner-composed-01 --blender 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
```

Biome choices are forest, desert, tundra, volcanic and alien. The composition command creates combined GLB/editable Blender output and the supported static Godot handoff by default. Actual target-engine import/play and visual approval require their own checks.

## Animate the generic human face

Studio's **Animate Generic Human Face** runs its supplied-timing demo. **Make Human Mouth React to My Audio** accepts a caller-owned PCM16 WAV up to the browser's 900 KB bound. This drives jaw motion from loudness; noise or music can also move it. It does not recognize speech sounds or clone a voice.

For an existing authorized WAV through the CLI:

```powershell
python -m forge.cli human-audio-motion --wav 'C:\path\to\approved-voice.wav' --actor-id owner-generic-human --fps 24 --out artifacts/owner-audio-human-01 --blender 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
```

Replace the placeholder WAV path. The CLI accepts bounded uncompressed PCM16 RIFF/WAVE, mono/stereo, 8–48 kHz, 100 ms–120 seconds, at most 20 MB; the browser has the smaller bound above. Keep private audio outside public Git.

For caller-supplied phonemes, save a JSON file such as `artifacts/owner-phonemes-01.json` with this exact structure:

```json
{
  "schema": "mgr.forge.phoneme-timeline.v1",
  "actor_id": "owner-generic-human",
  "language": "en-US",
  "duration_ms": 1000,
  "phonemes": [
    {"phoneme": "M", "start_ms": 100, "end_ms": 250},
    {"phoneme": "AA", "start_ms": 250, "end_ms": 700}
  ]
}
```

Then run:

```powershell
python -m forge.cli human-lipsync --timings artifacts/owner-phonemes-01.json --fps 24 --out artifacts/owner-timed-human-01 --blender 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
```

Events must be ordered, nonoverlapping and within duration. Source `forge/lipsync.py` defines the supported uppercase phoneme vocabulary. Caller timing is input evidence; this command does not calculate alignment from speech. The actor label identifies this generic job and does not establish a person's likeness or consent.

## Preserve an existing model and find assets

Use **Inspect / Preserve 3D Model** in Studio for a small GLB; its browser upload limit is 900 KB. Preservation/inspection does not automatically rig, approve rights or place the model in a world. For an owned GLB via CLI:

```powershell
python -m forge.cli character-intake --source 'C:\path\to\owned-character.glb' --out artifacts/owner-intake-01
python -m forge.cli character-readiness --source artifacts/owner-intake-01/candidate.glb --out artifacts/owner-readiness-01.json
python -m forge.cli asset-sources --category fantasy-creatures
```

Replace the source path. Source Atlas offers directory discovery and explicit live metadata searches. Search results are leads; downloaded files stay quarantined until exact rights and quality acceptance. See [Source Vault and REA](HOW-TO-SOURCE-VAULT-REA.md) before acquiring a pack or redistributing source assets. Never interpret the research candidate count as installed models.

## Use Tevin and the shared MGR API/MCP

There is already one shared repository at `C:\Users\cool\Documents\Codex\Projects\MGR-API-MCP`. Its original Forge client/tool files connect to this Forge-owned runtime. Its current typed tools cover discovery; world, creature, biome, human and composed-world creation/status; artifact reading; and exact original-request verification. The shared edge enforces actor/tenant/audience and read/execute scopes. Discovery grants no execution authority.

Connected clients can now call `mgr_forge_saved_jobs` with `{"kind":"all","limit":20}` and pass its returned cursor for another page. Listing reports journal observations without accepting files. Call `mgr_forge_saved_job_reopen` with `{"kind":"creature","requestId":"the-original-request-id"}` to reopen the existing native result and independently validate its bounded GLB. Both use the existing `tools:read` scope and enrolled principal; neither creates a job or grants an approval. Actual protocol qualification currently covers world, creature and biome. The shared reader's 800 KB limit still applies; larger native files need the remaining delivery engineering.

The current owner-service handoff records Tevin's normal launcher enrolling the private Forge worker and five native creation operations. Use the normal Tevin desktop launcher configured by MGR-ONE, then propose a bounded Forge action and use the existing owner approval controls. Preserve the original request, returned native job/result and saved artifact. A locked owner session needs its normal sign-in/launch flow; do not bypass it with copied credentials or a guessed URL. The exact owner runtime contract lives in MGR-ONE's `docs/runtime/TEVIN-FORGE-OWNER-WORKER.md`.

For engineering verification, consult [Connect, verify and recover](HOW-TO-INTEGRATION-VERIFY-RECOVER.md) and the API repository's current handoff. Its `scripts/verify-forge-studio.py` and `scripts/verify-forge-creator-mcp.py` are controlled local integration harnesses; their fixture identities do not prove deployed OAuth/mobile acceptance. A skills-only ChatGPT plugin does not by itself host or execute Forge remotely.

## Find and reopen saved creations

In Creation Chat, open **Saved Creations** and choose **Find Saved Creations**. Filter by all five native kinds or one kind: world, creature, biome, human or composed world. **Next Page** moves through 20 records at a time. Ordering is deterministic by kind/request ID; it is not a newest-first timeline.

The list reads the same native request journals used by creation. A stored state is explicitly unverified until you choose **Reopen**. Reopen calls that kind's original status reader and verifies its current GLB before returning downloads. The normal private download helper checks the SHA again when saving the bytes. This reads existing work; it does not create, retry, delete or approve a job. Studio's **Build Edited World** now uses the existing durable world route too: identical source/edits have a stable content-derived request ID, so another click reconciles/replays the same result and saved-world history can find it.

Interrupted STARTED records and orphaned RUNNING records require reconciliation. A damaged kind's journal is reported while valid kinds remain available. History does not expose raw prompts, audio or local filesystem paths. Older relief/upload jobs and historical results made through the legacy nonstable world-edit route are outside this five-kind list. The read-only native routes are `/api/saved-jobs` and `/api/saved-job-reopen`. The shared MCP history extension has its own qualification in the living handoff; native endpoints alone do not establish a connected client. Current test/runtime acceptance belongs in that same handoff.

## Recover without creating duplicates

| What you see | What to do |
|---|---|
| Unlock screen or 403 | Open the current Studio launch link in the same local session. After server restart, use its new link. Do not remove authentication checks. |
| Invalid-input error | Correct the input bounds/schema before creating another request. Preserve previous request IDs and files. |
| Same ID with changed input | Treat the changed creative action as a new request/revision. Never mutate a saved request's identity to force replay. |
| RUNNING | Check the same request's status. A browser timeout does not prove the worker stopped. |
| NEEDS_RECONCILIATION, missing result or lost reply | Preserve the workspace and original input. Verify the original native request/result before another effect; do not blindly regenerate. |
| Hash mismatch, missing file or corrupted GLB | Preserve the evidence and treat the result as invalid until reconciled. Do not overwrite it or declare success from job JSON alone. |
| Blender failure | Confirm the actual executable path/version and inspect the saved error/proof. Use a fresh output path for a genuinely new attempt after its original outcome is known. |
| Reopened server has no old jobs | Confirm that `--workspace` is the same dedicated directory and that its original journals/artifacts were preserved. A new directory does not import previous history automatically. |

Keep the source world, workspace, edit JSON and generated project together in your own backup plan. Existing local persistence is distinct from a tested off-device restore. Private tokens, references/audio and purchased/raw assets do not belong in the public source repository.

## Check a changed installation

From the Forge repository, the standard checks are:

```powershell
python -m unittest discover -v
node --check viewer/runtime.js
```

Run the actual owner journey and receiving application needed for the change as well. Preserve exact results and limits in the current handoff/feature register. A Python test pass alone does not certify visual quality, Blender/Godot import, live providers or production delivery.
