# MGR 3D Forge — Native Architecture

**Status: proposed, no production code.** Never infer deployed capability from this document.

## Ownership

MGR-3D-FORGE owns the specialized 3D creation capability and contracts. It should expose callable interfaces to Creation OS, Create Loco, MGR-ONE/Tevin and MGR Agents after checking actual repos; do not duplicate their router, memory, approval gateway or workflow engine. Blender is the model/scene editing and validation environment, not the orchestration brain.

## Pipeline

```
User intent/reference + rights + constraints
 -> normalize brief and identity/world continuity locks
 -> scene/asset DAG (typed plan)
 -> asset memory lookup and deterministic CPU generation
 -> gap router: optional local open model / rented GPU / provider
 -> mesh/parts/material/rig/scene assembly
 -> geometry & visual QA + repair loop
 -> export/import verification, artifact manifest, cost receipt
 -> owner approval and versioned asset library
```

All stages must be restartable with immutable input IDs, idempotency keys and stage outcomes. No irreversible overwrites of approved canonical assets.

## Core domain objects

- `Project`: id, owner, canonical target, budget, privacy, target engine, approved requirements.
- `CreativeBrief`: prompt, reference IDs and consent, style, measures, limits, negative constraints.
- `CharacterDNA`: immutable base asset hash, landmark geometry, morphology constraints, skeleton profile, sockets, materials, approval revision.
- `WorldSpec`: coordinate system, seed, region graph, terrain, structure classes, landmarks, scene constraints, canonical locations.
- `AssetSpec`: type, size, geometry/UV/texture/rig targets, relationships, source/license, accept tests.
- `GenerationPlan`: DAG, method choices, cost estimates, compute target, fallbacks, approvals.
- `AssetRevision`: lineage, tool/model hashes, files, transform/mesh stats, source/rights, status.
- `QualityReceipt`: structured test results, reference/preview artifacts, human review, failures and repair history.
- `ComputeReceipt`: CPU/GPU minutes, peak memory, cloud/API billing, overhead, retry accounting.
- `PublicationManifest`: assets, target app, hash, license, export compatibility, status.

## Interfaces (contracts before implementations)

- `plan(brief, constraints) -> GenerationPlan`
- `asset.search(spec) -> candidates[]`
- `geometry.generate(spec, seed) -> AssetRevision`
- `model.generate(reference, spec, limits) -> AssetRevision` (adapter)
- `character.validate(dna, asset) -> QualityReceipt`
- `world.compose(worldSpec, assets) -> SceneRevision`
- `blender.execute(job, runtimeVersion) -> ExecutionReceipt`
- `quality.inspect/repair(asset) -> QualityReceipt`
- `export.build(scene, format, target) -> PublicationManifest`

## Compute policy

First reusable asset, then procedural CPU, then lightweight local inference if available, then explicitly approved rented GPU/paid API. Stronger models are only selected when measurable quality requirements justify cost. Estimate before dispatch and enforce ceiling, retry limit and cancellation semantics. MCP is a tool transport, not a free inference engine.

## Model/adapters

Candidate families: TripoSR, TripoSG, TRELLIS.2, optional Stable Fast 3D, Hunyuan3D 2.1, Hunyuan3D-Part, HY-World 2.0; each must have separate license and hardware gates. Research/paper-only methods cannot be marked installed. Avoid vendoring weights into Git.

## Procedural CPU stack

Deterministic seed; region/zoning graph; heightfield/noise terrain; road spline/grid + intersections; parametric building grammar; room layout; vegetation scattering with instances; collision proxies; navigation-ready metadata; scene streaming/chunking. Use Blender Geometry Nodes and Python where version-appropriate. Render quality and runtime speed are distinct from ability to construct geometry on CPU.

## Security and durability

- Public repository contains code/research only; no private reference imagery, API keys, authentication data or copyrighted vendor assets.
- Explicit authorization for uploading any image to cloud providers.
- Sandbox/limit model processing of untrusted 3D files (potential malicious embedded scripting in blend files/add-ons).
- SHA/digest provenance, original source, model license and human-approved acceptance.
- Keep jobs resumable; no fake queued/completed states. Expose actual worker status.
- Budget and publication approvals must be enforceable at server boundary.
- Test on a copy of important production assets and permit rollback.

## Integration gates

Before integrating, inspect owner repositories for AGENTS.md, architecture, routes, existing queues/router, asset store, auth, approval gateway, user data contracts, tests and current branch. Add a single common interface rather than cloning their infrastructure. GitHub Action runs should be deliberate and minimal.
