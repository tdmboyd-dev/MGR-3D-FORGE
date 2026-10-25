# Character GLB compatibility — standards evidence

Inspected 2026-10-25; research for F99, not a claim of ownership of glTF.

- Khronos, [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html): standard accessors include unsigned byte/short/int index types, VEC2 texture UVs, byte offsets/strides and optional sparse data. MGR intake now accepts uncompressed triangle geometry and validates actual index bounds; sparse data requires normalization rather than pretending support.
- Khronos, [glTF Sample Models](https://github.com/KhronosGroup/glTF-Sample-Models): sample `.glb` is a container for geometry, textures and materials. Individual sample licenses must be checked; no sample weights or assets were redistributed in this change.

Native design impact: use `forge/character_glb.py` for outside candidate intake, while preserving the older MGR-created-world contract validator for internally generated meshes. Do not infer human anatomy, deformability, owner-approved likeness or actual skinning from glTF metadata alone. The input validator is not a complete external glTF compliance certification or a replacement for Blender import, export and render acceptance. Future: sparse and compression normalization behind audited local decoders; large file streaming; vertex finite-coordinate checks, morph animation clip evaluation, and commercial reuse rights.
