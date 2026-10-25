# MGR Forge — Native Prototype Implementation Evidence

Date: 2026-10-25. This page distinguishes working code from future intent.

**Foundation S01–S05 proof:** Linux **168/168 PASS** on current code (previous Windows verified **153/153**, new Windows run pending). New positive/negative tests cover parallel calibrated stereo ray intersection (`forge/spatial_truth.py`), topology edge incidence (`forge/surface_truth.py`), and bounded sampled velocity/acceleration (`forge/motion_truth.py`). Research packets at `research/chapters/S01*`–`S05*` each have separately recorded source provenance. These **do not certify** rotated-camera calibration, watertight printing, continuous-time physics, Tevin likeness or photoreal production.

**Current wave evidence (supersedes earlier baseline test counts below):**
**153/153** unit tests passed on Linux and Time's Windows device. On real
Blender 5.2.2 LTS, the 20-part/11-bone generic mannequin has 48 dual-bone
elbow sleeve vertices and passes measured two-pose joint/weight QA; the world
has verified imported PBR materials; and editable CPU Cycles cinema scenes have
three distinct cameras, three camera-bound cuts and a measured **7.21726m**
moving-camera shot, and a real four-frame Cycles timeline proof showed moving
shot RGB MAE **5.98669**. Actual `.blend`, PNG and JSON receipts are stored under
`evidence/blender/windows-wave5-*`. Fantasy geometry and glTF emission additionally passed real Windows Blender CPU Cycles at two portal phases: `evidence/blender/windows-wave6-*`, 600×600 frames and normalized pixel delta **0.00897953**. This does not establish cinematic volumetric FX. The full 71-area feature inventory is in
`docs/BUILD-REGISTER.md`, including seven director and 17 FX tracks.

Further Windows Blender 5.2.2 render verification added two native point lights, an illuminated matte witness and the 5.x `Fog Glow` compositor. Actual PNG and JSON scene receipts are in `evidence/blender/windows-wave7-*`. This proves lighting and image-space composition in a controlled scene, **not** simulated fire, particle collisions, atmospheric volumes, game-runtime lighting or completion of the entire F51 track.

The current Atmosphere Field wave independently rendered no-volume, uniform-volume and noise-cloud volume scenes in Blender 5.2.2 CPU Cycles. The two real scattering materials are native `ShaderNodeVolumePrincipled` instances. A matched comparison found **156,410 materially changed pixels** for the uniform field against control and RGBA MAE **0.06582227**; cloud vs uniform MAE **0.02924215**. Actual receipts and PNGs: `evidence/blender/windows-wave8-*`. These results prove ray-scattered fog in a bounded proxy, not dynamic smoke or flawless cinematic diffusion.

MGR FX Judge now runs the matched comparison as a native validated CLI, not just an ad-hoc Blender console. The actual Windows control/volume proof passed with **22.37957 RGB MAE (8-bit)** against an explicit minimum of **3.0**, and the receipt is archived as `evidence/blender/windows-wave8-judge.json`. It refuses mismatched cameras and missing volume shader claims; it still does not recognize aesthetic defects semantically.

New reality-to-space research is now mapped over 20 disciplines and four cross-domain bridges. `forge/spatial_truth.py` implements and tests pinhole projection, pixel-to-camera ray and triangle/plane mesh sectioning; the `spatial-proof` command emits an inspectable JSON example. **Seven additional tests** brought both Linux and Windows to **153/153 PASS**. Windows CLI generated `evidence/blender/windows-wave9-spatial-truth.json` with measured section segments, identical projected pixels at depths 4m and 12m, and an explicit unknown-depth limitation. Nothing here implies monocular true-depth recovery or print-ready G-code.

## What you can actually run

