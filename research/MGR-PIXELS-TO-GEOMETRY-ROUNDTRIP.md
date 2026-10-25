# MGR Native: Pixels-to-Geometry and Two-Way Blender Bridge

**Date:** 2026-10-25  
**Scope:** F95 pixel relief and F96 authored scene roundtrip. MGR-named contracts and source implementation are independently authored.

## 16-field research packet

1. **Definition:** Turn bounded source image pixels into an explicit depth field; separately preserve movable MGR buildings through native Blender and back.
2. **Production use:** Heightmap terrain and bas-relief manufacturing; DCC edits retargeted into game world scene documents.
3. **Standards:** W3C PNG third edition row filters, CRC chunks and alpha; Khronos glTF 2.0 mesh primitives; Blender 5.2 Python API; MGR world-edit JSON v1.
4. **Research:** Actual pixels constrain height at observed positions; monocular images do not uniquely determine occluded shapes. Distinguish 2.5D relief from image-to-object inference.
5. **Open implementations:** Blender source Python mesh/scene APIs and Khronos open glTF reference materials; internal `forge/geometry.py`/`forge/glb.py` reused.
6. **Models:** None required for deterministic relief; full 3D reconstruction remains open candidate track F92.
7. **Datasets:** Synthetic white/black/ramp PNG fixtures with all five row filters, actual multi-byte RGB/RGBA and adversarial corruption.
8. **Licensing:** Image copyright/identity rights belong to image owner; code is MGR-authored; external standards are research references, not copied implementation.
9. **APIs/providers:** None; CPU Python stdlib + owner's installed Blender.
10. **MGR-native alternative:** Decode PNG → luminance matrix → bounded 3D columns → GLB+OBJ+MTL receipt; extract Blender object transforms into strictly validated MGR JSON.
11. **Hardware:** Offline CPU, Python 3; optional Blender 5.2 Windows for independent native scene and import tests.
12. **Cost:** No paid inference or remote image upload. Geometry grows with square of grid cap and remains bounded at 48×48 cells.
13. **Failures:** CRC tamper, ZIP bombs, bad filters, huge dimensions, interlaced/indexed/16-bit PNG, topology edits beyond cuboids, rotated/ungrounded Blender objects, stale source SHA, overwritten outputs.
14. **Evaluation:** Pixel truth, deterministic checksums, GLB structural inspection, exported height range, Blender independent import/reopen, transformed object roundtrip.
15. **Placement:** F95 under `forge/image_relief.py`, F96 under `forge/blender_roundtrip.py`, Blender-only script under `bridge/`, exported manifests versioned.
16. **Acceptance:** User PNG produces real GLB inspected in Blender; Blender-edited building returns to Forge as a changed actual GLB; negative inputs rejected; Windows runtime receipts published.

## Current hard boundaries

- PNG accepted: **8-bit non-interlaced grayscale/RGB/RGBA**, with max 256×256 source and max 48×48 mesh samples. Indexed palette, 16-bit, interlace, animated PNG and JPEG require an authorized converter before use.
- Relief is a 2.5D depth extrusion, **not** realistic image-to-3D subject reconstruction or a generated backside. MGR must not label it Tevin likeness/mesh inference.
- Blender return contract currently supports distinct axis-aligned cuboid buildings only. Arbitrary geometry edits, sculpture, topology changes and object rotation must fail instead of silently corrupting world data.
- Advanced full image-to-3D needs evaluated models, image rights, multi-view identity, texture maps, topology, rigging, geometry QA and hardware budget.

Primary external technical references and source URLs are isolated in `research/external-provenance/MGR-PIXEL-RELIEF-STANDARDS.md`.

**Disposition:** MGR-NATIVE bounded relief/roundtrip, no source-code copying, future study for neural hidden-surface reconstruction.
