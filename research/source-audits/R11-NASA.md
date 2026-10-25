# R11 — NASA Scientific Visualization Extraction for MGR Forge

**Research wave:** 2026-10-25. **Boundary:** four focused NASA/JPL-related technical practices from official mission and developer sources; **not** full NASA catalog/source audit. Exact source URLs and read depth are in `research/external-provenance/R11-R12-SOURCES.md`. NASA examples inform MGR mathematical/UX contracts; NASA insignia, contractor imagery and individual model/data rights remain separate.

## Four high-value techniques and native derivation

| Official scientific practice | Engineering principle | MGR-native capability | Main proof |
|---|---|---|---|
| JPL NAIF SPICE observation geometry | Versioned reference frames, clock/time kernels and frame transforms | **MGR Space-Time Truth Grid** | Camera/world transforms commute, stable under time scrub |
| JPL SPICE Geometry Finder | Search time intervals satisfying exact spatial event predicates | **MGR Celestial Event Director** | Eclipse/occlusion/contact root-finding with tolerances |
| NASA OpenSpace/NASA Eyes | Interactive scale/time exploration grounded in measured ephemerides/data | **MGR Infinite Scale Atlas** | Camera near/far precision and scale-aware LOD |
| NASA SVS + LRO lunar model production | Scientific datasets → geometrically/visually documented model and metadata-backed shot | **MGR Reality Provenance Studio** | Height/displacement validation and traceable imagery/units |

## 1. Reference frames are not optional bookkeeping

**Inspected:** NAIF/JPL SPICE reference-frame required reading plus SPICE concept and tutorial index. SPICE treats body, instrument, spacecraft and inertial/fixed-offset frames as objects whose transforms depend on kernels and time; C-kernel attitude definitions can use spacecraft clock ticks, requiring a matching SCLK kernel. Composition can be expressed `T_world←camera(t) = T_world←body(t) · T_body←rig(t) · T_rig←camera(t)`. Matrix inverse should return original point within tolerance; quaternion frame handedness and time-system conversion must be explicit. **Important:** the existence of a kernel system does not tell us an accurate transform absent the relevant trusted data files.

**MGR-native:** MGR Space-Time Truth Grid stores `world_id`, `frame_id`, parent, handedness, unit scale, time basis, transform function, source revision, uncertainty and locked anchors. Tevin's camera, iKickItz planets, physics bodies, magical portals and shots all consume the same frame graph. **Acceptance:** a four-frame hierarchy with rotating body and camera, 10,000 random points across times, compose/inverse repeatability, no frame cycles, no undefined clock basis; report error in world length units and camera pixels. **Limits:** need floating-origin/high-low coordinate representation in world-scale scenes, not a naive single 32-bit float for astronomical distances.

## 2. Compute when an event is possible, then render it

**Inspected:** JPL Geometry Finder (GF) required-reading description of finding time windows satisfying user-specified geometric conditions. This maps to a director's problem: find when a shadow, occlusion or alignment occurs rather than manually scrub thousands of frames. Generic predicate `g(t)=dot(direction_to_light, surface_normal)` or separation `distance(target, camera_ray) - radius` changes sign around a threshold. Partition time intervals, bound derivatives/step size and bracket/refine roots; do **not** assume sign-change detects a zero-width tangency. Conditions need sampling safety, event priority and precision receipts.

**MGR-native:** Celestial Event Director handles eclipse, sunrise, line-of-sight, spell beam crossing, portal alignment and animation contact windows with reusable temporal predicates. **Acceptance:** analytic rotating orbit/occluder fixtures with known start/end, tolerance-bound timestamp, tangency scenario, discontinuous animation pose and missing-data refusal. This is deterministic CPU math, no expensive GPU required for event timing; final shadows and optical phenomena still need render verification.

## 3. One world spans many scales and rates of time

