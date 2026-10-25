# MGR 3D FORGE — Product Bible

Status: SPECIFIED / NOT IMPLEMENTED. Updated 2026-10-25.

## What it is

MGR 3D Forge is a native creation platform, not a chatbot and not a rebadged Tripo/Hyper3D client. A plain-English creative director compiles an idea or reference into **structured, persistent, editable 3D**. Forge owns planning, character identity, scene rules, asset provenance, cost routing, QA and export. Model weights or outside APIs are interchangeable workers.

## Intended consumers

- **Tevin Rain / MGR-ONE:** adult Black character identity, accurate hands/proportions, separable outfit components, rig, animation, environments.
- **Creation OS:** parent creative orchestration when verified against actual source tree.
- **Create Loco:** screenshot/concept-to-3D experiences when appropriate, via shared contracts.
- **iKickItz:** reusable environments, avatars, rooms and world assets.
- **MGR Blender Expert:** Blender execution, scene assembly, validation and export.
- **MGR Agents / RAE:** authorized research, evidence, audits; not a duplicate inference server.

## Inputs

Text description; reference image(s); multi-angle turnaround; existing GLB/FBX/OBJ/USD asset; video/stills for authorized reconstruction; scene layout; asset and character identifier; constraints for polygon count, rig standard, scale, performance, rights, budget, deadline, target engine.

## Outputs

- Editable meshes and/or scene graph, materials/UVs, named separable components.
- Rigged characters and animation clips only when validated.
- World layout, terrain, roads, buildings, region and room hierarchy.
- `.blend` working source, GLB/glTF delivery, optional FBX/USD based on need.
- Proof package: preview renders, geometry report, skeleton/part report, source/license provenance, estimated and actual cost, tool/model versions, acceptance status.
- Generated 3DGS/point cloud optionally for visualization; do not claim these are automatically collision-ready game meshes.

## MGR Native features (proposed)

| ID | Capability | In plain English | Acceptance criterion |
|---|---|---|---|
| N01 | Creation Director | Turns a vague prompt into scene, character, asset and validation tasks | Reproducible typed plan and dependency graph |
| N02 | Method/Compute Router | Picks existing asset, procedural CPU, local model or optional rented compute | Logged decision, estimate and caps |
| N03 | Character DNA Vault | Locks face/body identity and reference provenance | Geometry/landmark deviations within approved tolerances |
| N04 | Outfit Anatomy | Clothing, hair, jewelry and footwear as editable/replaceable parts | Correct named components with clean visibility and attachments |
| N05 | Anatomical Guardian | Spots missing hands/fingers, wrong limb length and malformed pose | Passes scripted landmarks, mesh and pose suite |
| N06 | Rig & Motion Factory | Skeleton, weights, pose test and exportable motion | Rest/idle/walk and deformation tests pass |
| N07 | Infinite World Architect | Plans persistent connected terrain, regions, streets, structures | Reopened scene preserves locations/scale and connectivity |
| N08 | Procedural Construction Kit | CPU-generated buildings, roads, rooms, vegetation, terrain | Deterministic seed, editable geometry and bounded performance |
| N09 | Reality-to-World | Photos/video into spatial scene evidence | Registered cameras, exported geometry and measured drift |
| N10 | Asset Surgeon | Segments and reconstructs individual parts | Independent watertight/usable parts where required |
| N11 | Universal Asset Memory | Reuses owned meshes with license/provenance metadata | Deduplication and similarity retrieval verified |
| N12 | Self-Healing Geometry | Diagnose and repair mesh/UV/normal/scale/export defects | Before/after evidence; never silently erase details |
| N13 | Continuity Locks | World facts, dimensions, style and canon persist | Invariants survive regeneration, editing and reload |
| N14 | Blender Scene Compiler | Generates verified Blender operations/scenes | Exact runtime version QA, export/reimport |
| N15 | Quality & Cost Judge | Scores usable assets vs money/time | Benchmark report with approved asset denominator |
| N16 | Provider Independence | Replace model or API without rewriting products | Two dissimilar adapters pass same contract suite |
| N17 | Human Approval Gateway | Preserve high-risk actions behind explicit approvals | No hidden spending, deletion, license violation or public uploads |
| N18 | Local-First Execution | Supports no discrete GPU when task allows | CPU-only procedural project verified |
| N19 | World Streaming & LOD | Work on only nearby regions and detail levels | Repeatable performance and culling benchmarks |
| N20 | Project Export Packs | Deliver consumer-specific material, mesh and metadata | Engine import with correct scale, animation, PBR |

## Proposed creative workflows

### Tevin
1. Load owner-approved base model and references. Record identity landmarks.
2. Verify head/body and symmetric hands; preserve base as immutable source.
3. Generate and fit coat, shirt, pants, boots, chains, rings, hair as separate named meshes.
4. Bind accessories to defined sockets and garment to appropriate deformation rig.
5. Generate T- and A-pose, 360° views, idle/walk/gesture test; flag missing parts.
6. Reimport exported GLB/FBX; compare proportions and skeleton.
7. Owner approval before marking character canonical.

### World
1. Prompt becomes bounded spatial spec: theme, regions, landmarks, terrain, roads and scale.
2. Create deterministic CPU terrain/road/building shells.
3. Search reusable asset library; synthesize only missing artistic assets.
4. Place semantics-aware objects, collision/navigation scaffolds, lighting, LOD.
5. Render previews, validate traversability, export scene and reopen.
6. Persist the map/seed/asset IDs so the world can grow without forgetting.

### Reconstruction
Use only authorized photos/video; estimate cameras/depth/scene; convert into editable source components where feasible. Measured reconstruction is not proof that unseen geometry is true.

## What it is NOT (yet)

- Not a trained proprietary frontier foundation model.
- Not guaranteed superior to any commercial model in photorealism.
- Not GPU-free for all neural inference.
- Not a game engine or physics runtime replacement.
- Not a production character/whole-world generator until tests and actual artifacts pass.
- Not authorized to copy proprietary weights, private endpoints or artwork.

## Competitive advantage hypotheses

Potential 10x gains are **hypotheses** in (a) cost per accepted asset by procedural reuse, (b) setup speed for large structured worlds, (c) reduction in revisions through continuity locks, (d) percentage of assets reusable across MGR products. Each needs a baseline, 30+ comparable trials, quality gate and cost accounting. Visual fidelity superiority requires a separate blinded human review and objective geometry tests.
