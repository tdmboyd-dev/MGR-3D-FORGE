# MGR 3D FORGE — Current Native Inventory

**Updated 2026-10-25. Owner: Money Grind Religion Corp. Canon: `docs/MGR-NATIVE-CANON.md`.** This is a current status document, not the historical creation baseline.

**FIRST LIVE WEBGL WORLD:** Windows Google Chrome actually rendered the standalone `demos/mgr-world-flight.html` on ANGLE software WebGL2. Screenshot `evidence/browser/windows-wave13-world-flight.png` visually confirms 10 generated buildings, roads and world perspective; independent machine receipt in matching JSON. **216/216 Python tests PASS on both Windows and Linux.** The world is visually blocky, and keyboard controls/sustained FPS have not yet been independently automated. This is the first user-openable runtime slice, not the completed photoreal Forge engine.

**CURRENT verified scope:** **212/212 tests PASS on both Linux and Time's Windows PC**, covering F82 layered scenes, F83 GLB/OBJ geometry parity, F84 local integrity-checked disk-cell residency, and F85 continuous actor-vs-box swept contact. These are bounded CPU prototypes, **not** a production live 3D/game engine. Real Blender 5.2.2 CPU Cycles studio fixture created a `.blend`, render PNG and JSON receipt (`evidence/blender/windows-wave12-studio-witness.json`). New F83–F85 functions passed Windows regression but still need independent game-engine import/render/playback. Full new engineering contracts are `research/MGR-RUNTIME-FOUNDATIONS-WAVE.md`.

**New foundation wave:** five sourced 16-field packets (S01–S05) and CPU tests for parallel-camera depth triangulation, triangle-edge surface defects, and sampled motion speed/acceleration are now implemented. Linux **168/168 PASS**; Windows verification on this new code is still pending (previous Windows run **153/153 PASS**). These checks are partial safeguards, not proof of reconstructed photoreal characters, printable watertight meshes or a full physics solver.

**Latest research expansion:** twenty 16-field cross-disciplinary chapters plus twenty isolated source ledgers are written, with a focused production-paper/technical-engine research overlay under `research/MGR-STUDIO-TO-NATIVE-ENGINE-LESSONS.md`. Code now also includes oriented-camera depth and CPU chunk-residency *planning*: **175/175 Linux and Windows tests PASS**. Real Windows evidence `evidence/blender/windows-wave11-oriented-stereo.json` confirms calibrated rotated-view depth at 0-pixel reprojection error. The research is a foundation and implementation contract, **not** a fully finished film/game/VR engine.

**Prior source/quality wave:** all 24 separately named industry/lab/spec/patent/VFX source families have selected-technique audits and traceable provenance under `research/source-audits/` and `research/external-provenance/`. Ten independent native studio-quality guards are implemented in `forge/studio_quality.py`; `forge.cli studio-proof` generates a ten-check JSON fixture receipt. The Blender 5.2.2 CPU studio witness render **passed on Windows**, confirming an authored proxy scene with PBR/SSS materials, curve strand, two lights and a low-density medium. This is not full realistic hair/skin/light simulation.

## What MGR owns and can run now

