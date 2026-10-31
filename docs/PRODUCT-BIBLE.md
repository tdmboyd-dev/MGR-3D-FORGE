# MGR 3D FORGE — Product Bible

Status: TARGET SPECIFICATION WITH VERIFIED PARTIAL PROTOTYPES, not a production release.
Updated 2026-10-30. Code state and acceptance live in `docs/BUILD-REGISTER.md`;
the single live progress handoff is `docs/HANDOFF.md`.

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

## The full MGR Forge creation universe — approved direction

The first six owner-selected Forge ideas are **not the limit**. The systems
below are MGR-native destinations, with existing tested pieces reused wherever
possible. An item in this map is a planned product lane, **not** a build claim.

| MGR-owned system | What Time asks Forge to do | What exists / first honest next result |
|---|---|---|
| **MGR Forge Vault / Source Atlas** | Find free/approved kits, faces, animals, materials and source models, with exact rights and search | F05/F118/F119: hash vault, two live search providers, one real quarantined dragon; next per-file rights review and production search index |
| **MGR Human Forge** | Build varied faces, body types, realistic skin tones/textures, hair, clothes, anatomy and character DNA | F09–F12/F99–F116: generic geometry, reference intake/segmentation and part tools; next generator/morph library + real face/skin/hair/rig QA |
| **MGR Creature Forge** | Create ordinary and fantasy animals, hybrids, anatomy variants, skin/fur/feathers/scales, creature rigs | Source directory exists; species anatomy, modular creature base meshes, rig/retarget and deformation acceptance remain open |
| **MGR Creation Forge** | Turn plain-English concepts, image references and approved kits into editable objects and scenes | F87–F97: world edit/chat/GLB/Blender flow works locally; next reusable component placement and multi-object scene graph |
| **MGR World Forge** | Author villages, cities, biomes, terrain, interiors, dungeons, sky, weather and portals at different scales | CPU buildings, basic parks/rooms, world flight and Godot handoff exist; high-detail worlds, terrain and navigation remain open |
| **MGR AI Shape Lab** | From text, 1–4 views or existing models, construct/smooth/retopo/UV new editable forms | F95/F106–F113: relief, mask extraction, visual hull, surface nets; no licensed photoreal neural model execution proven |
| **MGR Material & Skin Lab** | Build realistic skin undertones, PBR fabric/leather, fur, stone, metals, scars, makeup and weathering | PBR contract and Source Atlas material search exist; next actual UV texture download/use/visual shader tests |
| **MGR Motion & Performance Forge** | Rig/animate humans and beasts, retarget motions, lip-sync and hundreds of moves | Generic mannequin and constrained Blender rig proof; production rig, 200+ accepted moves and voice/lip proof remain open |
| **MGR Kit / Prop Forge** | Snap modular buildings, furniture, vehicles, weapons, wearables and props into reusable kits | Procedural pieces and Source Atlas candidates exist; connector sockets, dimensions, dependencies and source-license admission next |
| **MGR Reality & Scan Forge** | Turn allowed video, photogrammetry, lidar and object scans into measured editable geometry | Depth/camera math and silhouette methods exist; capture calibration and full scan-to-mesh acceptance open |
| **MGR FX & Cinematic Forge** | Make lighting, atmospheres, magic, fantasy worlds, camera moves and rendered sequences | CPU FX, lights and Windows Blender witnesses exist; production simulation and live cinematic interaction open |
| **MGR Export / Runtime Forge** | Deliver reusable GLB/OBJ/.blend/Godot and later Unreal, Unity, USD, VR and AR projects | GLB/Blender and Godot headless proof exist; independent multi-engine/visual/mobile acceptance open |
| **MGR Tevin Command Bridge** | Let Tevin search Forge, request bounded creation, inspect proofs, save/reopen assets | F120 read-only catalog through existing API/MCP edge works locally; creation dispatch remains Creation OS-owned, hosted Tevin session unverified |
| **MGR Verification / Recovery Lab** | Detect broken models, wrong faces, bad licensing, missing parts, visual defects, repeated jobs and spend overruns | Existing QA, durable queue, hashes and new quarantine; end-to-end rights/visual/device acceptance remains open |

**How finished 3D creation works:** source kits + parametric templates + modeling
operations + learned models are different parts of the stack. A model builder
may reuse a known mesh, deform a human base to match face/body controls, grow
procedural geometry, reconstruct viewed shapes, or synthesize a new mesh. Forge
must identify which method produced each surface and keep invented hidden
geometry separate from measured reference data. A catalog alone is not the
creator; source selection, assembly, rigging, textures and independent visual
validation make it a usable 3D result.

### Delivery order (parallel lanes, shared acceptance contracts)

1. **Inventory + rights:** discover selected assets/kits, cite exact source and
   license, hash small samples, preserve private/purchased sources outside Git.
2. **Source-to-scene:** inspect, normalize orientation/scale/topology, build a
   recoverable prefab and place it into an actual world/character part, then
   reopen in Blender/Godot with a provenance receipt.
3. **Humans/creatures:** integrate an approved human generator and legal base
   shape packs, then species templates, face/skin/fur/wardrobe, anatomy and rig.
4. **AI creation:** install optional approved model+weights behind Model Dock,
   benchmark output and cost, maintain a procedural/asset-reuse fallback.
5. **MCP + Tevin:** the shared MGR-API-MCP edge performs verified auth and
   read access; Creation OS routes creation-domain effects into Forge-owned
   jobs. Tevin consumes receipts/previews, with no duplicate policy engine.
6. **Runtime acceptance:** real browser, Blender, Godot and future engine
   interoperability with source SHA, scene preview, rights and recovery proof.

Run these lanes together when independent, but do not promote any feature past
its acceptance gate merely because another lane's tests passed.

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
