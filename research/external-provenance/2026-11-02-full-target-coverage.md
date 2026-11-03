# Full original target and native path coverage — 2026-11-02

The original research universe contains 187 targets. It does not contain 187 companies or 187 completed reverse-engineering audits. This ledger preserves every original XR ID and original entry, adds the eight user-named systems separately, and keeps unknown identities and unexecuted paths visible. The earlier eight-system study is one evidence packet inside this larger scope; it does not close Forge.

This file records research and source accounting. It does not assert commercial generation parity, recovered proprietary backends, completed production acceptance, or current qualification of every native path. The machine-readable companion preserves dated states without overwriting the source registry.

## Counts and evidence boundaries

| Category | Count |
|---|---:|
| asset_pack | 67 |
| source_platform_or_authoring_system | 18 |
| existing_profile_not_execution | 14 |
| geometry_or_reconstruction_system | 25 |
| human_rig_motion_system | 31 |
| world_scene_authoring_system | 32 |

The original registry has 85 source locators that point only to generic github.com. 71 were resolved additively in this pass, including four primary-study locators and bounded publisher repository metadata; 14 remain unresolved. Metadata is identity evidence only, not an algorithm or runtime audit. Original locator values are preserved. Original REA states are 183 NOT_RUN, 3 PARTIAL_PINNED_SELECTED_FILES and 1 COMPLETE_PUBLISHER_SOURCE_ZIP_ENTRIES_ONLY. The last state proves archive entry inventory, not algorithm review or runtime quality.

Native coverage index: 241 Python files parsed, 66 CLI declarations, 29 Studio API string literals, 22 shared MCP text declarations (17 Forge literals, one creation route and four legacy tools) and all F01–F156 register rows. The static scan omits dynamic registrations; use official SDK evidence for the runtime tool catalog. These are source search boundaries, not successful workflows. Import-associated tests are a heuristic; AST parsing does not read the meaning of every function. The JSON records each file digest, declaration and source location. It also lists source owners in 11 product lanes without inventing replacement components.

## User-named systems, distinct from original XR IDs

| System | Primary locator | Scope |
|---|---|---|
| Meshy | https://docs.meshy.ai/en/api/text-to-3d | Prior dated documentation comparison; runtime/API acceptance separate |
| Tripo commercial service | https://developers.tripo3d.ai/en | Prior dated documentation comparison; runtime/API acceptance separate |
| Higgsfield | https://higgsfield.ai/ | Prior dated documentation comparison; runtime/API acceptance separate |
| Artlist.io | https://help.artlist.io/hc/en-us/articles/39755194637597-Artlist-AI-Tools-Generating-3D-Models | Prior dated documentation comparison; runtime/API acceptance separate |
| Unreal Engine | https://dev.epicgames.com/documentation/en-us/unreal-engine | Prior dated documentation comparison; runtime/API acceptance separate |
| Hyper3D / Rodin | https://docs.hyper3d.ai/en | Prior dated documentation comparison; runtime/API acceptance separate |
| Hi3D | https://www.hi3d.ai/ | Prior dated documentation comparison; runtime/API acceptance separate |
| SAM 3D Objects and Body | https://ai.meta.com/sam3d | Prior dated documentation comparison; runtime/API acceptance separate |

Commercial Tripo is not automatically TripoSR or TripoSG. Hi3D is not automatically Hunyuan3D. Artlist was clarified by the owner as Artlist.io. SAM 3D Objects and Body have different tasks. A service front end can expose another system without revealing the generation implementation. Follow the prior comparison and new parent runtime receipts for observed access failures and visible behavior.

## Source-grounded native decisions

These decisions are implementation recommendations from selected source reads, not completed code or full-system audits. No model weights, asset archives, provider generations or private application assets were acquired. Each bounded file checkpoint below records an exact current commit and SHA-256. Third-party code is not copied into Forge.

