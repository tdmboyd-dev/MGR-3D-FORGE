# R24 — First-Party Studio and SIGGRAPH Technical Provenance

**Date:** 2026-10-25. Product-native research translation: `research/source-audits/R24-VFX-STUDIOS.md`. Three studios kept **separate** below for historical/trademark/rights traceability. Technical pages, talks and papers were inspected at documented web/publisher depth—not production source code or entire protected film workflows.

## Wētā FX (at least five first-party technical strands)

| Studio source | URL | Documented lesson | Evidence limit |
|---|---|---|---|
| Tissue technology | https://www.wetafx.co.nz/research-and-tech/technology/tissue | Internal linear-elastic finite-element muscle, fat and skin layers drive visible creature deformation. | Technical product history, not closed FEM code, parameter fits or exact production asset. |
| Key research publications | https://www.wetafx.co.nz/research-and-tech/key-publications | Lists original SIGGRAPH technical work on coupled cloth/hair simulation, body deformation, water and guided bubbles/foam. | Official publication index, full underlying papers require per-method review before numerical replication. |
| Pahi: unified water pipeline and toolset | https://www.wetafx.co.nz/assets/Uploads/PDFs/2023-Pahi-A-unified-water-pipeline-and-toolset.pdf | Multi-technique water workflow and scene/render graph handoff for simulation and final images. | Studio-authored technical paper discovered; figures and code rights not assumed reusable. |
| Deep compositing | https://www-ext.wetafx.co.nz/research-and-tech/technology/deep-compositing | Layer/holdout independence, depth of field and complex edge blending improve VFX element integration. | First-party explanation, proprietary compositor implementation unavailable. |
| Physically-based material renderer | https://www.wetafx.co.nz/research-and-tech/technology/manuka | Handles complex combined apes/hair passes under production memory constraints. | Official technique page; not renderer source or licensed shader code. |
| Creature/water production | https://www.wetafx.co.nz/articles/our-work-on-avatar-the-way-of-water | Specialized integrated underwater capture, creature effects and water simulation development. | First-party production breakdown, not underlying footage/assets/solver. |
| Anatomical layering in practical scenes | https://www.wetafx.co.nz/articles/jungle-cruise | Character setup with skeleton/muscle/skin and water behaviors. | Studio disclosure, no independent scientific calibration established. |

## Industrial Light & Magic (at least five first-party technical strands)

| Studio source | URL | Documented lesson | Evidence limit |
|---|---|---|---|
| StageCraft official technology | https://www.ilm.com/stagecraft/ | Integrated tracked virtual production/performance capture and studio controls. | Studio platform overview, proprietary software not disclosed. |
| On-camera environment/parallax | https://www.ilm.com/groundbreaking-led-stage-production-technology-created-for-hit-lucasfilm-series-the-mandalorian/ | Correct environment rendered from tracked camera perspective for live parallax and interactive lighting. | Official production disclosure, not a reusable camera calibration implementation. |
| Virtual Art Department | https://www.ilm.com/virtual-art-dept/ | Practical/virtual space design and shot scouting before physical production. | Studio description, not assets or workflows under open license. |
| Lama material system | https://www.ilm.com/lama-sci-tech-award-win-interview/ | Physically interpretable layered material-network surface optics. | Award/interview summary, not shader equations or open code. |
| Photographic neural reconstruction | https://www.ilm.com/ilm-nerfstudio-ironheart-hpa-award-interview/ | Neural radiance fields reconstruct photorealistic view-dependent environments from real images. | Studio partnership story; external library/license and training data require separate audit. |
| Real-time synchronization | https://www.ilm.com/ilm-nbc-universal-winter-olympics-milan-stagecraft-interview/ | Precise alignment of camera/content/LED timing and parallax is operationally necessary. | First-party interview, no calibration measurements supplied to MGR. |
| Performance/real-world captures | https://www.ilm.com/how-to-build-the-razor-crest-star-wars-mandalorian-grogu/ | Photographic reference tied to digital and physical miniature building; tolerances matter for printed components. | Studio modelmaking article; production rights, source models and closed tools not available. |

