# R03 — MGR Technical Source Audit: Subdivision, Scene Composition, Hair, Render Control

**Date:** 2026-10-25 · **Depth:** Public Pixar-originated primary papers, technical publication pages and OpenSubdiv/OpenUSD documentation inspected selectively. Not a complete RenderMan/Presto/internal-tool code audit, not evidence that MGR has implemented or licensed proprietary studio systems. Source bibliography and URLs are quarantined in `research/external-provenance/R03-R04-SOURCES.md`.

## 1. What is useful to MGR

We can derive a coherent technical pipeline from six public techniques: (1) feature-adaptive Catmull–Clark subdivision; (2) layered scene composition and variation; (3) physically grounded hair/fur light transport with importance sampling; (4) separate production material controls; (5) curve/groom stylization tied to character surface/animation; (6) camera-distance-aware render budgets. None requires copying Pixar's brand-specific proprietary implementation. The MGR-native synthesis is below.

## 2. Technique audit and scientific method

### P1 — Smooth surfaces that remain animatable

**Source insight:** Catmull–Clark subdivision refines coarse control topology into smooth surfaces, including nonquad and extraordinary-vertex cases, with feature-adaptive processing and CPU/GPU evaluation. The public feature-adaptive GPU paper describes evaluating the subdivision limit surface and adaptive subdivision of irregular regions.

**Technical kernel:** At regular quad regions, bicubic B-spline behavior; at extraordinary vertices, evaluate subdivision rules/eigenbasis or an approved library's exact limit functions. Adaptive tessellation uses camera-space projected edge/error, crease bounds and curvature rather than uniformly quadrupling every polygon. Topological boundary/crease rules are not optional.

**Constraints:** Subdivision does not fix bad base topology, ripped shoulders, missing hands or clothing/body intersections. More faces increase skinning, collision and memory costs; displacement must remain consistent with UV/normals.

**MGR tests:** a cube, quad sphere, mixed n-gon topology, extraordinary five-way vertex, sharp crease and UV seam; compare control-mesh→limit surface against reference to a measured geometric tolerance across rotations; measure CPU build time, memory and surface continuity. Test actual arm/hand deformation before calling a character film-ready.

### P2 — One canonical world with reversible asset composition

**Source insight:** OpenUSD composition can assemble layers, references, payloads, variants and overriding opinions without destructively changing referenced sources.

**Technical kernel:** A composed scene view resolves prim paths and property opinions across ordered composition arcs; weak/strong opinions must remain deterministically explainable. Time-sampled animation and sparse overrides allow changing one character outfit or material while retaining common base geometry.

**Constraints:** Incorrect layer strength, missing asset resolver paths and nonportable references create invisible conflicts. USD is richer than lightweight glTF but not automatically supported identically by every consuming engine.

**MGR tests:** compose base TEVIN rig + separate coat, shirt, boots, hair, chains + staged animation overrides; validate reference changes do not mutate base; replay layer order; detect dangling prim paths, duplicate units, missing textures and unapproved variants. Export to Blender and roundtrip with explicit known-loss report.

### P3 — Hair is a 3D light transport problem

**Source insight:** Pixar-authored hair publications investigate Marschner-type fiber scattering, multiple lobes, internal reflection and importance sampling to control path-tracing noise; dense hairstyles can contain millions of curves.

**Technical kernel:** Hair radiance is angle-dependent scattering along fiber direction, involving cuticle tilt, refractive interfaces and absorption. Sampling directions near high-probability lobes reduces variance; aggregate inter-fiber shadowing changes observed brightness/appearance. A simple flat color or sprite does not model this.

**Constraints:** Fiber-level curves, BVH/visibility and multi-bounce transport can dominate render time and memory. Light blond/white hair exposes missing multiple scattering. Artist-friendly controls require bounded physically interpretable parameterization.

**MGR tests:** locks of black, dark brown and platinum hair under frontal, rim and back lights; compare silhouette/transmittance/shine over 12 angles and multiple light conditions; measure sample variance, hair count and render cost; separately test pose-driven groom attachment to scalp.

### P4 — Material definitions must travel from viewport to final render

**Source insight:** Pixar's published foundation-material course describes surface and Marschner-hair categories for physically based production shading.

**Technical kernel:** The material contract separates albedo, roughness, normal/bump, coat, transmission, fiber melanin, strand width/density and medium properties; each property must have units/color-space provenance, limits and intended integration semantics. Compare angular response, not only front-view colors.