1. **Controlled morphing:** libigl ARAP separates fixed-handle precomputation from iterative rotation fitting and constrained solves; harmonic deformation solves for boundary-driven fields. Forge’s reviewed morph engine currently provides bounded global scale, twist, bend and taper. Preserve that owner and topology ABI. Add original bounded local handle/cage fields first, with explicit fixed vertices, deterministic falloff, face inversion/area checks and undoable source identity. ARAP is a later quality option requiring a solver/performance decision; it is not achieved by renaming a global transform. [ARAP source](https://raw.githubusercontent.com/libigl/libigl/b41f1944a703653ae0da81e6588650ba14c270ea/include/igl/arap.cpp), [harmonic source](https://raw.githubusercontent.com/libigl/libigl/b41f1944a703653ae0da81e6588650ba14c270ea/include/igl/harmonic.cpp).

2. **Reconstruction evidence:** Open3D’s selected CPU TSDF code projects voxels with camera intrinsics/extrinsics, rejects invalid depth and integrates a truncated depth residual with accumulated weights. Therefore measured RGB-D plus known poses is a viable bounded CPU lane; one RGB photo supplies neither those depths nor poses. Retain Forge’s relief, planar rectification and orthographic visual hull as explicitly different input contracts. A metric reconstruction receipt must preserve units, camera calibration, source hashes and depth provenance. [TSDF implementation](https://raw.githubusercontent.com/isl-org/Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/pipelines/integration/UniformTSDFVolume.cpp).

3. **Multi-view geometry:** COLMAP triangulates corresponding camera rays using small linear systems and checks numerical failure and ray geometry. Its angle helper documents unstable near-parallel geometry. Forge should reject uncalibrated perspective photos in an orthographic contract, and require calibration, correspondences, positive depth, reprojection error and adequate baseline before calling a new lane measured multi-view reconstruction. Implementing triangulation alone does not deliver SfM, feature matching or camera recovery. [Triangulation source](https://raw.githubusercontent.com/colmap/colmap/138119b7640d46f1f51fe329694a9ddae3ae0908/src/colmap/geometry/triangulation.cc).

4. **Export and deformation ABI:** glTF morphs are indexed displacement attributes applied before skinning/transforms. Primitive target order and vertex counts must agree. Joint-index order must agree with inverse bind matrices. Imported mesh edits must preserve indices, UV seams, primitive boundaries, skin weights and target semantics or explicitly regenerate/reject them. Use an independent importer/render and posed/skinned round trip, not merely JSON parsing, to accept the result. This source read covers these specific normative sections, not the whole standard. [glTF morph and skin specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#_morph_targets).

5. **Solid topology:** Manifold’s publisher describes solid manifold triangle meshes and topological robustness. That is useful for optional bounded boolean/solid validation experiments, not evidence that arbitrary imported surfaces are already valid solids. Preserve Forge mesh QA; test watertightness, orientation, degenerates, self-intersections, material/property propagation and dimensional tolerance before admitting a backend. This was a README-level read, not algorithm inspection. [Publisher repository](https://github.com/elalish/manifold).

6. **World composition:** OpenUSD separates elemental assets, layers, overrides and composed stages, and explicitly says topology changes do not automatically repair stronger-layer shading. Apply the architectural principle through existing scene/layer/world owners: stable asset identity, explicit edit layers, deterministic seed/version, collision and placement constraints, and dependency invalidation when geometry changes. This does not justify introducing a duplicate scene authority or promise USD is a rigging system. [USD introduction](https://openusd.org/release/intro.html).

7. **Rig, speech and terrain:** preserve the exact prior selected-source/ZIP-entry boundaries for UniRig, SkinTokens, Rhubarb and Terrain3D. Their study motivates explicit skeleton parent graphs, normalized influences, rest-pose/morph compatibility, source-time speech cues, bounded terrain chunks/LOD/seams and independent pose/engine checks. These are separate correctness tasks. See the dated rig/audio/terrain source study; do not promote its source reads into live neural/provider execution.

8. **Optional neural systems:** Stable Fast 3D, InstantMesh, TripoSG, TRELLIS, Hunyuan, SAM and other model candidates remain distinct sources. GPU model architectures may inform staged segmentation, geometry, texture, topology and packaging workflows, but do not imply CPU parity without weights. The near-term native route is controlled reconstruction/procedural generation and explicit uncertainty, with optional owner-controlled adapters. [Stable Fast 3D publisher](https://github.com/Stability-AI/stable-fast-3d), [InstantMesh authors](https://github.com/TencentARC/InstantMesh), [TripoSG authors](https://github.com/VAST-AI-Research/TripoSG). These three locators were resolved; their algorithm implementations and weights were not fully inspected or executed in this pass.

## Whole Forge acceptance lanes

Each lane remains open until its actual clients and results are reconciled against current evidence. The following checks are needed in addition to selected mathematical ideas. No single image/morph change closes the other lanes.

| Native lane | Required proof |
|---|---|
| Intent/planning | Typed request reaches existing owner; schema errors, dependency ordering, bounds and saved plan are reproducible |
| Image/reality reconstruction | Correct input contract, uncertainty, true mask IoU/fit semantics, camera/scale provenance and reopenable artifact |
| Mesh/morph/repair | Imported and generated topology, attributes, local/global edits, degeneracy and independent render |
| Characters/creatures/rig/motion | Anatomy and rest-pose contract, skin deformation, retarget/animation and target importer |
| Speech/facial/audio | Timebase, cue mapping, negative/empty input, viseme target compatibility and playback |
| World/space/scene | Layout constraints, collisions, seams, streaming/LOD, deterministic seed and layer invalidation |
| Materials/FX/cinematic | UV/material identity, texture channel/color-space correctness, shot timing and rendered result |
| Asset/provenance | Exact package/source/license identity, path safety, bounded downloads and geometry admission |
| Delivery/viewers/engines | GLB/OBJ/other supported path round trips, actual Blender/engine/browser render and unsupported-formats behavior |
| Jobs/security/recovery | Authorization, host/request binding, bounds, cancel/restart, no replay or duplicate execution and saved artifact identity |
| Optional models/compute | No silent paid fallback, exact provider/weights/version rights, cost guard, cancellation and truthful absence |

Security and client acceptance come from actual Forge behavior and repository contracts, not competitor marketing. The CLI, Studio routes, shared MGR-API-MCP declarations and worker need full end-to-end matching; a declaration is not an integration receipt. The AST inventory deliberately keeps all 156 feature rows unassessed by this accounting pass.

## Complete original target ledger

Every row below was read from the original registry. “Row read” means the registry identity/locator/state was inspected. It does not mean the target source or application was fully read or run. Original JSON objects remain in the companion. Generic placeholders remain unresolved; no convenient guessed identity silently replaces them.

### Kenney game kits

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0001 | Nature Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0002 | Prototype Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0003 | Platformer Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0004 | Car Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0005 | City Kit Commercial | explicit locator; not full current audit | NOT_RUN |
| XR-0006 | City Kit Suburban | explicit locator; not full current audit | NOT_RUN |
| XR-0007 | City Kit Roads | explicit locator; not full current audit | NOT_RUN |
| XR-0008 | Food Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0009 | Furniture Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0010 | Space Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0011 | Pirate Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0012 | Castle Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0013 | Tower Defense Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0014 | Mini Dungeon | explicit locator; not full current audit | NOT_RUN |
| XR-0015 | Blaster Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0016 | Graveyard Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0017 | Cube Pets | explicit locator; not full current audit | NOT_RUN |
| XR-0018 | Mini Characters | explicit locator; not full current audit | NOT_RUN |
| XR-0019 | Blocky Characters | explicit locator; not full current audit | NOT_RUN |
| XR-0020 | City Kit Industrial | explicit locator; not full current audit | NOT_RUN |
| XR-0021 | Factory Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0022 | Fantasy Town Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0023 | Modular Space Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0024 | Train Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0025 | Modular Dungeon Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0026 | Modular Cave Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0027 | Mini Forest | explicit locator; not full current audit | NOT_RUN |
| XR-0028 | Mini Skate | explicit locator; not full current audit | NOT_RUN |
| XR-0029 | Mini Arena | explicit locator; not full current audit | NOT_RUN |
| XR-0030 | Retro Fantasy Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0031 | Retro Urban Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0032 | Racing Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0033 | Watercraft Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0034 | Industrial Kit | explicit locator; not full current audit | NOT_RUN |

### KayKit repositories

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0035 | KayKit-Prototype-Bits-1.0 | explicit locator; not full current audit | NOT_RUN |
| XR-0036 | KayKit-Character-Pack-Adventures-1.0 | explicit locator; not full current audit | NOT_RUN |
| XR-0037 | KayKit-Character-Pack-Skeletons-1.0 | explicit locator; not full current audit | NOT_RUN |
| XR-0038 | KayKit-Dungeon-Remastered-1.0 | explicit locator; not full current audit | NOT_RUN |
| XR-0039 | KayKit-City-Builder-Bits-1.0 | explicit locator; not full current audit | NOT_RUN |
| XR-0040 | KayKit-Halloween-Bits-1.0 | explicit locator; not full current audit | NOT_RUN |
| XR-0041 | KayKit-Medieval-Hexagon-Pack-1.0 | explicit locator; not full current audit | NOT_RUN |
| XR-0042 | KayKit-Space-Base-Bits-1.0 | explicit locator; not full current audit | NOT_RUN |

### Quaternius packs

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0043 | Medieval Village MegaKit | explicit locator; not full current audit | NOT_RUN |
| XR-0044 | Sci-Fi Essentials Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0045 | Modular Sci-Fi MegaKit | explicit locator; not full current audit | NOT_RUN |
| XR-0046 | Stylized Nature MegaKit | explicit locator; not full current audit | NOT_RUN |
| XR-0047 | Ultimate Fantasy RTS | explicit locator; not full current audit | NOT_RUN |
| XR-0048 | Cyberpunk Game Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0049 | Ultimate Stylized Nature Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0050 | Ultimate Modular Women Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0051 | Ultimate Modular Men Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0052 | Platformer Game Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0053 | Sci-Fi Modular Gun Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0054 | Ultimate Modular Ruins Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0055 | Ultimate Animated Animal Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0056 | Ultimate Spaceships Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0057 | Animated Mech Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0058 | Ultimate Modular Sci-Fi Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0059 | Medieval Village Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0060 | RPG Character Pack | explicit locator; not full current audit | NOT_RUN |
| XR-0061 | Downtown City MegaKit | explicit locator; not full current audit | NOT_RUN |
| XR-0062 | Sushi Restaurant Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0063 | Zombie Apocalypse Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0064 | Pirate Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0065 | Cube World Kit | explicit locator; not full current audit | NOT_RUN |
| XR-0066 | Universal Animation Library | explicit locator; not full current audit | NOT_RUN |
| XR-0067 | Ultimate Space Kit | explicit locator; not full current audit | NOT_RUN |

### Existing Forge Source Atlas

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0068 | 3DAssets.dev | explicit locator; not full current audit | NOT_RUN |
| XR-0069 | Poly Haven | explicit locator; not full current audit | NOT_RUN |
| XR-0070 | ambientCG | explicit locator; not full current audit | NOT_RUN |
| XR-0071 | MakeHuman / MPFB | explicit locator; not full current audit | NOT_RUN |
| XR-0072 | Kenney | explicit locator; not full current audit | NOT_RUN |
| XR-0073 | Quaternius | explicit locator; not full current audit | NOT_RUN |
| XR-0074 | Smithsonian Open Access | explicit locator; not full current audit | NOT_RUN |
| XR-0075 | OpenGameArt | explicit locator; not full current audit | NOT_RUN |
| XR-0076 | Poly Pizza | explicit locator; not full current audit | NOT_RUN |
| XR-0077 | Blendkit | explicit locator; not full current audit | NOT_RUN |
| XR-0078 | Sketchfab | explicit locator; not full current audit | NOT_RUN |
| XR-0079 | Hugging Face | explicit locator; not full current audit | NOT_RUN |
| XR-0080 | GitHub | resolved additively: https://github.com/ | NOT_RUN |
| XR-0081 | Blender Extensions | explicit locator; not full current audit | NOT_RUN |
| XR-0082 | Godot Asset Library | explicit locator; not full current audit | NOT_RUN |
| XR-0083 | Objaverse | explicit locator; not full current audit | NOT_RUN |
| XR-0084 | Adobe Mixamo | explicit locator; not full current audit | NOT_RUN |
| XR-0085 | KayKit Official Game Asset Packs | explicit locator; not full current audit | NOT_RUN |

### Existing Forge AI model profiles

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0086 | mgr-native-imagination | explicit locator; not full current audit | NOT_RUN |
| XR-0087 | trellis-2 | explicit locator; not full current audit | NOT_RUN |
| XR-0088 | pixal3d | explicit locator; not full current audit | NOT_RUN |
| XR-0089 | triposr | explicit locator; not full current audit | NOT_RUN |
| XR-0090 | trellis-original | explicit locator; not full current audit | NOT_RUN |
| XR-0091 | hunyuan3d-2.1 | explicit locator; not full current audit | NOT_RUN |
| XR-0092 | makehuman-mpfb | explicit locator; not full current audit | NOT_RUN |
| XR-0093 | anigen | explicit locator; not full current audit | NOT_RUN |
| XR-0094 | unirig | explicit locator; not full current audit | PARTIAL_PINNED_SELECTED_FILES |
| XR-0095 | hunyuan3d-omni | explicit locator; not full current audit | NOT_RUN |
| XR-0096 | sam-3d-objects | explicit locator; not full current audit | NOT_RUN |
| XR-0097 | meshanything-v2 | explicit locator; not full current audit | NOT_RUN |
| XR-0098 | riganything-research | explicit locator; not full current audit | NOT_RUN |
| XR-0099 | higgsfield-3d-service | explicit locator; not full current audit | NOT_RUN |

### Neural geometry source candidates

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0100 | Stable Fast 3D | resolved additively: https://github.com/Stability-AI/stable-fast-3d | NOT_RUN |
| XR-0101 | InstantMesh | resolved additively: https://github.com/TencentARC/InstantMesh | NOT_RUN |
| XR-0102 | OpenLRM | resolved additively: https://github.com/3DTopia/OpenLRM | NOT_RUN |
| XR-0103 | LGM | resolved additively: https://github.com/3DTopia/LGM | NOT_RUN |
| XR-0104 | Shap-E | resolved additively: https://github.com/openai/shap-e | NOT_RUN |
| XR-0105 | Point-E | resolved additively: https://github.com/openai/point-e | NOT_RUN |
| XR-0106 | DreamGaussian | resolved additively: https://github.com/dreamgaussian/dreamgaussian | NOT_RUN |
| XR-0107 | Wonder3D | resolved additively: https://github.com/xxlong0/Wonder3D | NOT_RUN |
| XR-0108 | SyncDreamer | resolved additively: https://github.com/liuyuan-pal/SyncDreamer | NOT_RUN |
| XR-0109 | Zero123++ | resolved additively: https://github.com/SUDO-AI-3D/zero123plus | NOT_RUN |
| XR-0110 | CraftsMan3D | resolved additively: https://github.com/HKUST-SAIL/CraftsMan3D | NOT_RUN |
| XR-0111 | CRM | resolved additively: https://github.com/thu-ml/CRM | NOT_RUN |
| XR-0112 | SPAR3D | resolved additively: https://github.com/Stability-AI/stable-point-aware-3d | NOT_RUN |
| XR-0113 | Unique3D | resolved additively: https://github.com/AiuniAI/Unique3D | NOT_RUN |
| XR-0114 | MVDream | resolved additively: https://github.com/bytedance/MVDream | NOT_RUN |
| XR-0115 | Open3D | resolved additively: https://github.com/isl-org/Open3D | NOT_RUN |
| XR-0116 | Kaolin | resolved additively: https://github.com/NVIDIAGameWorks/kaolin | NOT_RUN |
| XR-0117 | nvdiffrast | resolved additively: https://github.com/NVlabs/nvdiffrast | NOT_RUN |
| XR-0118 | PyTorch3D | resolved additively: https://github.com/facebookresearch/pytorch3d | NOT_RUN |
| XR-0119 | MeshLab | resolved additively: https://github.com/cnr-isti-vclab/meshlab | NOT_RUN |
| XR-0120 | OpenVDB | resolved additively: https://github.com/AcademySoftwareFoundation/openvdb | NOT_RUN |
| XR-0121 | Manifold | resolved additively: https://github.com/elalish/manifold | NOT_RUN |
| XR-0122 | CGAL | resolved additively: https://github.com/CGAL/cgal | NOT_RUN |
| XR-0123 | GaussianDreamer | resolved additively: https://github.com/hustvl/GaussianDreamer | NOT_RUN |
| XR-0124 | TripoSG | resolved additively: https://github.com/VAST-AI-Research/TripoSG | NOT_RUN |

### Human and motion tooling candidates

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0125 | Rigify | resolved additively: https://developer.blender.org/docs/release_notes/3.0/add_ons/ | NOT_RUN |
| XR-0126 | MB-Lab | resolved additively: https://github.com/animate1978/MB-Lab | NOT_RUN |
| XR-0127 | MakeHuman | resolved additively: https://github.com/makehumancommunity/makehuman | NOT_RUN |
| XR-0128 | MPFB2 | resolved additively: https://github.com/makehumancommunity/mpfb2 | NOT_RUN |
| XR-0129 | Diffeomorphic | resolved additively: https://diffeomorphic.blogspot.com/ | NOT_RUN |
| XR-0130 | Auto-Rig Pro | resolved additively: https://www.lucky3d.fr/auto-rig-pro/doc/ | NOT_RUN |
| XR-0131 | Rigger | resolved additively: https://github.com/asu37/Rigger | NOT_RUN |
| XR-0132 | CaptureForge | unresolved publisher placeholder | NOT_RUN |
| XR-0133 | Mixamo | resolved additively: https://www.mixamo.com/ | NOT_RUN |
| XR-0134 | Rokoko Studio | resolved additively: https://www.rokoko.com/products/studio | NOT_RUN |
| XR-0135 | AccuRIG | unresolved publisher placeholder | NOT_RUN |
| XR-0136 | DeepMotion | unresolved publisher placeholder | NOT_RUN |
| XR-0137 | RADiCAL | unresolved publisher placeholder | NOT_RUN |
| XR-0138 | VRM Add-on | resolved additively: https://github.com/saturday06/VRM-Addon-for-Blender | NOT_RUN |
| XR-0139 | UniRig | resolved additively: https://github.com/VAST-AI-Research/UniRig | NOT_RUN |
| XR-0140 | AniGen | resolved additively: https://github.com/VAST-AI-Research/AniGen | NOT_RUN |
| XR-0141 | RigAnything | resolved additively: https://github.com/Isabella98Liu/RigAnything | NOT_RUN |
| XR-0142 | SMPL-X | resolved additively: https://github.com/vchoutas/smplx | NOT_RUN |
| XR-0143 | GHUM | resolved additively: https://github.com/google-research/google-research/tree/master/ghum | NOT_RUN |
| XR-0144 | MediaPipe Pose | resolved additively: https://github.com/google-ai-edge/mediapipe | NOT_RUN |
| XR-0145 | Blender Auto IK | resolved additively: https://github.com/blender/blender/blob/main/source/blender/editors/transform/transform_convert_armature.cc | NOT_RUN |
| XR-0146 | Animation Nodes | resolved additively: https://github.com/JacquesLucke/animation_nodes | NOT_RUN |
| XR-0147 | VRoid Studio | resolved additively: https://vroid.com/studio | NOT_RUN |
| XR-0148 | VRM 1.0 | resolved additively: https://vrm.dev/en/vrm1/ | NOT_RUN |
| XR-0149 | ARKit Blendshape Targets | resolved additively: https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapes | NOT_RUN |
| XR-0150 | BVH Motion Capture | unresolved publisher placeholder | NOT_RUN |
| XR-0151 | Human DNA 3D | unresolved publisher placeholder | NOT_RUN |
| XR-0152 | Rig Retarget Library | unresolved publisher placeholder | NOT_RUN |

### World and scene production candidates

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0153 | Blender Geometry Nodes | unresolved publisher placeholder | NOT_RUN |
| XR-0154 | Blender Asset Browser | resolved additively: https://docs.blender.org/manual/en/5.0/editors/asset_browser.html | NOT_RUN |
| XR-0155 | Godot Terrain3D | explicit locator; not full current audit | PARTIAL_PINNED_SELECTED_FILES |
| XR-0156 | Godot Engine | resolved additively: https://github.com/godotengine/godot | NOT_RUN |
| XR-0157 | LibreTerrain | unresolved publisher placeholder | NOT_RUN |
| XR-0158 | Houdini | resolved additively: https://www.sidefx.com/products/houdini/ | NOT_RUN |
| XR-0159 | Unreal PCG | resolved additively: https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-overview | NOT_RUN |
| XR-0160 | Unity Terrain | resolved additively: https://docs.unity.com/en-us/engine/6000.6/manual/creating-environments/script-terrain/terrain-using-terrains | NOT_RUN |
| XR-0161 | OpenUSD | resolved additively: https://github.com/PixarAnimationStudios/OpenUSD | NOT_RUN |
| XR-0162 | BlenderGIS | resolved additively: https://github.com/domlysz/BlenderGIS | NOT_RUN |
| XR-0163 | Cesium for Unreal | resolved additively: https://github.com/CesiumGS/cesium-unreal | NOT_RUN |
| XR-0164 | OSM2World | resolved additively: https://github.com/tordanik/OSM2World | NOT_RUN |
| XR-0165 | OpenStreetMap | resolved additively: https://www.openstreetmap.org/about | NOT_RUN |
| XR-0166 | TrenchBroom | resolved additively: https://github.com/TrenchBroom/TrenchBroom | NOT_RUN |
| XR-0167 | Blockbench | resolved additively: https://github.com/JannisX11/blockbench | NOT_RUN |
| XR-0168 | MagicaVoxel | resolved additively: https://ephtracy.github.io/ | NOT_RUN |
| XR-0169 | Gaea | resolved additively: https://quadspinner.com/ | NOT_RUN |
| XR-0170 | World Machine | resolved additively: https://www.world-machine.com/ | NOT_RUN |
| XR-0171 | World Creator | unresolved publisher placeholder | NOT_RUN |
| XR-0172 | BlenderKit | resolved additively: https://www.blendkit.com/ | NOT_RUN |
| XR-0173 | Poly Haven | resolved additively: https://polyhaven.com/ | NOT_RUN |
| XR-0174 | ambientCG | resolved additively: https://ambientcg.com/ | NOT_RUN |
| XR-0175 | USD Composer | resolved additively: https://docs.omniverse.nvidia.com/composer/latest/index.html | NOT_RUN |
| XR-0176 | Godot Asset Library | resolved additively: https://godotengine.org/asset-library/asset | NOT_RUN |
| XR-0177 | Blender Extensions | resolved additively: https://extensions.blender.org/ | NOT_RUN |
| XR-0178 | GeoScatter | resolved additively: https://www.geoscatter.com/ | NOT_RUN |
| XR-0179 | Cell Fracture | resolved additively: https://extensions.blender.org/add-ons/cell-fracture/ | NOT_RUN |
| XR-0180 | Molecular Nodes | resolved additively: https://github.com/BradyAJohnston/MolecularNodes | NOT_RUN |
| XR-0181 | OpenVDB Terrain | unresolved publisher placeholder | NOT_RUN |
| XR-0182 | Geometry Nodes Biomes | unresolved publisher placeholder | NOT_RUN |
| XR-0183 | Procedural City Grammar | unresolved publisher placeholder | NOT_RUN |
| XR-0184 | Game World Streaming | unresolved publisher placeholder | NOT_RUN |

### Character/rig/motion candidates

| XR ID | Target | Locator state | Historical REA scope |
|---|---|---|---|
| XR-0185 | SkinTokens/TokenRig | explicit locator; not full current audit | COMPLETE_PUBLISHER_SOURCE_ZIP_ENTRIES_ONLY |
| XR-0186 | NVIDIA Audio2Face-3D SDK + models | explicit locator; not full current audit | NOT_RUN |
| XR-0187 | Rhubarb Lip Sync (timing cue reference) | explicit locator; not full current audit | PARTIAL_PINNED_SELECTED_FILES |

## Exact selected source checkpoints

| Repository/file | Commit | Bytes | SHA-256 |
|---|---|---:|---|
| libigl/libigl/include/igl/arap.cpp | b41f1944a703653ae0da81e6588650ba14c270ea | 8542 | efc042c985a6be69793d65a2dd4bd751baeea436b8401c21a3f605952107f480 |
| libigl/libigl/include/igl/harmonic.cpp | b41f1944a703653ae0da81e6588650ba14c270ea | 8769 | ab3ecda53e783b0607a85823c371e3229e5f34703d060c35323bdded15269740 |
| isl-org/Open3D/cpp/open3d/pipelines/integration/UniformTSDFVolume.cpp | b6c5e196384ad71e75b6e6f9c5da22d046221f1d | 26912 | ddbc61852c43cd2c0573b7de5c5fddcb8cff4d12ee3990160b60618971940496 |
| colmap/colmap/src/colmap/geometry/triangulation.cc | 138119b7640d46f1f51fe329694a9ddae3ae0908 | 9175 | 9310fe781d6319473053d03cf1e8ffc29085545aa5108700bc42c2943e757c0a |

The libigl selected files carry MPL-2.0 headers; the Open3D selected file carries MIT and the COLMAP selected file carries BSD-style terms. Those file headers do not establish all dependency/asset/model rights. No redistribution or integration decision was taken.

## Next exact work

Resolve the remaining 14 placeholder identities in bounded publisher-backed batches before fetching code. Prioritize a source because it closes an observed native acceptance gap, not because its name sounds powerful. Execute selected lawful workflows through REA/runtime when that evidence is requested; retain blank/challenge/403 outcomes. For source-only algorithms use normal source tools and label their scope. Reconcile every current path and F row with exact source hashes, tests and independent result evidence. Keep the original registry and existing domain owners authoritative.

## Actual offline path repair evidence

The completed scoped command matrix accounts for all 66 declarations: 64 actual local/receiver workflows and two original offline injected-transport contracts. No declaration remains wholly unrun in this pinned set. Original world, FX/materials/cameras, composition, release, image/reference, morph/UV, character and Blender receiver workflows all have bounded receipts. Actual REA runtime and every other whole-product requirement remain separate evidence. See `evidence/all-paths-2026-11-02/REPORT.md` and `cli-command-coverage.json`. No F01–F156 feature is closed from these receipts alone.

## Remaining identity and access work

| ID | Entry | Kind | Exact outstanding issue |
|---|---|---|---|
| XR-0132 | CaptureForge | ambiguous_named_target | AMBIGUOUS_NAME; publisher implementation not established; exact implementation/version needed |
| XR-0135 | AccuRIG | vendor_rigging_app | PRIMARY_PAGE_BLOCKED_OR_PREFIX_INSUFFICIENT; PAGE_IDENTITY_NOT_CONFIRMED |
| XR-0136 | DeepMotion | hosted_motion_service | PRIMARY_PAGE_BLOCKED_OR_PREFIX_INSUFFICIENT; PAGE_IDENTITY_NOT_CONFIRMED |
| XR-0137 | RADiCAL | hosted_motion_service | PRIMARY_PAGE_BLOCKED_OR_PREFIX_INSUFFICIENT; HTTP Error 403: Forbidden |
| XR-0150 | BVH Motion Capture | motion_file_format | NOT_A_SINGLE_COMPANY_OR_PRODUCT; exact paper/implementation/version required; exact implementation/version needed |
| XR-0151 | Human DNA 3D | ambiguous_named_target | AMBIGUOUS_NAME; publisher implementation not established; exact implementation/version needed |
| XR-0152 | Rig Retarget Library | ambiguous_named_target | AMBIGUOUS_NAME; publisher implementation not established; exact implementation/version needed |
| XR-0153 | Blender Geometry Nodes | authoring_application_feature | PRIMARY_PAGE_BLOCKED_OR_PREFIX_INSUFFICIENT; HTTP Error 403: Forbidden |
| XR-0157 | LibreTerrain | ambiguous_named_target | AMBIGUOUS_NAME; publisher implementation not established; exact implementation/version needed |
| XR-0171 | World Creator | commercial_terrain_app | PRIMARY_PAGE_BLOCKED_OR_PREFIX_INSUFFICIENT; HTTP Error 503: Service Unavailable |
| XR-0181 | OpenVDB Terrain | generic_workflow_concept | NOT_A_SINGLE_COMPANY_OR_PRODUCT; exact paper/implementation/version required; exact implementation/version needed |
| XR-0182 | Geometry Nodes Biomes | generic_workflow_concept | NOT_A_SINGLE_COMPANY_OR_PRODUCT; exact paper/implementation/version required; exact implementation/version needed |
| XR-0183 | Procedural City Grammar | generic_workflow_concept | NOT_A_SINGLE_COMPANY_OR_PRODUCT; exact paper/implementation/version required; exact implementation/version needed |
| XR-0184 | Game World Streaming | generic_workflow_concept | NOT_A_SINGLE_COMPANY_OR_PRODUCT; exact paper/implementation/version required; exact implementation/version needed |

Of 85 original generic GitHub locators, 71 were resolved additively and 14 remain (five access/visibility limits, four ambiguous names and five formats/concepts without one publisher). The bounded primary metadata/page files preserve failures as well as confirmations. Registry identities and historical REA states are untouched.