| Feature | Module | Actual behavior | Evidence | Still missing |
|---|---|---|---|---|
| Bounded prompt | `forge/planner.py` | Parses simple building counts and caps oversized requests | `test_bounded_prompt_planner`, `test_planner_refuses_unbounded_request` | Freeform scene understanding |
| Typed project input | `forge/spec.py` | Validated rows, columns, buildings, seed, lot sizes | `test_spec_rejects_*` | Full scene/character schema |
| Procedural street scene | `forge/geometry.py` | Creates street meshes and colored massing buildings | `test_world_qa`, `test_large_world_no_missing_lots` | Landscape, interiors, doors, roads beyond grids |
| Native 3D export | `forge/glb.py` | Produces GLB 2.0 with normals, indices and PBR colors | Internal tests + five actual Blender 5.2.2 imports PASS | Engine (Unreal/Unity) and render/roundtrip acceptance |
| Reproducibility | `forge/geometry.py` | Same seed yields identical output | `test_seed_deterministic` | Persistent multi-stage workflows |
| Asset memory | `forge/assets.py` | SHA deduplication and provenance; tamper detection | `test_asset_registry_*`, `test_asset_provenance_required` | Search, version history and approvals |
| Character guard | `forge/quality.py` | Checks missing landmarks, symmetry and identity proportions | `test_character_*` | Mesh/rig/pose analysis; real Tevin inputs |
| Build quality receipt | `forge/cli.py` | Writes scene manifest, GLB integrity and SHA | `test_build_manifest_and_file` | Automated independent render, visuals, performance ledger |
| DAG / dependency guard | `forge/workflow.py` | Deterministic ordered steps; rejects missing/cyclic dependencies | `test_workflow_*` | Full scene dependency graph, worker orchestration |
| Approval and spend protection | `forge/workflow.py` | Fail-closed budget, network and license gates | `test_paid_plan_*`, `test_license_gate_*` | Human approval UI, authenticated approvals and model license verification |
| Durable local progress | `forge/workflow.py` | Atomic checkpoint with restart recovery | `test_workflow_restart_checkpoint` | Concurrent jobs, queued workers, true retries and cancellation |
| Road graph/path | `forge/world.py` | Symmetric road intersections and reproducible shortest paths | `test_world_road_graph_*`, `test_route_*` | True navmesh, dynamic obstacles and engine traversal |
| Coarse collision | `forge/world.py` | Stationary disk against building bounding boxes | `test_collision_*` | Physics engine, moving collision, detailed mesh collisions |
| Alternative export | `forge/obj.py` | Writes OBJ geometry and MTL colors | `test_obj_*` | Independent application import and material fidelity |
| Isometric preview | `forge/preview.py` | Creates SVG approximation directly from world manifest | `test_svg_*` | Actual GLB rendering and interactive 3D editing |
| Mesh health | `forge/meshqa.py` | Identifies broken indices/degenerate triangles and safely drops invalid triangles | `test_mesh_*`, `test_world_meshes_*` | Watertight manifold repair, retopology, topology-aware normals |
| Coarse LOD/chunks | `forge/streaming.py` | Exports building-only LOD1 mesh and stable chunk cover | `test_chunks_*`, `test_simple_lod_*`, `test_lod_distance_*` | LOD scene parity, runtime streaming, instancing, FPS |
| Native world flight | `forge/cinematic.py`, `forge/director.py` | Authored 3D camera positions, collision/clearance, distinct cuts and sampled easing | Unit tests and actual 3-camera Blender Cycles scene/receipt | Timeline scrub UI, video production and advanced camera tracks |
| Local Model Dock | `forge/recipes.py` | Static model manifest license/checksum/VRAM validation | `test_model_recipe_*` | Installer, sandbox, execution, provider verification |
| Spatial Eyes | `forge/perception.py` | Geometry-grounded object distances and center-ray occlusion with evidence labels | `test_spatial_overview_*` | True scene parsing, live data, image reconstruction, HUD |
| Beyond Imagery prototype | `forge/interiors.py` | Creates separate two-room interior meshes from building footprints with hypothesis provenance | `test_interior_*` | True reconstruction, multi-floor architecture, visual/user approval |
| Detachable generic character | `forge/character.py`, `forge/wardrobe.py` | T/A full-arm/hand proxy with 20 detachable parts and typed garments | `test_generic_character_*`, garment tests, actual 20-part Blender rig PASS | Tevin likeness, real tailored clothing, full smooth skin, visual review |
| Kinematic pose samples | `forge/animation.py` | T-A-T bone-length-preserving editable landmarks over time | `test_pose_track_*`, `test_a_pose_*` | Skinned mesh weights/deformation and playback |
| Native provider contract | `forge/adapters.py` | Selects executable approved offline CPU generator, rejects absent or unapproved neural/provider work | `test_adapter_*` | Real model engines, GPU workers, quality comparisons |
| Blender import probe | `bridge/blender_probe.py`, `forge/blender_bridge.py` | Actual bpy GLB import, triangle/mesh count receipt | Windows Blender 5.2.2 **five PASS** receipts under `evidence/blender/` | Render appearance, edit/re-export and skin/animation testing |
| Park/foliage props | `forge/environment.py` | Generated trees/trunks on empty lots with distinct materials | `test_parks_*` | Natural tree topology, biomes, asset instancing and collisions |
| Bundle integrity | `forge/receipt.py` | Hash/size receipts for all 13 world output artifacts, detects tampering | `test_world_bundle_*` | Signed provenance, cross-consumer receipts |
| CPU benchmark | `forge/benchmark.py` | Reproduces 10/100/1000 building scene generation + GLB export measurements | `test_benchmark_*` and local measured run | Independent runtime/quality/performance comparisons |

