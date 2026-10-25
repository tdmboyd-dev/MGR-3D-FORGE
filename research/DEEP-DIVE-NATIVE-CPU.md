# Deep Dive: CPU-native / Procedural World and 3D Core

Inspected: 2026-10-25. Research status: SOURCED / ARCHITECTURE SPECIFIED; implementation/test NOT RUN.

1. **Definition:** Deterministic generation of actual mesh geometry/scene graphs from algorithms and parameters, without relying on a neural text-to-3D inference call.
2. **Production:** Heightfield terrain; L-systems and scatter for vegetation; road/parcel networks; building grammars; parametric rooms/furniture; modular assembly, instancing and LOD; Blender scene authoring.
3. **Standards:** Blender data IDs; glTF/GLB; scene axes and units; PBR; navmesh/collision metadata; material/mesh integrity.
4. **Research:** WorldClaw 2026 global-to-regional planning and WorldGen 2025 hybrid scene layout support planning + procedural/local asset synthesis.
5. **Open source:** Blender Python/data API, Geometry Nodes, Blender source; Recast navigation as candidate. See https://docs.blender.org/api/current/ and https://github.com/blender/blender.
6. **Models:** No foundation 3D model required for procedural geometry. Optional small LLM/planner converts text into typed JSON scene grammar.
7. **Datasets:** Reusable procedural fixtures first; public data only with verified license. No need to train for first scene generator.
8. **Licensing:** Blender GPL and extension obligations apply to some packaging. Geometry outputs generally separate concern, but verify add-ons/assets.
9. **API:** Run Blender background Python by validated, versioned scripts. Do not use brittle UI clicks as source of truth.
10. **MGR Native:** Region/roads/buildings/asset selection engine with deterministic seed, stable coordinates and constraint solver; separate geometry from style/texture generation.
11. **Hardware:** CPU works for geometry and scene operations; RAM and mesh count become bottlenecks; GPU can accelerate preview/render.
12. **Cost:** No per-object inference credits; labor, CPU time, RAM/disk and rendering still cost. Count instancing reuse savings.
13. **Failures:** Floating/disconnected roads, intersections, inaccessible entrances, non-manifold geometry, too many realized objects, giant file, UV stretch, different seeds unexpectedly changing canon.
14. **Evaluation:** Reopen scene; same-seed deterministic hashes, 10/100/1,000 buildings, road connectivity, door access, world scale, bounded file size/memory, GLB roundtrip.
15. **Placement:** MGR-3D-FORGE packages/geometry and packages/world, with Blender adapter; consumer integration via shared contract.
16. **Acceptance:** CPU-only executable generates seeded 10-building block, exports valid GLB, verifies road connectivity and reopens with identical asset IDs; no paid service call.

**Disposition:** MGR-NATIVE / ADOPT procedural architecture. Confidence high for feasibility of constrained worlds, unknown for quality and runtime on owner hardware.

Sources: https://arxiv.org/html/2608.05248v1 ; https://arxiv.org/abs/2511.16825 ; https://docs.blender.org/api/current/ ; https://github.com/blender/blender.
