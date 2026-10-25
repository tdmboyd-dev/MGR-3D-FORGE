# S10 — External provenance: rigging, retargeting and animation

Inspection date: **2026-10-25**. This document stores source attribution and limitations; the MGR-native product architecture belongs in `research/chapters/S10-ANIMATION-RIGGING.md`. A source being linked/reviewed is **not** an end-to-end code or licensing audit. No external code, datasets or models were copied, downloaded or executed for this packet.

| Primary source | Evidence and specific practical lesson | Verification level | Rights, limits and disposition |
| --- | --- | --- | --- |
| [Khronos glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) | Explicit `skins`, `joints`, `inverseBindMatrices`, per-vertex influences, keyed channel data and interpolation. Skeletal motion requires skin and animated joint transforms, not simply a mesh node moving. | Official spec section reviewed, not file validator run | **ADOPT interface standard** after tests; spec is a technical reference, not bundled source/assets. |
| [Khronos skin tutorial](https://github.com/KhronosGroup/glTF-Tutorials/blob/main/gltfTutorial/gltfTutorial_020_Skins.md) | Rest inverse-bind transforms and joint/mesh hierarchy details | Primary maintainer tutorial reviewed | **STUDY** for independent MGR exporter checks; example assets/licenses not reviewed. |
| [OpenUSD UsdSkel introduction, v25.05](https://openusd.org/25.05/api/_usd_skel__intro.html) | Exchange skeletons, blend shapes, skinned rigs and animation/crowds | Official API introduction reviewed | **ADAPT interoperability goals**; not proof of complete controls, physics or lossless export. |
| [OpenUSD UsdSkel API](https://openusd.org/dev/api/usd_skel_page_front.html) | Schema vocabulary and skeletal binding APIs | Official developer docs reviewed | **STUDY**; development docs may differ from production-pinned version. |
| [Blender armature and pose gotchas](https://docs.blender.org/api/main/info_gotchas_armatures_and_bones.html) | Shared armature data versus object-specific pose data, access through object pose bones | Official API guidance read | **ADOPT documented distinction**; exact Windows Blender API version and evaluated dependency graph require executable test. Blender license/linked dependencies assessed at build-time. |
| [Blender 4.4 Action API](https://docs.blender.org/api/4.4/bpy.types.Action.html) | Layered actions impact older F-curve access patterns | Official API doc inspected | **STUDY migration risk**; Blender 5.x API must be checked against installed build, not assumed identical to 4.4. |
| [Godot stable AnimationTree manual](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html) | Clip blending, state machines and Skeleton3D bone track rest semantics | Official stable docs reviewed | **ADAPT architecture** to MGR clip mixer; no game-runtime execution or import proof yet. |
| [Godot SkeletonProfile](https://docs.godotengine.org/en/stable/classes/class_skeletonprofile.html) | Canonical target virtual skeleton enables bone-mapping/retarget workflows | Official stable API docs reviewed | **ADAPT semantic mapping idea**, not an API dependency. |
| [Godot RetargetModifier3D](https://docs.godotengine.org/en/stable/classes/class_retargetmodifier3d.html) | Retarget modification is a distinct pass requiring target skeleton pose handling | Official stable API docs reviewed | **STUDY**; dynamic behavior untested. |
| [Godot 4.1 retargeting guide](https://docs.godotengine.org/en/4.1/tutorials/assets_pipeline/retargeting_3d_skeletons.html) | Bone paths, transform tracks and source/target skeleton mapping | Official older guide reviewed | **STUDY historical concepts**, do not treat 4.1 implementation details as current stable requirements. |
| [Unity humanoid Avatars manual](https://docs.unity3d.com/cn/2018.3/Manual/AvatarCreationandSetup.html) | Explicit humanoid bone correspondence is prerequisite for reusable retargeting and IK | Official but older manual reviewed | **STUDY approach**; Unity isn't an MGR native dependency; modern engine version requires verification. |
| [Unity Root Motion manual](https://docs.unity3d.com/kr/2018.3/Manual/RootMotion.html) | Separating root locomotion from body motion and foot IK goals | Official but older manual reviewed | **ADAPT contract**, not current API guarantee. |
| [Fairmotion repository](https://github.com/facebookresearch/fairmotion) | Mocap processing and visualization tools; possible format/kinematics reference | Public primary repository identified; source/tests/dependency/license revision **not** fully audited | **STUDY**, not vendored. GitHub visibility does not resolve motion dataset restrictions. |
| [OpenPose official repo](https://github.com/CMU-Perceptual-Computing-Lab/openpose) | Body/hand/face/foot keypoint pipeline, which can propose—but not prove—3D rig motion | Official README inspected; model/data licenses and GPU performance not reproduced | **STUDY ONLY**; official license statements indicate non-commercial terms and separate commercial licensing path. Do not import code/weights into commercial Forge without counsel/review. |
| [Velocity Skinning paper](https://arxiv.org/abs/2104.04934) | Research on using skeletal velocities to produce stylized secondary effects | Original research abstract inspected, no code/bench reproduction | **STUDY** optional artistic deformation; runtime claims are paper claims, not Forge measurements. |
| [PhysRig paper](https://arxiv.org/abs/2506.20936) | Differentiable/physics-based skinning to reduce limitations of linear skinning | Original research abstract inspected, no source audit | **STUDY** future volumetric mesh/skin tests; expensive solver practicality and licensing unknown. |
| [Skeleton prediction paper](https://arxiv.org/abs/1908.08506) | Automatic rig skeleton fitting to arbitrary mesh | Original paper abstract inspected, no training/reproduction | **STUDY** optional rig proposal model; training set provenance and geometry/generalization unknown. |

## Methodology and findings

**Verified at reading level:** skinned animation has explicit skeletal and vertex-weight representation; modern authoring/engine stacks distinguish bone rest structure, pose evaluation, skeleton mapping, animation state, interpolation and export. These independently support a semantic MGR Living Rig contract with export and physical-contact test receipts.

**Inference from sources:** automating one end-to-end pipeline is practical by composing Blender authoring, deterministic kinematics and export validation, but 100% accurate arbitrary auto-rigging, zero-GPU AI animation, believable clothing and universal retargeting are **not established**. A single generated image does not determine hidden geometry or contact; multi-view geometry checks are necessary.

**Research gaps explicitly open:** exact Blender 5.x installed API and export regression; valid skin/weight count limits per target runtime; USD import/export parity; modern Unity retargeting/current license; fairmotion license/dependency audit at selected commit; OpenPose permitted commercial path; real reference person consent; AMASS/Human3.6M/LaFAN1/CMU dataset commercial rights; CPU/GPU runtime data on user hardware; professional character/cloth/face evaluation.

## Licensing, compute and model risk register

1. A repo software license, model weight terms, pretraining dataset terms and sample asset terms are separate. Verify all four for each candidate before use. Fairmotion has no approved code-vendoring status here.
2. OpenPose should not be characterized as permissively reusable for commercial deployment based merely on repo access; treat commercial rights as unresolved.
3. Dataset owners and captured humans may have privacy/personality interests in motion data. Ensure lawful collection and documented consent, especially for recognizable figures or performances.
4. Video-to-mocap estimation can be CPU-only on tiny workloads but may be unacceptably slow; no measured benchmark or blanket GPU-free claim is warranted. Skeletal FK/constraints/weight validation are lower-demand than high-fidelity cloth or neural capture.
5. Retarget quality is not settled by matching bone names: rest-pose axes, differing proportions, joint twist, global/root motion, contact state and rig constraint topology all affect output.
6. Vendor/API pricing, subscription policies and Blender/engine plugin compatibility may change and must be reverified when selecting a paid or executable integration.

## Executable research follow-up

- Build two different-proportion rigs and one intentionally broken control fixture in installed Blender; assess rest matrix, hierarchy, influences and deformation via sampled animation.
- Export to GLB and USD and reimport independently; compare evaluated joint and vertex world positions for every canonical stress pose, and capture visual evidence.
- Create a minimal gait contact fixture with planted intervals; measure foot world velocity, penetration and loop closure; reject obvious clipping despite visually similar renders.
- Inspect plugin/repository licenses and version-lock checksums before adopting any mocap conversion library or pretrained model.
- Run the ten-clip MGR rehearsal suite at several fixed ticks and presentation FPS, recording actual processing cost and memory.

**Truth label:** sourced design; primary docs reviewed; no motion data downloaded, no models run, no third-party full-source audit, no target-engine tests performed in this S10 task.
