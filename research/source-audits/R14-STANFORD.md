# R14 — Stanford Computer Graphics Laboratory: MGR Space/Light Research Audit

**Date:** 2026-10-25 · **Depth:** Stanford Graphics Lab primary technical-paper abstracts/selected paper text, project descriptions and repository/dataset conditions. Not a complete paper archive/source-code review or dataset license grant. Source URLs and reuse caveats appear in `research/external-provenance/R13-R14-SOURCES.md`.

## Native verdict

The crucial lesson is **different representations of a 3D world prove different things**. Meshes give editable surfaces and collisions; captured light fields give image-based novel views over their sampled range; point splats can display massive scanned surfaces without conventional triangles; volume samples store density/light inside space. The best MGR architecture can visualize all of them while refusing to confuse a beautiful projected image with fully editable, navigable geometry.

## S1 — Light field rendering: reconstruct views by sampling rays

**Primary research:** Original Levoy–Hanrahan Light Field Rendering paper and university project archive.

**Math:** In free space, radiance traveling along a ray can be parameterized in a 4D two-plane coordinate scheme `L(s,t,u,v)` for position/direction (under stated assumptions). A new view samples/rebins recorded rays, with interpolation error dependent on capture density, occlusion and scene appearance.

**Constraints:** A light field does not automatically contain scene meshes, physics, back sides unseen by cameras or infinite camera freedom. Sparse camera arrays cause ghosting, doubled edges and extrapolation artifacts.

**MGR native:** **Ray Memory View**: retain observed view-dependent radiance separately from generated 3D mesh and hallucinated extrapolation. Director can compare image-based eye candy with actual geometric rendering.

**Proof:** Own Blender scene rendered from calibrated 5×5 camera grid. Interpolate central withheld view and test PSNR/SSIM plus silhouette/depth discontinuity errors; deliberately extrapolate beyond camera convex hull and flag unsupported region.

## S2 — Multiresolution point visualization at scale

**Primary research:** QSplat paper on multiresolution point rendering for very large meshes/scans.

**Math:** Spatial hierarchy over sample points/patch approximants; choose projected-size/visibility-dependent nodes, rendering a bounded number of point splats (or oriented discs) while preserving apparent shape. Error envelope is screen dependent and smooth LOD changes matter.

**Constraints:** A point cloud lacks robust watertight surface and physical contact by default. Thin gaps may disappear, point normals can be noisy, transparent objects may be absent and some input model datasets have restricted reuse.

**MGR native:** **Infinity Surface Budget**: allow enormous worlds/photogrammetry point assets to be explored with progressive LOD while explicitly labeling them non-collision surfaces until meshed.

**Proof:** MGR-owned sampled sphere, stepped terrain and building facade point clouds; compare silhouette pixel error and frame-time/memory across camera distance; verify near-surface holes and require explicit collision proxy provenance.

## S3 — Direct volume rendering instead of fake exterior shells

**Primary research:** Stanford volume rendering technical project and Marc Levoy's early research on rendering 3D scalar fields.

**Math:** Along ray `r(t)`, accumulated transmission follows `T(t)=exp(-∫₀ᵗ σ_t(r(s))ds)` under standard extinction model, with emitted/scattered contributions integrated along ray. In discretized ray marching, `T≈∏_i exp(-σ_i Δt_i)`; sampling step and transfer function drive quality.

**Constraints:** Scalar volume data may depict fog, smoke, medical measurements or implicit material—not necessarily solid geometry. Transfer functions, sampling steps and ray errors can fabricate or hide structure. High-res 3D grids consume large memory.

**MGR native:** **Inside Matter Vision**: expose editable depth into magic, smoke, storms and energy fields while keeping separate emission, density, scattering, temperature/art-direction channels.

**Proof:** constant-density box with analytic Beer–Lambert attenuation; concentric density volumes, lights and camera-angle sweep; compare transmittance numeric truth and ray-step convergence with scene-linear EXR. Never infer a watertight physical object from volumetric appearance.

## S4 — Measured scanning and geometry reconstruction

**Primary resource:** Stanford 3D Scanning Repository/Stanford Bunny material, with research-use condition.

**Math:** Input 3D samples `p_i`, normals `n_i` and camera scans approximate a surface. Mesh reconstruction from noisy point clouds needs registration, normal orientation, outlier rejection and topology choices; nearest-surface Hausdorff/Chamfer distance gives a geometric comparison but does not certify semantics/rigging.

**Constraints:** Scans can miss occluded surfaces, contain range noise and reflectance artifacts, and are not automatically animation-ready; old benchmark datasets may be research-only. Do not vendor Stanford Bunny into commercial Forge without permission review.

**MGR native:** **Scan Honesty Inspector**: separately display measured points, reconstructed mesh and unresolved gaps; attach confidence heat map and cleanup queue.

**Proof:** scan synthetically rendered primitive from limited camera arcs; compare point coverage, hole fraction, Chamfer distance and topology; verify moving rig/bind-pose asset remains a separate production phase.

## S5 — Realistic rendering of materials as measured light interaction

**Primary resource:** Stanford Graphics Lab rendering research program documenting material appearances, scattering models, lighting and hardware acceleration.

**Math:** The rendering equation `L_o = L_e + ∫ f_r L_i |n·ω_i| dω_i` provides a design target; measured image fitting is underdetermined across unknown lights, material and shape unless reference conditions are constrained. Microfacet and volumetric models require separate tests.

**Constraints:** Research focus statements alone do not prove an independently executable specific shader. A gorgeous photographic material on an uncalibrated monitor is not reflectance measurement.

**MGR native:** **Light-Matter Crosscheck**: reference capture + render under locked lights/color to identify whether discrepancies stem from shape, material, lighting or camera.

**Proof:** Lambertian and metallic spheres plus roughness sweep and neutral gray card in Blender; compare sphere normals and scene-linear radiance trends over view/light angle; fail if color transform metadata changes or specular energy is unconstrained.

## Representation-first MGR contract

```json
{
  "asset_id": "mgr-spatial-asset",
  "representation": "mesh|points|volume|light_field",
  "observed": {"camera_coverage": "known|unknown", "source_hash": "sha256:..."},
  "capabilities": {"novel_view": "bounded", "collision": false, "editable_geometry": false},
  "uncertainty": {"unobserved_mask": "required", "confidence": "method-specific"},
  "proof": {"geometry": "pending", "image": "pending", "performance": "pending", "license": "pending"}
}
```

## Practical R14 acceptance route

1. Produce owned multi-camera radiance/light-field witness with one withheld view and hidden rear surface.
2. Build point-LOD witness with screen-error and time/memory budget.
3. Build analytic constant-density volume proof with numerical transmittance.
4. Reconstruct owned synthetic scan with explicit missing-face/coverage metrics.
5. Connect S02/07 renderer-light proof to representation-specific metadata, display **unsupported capabilities** as such.

**Licensing/source discipline:** Stanford archives are research/education sources. The scanning repository explicitly welcomes research use, which does **not** automatically authorize commercial redistribution. Some historical software has custom license terms. Read original agreements and the exact asset provenance before any vendor inclusion. Academic published methods can motivate independent implementations; model/photograph downloads and original source code need their own authorization.

**Completion state:** Five research techniques documented with equations and tests. No local implementation benchmark, complete paper-source audit or commercial dataset authorization is claimed.
