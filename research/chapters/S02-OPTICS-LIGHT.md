# S02 — MGR Light Reality: Optics, Radiometry and Camera Truth

**Owner:** MGR · **Research date:** 2026-10-25 · **Capability family:** S02 Optics and Light / F51 Light Sculptor / F52 Shadow Intelligence / F59 Shader Alchemist / F62 Color Master.  
**Research lifecycle:** SOURCED → primary technical chapters reviewed → scoped research packet. **NOT end-to-end audited for all underlying renderer/source modules, NOT a validated photometric engine, NOT production-complete.** Source URLs and licensing notes live only in `research/external-provenance/S02-OPTICS-SOURCES.md`.

## Native verdict

MGR's next quality jump should come from treating a shot as a **measurable light experiment**: known 3D geometry and scale → known light configuration → known material → known calibrated camera → scene-linear render → intended output transform → a reproducible comparison and diagnosis. A pretty frame alone cannot distinguish correct illumination from exposure compensation, emission, post-production glare or an incorrectly placed source. The engine needs **counterfactual controls**: light ON vs OFF, blocked vs unblocked, near vs far, smooth vs rough, refractive vs opaque and linear vs display-encoded pixels.

The physically based rendering abstraction describes outgoing radiance as emitted radiance plus incident radiance integrated over directions, weighted by a surface-scattering model and the surface normal. This provides a structure for what Forge can test; an arbitrary emissive color or bright image overlay does **not** demonstrate global illumination.

## 1 — Definition and boundaries

1. **Geometric optics:** rays, pinhole projections, reflection/refraction, thin lens approximations and view-dependent occlusion.
2. **Radiometry:** radiant flux (W), intensity (W/sr), irradiance (W/m²), radiance (W/(m²·sr)), spectral power and light transport. Do not conflate actual fixture electrical draw with optical radiant output.
3. **Surface scattering:** BRDF reflection, BTDF transmission and BSDF umbrella; surface-normal and Fresnel effects; metallic/dielectric response and microfacet roughness.
4. **Participating media:** absorption, scattering, phase anisotropy, extinction and volume integration; distinct from image-space bloom.
5. **Sensor/display pipeline:** exposure, film/sensor response, white balance, noise, lens distortion, view transform, gamut and tone mapping.
6. **Artistic controls:** motivated lighting, key/fill/rim, fog mood, lens flare and illusion deliberately diverge from measured physics. Preserve **ART-DIRECTED** labels rather than calling everything **PHYSICALLY-MEASURED**.

## 2 — How production uses it

VFX pipelines render surfaces/volumes as scene-linear light values, layer physical and artistic passes, transform images through a documented display color pipeline, and evaluate both perceptually and against measured references where available. Film shots frequently use artistic cheats deliberately; correctness means those cheats are explicit, stable across shots and do not masquerade as verified measurements. Game engines use reduced-budget approximations, temporal reuse and virtualized/shadow buffers, then evaluate quality at target frame time.

## 3 — Standards and protocols

- International System of Units: distinguish meters, radiant watts, photometric lux/lumens, camera focal millimeters and angles; declare unit domain per field.
- glTF 2.0 metallic/roughness/normal/emission interchange as baseline, with explicit receiving-renderer tests and color space mappings.
- OpenColorIO / ACES scene-referred color management as a candidate transport/display contract; do not hard-code a particular ACES config into every scene.
- Camera calibration uses intrinsics, extrinsics and distortion parameters; orthographic cameras must be labeled as such because they do not prove perspective-depth or thin-lens behavior.
- Radiometric energy conservativeness and plausible Fresnel trends are physical quality gates, with accepted approximation tolerances.

## 4 — Top theory and published research

- Rendering/transport integral and Monte Carlo sampling methods from modern physically based rendering references.
- Microfacet reflectance, Fresnel and geometric masking/shadowing formulations for glossy materials.
- Surface appearance BRDF workflow in feature-film physically based shading literature.
- Thin-lens and realistic multi-element lens simulation; vignetting/barrel/pincushion distortion and finite-aperture depth of field.
- Volume equation of transfer: extinction, scattering/emission, light-path sampling and noise/variance tradeoffs.

**Research gap:** Compare production alternatives beyond official chapters—temporal denoising, path guiding, spectral vs RGB workflows, polarized light and glass caustics—using exact reference scenes and error metrics; these have not been read end-to-end here.

## 5 — Relevant open implementations

| Candidate | What to study | Deployment role | Evidence |
|---|---|---|---|
| `pbrt-v4` | Source-defined physically based reflection, camera and light transport; compact reference scenes | Independent CPU/GPU reference renderer candidate, not a runtime dependency now | Official book deep chapters reviewed; source tree **not** audited/build-tested |
| Blender Cycles | Scene shader nodes, light units/radius, light-path budgets and material/volume output | Existing authorized Windows 5.2.2 test renderer | Native MGR portal/light witness actually rendered; calibrated light tests not yet implemented |
| OpenColorIO | Encoding/view/display transforms and reproducible color configs | Replaceable color pipeline contract, not proprietary MGR identity | Official framework/concepts inspected; install not tested |
| Disney published BRDF notes | Artistic parameterization of principled physical materials | Conceptual study | Public course notes, no code copied |

