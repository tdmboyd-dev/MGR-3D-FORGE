# R18 — MGR Technical Source Audit: Published OpenAI 3D and World Research

**Research date:** 2026-10-25. **Scope:** five concrete method families from official publications and two first-party code/model repositories. **Evidence depth:** first-party methods and README/model-card review, not trained-weight download/benchmark or entire training-source audit. Primary links/rights are separated in `research/external-provenance/R17-R18-SOURCES.md`.

## Executive finding

There is a practical spectrum from **point clouds → implicit 3D fields → generated video**. The first two have officially released historical research code/checkpoints; the more visually impressive video-world methods have not thereby become editable 3D geometry engines. Forge should reuse the *ideas* to create a native pipeline with measurable geometry and consistent scene state, evaluate older open weights optionally against newer candidates, and avoid dependence on proprietary video access as its foundation.

## Five published method families

| Research | Technical operation | MGR opportunity / limitation | Official code/weights/access evidence |
|---|---|---|---|
| **Point-E (2022)** | Diffusion synthesis of 3D point clouds from text, with an image-conditioned route and optional point-cloud→mesh step. Optimizes generation speed relative to earlier computationally intensive text-to-3D methods. | Fast concept geometry, point sampling and synthetic scan-like candidate; sparse/noisy point clouds require mesh reconstruction, watertightness, topology, UV, skeleton and artistic cleanup. | First-party `openai/point-e` code/model release and MIT LICENSE found. Check exact checkpoint file terms, upstream dependencies and local VRAM before use. |
| **Shap-E (2023)** | Encodes 3D assets as parameters of implicit neural functions representing geometry and texture, then trains a conditional diffusion model over those implicit-function parameters; text/image conditions available. | Alternative to raw point sampling; implicit shape must be extracted, cleaned, surfaced/UV'd/rigged and judged for identity/pose consistency before shipping. | First-party `openai/shap-e` model/code release and model card confirmed; repository presents MIT license, but pin revision and license/weight/dependency scope before import. |
| **Sora original world simulation (2024)** | Spatiotemporal latent-patch representation of video/image data and diffusion-transformer-style video generation across varied dimensions/aspect ratios. Official report analyzes emergent 3D consistency but documents physics/causality failures. | Cinematic shot proposals, world moodboards and camera concepts; **cannot be treated as a metric reusable 3D world or validated physics engine**. | Technical report/system card public; full original model training source and open checkpoints **not confirmed**. Product access ≠ raw weight license. |
| **Sora 2 video/audio simulator (2025)** | Text/video-based worldlike video generation emphasizing improved motion physics, causality and synchronized audio, with acknowledged remaining errors. | Visual previs, directors' candidate shots, sound/action timing research; final object trajectories, contacts and frame continuity must be checked with native scene/physics truth. | First-party report/system card; no free commercial self-hosting weights/full model implementation established here. Use only permitted access route if explicitly chosen. |
| **Consistency Models / continuous-time simplifications (2023–24)** | Train/distill mappings that directly predict data from noise with one/few sampling steps instead of long diffusion chains; later improvements stabilize continuous-time formulation. | Engineering idea for accelerating local candidate texture/shape/image generation **if** quality, rights and output structure prove fit. General sampling research is not itself a ready 3D world engine. | Papers published. The specific evaluated 3D-ready model weights/code and commercial permissions are **not established** by this source set. |

## Native creation changes the research suggests

1. **MGR Shape Candidate Lane:** text/image/voxel/implicit/point providers output common candidate manifest with frame coordinates, scale, confidence and source model; isolate all paid/neural adapters.
2. **MGR Surface Recovery:** point-to-mesh/implicit-to-mesh reconstruction with normals, watertightness/UV/LOD and a separate deformation-friendly retopology gate.
3. **MGR Geometry First:** store actual mesh scene IDs, camera transforms, collision volumes and rig attachment; optional generated video is a render concept tied back to persistent geometry.
4. **MGR Spacetime Director:** story/shot timeline that controls real scene camera/actors/FX; generated footage can serve as a prompt/reference, never overwrite measured spatial state.
5. **MGR Few-Step Benchmark:** evaluate candidate accelerated local inference using *task-specific* quality-vs-latency and VRAM budgets; reject speed claims lacking visual/3D accuracy receipts.
6. **MGR False-Physics Sentinel:** test cause/effect such as glass breakage, object counts, gravity, contact and pose permanence across frames; flag plausible-looking hallucination.

## Accurate model/hardware economics

- Point-E and Shap-E repositories contain real code and checkpoint references; generation can be GPU-intensive. The source review does not determine exact real-time viability or VRAM for the owner's hardware. CPU fallback may function for limited cases but is not guaranteed practical until measured.
- Sora-class video inference and training cannot be assumed GPU-free; no official complete local installation/checkpoint was verified, so claiming local CPU/GPU cost is not possible.
- The native CPU-first approach to mesh validation, scene state, rig/pose checks and deterministic world creation remains independently implementable. No pay-per-output API is required for these foundations.
- Third-party models and sample galleries may use licenses different from the code repository. Pin and record each checkpoint, dependencies (including ML packages and downloads), commercial rights and human identity use before executing or vendoring.

## Hard acceptance and benchmarking tests

1. **Candidate repeatability:** same model/seed/input plus version/dependency metadata produces an output hash or well-defined statistical difference bound. No reproducibility promise if provider hides seed.
2. **3D valid geometry:** mesh candidate needs finite coordinates, normals, scale, face winding, topology/manifoldness when printable, UV material coverage and export integrity. Reject malformed sparse point clouds from high-quality asset lane.
3. **Identity/pose:** test same approved canonical *synthetic* character across T/A/camera viewpoints and frame-aligned 3D landmarks; matching still-image pixels alone fails pose equivalence.
4. **Video causality:** action/contact/physics failure fixtures (glass/contact/object transfer) compared against the scene's measured state, not generic video aesthetic scores.
5. **Dynamic occlusion:** camera circle around 3D world compares depth, silhouette and object identity; reveal actual geometry or explicit unknown-mask, not invented rear surfaces.
6. **Sora-style timing:** storyboard shots at fixed duration/FPS/lens/poses, audio event timestamps and cross-shot continuity; report failures rather than aesthetic “almost good.”
7. **Generation budget:** measured wall-clock p50/p95, GPU/CPU/RAM/VRAM, output triangles/points/texture resolution, source license and cost per accepted asset. Benchmark at least 10 repeat seeds.
8. **Production import:** export GLB and Blender reimport, pose sweep, clothing separation/material semantics and independent viewer visual check; a point cloud or view-only clip alone cannot pass.
9. **Legal refusal:** missing weights rights, identity permission, provider spend approval or version trace fails before download or request.

## Audit disposition

| Scope | Evidence | Status |
|---|---|---|
| Publication methods | Original reports and repos | RESEARCHED |
| Historical open research code | Point-E and Shap-E public repos exist | DISCOVERED, NOT INTEGRATED |
| Local model downloads/weights license audit | Not performed | OPEN |
| Sora source weights/self-host | Not publicly verified by these primary sources | UNAVAILABLE/UNPROVEN |
| MGR native image→mesh/implicit adapter | Technical contract only | SPECIFIED, NOT BUILT |

**Recommendation:** Run a controlled optional Point-E/Shap-E historical baseline only if machine resources and exact weight licenses check out. Prioritize deterministic MGR mesh world state and the Visual Judge's multi-view 3D evidence; generated video remains a cinematic aid until it can meet editable spatial truth requirements.
