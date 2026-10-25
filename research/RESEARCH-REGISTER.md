# MGR Forge Research Register — 2026-10-25

This is a **sourced strategic survey**, not an exhaustive source audit or benchmark. Public paper or code appearance does not prove installation, integration, rights, speed or quality. Status abbreviations: S=SOURCED, R=README/docs inspected, E=end-to-end code read, T=executed tests. Currently none E/T.

## Candidate matrix

| ID | Candidate | What it actually does | Public artifacts / maturity | Hardware known | Preliminary disposition |
|---|---|---|---|---|---|
| R01 | Blender Python/Geometry Nodes | Editable CPU procedural geometry, rigs, worlds and export | Mature source + official APIs; R | CPU sufficient for modeling; GPU helps render | ADOPT |
| R02 | TripoSR | Single-image to draft mesh | Code + weights MIT; R | ~6GB VRAM default, CPU fallback slower | ADOPT for baseline |
| R03 | Stable Fast 3D / SPAR3D | Fast single-image generation and point-aware edits | Code/weights subject to Stability license; S | GPU desirable; CPU test needed | STUDY |
| R04 | TripoSG | Image-conditioned high-fidelity shape | Code + weights MIT; R | >=8GB NVIDIA VRAM published | ADAPT |
| R05 | TripoSplat | Image to Gaussian scene representation | Code + weights MIT reported; S | To verify | STUDY |
| R06 | TRELLIS.2 | Image->PBR mesh via sparse O-Voxel, 4B model | Code/weights MIT, dependencies separately licensed; R | >=24GB NVIDIA GPU; Linux tested | ADAPT if hardware |
| R07 | Hunyuan3D 2.1 | Shape + PBR texture using separated models | Code/weights under Tencent terms; R | 10GB shape; 21GB texture; 29GB combined | STUDY / LICENSE GATE |
| R08 | Hunyuan3D-Part | P3-SAM segmentation + X-Part reconstruction | Code/weights, lighter X-Part release; R | Benchmark required | STUDY / LICENSE GATE |
| R09 | HY-World 2.0 | Text/image/video to persistent meshes/3DGS worlds | WorldMirror/Pano/Stereo weights and inference; R | CUDA; 17B stereo, 80B pano, 425M small pano | STUDY / LICENSE GATE |
| R10 | HunyuanWorld 1.0 | Scene-scale 360° worlds and semantic layers | Code/weights community license; R | Consumer GPU 'lite' version claimed | STUDY |
| R11 | WorldClaw (2026) | Agentic world planning by regions then local assets | Research paper; R | No working MGR benchmark | ADAPT IDEAS |
| R12 | WorldGen (2025) | Text->traversable editable world via layout + procedural + diffusion | Research; R | Deployment proof pending | ADAPT IDEAS |
| R13 | UniForge3D (Oct 2026) | Multi-view reconstruction + generative completion | Paper; R | Code/weights verification pending | STUDY |
| R14 | UniRig | Generalized automatic skeleton rigging | Project/paper; R | Code/weights/license test pending | STUDY |
| R15 | LATTICE (CVPR 2026) | Sparse anchor then high-detail rectified flow | Paper; S | Runtime/checkpoint unknown | STUDY |
| R16 | MeshFlow (CVPR 2026) | Parallel art-like mesh synthesis | Paper; S | Runtime/checkpoint unknown | STUDY |
| R17 | FlashMesh (CVPR 2026) | Speculative autoregressive mesh acceleration | Paper; S | Runtime/checkpoint unknown | STUDY |
| R18 | MeshWeaver (CVPR 2026) | Sparse voxel-guided coarse-to-fine mesh topology | Paper; S | Runtime/checkpoint unknown | STUDY |
| R19 | PE3R (CVPR 2026) | Faster perception/3D reconstruction pipeline | Paper; S | Runtime/checkpoint unknown | STUDY |
| R20 | RnG (CVPR 2026) | Real-time-capable reconstruction + novel views | Paper; S | Runtime/checkpoint unknown | STUDY |
| R21 | Gaussian Splatting / gsplat | Novel-view rendering and scene reconstruction | Mature research implementations; R | Rendering generally GPU-accelerated | ADAPT for visualization |
| R22 | Recast Navigation | Navigation mesh creation and pathfinding | Open-source implementation; S | CPU practical | ADOPT after license review |
| R23 | Blender Rigify | Human control-rig acceleration | Blender add-on; R | CPU | ADOPT for baseline |
| R24 | Tripo paid API | Hosted text/image-to-model and processing | Public API docs; R | Provider GPU | BENCHMARK ONLY |
| R25 | Hyper3D Rodin | Hosted 3D model generation / MCP | Public API/MCP docs; R | Provider GPU | BENCHMARK ONLY |

