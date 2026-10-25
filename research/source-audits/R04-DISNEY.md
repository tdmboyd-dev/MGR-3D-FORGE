# R04 — MGR Technical Source Audit: Artist Control, Cloth, Hair and Hybrid Animation

**Owner:** MGR · **Date:** 2026-10-25 · **Inspection depth:** Original public research summaries and several direct paper texts/pages from Disney Animation/Disney Research. Selective conceptual/algorithm study; **not** access to private studio source, a full solver implementation audit or a recreation of proprietary systems. Sources: `research/external-provenance/R03-R04-SOURCES.md`.

## 1. Native R&D premise

Production-quality 3D isn't just throwing polygons and GPUs at a shot. The cited research repeatedly balances physically defensible modeling with usable artist controls, stable time evolution, perceptually important details and reversible stylistic overrides. MGR should turn those principles into a **creative truth stack** that keeps the whole scene editable while allowing deliberate magic and distortion without ruining anatomy, contact, depth and continuity.

## 2. Technique audit

### D1 — Art-directed but physically plausible surfaces

**Primary finding:** Published Disney physically based shading introduced an artist-usable BRDF for production characters and environments.

**Technical approach:** Think microfacet specular reflectance plus separable artist-controlled diffuse/roughness/coat/sheen response subject to energetic and parameter bounds; exact functions and version must be recorded. Material appearance is a function of light direction, view direction and surface properties, not a static RGBA swatch.

**Limits:** “Disney principled” implementations vary across software releases; labels may match while lobe weights and coat/IOR differ. A pretty screenshot under one studio light cannot establish physically calibrated behavior.

**MGR verification:** parameter sweep on spheres (base color, metallic, roughness, coat, sheen, subsurface where available), 5 lights, 12 cameras, fixed OCIO and render samples. Compare with stable reference, measure angular energy trend and numerical image error.

### D2 — Hair with meaningful artist handles

**Primary finding:** Disney's artist-friendly hair-shader paper separated physically grounded scattering behavior from unintuitive parameters; a later practical controllable fiber-scattering paper described energy-conserving path-tracing lobes, near-field formulation, azimuthal roughness and high-order internal reflection consolidation.

**Technical approach:** Per-strand geometry direction and melanin/absorption influence fiber highlights and transmittance. A practical control layer translates desired perceived color, highlight shape and shine into bounded scattering terms. Test multiple illumination directions because highlight position depends on hair/fiber tangent.

**Limits:** Every groom is a dense interacting volume; performance and multiple scattering remain expensive. Hair that looks correct front-facing may fail backlight and profile view, especially after motion.

**MGR verification:** dark/light strand swatches with front/rim/backlights and spinning head, canonical scalp attachment, near-camera LOD and energy consistency in scene-linear EXR. Verify no fake hair sheets are mislabeled actual curves.

### D3 — Efficient cloth requires contact-aware numerical solving

**Primary finding:** The published smoothed-aggregation multigrid paper applies an algebraic preconditioner and contact-aware filtering to cloth solves, reporting 6–8× speedups for a specific fully dressed 371k-vertex study case. A later nonlinear multiscale cloth paper discusses recursive multilevel trust-region solving.

**Technical approach:** Cloth mechanics use stretch/shear/bend energy, mass, velocities and collision/contact constraints. Solve time-stepped nonlinear or linearized equations with stabilization, preconditioning and suitable contact handling. Spatial discretization/mesh variation and material anisotropy demand more than one fixed stiffness slider.

**Limits:** Reported speedups are benchmark-specific, not universal MGR promises. Ill-conditioned constraints, cloth self-intersection, fast motion and collision coupling are hard. Cheap skin-bound garments should not be labeled real simulation.

**MGR verification:** shirt, long coat, cape/skirt witnesses on turning/running/bending mannequin; separate mesh meshes, shoulder/armpit contact, self-collision, ground contact, exact body interpenetration count, timestep convergence, CPU time and failed solve recovery.

### D4 — Perceptual fabric truth is both image and motion

**Primary finding:** Disney's published cloth-perception experiment studies the relative roles of dynamics and material appearance. Another perceptual-control paper describes mapping controls toward human judgments while treating the underlying simulator as a black box.

**Technical approach:** Evaluate movement signatures (drape, swing damping, fold frequency, settling time) in tandem with fabric appearance (reflectance, texture, thickness and normal/bump scale). Introduce MGR-friendly handles—heavy/light, stiff/loose, silky/rough—with calibrated transformations into actual solver/render parameters.

**Limits:** No single observer score proves accurate fabric properties; perceptual mapping changes with lighting and shot. Constraints must not silently override garment fit or collision.

