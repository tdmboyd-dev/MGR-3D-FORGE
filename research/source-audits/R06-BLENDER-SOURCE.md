# R06 — Blender source architecture audit: MGR native creation lessons

**Date:** 2026-10-25. Source accessible in official read-only GitHub mirror `github.com/blender/blender`; upstream development canonical host is Blender projects. Public **`main` branch paths are not version-pinned** and may move. Selected exact upstream files and CMake entries were inspected via the official mirror; no Blender code was copied or linked into Forge. [Provenance](../external-provenance/R05-R06-SOURCES.md).

## Verified source entry points and boundaries

| Blender source path | Direct source evidence | MGR architecture lesson |
|---|---|---|
| `source/blender/geometry/intern/transform.cc` | Geometry namespace and transform-related implementation present | Shape operations should be reusable apart from UI and rendering |
| `source/blender/nodes/CMakeLists.txt` | Built node-engine module with geometry-related execution code and explicit CMake dependencies | Creation graph scheduling deserves a typed engine, not freeform operator guesses |
| `source/blender/compositor/CMakeLists.txt` | Compositor is a distinct module, listing intern node-tree operations and dependencies | VFX compositing separate from geometric sculpture and base renderer |
| `intern/cycles/scene/geometry.h` | Path-tracer scene geometry is a renderer-specific structure | Renderer scene representation differs from editable mesh graph |
| `source/blender/python/intern/bpy_rna.cc` | Bridge between Python scripting and Blender data API (RNA) | Typed app object data can expose safe, inspectable Python-facing controls |
| `source/blender/python/intern/bpy_operator.cc` | `_bpy.ops` operator module implementation | Scripted commands are context-sensitive actions, not identical to direct data mutation |
| `source/blender/python/intern/bpy_rna_context.cc` | Context override mechanics exist separately | Repeatable headless automation must control context and object state explicitly |
| `source/blender/python/intern/bpy_app.cc` | Python app runtime/module-related bridge | Worker automation should inspect host version/capabilities before use |
| `doc/python_api/rst/info_advanced_blender_as_bpy.rst` | Blender can be compiled as `bpy` importable Python module | Optional host adapter possible, but not guaranteed on user's installed Blender |
| `COPYING` and `release/license/license.md` | Blender overall GPL licensing; distribution contains differently licensed dependencies | Do not move Blender GPL implementation into proprietary Forge without rights review |

**Inspection depth:** specific current public source files plus official API/build docs, *not* a full static analysis of entire Blender source, not a compilation of Blender `main`, not a reverse-engineered substitute for all Blender capabilities.

## Five actionable MGR-native lessons

**1. Keep editable data distinct from actions.** MGR's `CreationAsset`/`SceneGraph` and low-level geometry contracts hold durable state. `CreationCommand` has explicit preconditions, effects, idempotency, undo proof and scoped capability. This avoids brittle UI-context-dependent scripts. Verify by replaying 100 commands headlessly and comparing final scene hashes.

**2. Typed creation DAG beats script spaghetti.** A node-based work graph should model *typed input/output sockets*, revisions, invalidation, hash caching and step-specific diagnostics for geometry, motion, shader, simulation, light and compositor effects. An upstream graph concept is not a license to copy its implementation. Test editing one material while ensuring unrelated skeleton and terrain nodes do not recompute.

**3. Renderer adapters preserve scene meaning.** Geometry can be editable high-level mesh/volume while the Cycles-style offline renderer or real-time renderer uses device-specific converted geometry, acceleration structures and shaders. Keep original MGR asset ID, part relationships and exact units through conversion, and test both image appearance and underlying topology.

**4. Compositor is an independent creation layer.** Build `EffectGraph` for passes such as beauty, depth, masks, normals, motion vectors, ambient occlusion, glow, chromatic/fantasy distortion and compositing. Render proof requires multilayer data and deterministic camera/timing. A beautiful flattened PNG is not a reusable VFX project.

**5. Version-aware Python host bridge.** Wrap installed Blender through a bounded workspace adapter: detect Blender version, run an explicitly selected script in background mode, load/save only dedicated Forge files, emit structured logs/reports/preview renders, inspect object/mesh types, and return hashes/test artifacts. Never infer `bpy` Python-module availability from GUI install. Avoid arbitrary unrestricted scripts, personal files and `.env` traversal.

## Native build strategy

Forge should **orchestrate** Blender for advanced modeling/UV/sculpt/rig/render features that already work on Time's Windows machine; its own canonical knowledge graph/asset JSON/commands remain engine-independent. For a future standalone backend, independently implement only high-value deterministic kernels and specialized QA first, then assess whether a licensing-compatible geometry/render library is justified. Blender remains an optional production worker rather than a vendor-only API dependency.

Recommended minimal adapter contract:

```python
probe_blender_installation() -> HostCapabilityReport
execute_forge_job(job: ApprovedCreationJob, *, workspace: ForgeWorkspace) -> JobEvidence
inspect_scene(scene_path: ApprovedPath) -> SceneObjectGraph
render_test_views(scene_path: ApprovedPath, shots: ShotManifest) -> RenderEvidence
```

These are **proposed contracts**; this source audit does not claim the functions exist. The execution worker must enforce workspace ownership, time limits, file hashes and clear error handling. A host process executing Python is powerful; constrain untrusted asset scripts and avoid loading arbitrary add-ons by default.

## Acceptance checks before marking Blender integration complete

1. Probe actual Windows executable/version and Python API details; dump machine-readable capability report.
2. Headless creation of separate body, coat, pants, hair, chains and boots; validate independent object IDs and face/hand coverage in orbital renders.
3. Build deterministic geometry-node scene and test targeted cache invalidation from a changed parameter.
4. Reproduce render across two runs with same seed/engine/settings, stating acceptable tolerance and GPU variation.
5. Composite bloom/depth-mask/fantasy FX into layers without corrupting original geometry or render passes.
6. Fail malformed node/script scenes safely, time out runaway jobs, retain user workspace and credentials untouched.
7. Round-trip GLB/scene export and inspect rig/material/topology preservation.

## License and version reality

Blender's source is open and inspectable, but **overall GNU GPL**, so copying its internals into a closed/proprietary native library could create obligations. Merely driving a separately installed Blender executable with its documented Python API is structurally different from embedding modified source, but any distribution/commercial use should be reviewed on its actual facts. Dependencies can have different terms; tag source hashes/releases if running a fork or distributing binaries. Don't claim every internal Cycles node or geometry operation is replicable simply by reading a couple of headers.

**Status:** R06 source paths, module boundaries, licensing and five practical native lessons complete. No code changes or execution tests were performed by this audit.