**Constraints:** Blender's Principled BSDF, custom game shaders and reference path tracers do not necessarily produce identical artistic appearances. Renderer-specific controls require a documented translation and error envelope.

**MGR tests:** standard material-ball set with same labeled parameters in preview and reference; lock exposure/OCIO; verify angular BRDF changes and texture channel interpretation; mark material mismatches rather than hiding them with compositor bloom.

### P5 — Groom expression and animator control

**Source insight:** Pixar's public hair-styling technical notes describe layered surface-aware curve deformation and varying levels of detail for animated expressive hair/fur.

**Technical kernel:** Groom strands are embedded/attached in deforming scalp-surface coordinates, allowing rest/pose transformation and animation-scoped offsets. Layered shape controls preserve base groom and permit reversible per-shot art direction.

**Constraints:** Per-shot edits risk drift from approved canonical character; skinning and clipping require collision/LOD checks. A strand screen projection is insufficient for turntable geometry.

**MGR tests:** head yaw/pitch and squash, hood-on/off, running and wind; compare scalp anchors, curve penetration and temporal jitter while varying groom LOD.

### P6 — Adapt rendering budgets to what the camera can see

**Source insight:** Published adaptive subdivision considers camera-distance/view-dependent tessellation and target-specific control of subdivision depth. Production global-illumination literature likewise highlights shader and sampling cost in complex scenes.

**Technical kernel:** Model per-object projected screen error and performance budget: refine near-camera silhouette and large-displacement surfaces, preserve coarser distant regions and avoid needless path samples where variance is already low.

**Constraints:** Discrete LOD popping, shadow silhouette changes, reflection visibility and screen-size metrics for VR stereo can invalidate naive camera-only selection.

**MGR tests:** travel camera from macro face to full plaza; enforce silhouette/normal error envelope, smooth LOD transitions, no missing far-shadow caster and bounded memory/time.

## 3. New MGR-native system features

- **MGR Infinite Skin:** reversible subdivision and adaptive detail tied to animation/camera truth.
- **MGR Layer Sovereignty:** one owner-approved character/world source with independent garment, groom, prop, animation and effect overlays; diff and rollback without overwriting canon.
- **MGR Fiber Soul:** physically meaningful fiber appearance married to a separate deformation/character identity system.
- **MGR Shader Treaty:** portable semantic material definition with measured renderer-specific translation errors.
- **MGR Shot Elasticity:** adaptive mesh/curve/shader/render cost with screen-error proof.
- **MGR Groom Memory:** hair shapes remain attached to canonical scalp geometry across expressions and poses.

## 4. Implementation contracts

```json
{
  "asset_id": "tevin", "base_revision": "owner-approved-hash",
  "composition": {"geometry": "base.usd", "overlays": ["shirt", "coat", "chains", "boots", "hair"], "opinion_trace": true},
  "surface": {"scheme": "catmull_clark", "crease_policy": "explicit", "screen_error_px": null},
  "hair": {"groom_id": "hair-01", "scalp_bind": "valid", "fiber_bsdf": "documented-semantic"},
  "render": {"material_translation_report": "required", "lod_witness": "required"},
  "proof": {"topology": "pending", "surface": "pending", "pose_clipping": "pending", "license": "pending"}
}
```

## 5. Legal/ethics/portability

Open-source standards/libraries may be usable under their own licenses; do not infer rights to Pixar film characters, production assets, proprietary rigging software, demos or reference scene content. A published article is not a code license. Verify exact OpenSubdiv/OpenUSD version's source, notices, dependencies and distribution obligations before vendoring. Preserve citation in external ledger but keep native features named for MGR. Technical derivations should be independently implemented and tested.

## 6. Build-first acceptance

**Scope researched:** six techniques mapped to math, constraints and tests; paper abstracts and selected detailed texts checked, not every code path. **Engineering not yet proven:** add reproducible mixed-topology subdivision witness; loss-aware layered outfit/groom composition; hair angular-light witness; material translation suite; motion-attached groom LOD; cross-camera frame-time QA. Require real `.blend`/USD files, golden image/depth/normal results and owner-approved export bundle before calling features complete.

**Priority:** Layer Sovereignty and Infinite Skin first because the user's exact challenge—separated clothing, complete fingers, preserved proportions under pose—depends on canonical editable asset ownership more urgently than photorealistic fur.
