# External evidence ledger — MGR Neural Shape Intelligence (S16)

**Inspected:** 2026-10-25. Official papers, original research sites, upstream README, model card and license statements. **Inspection status:** public documentation/metadata and selected original research—not a local checkout, all-file source audit, model weight validation, inference benchmark or legal opinion. Published claims are credited to the authors and must be reproduced against MGR's own data before being marked verified.

| Primary upstream | URL | Evidence inspected and constraint learned | Rights / integration status |
|---|---|---|---|
| Microsoft TRELLIS.2 official repository | https://github.com/microsoft/TRELLIS.2 | Image-to-3D 4B structured 3D latents, PBR/mesh output; README declares tested Linux and NVIDIA ≥24GB VRAM | README says MIT model/code; audit transitive submodules, exact weights and revision; not run |
| Microsoft TRELLIS.2 research site | https://microsoft.github.io/TRELLIS.2/ | Native/compact 3D latent and material/mesh technique; performance/quality examples | Research claims unreplicated |
| Microsoft TRELLIS.2 weight/model card | https://huggingface.co/microsoft/TRELLIS.2-4B | Weight description and Linux/NVIDIA ≥24GB prerequisite | Check downloaded weight metadata and file license separately |
| Microsoft TRELLIS original | https://github.com/microsoft/TRELLIS | Structured 3D latent generation with multiple output representations | README inspected, not benchmarked |
| Microsoft TRELLIS original paper/site | https://microsoft.github.io/TRELLIS/ | CVPR 2025 structured latent rationale and target task | Paper/project overview only |
| Tencent Hunyuan3D-2.1 upstream | https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1 | Image-to-shape and PBR image-to-texture; README VRAM: approx 10GB shape, 21GB texture, 29GB combined | Repo published framework, exact installation untested |
| Tencent Hunyuan3D-2.1 license | https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/main/LICENSE | Custom community terms; territory excludes EU, UK and South Korea, plus other conditions | **Not approved for unrestricted MGR commercial distribution; legal/licensing review needed** |
| Stability SPAR3D upstream | https://github.com/Stability-AI/stable-point-aware-3d | Single-image shape reconstruction with point-aware editing | Published project/docs, no model run |
| Stability SPAR3D weight card | https://huggingface.co/stabilityai/stable-point-aware-3d | Community license; enterprise commercial terms required at ≥US$1M annual revenue | Revenue/output/territory terms require approval; not blanket free-commercial license |
| Stability release announcement | https://stability.ai/news-updates/stable-point-aware-3d | Publisher feature claims | Marketing announcement, not verified QA |
| Tencent HunyuanWorld 1.0 repository | https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0 | Panorama proxy, layered mesh export and semantic object elements | README/terms, no actual game performance verified |
| HunyuanWorld 1.0 original paper | https://arxiv.org/html/2507.21809v1 | Semantically layered world synthesis and 360° immersive rendering concepts | Research paper; output quality unreplicated |
| HunyuanWorld 1.0 license | https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0/blob/main/LICENSE | Custom community-use terms | Exact jurisdiction/use/redistribution review pending |
| INRIA original 3D Gaussian Splatting | https://github.com/graphdeco-inria/gaussian-splatting | 3DGS baseline, novel-view pipeline, released reference implementation | Explicit research/evaluation-only license; **not commercial permission** |
| Original INRIA/MPII 3DGS license | https://github.com/graphdeco-inria/gaussian-splatting/blob/main/LICENSE.md | Research-only/noncommercial conditions | Do not vendor into MGR production absent separate grant |
| Original 3DGS paper | https://arxiv.org/abs/2308.04079 | 3D Gaussian primitives and differentiable splat rendering | Scientific concepts, distinct from specific source code license |
| Nerfstudio upstream | https://github.com/nerfstudio-project/nerfstudio | Modular NeRF training, evaluation and some splatting methods | Code Apache-2.0 stated; check transitive packages/models |
| Nerfstudio Splatfacto manual | https://docs.nerf.studio/nerfology/methods/splat.html | Explicitly distinct implementation from original INRIA 3DGS | Verify exact package and dependent CUDA kernels |
| Nerfstudio `gsplat` upstream | https://github.com/nerfstudio-project/gsplat | CUDA-accelerated Gaussian splatting implementation, Apache-2.0 | Candidate production adapter after full license + GPU benchmark |
| `gsplat` research paper | https://arxiv.org/abs/2409.06765 | Authors report lower memory/training time in experiments vs original | Published comparative result, not measured on MGR hardware |
| NVIDIA Cosmos official platform | https://www.nvidia.com/en-us/ai/cosmos/ | World foundation model family and broad physical-AI capability framing | Release/model-specific license and hardware review |
| NVIDIA Cosmos upstream repository | https://github.com/NVIDIA/cosmos | Current world-model code, training/inference recipes and hardware setup | Model license custom; exact 2026 model/checkpoint must be pinned and reviewed |

## Source maturity and explicit exclusions

**Verified by reading original docs/repository pages:** TRELLIS.2's stated ≥24GB Linux GPU requirement, Hunyuan3D-2.1 GPU figures, the existence of separately licensed mesh/splat/world-model implementations, the original INRIA 3DGS research-only restriction, and the existence of HunyuanWorld layered representations. **Not verified experimentally:** absolute image-to-3D quality, Tevin likeness consistency, 3D-printability, rigging usability, commercial generated-output safety, network/API pricing, model inference speed, cross-OS support or persistent physics world quality.

## Commercial clearance and hardware checklist

1. Separate **code**, **pretrained weights**, **training data provenance**, **input imagery/likeness**, **generated outputs**, **third-party libraries**, **deployment geography** and **annual-revenue terms**. One MIT header is not a blanket warranty.
2. Pin every project/weight hash and obtain the actual license text stored with weights before download/inference or redistribution.
3. Reject license-incompatible model adapters by default and provide human-readable reason + optional alternative (native geometry or approved permissive model).
4. Query actual installed Windows Blender version, GPU CUDA support/dedicated VRAM, RAM and OS. Do not offer 24GB CUDA model as local-ready on unverified machine.
5. Test held-out views and physical topology/rigging, not just paper figures; retain owner-approved baseline and signed QA receipts.
6. Budget model experiments under dedicated Forge workspace, predeclared GPU/time limits and safe credentials isolation.

## Further first-party reading needed

- Full paper methods/appendices for TRELLIS.2, Hunyuan3D-2.1 and HunyuanWorld followed by selected model/source entrypoints at pinned revisions.
- NeRF foundational paper, dynamic radiance fields, Gaussian-to-mesh extraction under commercially viable implementation, and geometry error quantification.
- Modern 2026 model discovery with checked weights/licenses/benchmarks rather than taking “state-of-the-art” headlines as stable rankings.
- Side-by-side empirical tests on a fully owned character/room/prop data corpus with Blender and target game engine.