**MGR verification:** side-by-side garment motion on identical rigs under controlled material/lighting combinations; quantify fold silhouette, oscillation decay and self-contact, plus blind reviewer ranking; enforce separate simulation-vs-shader provenance.

### D5 — Combine 3D truth with 2D illustrative expression

**Primary finding:** Disney's Paperman technical talk/paper describes a 3D animated scene producing forward/backward motion fields which move artist-created vector strokes and paper textures through frames, preserving temporal coherence while the final line work remains directly artist-controlled.

**Technical approach:** Render object IDs, depth and motion vectors. Attach drawn lines to stable 3D features or vector-field flow; advect strokes and texture with occlusion-aware validity. Allow new drawn key poses; blend or replace expression while retaining 3D source geometry and camera trajectory.

**Limits:** At occlusions/disocclusions motion vectors are uncertain, and strokes may slide across surfaces or appear through backsides. Hybrid animation is a style layer, not proof of hidden real mesh.

**MGR verification:** line stroke on brows, garment seams and magical particle contour during 180° camera orbit and character spin; measure temporal jitter, object ID consistency, occlusion clipping and artist override retention.

### D6 — Hair/garments are their own production stages

**Primary finding:** Disney public production hair and modeling process descriptions explicitly separate groom construction, rigging/simulation control and animation/look-development collaboration. Motion can use a coarse animation rig plus layered simulation.

**Technical approach:** Canonical body topology remains separate from garment shell, cloth collision cage, hair scalp/curves, jewelry/accessories and their simulation/wind controls. A generation tool outputs semantically named objects and independent material/rig groups.

**Limits:** No clean separation can be inferred from a flat generated image; require explicit geometry files and object membership. Multi-layer physics can still intersect under extreme motion.

**MGR verification:** extract coat, shirt, pants, boots, hair, chains and rings from TEVIN as individual selectable objects, all visible in T-pose and 360° multi-pose witness. Test animation with outfit on/off and logged collisions.

## 3. MGR-native inventions derived from combined lessons

- **MGR Creative Physics Dial:** moves between locked physical truth and labeled deliberate fantasy while never hiding garment collision/identity errors.
- **MGR Cloth Personality:** creative, perceivable fabric descriptors transparently mapped to measured drape, fold and material response.
- **MGR Paint Beyond Matter:** independent, camera-aware line/paint/illusion layer linked to true world motion and visibility.
- **MGR Hair Dial:** high-level style controls backed by strand geometry and view-angle BSDF tests.
- **MGR Costume Anatomy Treaty:** body, garments, accessories, hair, collision proxies and skeleton remain independently editable with acceptance rules.
- **MGR Motion-Style Memory:** persistent custom expression lines/texture placements follow one actor through frames and camera changes.

## 4. Production contract sketch

```json
{
  "actor": "tevin", "canonical_model": "approved-id",
  "parts": {"body": "mesh", "skeleton": "rig", "shirt": "mesh", "coat": "mesh", "hair": "curves", "jewelry": ["chain", "rings"]},
  "cloth": {"solver": "documented", "physical_params": "recorded", "collision_witness": "pending"},
  "look": {"surface_model": "bounded-semantic", "hair_model": "fiber-semantic", "ocio": "locked"},
  "style": {"intent": "natural|fantasy", "stroke_motion_field": "optional", "real_geometry_unchanged": true},
  "proof": {"separation": "pending", "contact": "pending", "multi_pose": "pending", "temporal": "pending"}
}
```

## 5. Risks, licenses and research honesty

Papers and public process pages describe methods, **not** authorization to duplicate studio source, production models, fonts, shot data or characters. Verify independent library licenses and authored code. Avoid proprietary `Tonic`, `Presto`, `Meander` or internal simulation software copying. Numerical findings quoted from original research are restricted to the reported experiment configurations. This packet has not run an independent replication; evidence is conceptual/technical derivation and proposed acceptance, not completed implementation.

## 6. Build sequence and acceptance

1. Build independently selectable TEVIN body/garment/hair/jewelry contract and collision-aware pose witnesses.
2. Character material and strand angular-light evaluation under a common scene-linear workflow.
3. Cloth solver adapter with known garment/contact witness and deterministic time-step comparisons.
4. Cloth Personality user controls calibrated to solver variables while showing real fit/interpenetration alerts.
5. Paint Beyond Matter motion-vector/stroke mapping tied to depth/object IDs, tested against 360° cameras.
6. Fantasy director preset runs physical-truth validation before/after effects and preserves undoable layered provenance.

**Acceptance is not just a photo.** Deliver native editable separated objects, reproducible Blender test scene, camera sweep/animation sequence, raw depth/object/motion pass, cloth collision metrics and exported asset bundle that reimports with all component identities intact. Research: six techniques audited to selective public depth; runtime implementation and independent numerical reproduction remain open.
