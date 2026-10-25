# R09–R10 external provenance: Microsoft Direct3D and Unity

Inspected 2026-10-25. **Depth key:** DOC = official public documentation/API guide reviewed; TREE = repo/linked individual files inspected; SOURCE = full implementation file or tests read; RUN = executable sample or runtime tested. These two audits have DOC and selective TREE, **not SOURCE-complete or RUN**. No external code, SDK, shader, sample art or binary imported.

## R09 — Microsoft Direct3D 12

| Primary reference | Exact question/evidence covered | Depth | MGR use / risk |
| --- | --- | --- | --- |
| [D3D12 overview](https://learn.microsoft.com/en-us/windows/win32/direct3d12/) | API/Windows SDK context, platform location | DOC | Scope of optional D3D12 adapter; not consoles or non-Windows. |
| [D3D11→D3D12 key differences](https://learn.microsoft.com/en-us/windows/win32/direct3d12/important-changes-from-directx-11-to-directx-12) | Explicit queues, command lists, descriptor heaps, residency | DOC | Render graph resource contract. |
| [D3D12 work submission](https://learn.microsoft.com/en-us/windows/win32/direct3d12/command-queues-and-command-lists) | Command queue/list lifetime and application sync | DOC | DAG schedule and cancellation tests. |
| [D3D12 barriers](https://learn.microsoft.com/en-us/windows/win32/direct3d12/using-resource-barriers-to-synchronize-resource-states-in-direct3d-12) | Required read/write state transitions | DOC | Resource hazard negative tests. |
| [D3D12 residency](https://learn.microsoft.com/en-us/windows/win32/direct3d12/residency) | Application manages resource residence under memory pressure | DOC | Scene pressure broker with no assumed VRAM. |
| [D3D12 tiled volume resources](https://learn.microsoft.com/en-us/windows/win32/direct3d12/volume-tiled-resources) | Map virtual tile positions to heap storage | DOC | Optional tiled texture/volume streaming, feature-gated. |
| [D3D12 reserved resource sample](https://learn.microsoft.com/en-us/samples/microsoft/directx-graphics-samples/d3d12-reserved-resources-sample-win32/) | Official sample entrypoint description of tiled mip chain | DOC overview **only**, not SOURCE/RUN | Candidate reproducible Windows test fixture pending exact source and license review. |
| [Pipeline state management](https://learn.microsoft.com/en-us/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12) | PSO graphics-state description | DOC | Shader variant/warmup receipt. |
| [D3D11→D3D12 port guidance](https://learn.microsoft.com/en-us/windows/win32/direct3d12/porting-from-direct3d-11-to-direct3d-12) | HLSL Shader Model 6 via DXIL/DXC and migration | DOC | Target-specific compiler gate. |
| [Advanced Shader Delivery](https://learn.microsoft.com/en-us/windows/win32/direct3d12/advanced-shader-delivery) | Windows 11 technology to prepare compiled shaders for deployment | DOC overview | Study reduction of first-use stutter; Windows/version/distribution restrictions unknown. |

**R09 rights:** Microsoft Learn explanations can be studied; Windows SDK and sample code/binaries have licensing separate from documentation. DXC itself has its own repository license and third-party terms. Before vendoring, pin exact SDK/sample and inspect redistribution/notice requirements. No evidence here establishes Xbox/PlayStation SDK entitlement, Shader Model 6 on every GPU or that MGR D3D12 backend exists. Cost and CPU/GPU performance unmeasured.

## R10 — Unity documentation and open Graphics repository

| Primary reference | Exact question/evidence covered | Depth | MGR use / risk |
| --- | --- | --- | --- |
| [Unity Graphics repo](https://github.com/Unity-Technologies/Graphics) | Public SRP URP/HDRP package tree and overview | TREE overview, not deep SOURCE | Learn structure only; licensing is not blanket open source. |
| [Unity SRP Core documentation file](https://github.com/Unity-Technologies/Graphics/blob/master/Packages/com.unity.render-pipelines.core/Documentation~/index.md) | SRP reusable rendering utilities and common shader components | TREE individual docs | Abstract render director architecture. |
| [Unity SRP Batcher docs](https://github.com/Unity-Technologies/Graphics/blob/master/Packages/com.unity.render-pipelines.high-definition/Documentation~/SRPBatcher.md) | Compatible shader variants can reduce CPU draw preparation | TREE individual docs | Material grouping benchmark, not a universal performance claim. |
| [Unity HDRP LICENSE.md](https://github.com/Unity-Technologies/Graphics/blob/master/Packages/com.unity.render-pipelines.high-definition/LICENSE.md) | Unity Companion License declared for Unity-dependent projects | TREE license file | **Do not copy HDRP into standalone Forge.** Pin revision/seek legal review before code reuse. |
| [Unity Addressables manual](https://docs.unity3d.com/kr/6000.0/Manual/com.unity.addressables.html) | Async location/dependency asset loading | DOC official localized Unity 6 guide | Native dependency streamer concept. |
| [Unity Addressables LoadAssetsAsync API](https://docs.unity3d.com/kr/Packages/com.unity.addressables%401.21/api/UnityEngine.AddressableAssets.Addressables.LoadAssetsAsync.html) | Async operation and dependency/bundle memory behavior | DOC package version 1.21, not necessarily Unity 6 default | Stress repeated loads and release. |
| [Unity AssetBundle memory optimizing](https://docs.unity3d.com/jp/current/Manual/assetbundles-optimizing.html) | Compressed bundle/string/dependency memory overhead and advice | DOC current localized manual | Native memory receipts. |
| [Unity AssetBundle Unity 6 API](https://docs.unity3d.com/cn/6000.0/ScriptReference/AssetBundle.html) | Bundles/load API and memory cache setting | DOC Unity 6 API | Optional importer comparison only. |
| [Unity ModelImporter current](https://docs.unity3d.com/kr/current/ScriptReference/ModelImporter.html) | Axis conversion, unit/rig import and oversampling API | DOC current localized API | Native source transform and motion provenance. |
| [Unity humanoid animation import](https://docs.unity3d.com/es/current/Manual/ConfiguringtheAvatar.html) | Humanoid Avatar mapping and canonical T-pose setup | DOC localized, exact historical behavior may shift | Semantic rig contract, test Blender source. |
| [Unity humanoid preparation](https://docs.unity3d.com/es/current/Manual/UsingHumanoidChars.html) | Need actual rigged + skinned mesh for retarget; independent reimport verification | DOC localized | Directly reinforces Living Rig acceptance. |
| [Unity URP render asset](https://docs.unity3d.com/kr/Packages/com.unity.render-pipelines.universal%4015.0/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) | Render feature/quality options incl LOD crossfade/RenderGraph toggle | DOC pinned older package v15.0 | Feature ideas only, do not assume Unity 6 parity. |

**R10 rights and version hazards:** Unity Companion License may bind source use to Unity-related projects. A public `Unity-Technologies/Graphics` source repository is not authorization to repackage a separate renderer. URP/HDRP, Unity engine runtime, packages, samples and Asset Store content can each have separate terms. Package API documents span current, Unity 6, older versions and localized copies: actual installation must pin Editor version and package manifest to eliminate drift. No Unity editor, profiler, import/export, game build or license enforcement tested here.

## Native cross-system design choices and follow-up verification

| Native MGR feature | R09 lesson | R10 lesson | Required runtime proof |
| --- | --- | --- | --- |
| Hardware Admission / Render Budget | Driver feature tiers, memory residency/tile support | Quality options and LOD | Real low/medium/high device, memory pressure, no GPU fallback. |
| World Asset Stream | Tile/virtual resource commitments | Async asset-dependency graphs | Sector traversal, load/unload/cache leak/stall. |
| Render Director / Material Ledger | Explicit command dependencies/PSO shader warmup | SRP pass and variant grouping | Actual render graph, p95/p99 frame, no visual regressions. |
| Living Rig / Asset Admission | D3D12 only executes; does not establish anatomical fidelity | Avatar/rig and import transform lessons | Actual skinned deformation, altered proportions, independent export/reimport. |
| Production Receipts | Debug layer, timing, device status | Bundle load/retarget/import lifecycle | Immutable report with exact binaries/devices/commands/assets. |

**Next source-depth gate:** before implementation adopts third-party compiler/engine code, read actual implementation tree, manifests, build process, tests, benchmark and license notices at fixed SHA; then compile representative sample and record successful/failing runs. Until then call both R09 and R10 `SOURCED / selective review`, **not end-to-end source audits**.