| MGR capability | Native implementation | Verified proof | Production gap |
|---|---|---|---|
| MGR CPU World Creator | Typed seed-based neighborhood, streets, building massing | 10/100/1000 local benchmark; unit tests; real Blender world GLB import PASS | Real terrain, architectural detail, textures, world quality |
| MGR Scene Blueprint | Deterministic grid graph, routes, basic collision and output manifests | Unit tests + exported JSON | Navmesh, runtime physics, persistent editing |
| MGR World Logic | Reproducible sampled road-agent travel using intersection graph and building-collision checks | Positive/negative route tests and sample-budget fail-closed | Actual navmesh, door/room/vertical access, moving avatar and game runtime |
| MGR Beyond Imagery | Separate two-room interior hypotheses | GLB 1,200 triangles imported in Blender 5.2.2 | Truthful reconstruction from approved multiple references, rich interiors |
| MGR Environment Forge | Basic procedural parks, trees and path | Parks GLB 504 triangles imported in Blender | Natural assets, biomes, physics, textures |
| MGR Character Fabric | Anonymous T/A mannequin with 20 independently exported parts, including separate trousers and elbow sleeves | Windows Blender imported all 20 parts into skinned rig; inventory/unit tests PASS | Real owner-approved Tevin likeness, fingers/facial detail, fitted clothing |
| MGR Rig Intelligence | 11 named bones, 20 modular skinned parts, 48 blended elbow sleeve vertices, animated keyframes | Windows Blender 5.2.2 saved a `.blend`, 0.428m evaluated hand movement, pose audit PASS (0m arm-joint gap, normalized skin) | Smooth full-body deformation, full pose suite and approved Tevin |
| MGR Wardrobe Intelligence | Separate coat, shirt, left/right trousers, boots, elbow sleeves and chain, typed skeletal attachments | Missing-piece, wrong-bone and actual Windows 20-part assembly checks PASS | Fitted real garments, cloth simulation, collision/intersection QA |
| MGR PBR Material Guardian | Native standard metallic/roughness recipes, GLB overrides, Blender Principled material inspection | Five material sockets on Windows Blender 5.2.2 verified; values/bounds negative tests | Production UVs, textures, normal maps, color spaces and visual realism |
| MGR Motion Blueprint | Bone-length-preserving T→A→T landmark samples | Pose validation tests | Actual skinned rig, weights, deformation, animation playback |
| MGR World Flight | World-coordinate camera keyframes, clearance checks against known buildings | 3-keyframe Windows `.blend` generated and edited for real framing; negative intersection test | Playback controller, world walkthrough |
| MGR Cinematic Director | Three lighting moods, shot validation, Blender-created sun/world/camera and low-sample CPU Cycles render | Actual corrected world preview PNG and editable Blender project saved; visual framing improved on rerender | Cinematic lighting artistry, timelines/audio, quality targets and real-time preview |
| MGR Spatial Eyes | Known-object center ray occlusion, distances and evidence labels | Geometry test suite + JSON output | Visual scene comprehension and 3D reconstruction |
| MGR Scene Consciousness | Authored-object dimensional inventory and road-route facts, exported `scene_facts.json` | Deterministic and negative unit tests | Full Blender scene semantics, door portals, actual visual understanding |
| MGR Visual Judge | PNG/pixel comparison, transparent-alpha foreground, translation/90° image-plane silhouette tolerance and provenance-based identity | Synthetic shifted/rotated/transparent tests; actual Blender pose frames foreground and pixel-difference receipt | Arbitrary 3D camera views and moving poses cannot be proven from a single image; semantic visual diagnosis pending |
| MGR Code Architect | Scoped multi-file text changes, digest preconditions and recoverable rollback | Multi-file, traversal, symlink, size, stale-change and rollback tests | OS-level isolation and safe arbitrary code execution, job UI and approvals |
| MGR Creation Memory | Integrity-chained identity revisions and property locks | Lock, stale write and tamper tests | Authenticated owner approvals, concurrent DB, consumer replay |
| MGR Self-Repair Studio | Bounded repair proposals, trusted validation and automatic rollback | Synthetic fail→revert→pass and exhaustion tests | Vision-led diagnosis, Blender edit strategies and isolated execution |
| MGR Creation Pipeline | Fresh-workspace world build, optional actual Blender import/render, visual baseline and stage receipts | CPU path automated tests | Latest integrated pipeline still needs actual Windows Blender end-to-end run and visual acceptance |
| MGR Model Dock | Offline recipe schema, CPU adapter, license/spend guards | Mock/CPU adapter tests | Real installed licensed neural models and isolated execution |
| MGR Compute Admission | Hardware-aware CPU/GPU prerequisite gate, explicit license and shared-memory uncertainty | Local 103-test suite includes no-CUDA, no-license and shared-GPU negatives; Windows hardware inventory captured | Real neural inference and GPU backend benchmarking |
| MGR Asset Vault | Hash-based local dedupe and rights metadata | Tamper/provenance tests | Multiuser DB, revisions, search |
| MGR Geometry QA | Degenerate/bad index checks and conservative cleanup | Mesh tests | Watertight repair, retopo, UV validation |
| MGR Delivery Bundle | GLB, OBJ, MTL, LOD1, parks, interiors, scene facts/camera/lighting JSON, preview SVG | 16-file bundle with 15 artifact SHA receipts; Blender world and PBR inspection | Engine/film pipeline, full interoperability and rendered visual QA |
| MGR Fantasy Forge | GPU-free 3D magic meshes/particles, glTF emission, 2 real Blender point lights, illuminated witness, Fog Glow, bounded uniform/cloud-shaped Cycles atmosphere, and MGR FX Judge | **146/146** tests on both OSes; real Blender portal phases, glowing witness, volume/control renders; native matched-image FX Judge PASS with **22.37957/255 RGB MAE** on Windows | No real smoke dynamics, soft cloud boundary, interactive world illumination or production cinematic quality |
| MGR Spatial Truth | Same image pixel from different possible 3D depths; CPU camera rays, bounded triangle-plane cross-sections and materialized JSON proof | **153/153** Windows/Linux tests; actual Windows command proves same pixel at depths 4m and 12m and 8 section segments on a generic box | Multi-view calibrated reconstruction, confidence and camera/print interoperability |
| MGR Build Ledger | 71-area native register (including spatial F68–F71), provenance, **153 current tests**, benchmark receipts | Windows **153/153**, Linux **153/153**; rig, PBR, director frames, optical glow, volume styles, matched-image judge and spatial-proof PASS | 20-domain end-to-end research, live game-engine runtime and owner approval |

