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

## Repeatable smoke commands

```bash
python3 -m unittest discover -v
python3 -m forge.cli build --prompt "Create 25 buildings and streets" --out artifacts/prompt-25
python3 -m forge.cli inspect artifacts/prompt-25/world.glb
```

Observed result: **44/44 tests passed** in the latest suite (earlier checkpoints were 17/17, 25/25, 33/33). The 25-building run produced 756 triangles and a structurally valid GLB with 1,512 vertices, six primitives and six materials. The earlier example-spec run produced 10 buildings and 372 triangles. No Blender is installed in the current runner. Internal validation is not the same as an independent viewer rendering the asset correctly.

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
