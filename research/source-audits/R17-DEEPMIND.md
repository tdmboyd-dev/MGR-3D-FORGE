# R17 — MGR Technical Source Audit: Published Google DeepMind 3D and World Research

**Research date:** 2026-10-25. **Scope:** six published methods relevant to native MGR-3D-FORGE. **Evidence level:** reviewed authors' primary research pages/abstracts and release descriptions; **not** a replication, weight download, source-tree audit or measured performance benchmark. Source URLs reside in `research/external-provenance/R17-R18-SOURCES.md`.

## Executive finding

Three different capabilities must remain distinct: **video generation** makes convincing images over time; **interactive world prediction** responds to user/agent actions; **reconstruction** estimates actual 3D structure and motion from observations. An embodied agent additionally chooses actions. None alone guarantees an editable, persistent, collision-correct, exportable GLB/game world. Forge should independently build a native persistent geometric world, then attach optional learned image-world and action-control adapters backed by truth checks.

## Method-by-method technical packet

| Research method | Mechanism from primary publication | Outputs/limits for MGR | Code / weights / availability posture |
|---|---|---|---|
| **Genie (2024)** | Generative Interactive Environments, an 11B-parameter foundation world model trained from unlabelled internet videos with learned latent actions; action-conditioned frame evolution makes playable interaction without supplied ground-truth action labels. | Research lesson: infer action vocabulary and state transitions from videos. **Not equivalent to extracting watertight meshes or physical simulation rules.** | Original paper available. No official public model weights or complete hosted unrestricted API identified in cited primary release; model access must not be assumed. |
| **Genie 2 (2024)** | A large-scale foundation world model with autoregressive/diffusion-like action-conditioned future generation, initialized from a generated image, exploring plausible perspectives and scenes. | Lesson: action-conditioned visual continuity can be trained; long-horizon 3D consistency and editable scene graphs still require independent proof. | Research/blog and demo examples found; no full official public training code and weights verified for this model. |
| **Genie 3 (2025)** | General-purpose text-initialized, real-time interactive world model with video frames evolving in response to navigation/actions and longer visual continuity than prior versions. | Lesson: interactivity and image realism can be coupled, but the learned image world is not automatically a persistent metric mesh, physics engine or downloadable game. | First-party research/product description; no broad public checkpoint download or self-host licensing established by inspected pages. |
| **SIMA / SIMA 2 (2024–25)** | A generalist instructed agent for multiple 3D games; observes the environment, interprets goals and chooses game actions; SIMA 2 adds stronger language/multimodal reasoning. | Lesson: **agent control layer** is distinct from scene generator. Native MGR Camera/Director/Traversal can use visual observations plus typed actions while truth constraints test achieved outcome. | Papers/blogs and examples, but no official general-purpose public weights/full training implementation confirmed for these agents. Games/data have independent rights. |
| **DyST (2023)** | Dynamic Scene Transformer learns latent decomposition of content, per-view scene dynamics and camera pose from monocular real-world videos, targeting dynamic 3D scene representation. | Lesson: disentangle geometry/camera/object motion before claiming a shape is the same under view changes. Still susceptible to unconstrained depth/occlusion. | Publication summary discovered. Code/checkpoint availability not established; treat as research-only. |
| **D4RT (2026)** | Unified spatiotemporal scene representation from video, with an encoder compressing geometry/motion and query-style reconstruction/tracking. Primary demonstration discusses 3D point clouds without separately optimizing each video. | Lesson: share geometry+time+camera representation and test 4D tracking. Learned reconstruction remains prediction; benchmark against actual measured geometry and moving actors. | First-party 2026 release reviewed. **Third-party partial reproductions do not prove official code/weights release**; no official distributable checkpoint verified. |
| **Visual Particle Dynamics (2024)** | From RGB-D videos, jointly learn latent 3D particle scene representation, dynamics simulator and renderer for novel viewpoints. | Lesson: particle latent states can represent deforming objects; the renderer, inferred state and physical validity must be validated separately. | First-party publication page reviewed; no exact checkpoint/license confirmed. |

## MGR-native build translation (original feature proposals)

1. **MGR Action-World Contract:** deterministic `WorldState`, `Action`, `Observation`, `TransitionReceipt` and separate renderer; learned frame proposals cannot silently mutate canonical world geometry.
2. **MGR Living Camera Memory:** store object IDs, transforms, depth/occlusion evidence and pose history through time. Record visibility and unknown-space confidence.
3. **MGR Future Branch Studio:** simulate several future candidate action trajectories in a reversible sandbox; score collision/pose/camera continuity before committing a branch.
4. **MGR Screen-to-Scene Judge:** compare predicted video frames with independently rendered stable scene geometry, optical flow and landmarks; reject frame-only hallucinated portals/walls.
5. **MGR Director-in-World:** camera and embodied actor tools with typed movement/collision actions, navigation coverage and observed-result receipts.
6. **MGR Particle Reality Lane:** optional deformable/volumetric particle state coupled to a physics baseline, with units and energy/material validation.

## Model availability, licensing and compute audit

- No reviewed method above yields an **established, freely self-hostable, commercially cleared, lightweight** world model solely because a research webpage shows a demo. Do not route paid operations or download unknown weights without exact license/consent and a measured need.
- Training an 11B-parameter interactive video model from scratch is not a practical CPU-only quick feature. Inference on such large temporal models also commonly needs significant accelerators; the published summaries here do **not** document a trustworthy minimum GPU/VRAM specification, so no fake gigabyte estimate.
- Native procedural geometry, action/replay receipts, camera matrices, typed observation states and basic physics run on CPU with optional existing Blender validation.
- Research papers/figures and demonstrations may have copyright and partner-game footage rights; ideas can inform independent architecture, **not** wholesale copying of footage, game assets, proprietary network weights or branded content.

## Test plan and failure gates

1. Ten-turn deterministic input-action history replays identical **world state and camera transforms**, including save/restart; a generated video that merely looks consistent fails this gate.
2. Navigation agent succeeds/fails objective only after independent 3D collision/world-state query and pose receipt; no video-only success claim.
3. Novel camera orbit around owned scene returns consistent object identity, hidden/visible masks and 3D landmarks; deliberately swapped object identity fails.
4. Action-conditioned moving actor maintains contact, support and intentional physical limits; impossible motion is tagged stylized.
5. Synthetic RGB-D/video fixture with known moving meshes tests estimated camera/object transforms and point cloud errors versus ground truth.
6. Frame extrapolation test measures 1/10/100 step geometry drift, optical flow, loop closure and texture flicker; broken depth discontinuity fails even when beauty score high.
7. Hardware budgeted 1-minute job cancels safely when RAM/VRAM/time thresholds are reached; no credential/network fallback without approval.
8. Provenance gate rejects missing model weights license, unsupported output rights or ambiguous demo-only access.

## Audit disposition

| Area | Evidence | Status |
|---|---|---|
| Published methods/lessons | First-party descriptions/papers | RESEARCHED |
| Exact training code and weights per method | Not independently located/licensed/installed | OPEN |
| Practical reproduction and speed comparison | No hardware experiment | OPEN |
| Native MGR action/scene contracts | Design proposed only | SPECIFIED, NOT BUILT |
| User's Windows Blender integration | Not accessed in R17 | UNVERIFIED |

**Recommendation:** Prioritize procedural persistent geometry + action/observation receipts and capture-vs-render visual truth. Treat interactive video world models as swappable experimental render/forecast layers, never the only underlying MGR world state.