## Primary sources and why they matter

- Blender: https://docs.blender.org/api/current/ and https://github.com/blender/blender — scriptable modeling, nodes, animation, scene and exports.
- TripoSR: https://github.com/VAST-AI-Research/TripoSR and https://arxiv.org/abs/2403.02151 — fast image-to-3D baseline with CPU option.
- TripoSG: https://github.com/VAST-AI-Research/TripoSG — open flow-based shape architecture, >=8GB GPU.
- TRELLIS.2: https://github.com/microsoft/TRELLIS.2 — sparse O-Voxel/PBR implementation, Linux/NVIDIA/24GB.
- Tencent Hunyuan3D 2.1: https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1 — shape/PBR code, weights, known VRAM.
- Tencent Hunyuan3D-Part: https://github.com/Tencent-Hunyuan/Hunyuan3D-Part — mesh segmentation + part completion.
- HY-World 2.0: https://github.com/Tencent-Hunyuan/HY-World-2.0 — current world generation and reconstruction release.
- HunyuanWorld 1.0: https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0 — panorama and semantically layered mesh worlds.
- WorldClaw: https://arxiv.org/html/2608.05248v1 — global-to-regional semantic world architecture.
- WorldGen: https://arxiv.org/abs/2511.16825 — traversable world generation concepts.
- UniForge3D: https://arxiv.org/html/2610.15357v1 — reconstruct+generate with anchor-view and voxel conditions.
- UniRig: https://zjp-shadow.github.io/works/UniRig/ — automatic rigging.
- LATTICE: https://openaccess.thecvf.com/content/CVPR2026/html/Lai_LATTICE_Democratize_High-Fidelity_3D_Generation_at_Scale_CVPR_2026_paper.html
- MeshFlow: https://openaccess.thecvf.com/content/CVPR2026/html/Li_MeshFlow_Efficient_Artistic_Mesh_Generation_via_MeshVAE_and_Flow-based_Diffusion_CVPR_2026_paper.html
- FlashMesh: https://openaccess.thecvf.com/content/CVPR2026/html/Shen_FlashMesh_Faster_and_Better_Autoregressive_Mesh_Synthesis_via_Structured_Speculation_CVPR_2026_paper.html
- MeshWeaver: https://openaccess.thecvf.com/content/CVPR2026/html/Xu_MeshWeaver_Sparse-Voxel-Guided_Surface_Weaving_for_Autoregressive_Mesh_Generation_CVPR_2026_paper.html
- PE3R: https://openaccess.thecvf.com/content/CVPR2026/html/Hu_PE3R_Perception-Efficient_3D_Reconstruction_CVPR_2026_paper.html
- Tripo API cost: https://developers.tripo3d.ai/en/pricing and https://www.tripo3d.ai/help/api-plugins/tripo-studiotripo-api
- Hyper3D Rodin: https://hyper3d.ai/pricing and https://hyper3d.ai/features/mcp

## Important research findings

1. **Novel representation**: sparse voxels/latent sets, mesh generative flow and Gaussian splats improve efficiency or rendering, but are not evidence of universally GPU-free high-fidelity generation.
2. **World planning**: coherent spatial plan + reusable geometry + regional generation is promising for very large worlds. A fully playable game still requires collision, nav, gameplay and export validation.
3. **Parts over fused mesh**: segmentation and part completion can help outfit handling, but must be tested for human clothing and tiny jewelry rather than assumed.
4. **Cost advantage**: reuse and procedural CPU may cut costs for large batches; no claim of 10x without measured approved asset denominator.
5. **New results**: HY-World 2.0 includes 2026 updates with 425M small pano model, ~1.2B reconstruction and ~17B world stereo. That is a possible tiered compute architecture, not a guarantee small pano alone creates full worlds.

## 16-field deep-research packet template for each candidate

1 Definition; 2 production usage; 3 standards; 4 research/papers; 5 implementation/repo/tree; 6 weights/models; 7 training/eval datasets; 8 full code+model+data+dependency licenses; 9 APIs/providers; 10 MGR-native alternative; 11 OS/CPU/GPU/RAM/disk; 12 build/runtime/scale cost; 13 failures; 14 controlled evaluations; 15 canonical integration owner and contracts; 16 runnable acceptance tests.

## Remaining work — do not mark complete

For each adopted model, inspect manifests, code entry points, actual license, weight license, dataset origin, install, inference, outputs, tests, failure modes and performance on exact target hardware. Preserve commit hash, environment and observed output. For paper-only projects, verify code/weights availability. Measure rather than infer quality rankings. No model has been installed or evaluated by this repo yet.
