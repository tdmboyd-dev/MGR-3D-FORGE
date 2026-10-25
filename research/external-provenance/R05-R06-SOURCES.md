# R05–R06 external source audit provenance

Captured 2026-10-25. Official publicly accessible documentation and repository files, only. External products are research context; MGR output designs live in `research/source-audits/R05-UNREAL-SOURCE.md` and `R06-BLENDER-SOURCE.md`. **No external source was copied, cloned or built.** The exact docs version / repository branch is stated so these links cannot imply inspection of a pinned checkout.

| ID | Primary source | Link | Inspection and certainty | License/access boundary |
|---|---|---|---|---|
| U1 | Epic UE source download | https://dev.epicgames.com/documentation/unreal-engine/downloading-source-code-in-unreal-engine | UE 5.8 official: requires account linking, EULA and GitHub org access | GitHub repo licensed/gated, not public-domain; source unread here |
| U2 | Unreal source signup repository | https://github.com/EpicGames/Signup | Public README access procedure | Not Unreal runtime source itself |
| U3 | UE renderer module API | https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Renderer | UE 5.8 doc: location `/Engine/Source/Runtime/Renderer/` and `Renderer.Build.cs` | API listing only, no implementation read |
| U4 | UE render interface | https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/RenderCore/IRendererModule | UE 5.8 doc: `RenderCore/Public/RendererInterface.h` | API listing only |
| U5 | UE World Partition class | https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UWorldPartition | UE 5.8 class header path `/Engine/Source/Runtime/Engine/Public/WorldPartition/WorldPartition.h` | API listing only |
| U6 | UE World Partition behavior | https://dev.epicgames.com/documentation/unreal-engine/world-partition-in-unreal-engine | Public documentation for grid cells, streaming sources, HLOD and Data Layers | No proprietary source proof |
| U7 | UE HLOD | https://dev.epicgames.com/documentation/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine | Public HLOD baking/workflow docs | Exact runtime algorithm not inspected |
| U8 | Epic Perforce source access | https://dev.epicgames.com/documentation/en-us/unreal-engine/accessing-unreal-engine-with-perforce | Requires custom Epic license, confirms private dev streams | No access attempted |
| B1 | Blender official GitHub mirror | https://github.com/blender/blender | Public source `main`, rolling/non-pinned | GPL; confirm release/commit before distribution |
| B2 | Geometry transform | https://github.com/blender/blender/blob/main/source/blender/geometry/intern/transform.cc | Current source entry: `blender::geometry` module code | File-level SPDX; implementation not copied |
| B3 | Nodes module build | https://github.com/blender/blender/blob/main/source/blender/nodes/CMakeLists.txt | Current source CMake module dependency evidence | No installed target compile |
| B4 | Compositor module build | https://github.com/blender/blender/blob/main/source/blender/compositor/CMakeLists.txt | Current source CMake module dependency evidence | No installed target compile |
| B5 | Cycles renderer geometry type | https://github.com/blender/blender/blob/main/intern/cycles/scene/geometry.h | Current source type declaration | Renderer-specific structure; no MGR integration |
| B6 | bpy Python data API bridge | https://github.com/blender/blender/blob/main/source/blender/python/intern/bpy_rna.cc | Current source describes RNA/Python interface | GPL source not copied |
| B7 | bpy operators | https://github.com/blender/blender/blob/main/source/blender/python/intern/bpy_operator.cc | Source of `_bpy.ops` layer | Context-sensitive and API-version dependent |
| B8 | bpy context override | https://github.com/blender/blender/blob/main/source/blender/python/intern/bpy_rna_context.cc | Source implementation of context override bridge | No command execution |
| B9 | bpy app | https://github.com/blender/blender/blob/main/source/blender/python/intern/bpy_app.cc | Current source Python host bridge | No module availability assumed locally |
| B10 | Blender Python module docs | https://github.com/blender/blender/blob/main/doc/python_api/rst/info_advanced_blender_as_bpy.rst | Building Blender as importable bpy module possible | Special build; not promised in retail Windows GUI |
| B11 | Blender runtime Python context docs | https://docs.blender.org/api/current/bpy.context.html | Context depends on current UI area and data/operators distinctions | Rolling current docs, pin installed Blender version |
| B12 | Blender source build docs | https://developer.blender.org/docs/handbook/building_blender/ | Official source compiling workflow | Source build requires dependencies/platform toolchain |
| B13 | Blender root COPYING | https://github.com/blender/blender/blob/main/COPYING | Official GNU General Public License summary | GPL obligations, not license-free code |
| B14 | Blender packaged deps/license detail | https://github.com/blender/blender/blob/main/release/license/license.md | Distribution has multiple separately licensed dependencies | Audit individual included component/version |

## Evidence limitations

- Unreal source code paths are taken from the **published C++ API docs**; the private repository and implementation bodies were not accessible in this audit. No false claims about Fortnite, Nanite internals or game console code.
- Blender files are current source entry-points on `main`, not an exhaustive source-tree review and not fixed SHAs. An installed Blender version may diverge.
- Application/tool execution, unit tests, physical Windows rendering, GPU microbenchmarks and integration build outcomes belong to separate implementation evidence, not this source audit.
- MGR should record upstream version/SHA, dependencies, compiled artifacts, exact SPDX and commercial use rights at actual admission time. Original algorithms and interfaces may be inspired by research without pasting third-party code into MGR.