**Inspected:** NASA Science OpenSpace project page (angle, scale and timescale exploration), NASA Eyes web 3D product/features/FAQ, OpenSpace official upstream repo. OpenSpace provides data-driven interactive astrovisualization rather than a ready game engine; upstream claims an MIT license for its code. NASA Eyes' browser visualization shows measured/simulated mission context, but the browser implementation rights were not inspected and NASA mission data vary by source.

**MGR-native:** Infinite Scale Atlas combines `world_coordinate` high precision, camera-relative placement, origin rebasing, scale-aware LOD, timeline speed factor, terrain/body orbit streaming and consistent label/depth handling. A planet-scale flight should not cause a Tevin-sized object to jitter or disappear because of float precision. **Acceptance:** positions across 1 mm to 1 astronomical-unit synthetic scales, orbit for 100,000 ticks, 100× zoom, transition with camera-relative error under declared screen-pixel budget, stable physics local-space state, P95 CPU/VRAM data. **Hardware:** CPU can solve ephemeris/frame math; GIS textures, huge models and real-time cinematic rendering are GPU/storage-heavy. **License:** OpenSpace code MIT per official repo, exact dependencies/assets still require pinning and rights audit.

## 4. Dataset → meaning → image, with provenance and uncertainty

**Inspected:** NASA Goddard Scientific Visualization Studio mission/help pages (dataset metadata, animations/frame-series, scientific visualization), NASA LRO-based 2026 Moon 3D Models page and CGI Moon Kit notes. Scientific models are derived from source imagery/topography, then presented via displacement/material maps and camera animation; source scientific data may be necessary for metric interpretation. Example *MGR* heightmap `mesh(x,y) = (x, y, h_source(x,y)*vertical_scale)` needs an explicit reference datum, geolocation, resampling kernel and vertical exaggeration factor. A high-quality Earth/Moon shader does not imply survey-grade surface precision.

**MGR-native:** Reality Provenance Studio attaches to every `EarthLikeTerrain`/planet/volumetric render `data_source`, coordinate frame, spatial/temporal resolution, measurement uncertainty, transform version, interpolation, render-only exaggeration and asset rights. **Acceptance:** authored DEM grid of known hill/crater ground truth; generate multiple LODs, check height residual at sampled grid locations and label exaggeration. Rendered contact sheets compare camera/LUT while geometric benchmark remains independent. Test time-dependent scientific layers separately from static topology.

## Native integration and benchmark plan

| Component | Proposed input/output | Native test |
|---|---|---|
| Space-Time Truth Grid | Typed time+frame graph → metric transforms | Round-trip and time-varying composite transforms |
| Celestial Event Director | Temporal geometry predicate → event windows | Root-timing analytic orbits and occlusions |
| Infinite Scale Atlas | Global position+camera+LOD → stable view state | Pixel jitter/origin shifts, scale stress |
| Reality Provenance Studio | Data grid+rights+datum → spatial asset+receipt | DEM height test and provenance completeness |

**Priority:** CPU implementation of transform frames and timing predicates can start immediately. Then high-precision origin rebasing and geometry-derived imagery receipts. **No claim** NASA software or ephemeris data installed, Windows benchmarks passed, or external NASA 3D resources imported.

## Rights and source audits

NASA SVS says its content is public domain **unless otherwise noted**; individual pages/assets must be checked for third-party material. NASA's official brand policy distinguishes government content from protected insignia/logotype/identifiers, and bars endorsement implications. NASA/JPL software and kernels must be reviewed separately by project/version—NASA branding does not equal a universal source code license. OpenSpace repository says MIT; if MGR uses code rather than engineering concepts, pin releases, review dependencies and retain notices.

## Further investigation queued

Full SPICE API/transform/source-level tutorial reproduction, official SPICE Toolkit license per release, orbital timing/polar geometry tolerances, geospatial map projections and precision benchmarking, OpenSpace renderer/source architecture beyond README, NASA-specific asset metadata/rights per downloaded dataset, and validation against Time's Windows Blender rig. These are pending and **not folded into a false 100% research claim**.
