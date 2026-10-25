# Open-systems technical provenance — 2026-10-25

This is the **external** rights/source ledger. Nothing here assigns an outside product name to an MGR-native feature. The owner requested lawful architecture learning, not copies of competitor code.

| System | Primary source inspected | Concrete finding and status | Rights caution |
|---|---|---|---|
| Godot | https://godotengine.org/license/ ; https://github.com/godotengine/godot | Public MIT engine; selected official license/source overview | Assets, extensions have their own terms; runtime proof not done |
| Filament | https://github.com/google/filament ; https://github.com/google/filament/blob/main/docs/Filament.md.html | Cross-platform realtime PBR with physically oriented material documentation | Apache-2.0 core indicated; check bundled assets/deps |
| bgfx | https://bkaradzic.github.io/bgfx/overview.html | API-independent render backend; BSD-2-Clause | Bundled third-party notices separate |
| OGRE | https://github.com/OGRECave/ogre/blob/master/Docs/License.md | Modular graphics renderer, MIT | OGRE versions/modules may differ |
| Panda3D | https://github.com/panda3d/panda3d | Python/C++ game runtime, modified BSD | Bundled dependencies and asset terms separate |
| OpenSceneGraph | https://github.com/openscenegraph/OpenSceneGraph/blob/master/LICENSE.txt | Public OSGPL; not assumed permissive or same as MIT | Full rights review needed before code adaptation |
| Khronos Vulkan examples | https://github.com/KhronosGroup/Vulkan-Samples | Real Vulkan example repo, Apache-2.0 | Examples and asset submodule rights must be checked |
| Khronos OpenXR | https://github.com/KhronosGroup/OpenXR-SDK-Source | Public loader, layers and basic examples | Runtime/device extension conformance untested |
| Bullet | https://github.com/bulletphysics/bullet3/blob/master/LICENSE.txt | Core zlib license, exceptions in Extras/ThirdPartyLibs | Exact source folder terms required |
| Jolt | https://github.com/jrouwe/JoltPhysics | Multicore rigid body architecture, MIT and GDC talk reference | No measured Forge integration |
| Pixar OpenUSD | https://github.com/PixarAnimationStudios/OpenUSD ; https://openusd.org/release/api/index.html | Composed scene description, time-sampled authored data | TOST licensing; no claim of full USD support |
| Cesium | https://github.com/CesiumGS/cesium-native ; https://github.com/CesiumGS/cesium | 3D Tiles, geospatial streaming, own data allowed | Cesium ion hosting optional/paid; data licenses distinct |
| Nerfstudio | https://github.com/nerfstudio-project/nerfstudio | Camera-driven NeRF pipeline, modular training/evaluation | Model, capture data, compute and downstream packages may vary |
| Instant-NGP | https://github.com/NVlabs/instant-ngp/blob/master/LICENSE.txt | Neural hash encodings / NeRF acceleration | **NVIDIA Source Code License-NC: noncommercial. Study only.** |
| Gaussian Splatting | https://github.com/graphdeco-inria/gaussian-splatting | View synthesis research and reference code | Inria Gaussian Splatting restrictions require exact license review; not automatic commercial use |

## Still awaiting module-by-module audit

Mesa, Box2D, ODE, OpenStreetMap dataset ODbL obligations, Isaac Sim components, photogrammetry packages, code-level shader implementations, OpenUSD authoring APIs, and any Epic-gated Unreal source. The queued state is deliberate. Public licensing/access can be open while commercial assets, SDKs and model weights are restricted. These entries are evidence of discovery, not completion.
