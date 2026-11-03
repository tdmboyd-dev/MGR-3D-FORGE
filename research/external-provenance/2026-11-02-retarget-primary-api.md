# Retarget implementation research — primary API and exact runtime

This research informs an original bounded native motion-transfer design. It is not an installed third-party retarget engine or evidence of arbitrary skeleton recognition.

## Sources and limits

- [Blender 5.2 PoseBone reference](https://docs.blender.org/api/5.2/bpy.types.PoseBone.html): indexed official documentation distinguishes the final armature-space pose matrix from the local rotation/translation/scale basis relative to parent/rest state. The full-page web fetch returned HTTP 402 in this tool; only indexed excerpts were available through that route.
- [Blender 5.2 glTF import operator reference](https://docs.blender.org/api/5.2/bpy.ops.import_scene.html): indexed official documentation describes the Blender round-trip bone heuristic and warns that glTF can split vertices at discontinuous normals/UVs. Vertex counts alone therefore do not establish lost topology across an interchange round trip.
- [Blender Bone API reference](https://docs.blender.org/api/5.0/bpy.types.Bone.html): the earlier stable official API describes parent-aware conversion between local/basis and pose matrices using explicit rest/parent matrices. This earlier page is supporting context; exact 5.2.2 runtime behavior below controls execution.
- [Blender glTF export operator reference](https://docs.blender.org/api/5.0/bpy.ops.export_scene.html): earlier official API describes separate rest-pose/current-frame and influence export settings. These are checked in the actual target runtime below rather than assumed from a different version.

## Actual runtime probe

Executed the local `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe` in a separate background process with a disposable, original two-bone armature. `artifacts/retarget-api-probe-20261102/probe.py` and its JSON/log preserve the probe. Result: `ACTUAL_BLENDER_52_RETARGET_API_PROBE_PASS`, Blender **5.2.2 LTS**.

The probe constructed a rotated desired child pose, converted it to local basis with explicit parent/rest matrices, converted it back and measured a maximum matrix-element error of **5.960464477539063e-08**. Actual glTF operator RNA confirms rest-position export, current-frame export, skin/animation export, influence-count/all-influence and animation-splitting controls. This proves those specific local API contracts, not the later full retarget pipeline.

## Native design derived from those contracts

Use explicit caller-authored bone correspondence and two original skinned GLBs. Compute each source bone's world-space rotation change from its original bind rest; apply that change to the mapped target rest orientation. Solve target local rotations in parent-first order using the target's rest hierarchy, preserving its bone translations and lengths. Bake a bounded in-place clip at declared FPS, keeping the source/target originals and source hashes in a new output revision.

This design deliberately starts with explicit maps and in-place rotation transfer. It does not infer anatomy, root travel, foot contacts, IK, cross-topology skin weights or original rig constraints. Unsupported scale/shear/translation semantics and ambiguous source clips must refuse or remain an explicit caller-selected limitation. A second process must independently import the derived GLB, evaluate target mesh deformation and compare actual sampled target orientations/rest topology/material/UV facts. Creator-side quaternion arithmetic or an action inventory alone cannot count as a working receiving rig.
