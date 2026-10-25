# Character readiness technical provenance — 2026-10-25

- Khronos glTF 2.0 standard: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html — skin joints reference nodes; inverse-bind matrices are float MAT4 with accessor count **at least** the joint count; JOINTS_n and WEIGHTS_n drive skinning. **ADAPT** for native structural evidence, not deforming quality certification.
- Blender Python import API: https://docs.blender.org/api/main/bpy.ops.import_scene.html — fixed `bpy.ops.import_scene.gltf` import and documented import options. **ADAPT** into controlled import, not arbitrary remote code execution.
- Blender Object API: https://docs.blender.org/api/5.1/bpy.types.Object.html — `material_slots`, modifiers, vertex groups and mesh/object properties. **ADAPT** into per-object Blender intake receipt.

These are scoped primary-source excerpts inspected for this implementation, **not** full Blender or Khronos codebase research. Live modified-script Blender proof, animated skin deformation, semantic clothing/hair separation and owner-approved likeness remain open.
