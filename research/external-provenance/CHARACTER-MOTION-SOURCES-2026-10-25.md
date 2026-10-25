# Character motion exchange — primary-source research 2026-10-25

- Blender Python export operator (documented `export_animations`, `export_skins`, frame range, forced sampling and GLB): https://docs.blender.org/api/5.1/bpy.ops.export_scene.html — **ADAPT** for controlled Blender 5.2 exporting, version-specific live acceptance still gated.
- Khronos glTF 2.0.1 specification (animation channels, samplers and skin joints): https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html — **ADAPT** acceptance of actual skeleton, skinned geometry and motion tracks in an independent receiving import.
- Original MGR implementation: `bridge/blender_motion_export.py` and `bridge/blender_motion_reimport.py`, not copied third-party code.

Scope and proof: official documented APIs examined; not exhaustive engine-source research. Blender runtime and receiving-engine validation still required. Source mannequin does not represent Tevin's approved likeness.
