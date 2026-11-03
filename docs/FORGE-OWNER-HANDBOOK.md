# MGR 3D Forge — Owner Handbook

This is the destination for the product: what Forge should let Time create, what a finished result must contain, and how its connections fit together. For today's measured state and the next engineering action, use the single [living handoff](HANDOFF.md), [build register](BUILD-REGISTER.md) and [full-build scorecard](full-build/SCORECARD.md). For instructions, use [How to use Forge](FORGE-HOW-TO.md). This handbook does not replace those records.

## What Forge should become

Forge should turn a creative brief, authorized references or an existing asset into an editable 3D project that the owner can inspect, revise, animate, export and reopen. Its strength should come from continuity and control: consistent characters, separate outfit parts, coherent worlds, recoverable work, clear rights and measured quality. A strong preview must lead to usable geometry and working source files.

Native procedural geometry, existing licensed assets, local models and optional external providers are different production methods. Forge should choose a suitable method, record the choice and preserve a portable project. No outside model, hosted account or expensive GPU should become mandatory for work the native CPU system already handles.

The [native canon](MGR-NATIVE-CANON.md) preserves the approved identity and execution boundaries. The [product bible](PRODUCT-BIBLE.md) and [master program](MASTER-FORGE-PROGRAM-2026-10-31.md) retain the larger vision. Older roadmap statements about missing components must be checked against current source and the handoff.

## What completion means to the owner

| Product lane | Finished owner experience | Acceptance required |
|---|---|---|
| Creation Director | Describe a bounded object or scene, review a plan, create it, then revise individual parts without losing prior versions | Real dispatch, input validation, visible errors, saved outputs and a repeatable revision/reopen journey |
| Human Forge | Create varied human forms with approved face/body continuity, skin, hair and replaceable clothing/accessories | Anatomy and topology checks, approved reference comparison, separate named parts, skin/rig deformation and owner visual acceptance |
| Creature Forge | Design recognizable or invented anatomy, adjust proportions, rig it and produce believable species-appropriate motion | Stable mesh/joint transforms, skin weights, animated pose tests, independent import and art acceptance for the chosen anatomy |
| World Forge | Build and extend persistent cities, interiors, terrain and biomes while preserving scale and placement | Reopened scene identity, collision/navigation appropriate to the target, editable components and actual target-engine play/visual checks |
| Material, FX and Cinematic Forge | Author materials, lighting, atmosphere, effects, shots and timelines as reusable scene data | Actual shader/render/timeline evidence, acceptable appearance and target-runtime behavior where required |
| Shape, Scan and Repair | Use authorized references or imported models to produce editable geometry and repair real defects | Source provenance, measured versus invented geometry labels, before/after checks and reversible edits |
| Motion and Performance | Animate bodies and faces with timing and emotional direction while preserving character identity | Source motion/audio rights, alignment evidence, deformation checks, animated export/reimport and owner performance review |
| Source Atlas and Forge Vault | Find, admit, reuse and restore assets with their source, rights, revisions and receipts | Exact file/version/license scope, hashes, independent import, correct permissions and a tested restoration path |
| Connected creation | Use the same Forge jobs from Studio, Tevin and approved connected apps | Correct actor/tenant/audience/scopes, approval binding, exact request/result identity, secure artifact delivery and restart/reconciliation proof |
| Export and Runtime | Deliver editable source plus the formats needed by the receiving application | Correct units, parts, materials, animation and metadata in an independent application; engine-specific proof remains specific to that engine |

These are acceptance targets, not claims that every lane is delivered. Whole-product completion remains unassessed until the applicable journeys and their acceptance checks are defined and passed. Source counts and unit-test totals are evidence within a scope; they are not a product percentage.

## The connections and who owns what

```text
Forge Studio --------------------> Forge workstation / jobs / artifacts
Tevin / MGR-ONE -> MGR-API-MCP ---> the same Forge workstation / jobs / artifacts
Authorized connected clients ---> MGR-API-MCP -> the same Forge execution
Optional Creation OS -----------> shared contracts when several factories cooperate
```

Forge owns 3D creation, native validation, durable native request records, generated artifacts and their quality receipts. MGR-API-MCP is the existing shared connection edge: authentication, tenancy, audience and scoped tool access. MGR-ONE owns its reasoning, owner/delegated approvals and saved conversation/workflow results. Creation OS coordinates multiple creation factories when useful. It is optional for a direct Forge action.

Blender is an execution and independent receiving application for editable scenes, skinning, animation and renders. Godot is a receiving game-engine target; a generated project is distinct from a successful import/play/visual acceptance. Create Loco, iKickItz and other MGR applications are intended consumers described in the product bible; their mention alone is not a current integration receipt. REA and the optional MGR X-Ray workflow inspect selected authorized artifacts and preserve evidence. They do not become a second generator, approval authority or asset store.

The current owner-service handoff records a normal-launcher Tevin journey for five native operations: world edits, procedural creature/morph, biome, supplied-phoneme human animation and Blender world composition. That existing route should be extended. The skills-only ChatGPT Forge Creator plugin helps specify and route work; its existence does not establish a deployed mobile generation service. A genuinely hosted route still needs its own authenticated worker, private storage, remote artifact delivery and receiving-client acceptance.

## What every accepted result should retain

For each selected journey, keep the original brief and typed input, stable request ID, native job ID, source revision/content identities, artifact SHA-256 and byte length, production method, rights/provenance state and the exact checks performed. Keep editable project files and revisions when that journey promises them. Record the receiving application/version and actual render/import result separately from native structural validation.

A revised creative request is a new revision with lineage. A lost response to the same action must first be reconciled with the original input and saved native result. A running, failed, unknown or reconciliation-required state cannot be presented as finished. Cancelling a UI request does not prove that an already dispatched Blender or remote job stopped.

The final acceptance should explicitly answer: can the owner reopen the result, make the intended edit, export it, use it in the target and recover after an interruption without duplicated effects or lost source? Visual quality and character canon remain owner decisions even when technical checks pass.

## Current proof boundary

The November 1 handoff records native CPU creation, real Chrome/Blender desktop flows, shared API/MCP input/result verification and a permanent owner-service save/restart/recovery journey. The [November 2 native creature quality witness](../evidence/native-creature-quality-2026-11-02/REPORT.md) adds actual fixed-camera same-anatomy Blender renders and independent winged/tailless rig imports after tapered-surface and shared-joint improvements. These are dated, source-specific records, with owner art and production acceptance explicitly open.

Still distinct are premium neural generation, arbitrary topology/rigging, professional anatomy/materials/hair, automatic speech-phoneme alignment, large-asset delivery, cross-session custody, postdispatch cancellation, full remote ChatGPT/mobile delivery, off-device restore and whole-product production acceptance. The current handoff governs which of these has subsequently changed. Native WAV jaw motion responds to loudness; supplied phoneme animation consumes timing provided by the caller. Neither establishes an automatic speech aligner.

Forge should stay portable and recoverable: preserve source projects and domain ownership, use existing stores/contracts, keep optional providers replaceable and record actual costs when a provider is authorized. The current native no-spend workflows do not prove that electricity, maintenance, cloud generation or future production operation are free.

## Keep the handbook useful

When a capability changes, update its existing feature entry and the living handoff with source, acceptance and limits. Update this handbook when the approved product destination or ownership changes, and the how-to when the owner-facing workflow changes. Keep historical receipts dated. Do not create another competing status database or declare a target complete because its documentation exists.
