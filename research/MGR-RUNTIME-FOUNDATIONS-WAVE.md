# MGR Forge — Native Runtime Foundations, Wave 2026-10-25

**Native owner:** MGR. **Research depth:** selected published source and algorithm synthesis only. Upstream source links and rights are isolated in `research/external-provenance/OPEN-SYSTEMS-SOURCES.md`. Production claims are governed by executed evidence, not prose.

## Native capability map

| Native component | Creative purpose | This-wave implementation | What constitutes finished |
|---|---|---|---|
| F82 Layered Reality Composition | Preserve deliberate artist/world/shot overrides | Stable paths, field origins and deterministic hash | USD/GLB round-trip with variants, references and real application importer |
| F83 Runtime Parity Lab | Catch missing geometry across file formats before trusting a world export | Independent parser of actual OBJ vertices/faces and actual GLB float3 positions; geometry count, bounds and numeric tolerance | Independent application imports of two target runtimes, rendered material/lighting and animation parity |
| F84 Cell Transport | Move world content from disk into a bounded active working set without silently losing geometry | Actual synchronous per-cell `.glb` reads, SHA-256 verification, bounded memory, protected active priority, error receipts | Streaming game renderer with async requests, cancellation, geometry residency, collision continuity, frame-time proof |
| F85 Dynamics Binding | Catch avatar motion that jumps through walls | Conservative continuous segment-vs-expanded-box guard, earliest impact and approximate normal | True character capsule controller with stairs, slopes, skeletal meshes, physics engine and repeated motion tests |
| F86 Render Truth Lab | Require image-space proof of visual consistency | Earlier `forge/visualqa.py` and independent Windows Blender render receipt; no new renderer this wave | Same camera/light scene on two runtimes, calibrated image comparison, FPS/p95/p99 and hardware ledger |

## Sixteen research/build fields

1. **Definition:** Portable 3D scenes should have editable revisions, validated geometry transport, observable residency and collision-aware actors.
2. **Production practice:** Professional scene pipelines compose authored revisions, reduce scene size by visible-cell budgets and validate exports independently.
3. **Standards:** glTF 2.0/GLB, OBJ, OpenUSD scene composition, 3D Tiles and physics-engine contact abstractions. Those standards are **not** implemented in full here.
4. **Technical research:** Segment–AABB slab intersection, SHA-256 content integrity, bounding-box export comparisons, deterministic layered field precedence and LRU memory admission.
5. **Open implementations studied:** Rendering, scene, physics and geospatial packages tracked in `OPEN-SYSTEMS-RESEARCH-QUEUE.md`; no external code vendored.
6. **Neural models:** None required for correctness of these deterministic components. Optional generative geometry is upstream of this runtime acceptance.
7. **Datasets:** Synthetic generator worlds and malformed/tampered asset fixtures. Real production worlds, animation clips, scans and heterogeneous GPU tests still needed.
8. **Licensing:** New Python code is independently authored; individual source, asset and model licenses require exact release checks before borrowing or shipping.
9. **APIs/providers:** Pure local Python components plus `forge.cli audit-export` and `forge.cli load-cells`; no paid API calls.
10. **Native alternative:** Own small reproducible contracts; export/import via open standards rather than binding the entire MGR product to one external engine.
11. **Hardware:** Python CPU and file I/O only for this slice. Rendering and GPU residency remain untested.
12. **Cost:** No API spend; disk and resident memory are bounded. Actual disk cold/hot latency, GPU upload and total runtime costs not benchmarked.
13. **Failure modes:** Corrupt byte receipt, missing cell, oversized cell, fake parity from matching file names, tunneling through thin collision geometry, nonfinite dimensions, duplicate/unsafe IDs.
14. **Evaluation:** Unit and CLI assertions for positive/negative fixtures; exact SHA, bytes in memory, disk reads, cross-format vertices/triangles and bounds drift. Independent visual/game proof remains necessary.
15. **Placement:** `forge/asset_parity.py`, `forge/cell_transport.py`, `forge/dynamics.py`, and existing `forge/scene_layers.py`; replaceable upstream modeling/renderer backends.
16. **Acceptance tests:** Actual synthetically generated world parity; invalid OBJ rejection; tamper rejection; memory cap and active-cell retention; continuous thin-wall contact; exact Windows/game-engine round-trip later.

## Explicit caveats

- OBJ material approximations are **not** PBR parity, and raw geometry parity does not establish true rendered appearance.
- The local warehouse uses synchronous trusted-directory reads and an in-memory LRU. It is neither network streaming nor GPU mesh residency. Active cells exceeding aggregate memory budget are explicitly skipped, never falsely claimed resident.
- Collision uses conservative *expanded rectangles*; it can report a collision early at rounded corners. It has no vertical slope, gravity or rigid-body impulse dynamics.
- New code is testable without buying any models or GPUs, but this does not prove a no-GPU full real-time graphics product.

## Next proof order

1. Run the same test suite on the authorized Windows Blender machine after syncing exact GitHub `main`.
2. Independently import the same generated GLB/OBJ into a second runtime (a locally permitted open engine), inspect material and bounds differences.
3. Connect cell plans to moving camera events and persistent world files; measure actual cold/hot disk I/O and memory usage.
4. Bridge swept contacts to rigged mannequin foot/body motion and capture continuous playback.
5. Establish side-by-side render and frame-time baselines without conflating quality, speed and cost.
