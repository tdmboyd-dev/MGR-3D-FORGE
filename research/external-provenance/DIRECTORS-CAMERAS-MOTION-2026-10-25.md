# Technical sources — director / camera / motion

Inspected 2026-10-25. External sources here support original MGR-native
contracts; they are **not** MGR feature names or an instruction to clone them.

- Blender 5.2 LTS camera behavior, lens and DOF:
  https://docs.blender.org/manual/en/latest/render/cameras.html
- Blender 5.2 LTS animation editors, Action, NLA and F-Curves:
  https://docs.blender.org/manual/en/latest/animation/animation_editors.html
- Blender 5.2 LTS follow path for camera motion:
  https://docs.blender.org/manual/en/latest/animation/constraints/relationship/follow_path.html
- Blender timeline markers and camera binding:
  https://docs.blender.org/manual/en/5.4/animation/markers.html
  (API verified separately against user's actual Blender 5.2.2 runtime).
- OpenUSD time-sampled transforms and animation layering:
  https://openusd.org/release/tut_xforms.html
- Unreal official cinematic sequence model, for cross-engine comparison:
  https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematics-and-sequencer
- Khronos glTF 2.0 animation/camera/PBR standard:
  https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

Current disposition: **STUDY** timelines, animation layers, camera constraints
and interchange semantics; **MGR-NATIVE** shot/cut/motion contracts. No
third-party scene, motion clip, licensed asset, source file or code copied.

Still to research end to end before advanced implementation: focal length
versus camera sensor/lens distortion; constraint priority and interpolation
in current Blender; USD schemas for complex animation; glTF animation
roundtrips; game-engine camera blending; physically grounded actor locomotion;
rendered/multimodal temporal QA and viewer performance.