Avoid adding yet another render engine to Forge's package set merely to appear sophisticated. First create comparison fixtures and verify outputs independently.

## 6 — Models

Analytic models first: Lambert diffuse, dielectric Fresnel, GGX-style microfacet, thin lens, pinhole, homogeneous medium, controlled light-source geometry. Later candidate learned reflectance/inverse-rendering and neural denoisers should be assessed behind isolated providers and **must not overwrite physical measurement labels**. No learned optics checkpoint has been admitted to MGR.

## 7 — Datasets and reference scenes

- MGR-authored synthetic controlled calibration suite is the immediately usable test data: gray card, white sphere, diffuse cube, rough/metallic spheres, glass slab/ball, shadow blocker, distance/radius light panel, lens grid and colored fog witness. Own the synthetic ground truth and record source units.
- MERL BRDF measured reflectance database is useful for research but upstream says **research and academic use only**; **do not bundle commercially** without separate clearance.
- Public pbrt example scenes and high-quality HDRI/photometric lighting can inform benchmarks only after per-asset licensing, download/version/hash and commercial rights audit. No third-party dataset is imported by this research packet.

## 8 — Licensing

Check exact release/commit text before any source vendoring: modern PBRT source declarations identify Apache-2.0 in files; OpenColorIO's current upstream states BSD-3-Clause; Blender/Cycles remains under Blender's GPL ecosystem, requiring attention if copying source rather than using Blender as an external tool. Public academic notes are not a blanket code/data license. MERL measured BRDF dataset is restricted to academic/research use. **Current native MGR code is independently authored; no external implementation or dataset is copied.**

## 9 — Commercial APIs / providers

Rendering may use existing local Blender, future licensed software through replaceable bridges, or rented compute only after explicit budget approval. Image-generation APIs can suggest mood boards but cannot substantiate light-transport correctness; no paid provider is needed for the proposed baseline tests.

## 10 — Original MGR architecture (S02 synthesis)

Introduce a typed **MGR Light Reality Contract**:

```text
LightSource { kind, position_m, orientation, radiant_power_W?,
              RGB_or_spectrum, emitter_radius_m, casts_shadow, source_type }
SurfaceWitness { id, geometry_hash, transform_m, material_hash,
                 expected_observation, visibility_confidence }
CameraWitness { projection, focal_px_or_mm, sensor_mm, aperture,
                pose, exposure, distortion, color_pipeline_id }
LightExperiment { baseline_scene_hash, single_variable_delta, fixed_seed,
                  renderer_version, light_paths, sample_count, output_passes }
LightProof { scene_linear_measurements, display_render_hash,
             contrast/change thresholds, uncertainty, verdict }
```

Separation rules:

1. A material's **emissive shader factor** is not equivalent to physically illuminating a witness; require the witness/null-control test.
2. A compositor `Fog Glow` is image-space optics; it may make a pixel brighter without actual fog/light scattering. Measure it separately from a real volume.
3. A light's numeric **energy** should be recorded with renderer/version and interpretation, not relabeled “real-world calibrated photometric power” until cross-calibrated.
4. Always record exposure, view transform, tone curve, working color space and output encoding; no pixel comparison is meaningful if transforms differ.
5. A declared contact/volumetric shadow should require blocked-vs-open illumination evidence and threshold, not merely a node or shader name.

The contract should be renderer-independent and portable across Blender/target runtime; only adapters translate it to engine APIs.

## 11 — Hardware/runtime

- CPU: adequate for tiny reference scenes and bounded path-tracing regression renders, as proven by current MGR Windows Blender Cycles receipts. Noise decreases slowly with more stochastic samples; benchmark sample/time/quality.
- GPU: useful for interactive high-res and many shadows, especially real-time console worlds; selection subject to feature availability, VRAM and licensing/driver checks.
- Color-managed EXR/linear data requires more storage/bandwidth than 8-bit previews; use capped fixture resolution first, preserve receipts and avoid creating giant archives.
- Deterministic seed, fixed camera/material/light and render settings necessary for valid A/B evidence.

## 12 — Cost gates

Record per experiment: CPU/GPU seconds, samples per pixel, memory, image dimensions, output bytes, quality delta, cache time and external dollars (should be zero for owner machine tests). A speed or quality claim requires comparable scenes and thresholds. Do not extrapolate “10× faster” from one low-sample preview.

## 13 — Failure modes and adversarial examples

