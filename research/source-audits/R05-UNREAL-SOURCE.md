# R05 — Unreal source architecture audit: MGR learning, not engine cloning

**Audit date:** 2026-10-25. **Access:** public Epic documentation/API class listings; source repository at `github.com/EpicGames/UnrealEngine` is gated behind Epic/GitHub account linking and Unreal EULA. **No private source tree was accessed**, and no source was copied. Version used for paths is current online **Unreal Engine 5.8 documentation**, not a pinned checked-out commit. [Provenance](../external-provenance/R05-R06-SOURCES.md).

## Verified code/documentation boundaries

| Epic-disclosed boundary | Exact published location | Meaning for native MGR architecture | Certainty |
|---|---|---|---|
| Runtime rendering module | `/Engine/Source/Runtime/Renderer/` with `Renderer.Build.cs` | Renderer is a module with managed build dependencies, not a universal scene/physics component | UE 5.8 API docs, not inspected source |
| Public renderer contract | `/Engine/Source/Runtime/RenderCore/Public/RendererInterface.h` (`IRendererModule`) | Engine runtime can keep a public render API distinct from internal GPU implementation | UE 5.8 API docs, not inspected source |
| World partition public class | `/Engine/Source/Runtime/Engine/Public/WorldPartition/WorldPartition.h` (`UWorldPartition`) | World streaming logic has typed lifecycle/actor data separate from renderer | UE 5.8 API docs, not inspected source |
| World Partition system | public UE 5.8 World Partition guide | Persistent level partitioned into loadable runtime grid cells; load driven by streaming sources; HLOD/data-layer/operator commands | Official functional docs |
| HLOD system | UE 5.8 World Partition HLOD guide | Distant cell actors may be represented by cheaper aggregate proxies | Official functional docs |
| Source access procedure | Epic docs “Downloading Source Code” | Epic account + accepted Unreal EULA + linked GitHub account; repo not globally public | Official access docs |

There are **no verified R05 private source function bodies, internal render algorithms or commit SHAs**. Do not pretend published API paths prove proprietary Fortnite implementation details. Internal Epic Perforce development streams are separately gated by custom licensing. Console SDKs also require separate vendor authorization.

## Five actionable MGR-native lessons

**1. Stable component boundaries.** Maintain `WorldGraph` and `GeometryTruth` independent of renderer backend; a versioned `RenderBridge` presents approved scene changes, snapshots and capture metrics. This lets MGR choose a GPU backend or an engine adapter without rewriting asset identity or licensing an entire game runtime as MGR source. Gate with renderer-off headless scene tests and renderer-on exact scene-ID correspondence.

**2. Spatial cells with explicit states.** Build `RealmCell` scheduler states (`UNSEEN`, `REQUESTED`, `FETCHING`, `PREPARED`, `ACTIVE`, `COOLING`, `EVICTED`), dependencies, memory budget, priority from camera/player motion, and always-ready colliders for active regions. Stress tests should teleport across 64 regions and detect missing floors, actor duplication or leaked memory.

**3. Semantic world layering.** Keep independent authoring layers for terrain, architecture, collision, audio, lighting, gameplay, navigation and cinematics, sharing world coordinates and stable IDs. A layer may be visible, load-on-demand or always-resident according to rules, with deterministic export behavior and continuity tests.

**4. Hierarchical proxy truth.** Generate far-view HLOD/proxies and switch by projected error and hardware budget. Preserve relevant silhouettes/landmarks, with measurable popping and shader/performance instrumentation. A proxy is a deliberate display simplification, never the authoritative physical collider or original high-quality source.

**5. Data pipeline as first-class code.** Treat baking HLODs, navigation, collision meshes and asset dependency packages as reproducible build tasks that run without loading the whole giant world. Content hashes, versioned artifacts, stage resume/retry and provenance are needed to prevent giant-world regeneration after a local edit.

## Design / prototype placement

Use the MGR-owned S08 Living World Runtime specification as implementation target. Initial candidates: `WorldGraph`, `RealmCellStore`, `VisibilityBudgeter`, `SceneLayer`, `RenderBridge`; interfaces may be implemented with native Python tests for identity/streaming and an approved engine adapter for actual display. Compile a 10-cell + 64-cell deterministic test fixture before optimizing. Reuse MGR geometric truth/asset contracts, avoid dependency on private UE source or Epic-specific export APIs in core.

## Rights/hardware/build caveats

- Unreal source availability for linked licensees is **not public-domain/open-source**, and redistribution/modification follows applicable Epic license; do not transplant internals into MGR's proprietary native core.
- The public API names and file paths may shift in UE updates; pin actual engine version/commit if an approved integration is chosen.
- Nanite rendering and source World Partition implementation details were not inspected; public behavior does not establish hardware performance parity.
- Runtime VRAM/CPU budgets and game frame rate must be measured on target hardware. No engine was built or benchmarked in this audit.

**Status:** R05 source architecture map and five independent implementation decisions complete; **code integration and validation not done by this research**.