## Exact Blender environment and measured Windows receipts

- User-owned device: **Time**, connected through authorized Desktop Commander; test clone in isolated Windows Temp folder. No existing user project overwritten.
- Blender executable: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`; actual version **5.2.2 LTS**.
- Windows Python **3.14.8**. Current enlarged wave **153/153 PASS** on both Windows and Linux; rig/material/director receipts: `evidence/blender/windows-wave5-*.json`; FX render/judge receipts under `evidence/blender/windows-wave6-*`, `evidence/blender/windows-wave7-*` and `evidence/blender/windows-wave8-*`; spatial command receipt `evidence/blender/windows-wave9-spatial-truth.json`.
- Actual headless import receipts: `world.glb` **372 triangles**, `interiors.glb` **1,200**, `parks.glb` **504**, anonymous T and A mannequins **204 each**; all returned Blender **PASS**.
- Real import verification includes earlier five GLBs and this wave's new world/20-part rig/materials. A real Windows Cycles PNG and editable `.blend` were generated. **Only narrow skinning mechanics and basic composition are verified; real human anatomy, cloth quality, photorealism and interactive runtime acceptance remain open.**

## What is still open

1. Owner-approved Tevin source/reference privately, precise character identity, detachable *actual* wardrobe, rig and animation.
2. Production-grade rendered-image aesthetics, continuous anatomy and skin quality, topology/UV/texturing and full pose/deformation tests; basic editable `.blend` and rendered proof now exist.
3. Real model inference, commercial weights/license approvals, GPU/CPU resource planning, image/video-to-3D reconstruction.
4. Full interactive Forge Studio: prompt editing, project browser, scene editor, asset library and in-world walkthrough.
5. Full region terrain, world streaming, detail levels with equivalent scene contents, collisions and engines.
6. MGR Creation OS, MGR-ONE/Tevin and Create Loco capability interface audit and integration.
7. Multiuser security, durable worker queue, provider installers, full benchmark/quality comparisons and owner acceptance.

## Source-of-truth precedence

- Product ownership and identity: `docs/MGR-NATIVE-CANON.md`.
- Product ambition and module boundaries: `docs/PRODUCT-BIBLE.md`, `docs/ARCHITECTURE.md`.
- Measured status and blockers: `docs/BUILD-REGISTER.md`, `docs/IMPLEMENTATION-EVIDENCE.md`, this file.
- Historical logs: `docs/PROGRESS-LOG.md` (dated entries may be superseded).
- Technical external code/data licensing: `research/external-provenance/` only; external projects **do not name or define MGR capabilities**.

**Honest verdict:** MGR Forge has working, tested native 3D prototypes and actual Blender 5.2.2 import, character, camera and fantasy FX renders. The full production creation platform, photorealistic content and owner-approved Tevin remain unfinished.
**NEW WORLD EDITOR (F88):** A runnable offline WebGL2 world now includes building position, height and color editing with browser JSON export/import and bounded local persistence. `forge.cli apply-world-edits` independently reconstructs edited GLB, OBJ, MTL, preview, hashed manifest and playable HTML without touching the source. **223/223 Python tests passed on Linux and Windows; Windows Chrome rendered the actual world and visible editor UI.** Physical editing controls have not been browser-automated. Screenshot receipt `evidence/browser/windows-wave14-world-editor.json`. Demo: `demos/mgr-world-editor.html`.

