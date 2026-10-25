# Technical provenance: material parameters and mixed-bone skin weights

Inspected 2026-10-25. This file is a technical-source ledger; the public MGR
capability names, source of truth and acceptance contracts are native.

## Geometry/material portability

- Khronos glTF 2.0 specification, materials section:
  https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Directly supported native design: standard glTF metallic/roughness/baseColor
  scalar and vector parameters, with numeric range checks and round-trip socket QA.
- Unresolved: texture color spaces, texture image rights, alpha modes, normal
  maps, ORM texture packing, transmission and external engine rendering variance.
- Disposition: MGR-native authored recipes using the public open interchange
  standard. No source implementation copied.

## Deformation weights

- Blender Manual, Using Vertex Groups:
  https://docs.blender.org/manual/en/latest/sculpt_paint/weight_paint/usage.html
- Verified concept: a mesh can have bone-associated vertex groups with painted
  or numerically assigned influences. MGR currently computes blended weights
  for tiny detached elbow sleeve proxies; full-body smooth deformation is open.
- Unresolved: topology and continuity of real character elbows/knees, automatic
  skinning of non-manifold clothing, weight normalization after export and import.
- Disposition: MGR-native weighting behavior behind its Blender bridge;
  production model acceptance still requires actual imported/posed evidence.

## Compute and quality boundary

- MGR CPU procedural mesh and glTF values do not require neural inference.
- MGR cinematic materialization renders a small CPU Cycles preview for evidence,
  not a Hollywood-quality benchmark.
- License: no external code/models/texture assets imported in this implementation.