## Repeatable smoke commands

```bash
python3 -m unittest discover -v
python3 -m forge.cli build --prompt "Create 25 buildings and streets" --out artifacts/prompt-25
python3 -m forge.cli inspect artifacts/prompt-25/world.glb
```

Observed result: **64/64 tests passed** on Linux and separately on Time's Windows PC. Actual Blender 5.2.2 headless imports of the example world (372 triangles), interiors (1,200), parks (504), generic T pose (204) and A pose (204) returned PASS. Hashes and Blender receipts are at `evidence/blender/windows-2026-10-25.json`. The generic T/A character has 16 detachable parts and passed anatomy tests. Blender imports are genuine independent interoperability proof for those five files, but **not visual, editing, rigging or game-engine acceptance**.

## CPU benchmark receipts (this runner, not broad performance promises)

Command: `python3 -m forge.benchmark --out artifacts/benchmarks/cpu.json`.

| Procedural buildings | Geometry + GLB seconds | GLB bytes | Python peak traced bytes | Triangles |
|---|---:|---:|---:|---:|
| 10 | 0.006222 | 28,804 | 189,027 | 408 |
| 100 | 0.043213 | 223,256 | 1,667,022 | 3,648 |
| 1,000 | 0.310850 | 1,525,788 | 12,012,848 | 25,356 |

Measured under CPython 3.12.14, x86_64. This excludes expensive Blender import, rendering, LOD streaming, textures, characters, commercial-quality detail or neural generation. Results can vary across hardware.

## Limits and honesty

- This is a **real, simple MGR procedural 3D mesh generator**, not yet a photorealistic neural text-to-3D production engine.
- Running on CPU with standard Python proves **this specific procedural path needs no GPU**. It does not prove neural high-quality image-to-3D inference is GPU-free.
- The unit tests inspect geometry and file structure. Five Blender imports independently check some interoperability, **not commercial readiness**, visual fidelity, rigging, or full editor use.
- No model weights, paid credentials or unapproved references were copied to the repository. The approved Tevin base remains a missing input for identity-grade output.
- Only partial progress on the **43 MGR-native** tracked work areas is claimed. The 10 additional F34–F43 capability contracts include a starter `forge/consciousness.py` generated-geometry fact index (four new tests); the full visual and self-repair engine is **not implemented**. Latest local suite: **71/71 pass**. Every other area remains open in `BUILD-REGISTER.md`.

## Next acceptance gates

1. Visually render the successfully imported GLBs in Blender; inspect full-frame limbs, outward normals, materials and editable object structure; test re-export.
2. Build editable component/room generators and a region dependency graph; stress-test export and collision.
3. Add versioned job persistence, cancellation, approval, asset reuse and licensed model adapters.
4. Ingest owner-approved Tevin base privately; compare anatomy, detachable wardrobe and animation deformation.
5. Connect to actual Creation OS and MGR-ONE consumers only after ownership/interface audit.
