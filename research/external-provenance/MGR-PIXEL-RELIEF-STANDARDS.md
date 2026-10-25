# External Technical Provenance — Pixel Relief and Blender Scene Export

2026-10-25. This file is the external-standards trace, not the public-facing MGR capability naming.

- **W3C PNG Third Edition** — https://www.w3.org/TR/png-3/ . Official PNG row filtering, CRC chunks, alpha/color formats. MGR parser deliberately supports a constrained 8-bit subset; broad PNG compatibility is not claimed.
- **Khronos glTF 2.0 specification** — https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc . Material and triangulated mesh interchange expectations; exported GLB independently inspected with existing MGR parser.
- **Blender Python API** — https://docs.blender.org/api/current/ . Native object transform, material and save APIs. Version-specific runtime differences must be checked against Windows Blender 5.2.2.

**Status:** official documentation reviewed at the targeted interfaces; no claim to have read each full standards/source tree. No proprietary assets, leaked source or paid model weights included. **Disposition:** STUDY technical semantics → implement MGR-NATIVE contracts.