| Failure | Consequence | Required guard |
|---|---|---|
| Wrong dimensions or non-unit scale | Intensity/distance behavior meaningless | Unit conversion, bounds and witness separation checks |
| Emission mistaken for light | Asset looks bright but nearby objects dark | Remove point lights, compare witness and shadow mask |
| Tone mapping/exposure shifts | Pixel MAE looks like lighting change | Lock scene-linear AOV and display transform; compare both |
| Inverted normals/negative scale | Shadows/reflections wrong or invisible | Geometry/normals check before material QA |
| Inverse-square near singular light | Extreme clipping/fireflies | Min-distance and bounded light radius/energy |
| Wrong metallic/roughness ranges | Unphysical reflection response | Existing MGR PBR validator plus on-render test |
| Glass/refraction incorrectly modeled | Silhouette warps and fake portal depth | Controlled normal incidence and oblique-angle witness |
| Orthographic camera used for depth QA | Missing perspective cue concealed | Explicit camera projection type and calibrated perspective fixture |
| Noisy low-sample path tracing | False pass/fail changes | Replicate seeds/samples, report variance and threshold sensitivity |
| Camera lens distortion unrecorded | Incorrect world-space inference | Calibration reprojection test, metadata provenance |
| Fog glow confused with atmosphere | “Volume” appears absent when glare disabled | Separate compositor ON/OFF from volume ON/OFF experiments |
| Color space drift between outputs | False apparent material change | Immutable OCIO config digest, scene/display encodings |

## 14 — Quantitative evaluation

For controlled fixtures use:

1. **Null-source test:** hold camera/material/exposure fixed; source ON and OFF. Compare a matte witness in a bounded pixel ROI and verify direction/sign of radiance change.
2. **Light-distance test:** measure a point-light-facing patch at distances d and 2d; after ambient subtraction and far-field approximation the direct contribution should trend toward 1/4, with tolerance for finite emitter and renderer specifics. Do not require exact inverse square near the source.
3. **Area/radius softness test:** enlarge emitter radius at fixed flux/geometry; contact-edge transition width should not shrink unexpectedly.
4. **Occlusion/shadow test:** insert known blocker on light-to-target path, verify reduced direct light, preserve ambient/indirect caveats.
5. **BRDF test:** diffuse/rough/glossy/metallic sphere series under fixed light; evaluate highlight spread, Fresnel view-angle trend and normal response.
6. **Transmission test:** camera rays through known glass/transparent plate with analytic Snell trend; screen-space distortions from a shader alone do not pass.
7. **Lens calibration:** synthetic checkerboard with known intrinsics/extrinsics/distortion; reprojection RMSE and FOV must meet a declared tolerance. Do not treat one reference photo as calibrated.
8. **Color pipeline:** render linear float pass and transformed PNG; verify config/version/exposure metadata and independent pixel math in the right domain.
9. **Volume test:** real participating medium vs zero density, `Fog Glow` held constant; compare brightness/attenuation and particle/witness visibility by ROI with known geometry.
10. **Repeatability:** same scene/build hash and seed returns within declared sampling variance. Evaluate both CPU-only and chosen target real-time engine when accessible.

## 15 — Placement and dependencies

Primary source of truth: `docs/MGR-NATIVE-CANON.md` → `docs/BUILD-REGISTER.md`. Candidate modules:

- `forge/light_contracts.py` (future): typed SI units, intent tags and source boundaries;
- `forge/light_guardian.py` (future): null/distance/blocker/roughness controlled measurements;
- `bridge/blender_light_probe.py` (future): Cycles scene execution and render-layer/AOV receipts;
- `forge/visualqa.py` (existing): deterministic PNG pixel comparator, not yet scene-linear lighting correctness;
- `bridge/blender_fx_render.py` (existing): two point lights, matte witness, Fog Glow, bounded atmosphere; currently a stylized render proof, not photometrically calibrated;
- `forge/materials.py` (existing): validates portable metallic/roughness factor bounds, no full texture/material reciprocity test;
- `docs/BUILD-REGISTER.md` tracks F51/F52/F59/F62 with scoped acceptance only.

## 16 — Definition of acceptance before declaring S02 researched/implemented

**Research gate:** source manifests and meaningful source modules for selected pbrt/Blender/OCIO paths inspected end-to-end, exact licensing checked, competing renderer/illumination approaches compared for our target use cases, current version bindings fixed. This gate remains OPEN.

**Implementation gate:** the first six physical tests and camera/color checks are implemented as bounded executable regression fixtures; at least one is independently rendered on the user's Windows Blender and archived with scene+receipt+PNG/EXR where appropriate; negative fixtures fail for the intended reason; the adapter gives portable parameter semantics; genuine CPU/GPU cost and visual variance are measured.

**Production/owner gate:** accepted Tevin material/skin, world lighting, scene mood and reference shoot are reviewed across perspectives and motion by the owner, not a single synthetic fixture. This gate remains OPEN.

### Immediate engineering order

1. Build null-source and shadow-blocker witness proof against existing point-light scene **before** modifying high-end cinematic rendering.
2. Record physically relevant light distance, energy and source radius with bounded units; hold camera exposure, world strength and compositor constant.
3. Add scene-linear EXR/AOV output and RGB preview with locked OCIO config, then compare exact ROI/metadata.
4. Add roughness/Fresnel and glass/lens calibration fixtures; avoid pretending pure pixel MAE is perceptual accuracy.
5. Reuse the same contracts in playable world rendering once a target engine is available; verify runtime frame cost and art direction separately.
