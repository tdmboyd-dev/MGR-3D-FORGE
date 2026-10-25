# MGR Forge — Native Prototype Implementation Evidence

Date: 2026-10-25. This page distinguishes working code from future intent.

## What you can actually run

| Feature | Module | Actual behavior | Evidence | Still missing |
|---|---|---|---|---|
| Bounded prompt | `forge/planner.py` | Parses simple building counts and caps oversized requests | `test_bounded_prompt_planner`, `test_planner_refuses_unbounded_request` | Freeform scene understanding |
| Typed project input | `forge/spec.py` | Validated rows, columns, buildings, seed, lot sizes | `test_spec_rejects_*` | Full scene/character schema |
| Procedural street scene | `forge/geometry.py` | Creates street meshes and colored massing buildings | `test_world_qa`, `test_large_world_no_missing_lots` | Landscape, interiors, doors, roads beyond grids |
| Native 3D export | `forge/glb.py` | Produces GLB 2.0 with normals, indices and PBR colors | `test_glb_export_roundtrip`, corruption checks | Blender/Unreal/Unity independent import verification |
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
| Native world flight | `forge/cinematic.py` | World-space camera keyframes and interpolation | `test_camera_*` | Timeline scrub UI, actual rendering/video |
| Local Model Dock | `forge/recipes.py` | Static model manifest license/checksum/VRAM validation | `test_model_recipe_*` | Installer, sandbox, execution, provider verification |
| Spatial Eyes | `forge/perception.py` | Geometry-grounded object distances and center-ray occlusion with evidence labels | `test_spatial_overview_*` | True scene parsing, live data, image reconstruction, HUD |
| Beyond Imagery prototype | `forge/interiors.py` | Creates separate two-room interior meshes from building footprints with hypothesis provenance | `test_interior_*` | True reconstruction, multi-floor architecture, visual/user approval |
| Detachable generic character | `forge/character.py` | T/A full-arm/hand proxy with 16 parts; exports whole and each part in GLB | `test_generic_character_*`, `test_character_exports_*` | Tevin likeness, real garment segmentation, rigging, visual review |
| Kinematic pose samples | `forge/animation.py` | T-A-T bone-length-preserving editable landmarks over time | `test_pose_track_*`, `test_a_pose_*` | Skinned mesh weights/deformation and playback |
| Native provider contract | `forge/adapters.py` | Selects executable approved offline CPU generator, rejects absent or unapproved neural/provider work | `test_adapter_*` | Real model engines, GPU workers, quality comparisons |
| Blender import probe | `bridge/blender_probe.py`, `forge/blender_bridge.py` | Actual bpy GLB import, triangle/mesh count receipt when Blender installed | `test_blender_bridge_*` only tests construction/unavailable gate | **Real Blender execution not run** in this environment |
| Park/foliage props | `forge/environment.py` | Generated trees/trunks on empty lots with distinct materials | `test_parks_*` | Natural tree topology, biomes, asset instancing and collisions |
| Bundle integrity | `forge/receipt.py` | Hash/size receipts for all 13 world output artifacts, detects tampering | `test_world_bundle_*` | Signed provenance, cross-consumer receipts |
| CPU benchmark | `forge/benchmark.py` | Reproduces 10/100/1000 building scene generation + GLB export measurements | `test_benchmark_*` and local measured run | Independent runtime/quality/performance comparisons |

## Repeatable smoke commands

```bash
python3 -m unittest discover -v
python3 -m forge.cli build --prompt "Create 25 buildings and streets" --out artifacts/prompt-25
python3 -m forge.cli inspect artifacts/prompt-25/world.glb
```

Observed result: **64/64 tests passed** in the latest suite. The 25-building run produced 756 triangles and a structurally valid GLB with 1,512 vertices, six primitives and six materials. The example-spec world produces 10 buildings, 372 triangles, and now also exports 18 trees in 6 parks as a separate 504-triangle GLB. The generic T/A character has 16 detachable parts and passed anatomy/geometry tests. Interior meshes export separately. No Blender executable is installed in the current runner; importing models in a real application remains open. Internal structural checks are not proof of game-ready visuals.

## CPU benchmark receipts (this runner, not broad performance promises)

Command: `python3 -m forge.benchmark --out artifacts/benchmarks/cpu.json`.

| Procedural buildings | Geometry + GLB seconds | GLB bytes | Python peak traced bytes | Triangles |
|---|---:|---:|---:|---:|
| 10 | 0.006222 | 28,804 | 189,027 | 408 |
| 100 | 0.043213 | 223,256 | 1,667,022 | 3,648 |
| 1,000 | 0.310850 | 1,525,788 | 12,012,848 | 25,356 |

Measured under CPython 3.12.14, x86_64. This excludes expensive Blender import, rendering, LOD streaming, textures, characters, commercial-quality detail or neural generation. Results can vary across hardware.

## Limits and honesty

- This is a **real, simple 3D procedural mesh generator**, not an AI neural text-to-3D engine. It does not match Tripo, Hyper3D or neural world-generator visual quality yet.
- Running on CPU with standard Python proves **this specific procedural path needs no GPU**. It does not prove neural high-quality image-to-3D inference is GPU-free.
- The tests inspect geometry and file structure, **not commercial readiness**, rigging, user-facing design or external interoperability.
- No model weights, paid credentials or unapproved references were copied to the repository. The approved Tevin base remains a missing input for identity-grade output.
- Only partial progress on the 30 tracked work areas is claimed. Every other area remains open in `BUILD-REGISTER.md`.

## Next acceptance gates

1. Independently render GLB in Blender or glTF validator and save exact screenshots/validator receipt.
2. Build editable component/room generators and a region dependency graph; stress-test export and collision.
3. Add versioned job persistence, cancellation, approval, asset reuse and licensed model adapters.
4. Ingest owner-approved Tevin base privately; compare anatomy, detachable wardrobe and animation deformation.
5. Connect to actual Creation OS and MGR-ONE consumers only after ownership/interface audit.
