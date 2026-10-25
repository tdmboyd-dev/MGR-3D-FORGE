# R17–R18 — Original World/3D Research Provenance and Rights Ledger

**Research date:** 2026-10-25. **MGR-native audits:** `research/source-audits/R17-DEEPMIND.md`, `research/source-audits/R18-OPENAI.md`. The upstream organizations and model names in this file are documentary citations, **not MGR product identities**. No weights, proprietary source, training data or sample assets imported.

## Google DeepMind first-party sources

| Method/date | Primary publication/source | Technical finding | Availability/license depth |
|---|---|---|---|
| Genie (Feb 2024) | https://deepmind.google/research/publications/60474/ | 11B-parameter video-learned model with latent action space for interactive environment generation. | First-party publication summary; no official self-host checkpoint/license established by inspected page. |
| Genie 2 (Dec 2024) | https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/ | Generalist action-conditioned generative world model with virtual navigation and future visual prediction. | First-party research/blog; code/weights and production API access not confirmed. |
| Genie 3 (Aug 2025) | https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/ | Real-time interactive environment generation from prompts/action, improved temporal consistency. | First-party model announcement, no reusable commercial training implementation established. |
| SIMA (Mar 2024) | https://deepmind.google/blog/sima-generalist-ai-agent-for-3d-virtual-environments/ | Visual instruction-following action agent across heterogeneous virtual environments. | First-party technical report summary; partner games/data terms separate. |
| SIMA 2 (Nov 2025) | https://deepmind.google/blog/sima-2-an-agent-that-plays-reasons-and-learns-with-you-in-virtual-3d-worlds/ | Enhanced multimodal reasoning/action agent for 3D game worlds, not itself a geometry generator. | Official announcement, no distributable pretrained agent license verified. |
| DyST (2023) | https://deepmind.google/research/publications/48657/ | Dynamic neural scene representation decomposes monocular real-world video into scene, camera pose and motion. | First-party abstract read; exact code/weights/third-party asset rights open. |
| Visual Particle Dynamics (2024) | https://deepmind.google/research/publications/50878/ | Learns particle-based 3D latent representation, dynamics and renderer from RGB-D videos. | First-party publication summary, no benchmark reproduction/weights license confirmed. |
| D4RT (Jan 2026) | https://deepmind.google/blog/d4rt-teaching-ai-to-see-the-world-in-four-dimensions/ | Shared 4D scene understanding allows 3D point-cloud reconstruction and tracking queries from videos. | First-party research article; unofficial partial replicas must not be mistaken for official model source. |

## OpenAI first-party sources

| Method/date | Primary publication/source | Technical finding | Availability/license depth |
|---|---|---|---|
| Point-E (2022) | https://openai.com/index/point-e/ | Point-cloud diffusion from prompts, with later geometric conversion. | First-party paper/release. |
| Point-E code/models | https://github.com/openai/point-e/blob/main/README.md | Official code and pretrained research models, including image/text routes. | Code repository public; exact commit/dependency/model asset licenses and runtime still to audit. |
| Point-E license | https://github.com/openai/point-e/blob/main/LICENSE | MIT-licensed repo source text at discovery. | License must be verified at selected commit and independently for checkpoints/training examples. |
| Shap-E (2023) | https://github.com/openai/shap-e/blob/main/README.md | Official code/model release for conditional neural implicit 3D functions. | Public repo; exact revision, weights, dependencies and usage rights need verification. |
| Shap-E model card | https://github.com/openai/shap-e/blob/main/model-card.md | Implicit shape+texture network parameterization and image-conditioned generation, with model limitations. | Upstream model documentation inspected, performance/rights not locally tested. |
| Original Sora world simulator (Feb 2024) | https://openai.com/index/video-generation-models-as-world-simulators/ | Spacetime patch-based video training and emergent simulated 3D; explicit physics limitations. | First-party technical report, not full model code/weights. |
| Sora release limitation statement | https://openai.com/index/sora/ | Cause/effect and complex scene physics can fail despite plausible video. | First-party product/research explanation; no claim of exported 3D geometry. |
| Sora 2 (Sep 2025) | https://openai.com/index/sora-2/ | Newer video/audio world-simulation behavior and imperfect physics consistency. | Official model announcement, no public full checkpoint/self-host source established. |
| Sora 2 system card | https://openai.com/index/sora-2-system-card/ | Published safety/capability limitations; contextualizes simulation claims. | First-party documentation; availability and rights governed by the applicable product terms. |
| Consistency models (2023) | https://openai.com/index/consistency-models/ | Direct mapping from noise with one/few generation steps. | Paper-level method, not a turnkey 3D engine. |
| Simplified continuous-time consistency models (2024) | https://openai.com/index/simplifying-stabilizing-and-scaling-continuous-time-consistency-models/ | Improvements to training/stability, potential few-step sampling acceleration. | First-party research; specific 3D-ready checkpoints and commercial rights unverified. |

## Research use versus implementation rights

**Open source is not a universal blanket:** Some upstream repositories publish code and weights while model cards, checkpoint hosts, dependency licenses, training datasets and demonstration imagery can have distinct limitations. Record repository URL, exact commit SHA, model ID/hash, weight license, dependency versions, output rights, identity-consent controls and accepted hardware benchmark before enabling a model. The existence of a patent, preprint, article or public demo is not permission to reconstruct closed weights, bypass paid access or extract unauthorized datasets.

**Methods can inspire original systems:** Learn abstract ideas such as point sampling, neural implicit surfaces, spacetime visual patching, latent actions and learned particle dynamics. Retain MGR scene/geometry/action/material and factual verification as independently owned contracts. Do not label images/videos as true metric 3D or physics unless independent 3D tests establish it.

## Concrete missing proof

1. Full papers and source tests need page/section-level technical replication in a dedicated experimental branch for any selected open model.
2. Two historical public OpenAI repos are candidates for version-pinned local evaluation; no GPUs/checkpoints installed as part of this audit.
3. No official public DeepMind Genie/SIMA/D4RT weights or complete licensed training implementations have been verified from the inspected primary sources.
4. No Sora raw training code and self-host model weights verified. Product availability is separate from source redistribution.
5. No benchmark demonstrates a new MGR implementation surpasses these models in image fidelity, 3D accuracy, action consistency or cost. Those comparisons require common owned datasets, tasks and measured hardware.
