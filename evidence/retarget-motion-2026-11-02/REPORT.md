# Original mapped cross-skeleton motion transfer

Forge previously offered authored rig creation, procedural pose tracks and independent deformation checks. It had no native operation transferring an existing animation to a different original skin. `forge/retarget_motion.py` now creates a source-bound local revision from two original skinned GLBs and an explicit bone map. It retains both original files intact and produces a new editable Blender scene, animated GLB, receiving receipt and same-camera before/after renders.

The creator samples source bone orientation changes from the original bind rest. It applies those world-space rotation changes to mapped target rest orientations and solves target local rotations parent-first, retaining target joint translations and scales. Unmapped target bones remain in their own rest relationship and can inherit their mapped parent's motion. Neither skeleton recognition nor root translation is inferred.

The separate receiver imports the original source clip, original target and derived target GLB afresh. It measures target orientation changes against the source animation independently at every requested frame; tests actual evaluated mesh vertex displacement; compares target bind hierarchy, positions, orientations and lengths; and checks triangle-corner rest positions, oriented triangle topology, UVs, skin influences, material assignments and observed embedded-image pixels. It compares measured receiving data with the original, without using the creator's claim of movement as its own proof.

## Executed proof

```
python -m unittest tests.test_retarget_motion -v
python scripts/verify_retarget_motion.py --out artifacts/retarget-motion-verification-20261102
```

Five focused tests passed. They verify source/target byte identities, exact map schema, explicit parent correspondence, bone names, unsupported settings, hierarchy cycles, invalid weights/joint indices/nonfinite animation values, rejection of a previously animated target, no-allocation preflight failures, missing Blender and overwrite protection.

The real verification returned `ACTUAL_MAPPED_CROSS_SKELETON_RETARGET_PASS`. It creates an original two-bone animated source and a differently named, longer, differently rolled/angled three-bone original target. The target includes an extra unmapped counterweight branch, three named skinned parts, mixed weights, authored UVs/materials and an original embedded 8×8 PNG. There is no external asset, downloaded model or paid operation. This is an owned engineering fixture, not production character art.

- Blender 5.2.2 LTS, 16 frames at 24 FPS, two mapped bones onto a three-bone target.
- 72 evaluated receiving vertices, all 72 move at the peak. Maximum measured deformation: **0.8533837 m** at frame 16.
- Maximum receiving source-to-target orientation error: **0.00069054 rad** (about 0.0396°). Maximum bind-bone length error: **0.000000298 m**.
- The original target's three parts, 36 triangles, material assignments, UV corner coordinates, mixed skin influences and decoded embedded-image pixels match the receiving artifact.
- Derived 12,720-byte GLB SHA-256: `a540d65cda640ef7233433bef0e49856b419c8537fe4906fed0b5d669237a715`.
- Final strict native source reran original-input preflight and the actual creator, reproducing **exactly** the independently imported GLB bytes above.
- A deliberately frozen derivative retains valid skeleton/skin/action inventories but replaces all animated rotation samples with the first value. Its distinct hash is supplied to the separate receiving process. That receiver explicitly refuses the frozen file because mapped rotations no longer match the original source motion; it creates no acceptance receipt.

The two actual CPU Cycles preview images were opened and inspected. The target's colored/textured parts visibly change pose at the peak; the original stylized rectangular joint proxies remain a simple motion witness. Exact safe JSON receipts, actual before/after PNGs, focused test log and source hashes are retained here. Raw GLBs, `.blend` and local process logs stay in the ignored artifact directory. Research API evidence is separately recorded under external provenance.

## Explicit support boundary

This is in-place, manually mapped skeletal rotation transfer for one source clip. Supply two caller-owned, self-contained standard GLBs with one valid skin each, a neutral target with no existing clip, and explicit corresponding named bones. Source motion that requires bone translation/scale or incompatible mapped parents refuses. Input limits include 24 MB per original, 128 joints per rig, 120,000 vertices, 180,000 triangles, 2–240 sampled frames at 12–60 FPS, up to eight original normalized influences and bounded embedded PNG textures. Unsupported extensions, external images/buffers, existing morph targets, ambiguous clips, reflected or sheared transforms and unsupported image types refuse. The source's selected sampling range must exist after importing at the declared FPS.

The editable `.blend` and animated GLB are a new target revision. No earlier source, target or result is overwritten. This path does not provide inferred skeleton names, IK, foot plants, root travel, cloth, constraint transfer, blend shape retargeting, clip merging, general production character quality or receiving game-engine acceptance. The measured rest/UV/skin/material signatures describe the verified round-trip subset; they do not establish arbitrary shader-graph fidelity. Owner art acceptance remains false.