## DNEG (at least five first-party technical strands)

| Studio source | URL | Documented lesson | Evidence limit |
|---|---|---|---|
| Anatomical creature technology | https://www.dneg.com/creative-technology/ziva | Anatomically informed musculoskeletal deformation and surrogate fast inference. | Studio product description. DNEG licensing is **exclusive/proprietary**, not free-source rights. |
| Technology acquisition/licensing | https://www.dneg.com/news/dneg-acquires-exclusive-license-to-ziva-technologies-from-unity | Licensing/business control is a core barrier to independent reproduction; commercial tool remains governed by rights. | First-party acquisition statement; no inference about availability to external developers. |
| Dune Part Two sandworm breakdown | https://www.dneg.com/news/return-to-arrakis-for-a-closer-look-at-our-work-on-dune-part-two | Sandworm animation and effects linked to actual photographed footprints/dust then extended with collapse/sand simulations. | First-party project article, no reusable simulator code or licensed plates. |
| FX SIGGRAPH 2024 | https://www.dneg.com/news/dneg-at-siggraph-2024 | Documents complex sand/pyro, crowds, CG environments and detailed hero animation. | Studio event write-up, not underlying SIGGRAPH technical paper details for every FX stage. |
| Procedural swarm technical paper | https://www.dneg.com/wp-content/uploads/2022/11/Creatures-_Taming-the-Swarm-Rippers-on-Pacific-Rim-Uprising.pdf | Group creature motion and surface effects combine procedural locomotion, animation and smoothing. | Studio technical PDF; algorithms must be independently formulated. |
| Artist-driven crowd framework paper | https://www.dneg.com/wp-content/uploads/2022/11/2017.pdf | Director/artist control of crowds and agent behaviors must be integrated with simulation. | Studio-authored publication PDF; exact licensed content not copied. |
| Last Night in Soho compositing | https://www.dneg.com/our-work/last-night-in-soho | Difficult composited sequences require extensive continuity finishing to look seamless. | First-party breakdown, no production masks/plates. |
| Plate/VFX compositing professional context | https://www.dneg.com/news/women-in-vfx-or-varnica-mathur | High dynamic range, deep compositing and complex worlds demand calibrated photography/color and coordinated VFX pipeline. | First-party practitioner interview; technical detail is high-level. |

## SIGGRAPH/published paper cross-check

- Wētā's first-party publication index lists conference papers on **Avatar cloth/hair coupled simulation, Bodyopt deformation and whitewater**; the studio-hosted **Pahi** paper provides a directly authored technical artifact. For detailed code-level replication, retrieve exact ACM DOI/paper revisions and clarify supplementary licenses rather than assuming award descriptions contain complete equations.
- First-party research paper on simulation-aided face strain extraction: https://research.nvidia.com/labs/prl/klar2023simulation/simulationstrain2023.pdf (SIGGRAPH 2023 Talks; credited authors include industry collaborators). It demonstrates a link between performance measurements and simulated strain, but not access to the production capture set or model weights.
- First-party Wētā production renderer/material and compositor listings identify layered optics and depth data as separate technical pillars. No “secret algorithm” was extracted; independent MGR acceptance must rely on mathematics, controlled observations and legal implementations.

## Explicit rights and deployment limits

The studio names, proprietary product names, film stills/plates, captured human performance, facial models, studio assets and closed simulation/render code are **not** MGR intellectual property and were not imported. Technical concepts—FEM, constrained dynamics, spectral/BRDF render ideas, deep samples, neural scene representations, camera parallax, timecode and shot staging—can inform independent implementations. Any code/material/weights copying requires exact-source license approval. Studio page publication is not an open-source grant.

**Evidence posture:** At least 3 distinct first-party techniques documented for each studio. Hardware/compositing/simulation equations described as generalized industry mathematics where studio specifics are not published. No workstation tests, source builds or claimed film-quality equivalence performed here.
