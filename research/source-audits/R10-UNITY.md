# R10 — Unity Engine Documentation / Graphics Source Audit

**Maturity:** `SOURCED / SELECTIVE SOURCE TREE AND DOCUMENTATION REVIEW`, 2026-10-25. No Unity Editor or target game executable run; no package imported or copied. The native systems proposed below are MGR-designed, not Unity-dependent. External attributions, Unity-specific rights and exact links are recorded in `research/external-provenance/R09-R10-SOURCES.md`.

## Research scope and source depth

Inspected first-party Unity manual and script/API descriptions for Addressables/AssetBundles/async loading and memory, ModelImporter rigging/humanoid mapping, retarget/resample, Scriptable Render Pipeline, SRP Batcher and Graphics repo. Located the official `Unity-Technologies/Graphics` repository README/tree, SRP Core package documentation, HDRP SRP Batcher document and HDRP license file. **Did not read full SRP rendering implementation end-to-end**, compile packages, test Editor workflows or verify current Unity 6 feature parity on a target platform. Some docs are older/version-scoped and must not be treated as exact current APIs.

## High-value technique 1 — MGR Asset Dependency Streamer

**Observed:** Unity Addressables builds on asset bundles to manage dependency loading and asynchronous asset access. Bundles and metadata carry memory overhead; asynchronous calls may load dependencies beyond the requested visible asset.

**Native design:** `Forge Asset Stream` uses content-addressed bundles and a dependency DAG with explicit asset size, visibility/use window, source rights, preferred device tier and reference count. Optional local/cloud workers can fetch approved assets, verify integrity, stage in bounded CPU storage, and release only when no world/shot consumers reference them. World sectors prefetch hero/interactive assets ahead of camera motion.

**Tests:** missing dependency, circular reference, duplicate assets in multiple bundles, corrupt hash, slow network, cancelled load, close/reopen sector, out-of-memory, overlapping load/unload and cache eviction. Assert that retained dependencies remain alive and unloaded assets really release memory. No Unity Addressables source/code required.

## High-value technique 2 — Semantic Rig Retargeting Gate

**Observed:** Unity humanoid animation depends on a configured humanoid Avatar mapping, canonical rest pose (historically T-pose for setup), rigged/skinned meshes, while non-humanoid rigs use different tracks. Unity importer may resample humanoid animation during retargeting.

**Native design:** `MGR Living Rig` defines semantic bone hierarchy, rest/bind matrices, rig type, joint limits, per-bone scales/axes, consistent contact markers, clip timing, and mapping profile. Retargeted results must be contact-corrected and visibly skinned; explicit `unknown` where source camera or animation lacks hands/feet. Preserve original editable clip and generate reproducible target variant.

**Tests:** T/A mismatch, mirrored limbs, missing finger, wrong root scale, 180° turn, knee reverse, foot sliding, invalid bind weights, mismatched sampling FPS and animation export/reimport. Compare evaluated mesh, not merely scene object transforms. Existing `forge/animation.py` landmark tracks do not count as full skin/rig proof.

## High-value technique 3 — Scene Render Pass Scheduling

**Observed:** Unity Scriptable Render Pipeline lets render frame behavior be scripted, and SRP Core exposes common pipeline utilities and shader libraries. The SRP Batcher reduces CPU material/draw preparation for compatible shader variants; this is a workload-specific mechanism, not blanket FPS uplift.

**Native design:** `MGR Render Director` schedules passes by semantic purpose—depth/camera, shadows, opaque materials, character skin/hair, transparencies, volume FX and output QA. A `Material Variant Ledger` groups stable shader requirements, records costly changes and scene-region render receipts. Use Blender or chosen native runtime as execution backend and avoid recreating Unity's entire pipeline.

**Tests:** graph dependency cycles, missing depth/shadow resource, transparent ordering, incorrect material shader variant, camera change, shadow leakage, shader compilation stutter, CPU submission time and actual rendered visual comparisons at fixed quality. Measure before describing batching improvement.

## High-value technique 4 — Asset Import Provenance / Axis Truth

**Observed:** Unity ModelImporter exposes axis conversion, model unit settings, animation resampling and rig import controls. Interoperability may alter meshes and animation even when import succeeds.

**Native design:** `MGR Asset Admission` captures original filename/hash/format, units, up/forward axes, handedness, rest transforms, skinned vertex/weight count, all individual garment parts, material/texture refs and animation sample rates. Import never silently replaces approved assets; conversions produce a versioned derivation and measured loss report.

**Tests:** meter/cm mismatch, flipped coordinate handedness, GLB/FBX/USD importer differences, negative determinant/mirrors, missing textures, malformed skeleton hierarchy, animation frame resample drift and independent Blender/game-engine roundtrip. The fidelity receipt marks unsupported features rather than passing a partial import.

## High-value technique 5 — Workload-Adaptive Scene Quality

**Observed:** Unity URP/HDRP exposes render quality features, LOD transitions and rendering performance tradeoffs; independent project and device profiles are required.

**Native design:** MGR's **Hero Truth Priority** locks anatomical hands/face, outfit silhouette, focal lighting and camera blocking before it permits lower-priority shadow, distant LOD or secondary FX degradation. `Hardware Admission` combines actual device probe with time/memory budget to approve a tier with explicit visual differences. Avoid pretending that batching/LOD erases heavy GPU requirements.

**Tests:** hero closeups vs distant crowd, low-memory integrated GPU, shader feature disabled, dynamic resolution transition, harsh camera move, warm/cold assets and stable p95/p99 frame rate with owner continuity checks.

## Source code and licensing boundary

The `Unity-Technologies/Graphics` repo is public source for SRP packages; HDRP license documentation says **Unity Companion License** for Unity-dependent projects. Public GitHub access does **not** make this entire codebase freely reusable in a standalone MGR renderer. Therefore **STUDY** architecture only and independently author MGR code unless package-specific legal review confirms permitted uses. No Unity SDK APIs, packages, example shaders or assets are bundled here. External motion datasets and Unity Asset Store content have separate rights.

## Acceptance roadmap

1. Implement asset dependency graph and importer metadata receipt in MGR without Unity package dependency.
2. Run real Blender-owned rig/glTF/FBX conversion and compare against separate target engine if available; log hierarchy, weight and contact fidelity.
3. Use one asset-heavy MGR world and repeated travel path to prove streaming memory/no leaks.
4. Benchmark render pass scheduling/variant grouping and quality decisions; record actual p50/p95/p99, GPU, RAM and errors.
5. Where Unity-specific interoperability is required, choose Unity Editor/package version, run import test project, inspect exact package source and full license chain before any embedding.

**Actionable verdict:** Independently build the five native contracts—streamer, Living Rig retarget, Render Director, Asset Admission and Hero Truth Priority—with game-engine grade tests. Unity is a useful technical school and optional output target, not the canonical MGR engine or a source to relabel.
