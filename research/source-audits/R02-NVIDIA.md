# R02 — NVIDIA Graphics Research Extraction for MGR Forge

**Research pass:** 2026-10-25. **Scope:** four selected first-party graphics/3D research contributions; **not all NVIDIA Research, GPUs, tools or papers**. Inspected project technical explanations, original papers/PDF excerpts, one current 2026 method and licensing notice; executable/code audits and reproducibility remain queued. MGR-native architecture below is independent product design informed by published scientific ideas.

## Decision table

| NVIDIA primary contribution | Technical method | MGR native invention | Commercial/hardware boundary |
|---|---|---|---|
| ReSTIR (2020 SIGGRAPH) | Weighted reservoir sampling and spatial/temporal reuse of dynamic direct lighting candidates | **MGR Light Memory** | GPU ray-tracing research; RTXDI SDK license is a custom NVIDIA agreement |
| Real-Time Neural Appearance Models (SIGGRAPH 2024) | Learned hierarchical textures, small decoder, material reflectance + direction sampling | **MGR Material Mind** | Neural inference / shader implementation requires benchmark; no code license grant from paper |
| Real-Time LoD Rendering with ReSTIR (SIGGRAPH 2026) | Surface point mapping permits sample reuse across geometry LoD/topology changes | **MGR Scene Continuity Renderer** | Specific renderer and trained? method not installed; paper is not SDK rights |
| GATOR: Generative and Agentic 3D Object Reconstruction (2026) | Image/mask/available geometry → generative mesh → agent edits actual Blender mesh against reference | **MGR Reconstruction Inspector** | First-party page says **code coming soon**; research method not a released installable pipeline |

## Method 1 — Reuse light samples rather than brute-force every ray

**Read depth:** NVIDIA original 2020 *Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting* paper PDF and first-party article overview; official RTXDI license. One-pixel Monte Carlo estimator for direct lighting chooses candidates `x_i` with target weight `w_i = p̂(x_i)/q(x_i)` where `q` is proposal density and `p̂` proportional to target contribution. Reservoir sampling keeps a representative candidate and accumulated weights with randomized replacement probability `w_i / Σ_{j≤i} w_j`. Reusing candidate reservoirs from neighboring pixels/prior frames increases effective samples. Correctness depends on sample-target densities, visibility/weights, temporal correspondence and resampling bias control; naive reuse after geometry change causes ghosting and wrong shadows.

**MGR-native:** MGR Light Memory stores `(frame, camera, surface_key, normal, material_id, light_set_version, candidate, weight, exposure)` and invalidates reuse after disocclusion, lighting/material changes or camera jumps. Fast low-quality preview estimates lighting, while final path tracer remains reference oracle. **Tests:** moving lights and occluders, flash/strobe magic, rotating reflective object, camera cuts, hidden shadow region, relit frame; compare ray-traced reference MSE, temporal flicker and milliseconds/frame. **Hardware:** relevance highest on GPU ray-tracing; CPU math proof possible but not meaningful performance comparison. **License:** NVIDIA RTXDI/SDK source has custom SDK terms, not generic MIT; implement original research ideas independently and audit rights for any SDK integration.

## Method 2 — Compress complex material behavior into neural evaluation

**Read depth:** first-party SIGGRAPH 2024 *Real-Time Neural Appearance Models* full PDF link and technical project description, inspected architecture, not source repository. Instead of storing every detailed BRDF response, the method learns **hierarchical texture latent codes**; a tiny decoder evaluates reflectance and optionally guides importance-sampled outgoing ray directions. A microfacet prior helps with directional distribution. In conventional rendering, outgoing radiance `L_o(ω_o)=∫_hemisphere f_r(ω_i,ω_o) L_i(ω_i) max(0,n·ω_i) dω_i`; `f_r` can be approximated by learned latent-decoder response, but stability, energy conservation and reciprocity are not automatic.

**MGR-native:** MGR Material Mind separates *truthful PBR measurements* from neural appearance approximations; offers an editable authoring graph that can approximate velvet, complex brushed metal, gemstones, iridescence, enchanted fabrics and fantasy shifting materials. Parameter `material_type`, train/bake provenance, viewing directions, PBR fallbacks, roughness/color and compressed latency. **Tests:** furnace/energy check on passive material, directional reflectance vs multi-light path-traced reference, texture seams, grazing angles, temporal shimmering, texture size and GPU performance. **Risks:** network weight may bake illumination, violate energy constraints or shift identity color; never treat pretty image alone as material validation. **Code/license:** study project paper for algorithm only; no inspected redistributable implementation or weight rights established.

## Method 3 — Reuse shading while changing geometric detail

**Read depth:** original 2026 NVIDIA paper PDF first page/abstract+method summary *Real-Time Level-of-Detail Rendering with ReSTIR*; actual implementation release not identified/installed. Traditional temporal reuse uses geometry correspondences keyed to a triangle or surface; LOD replacement changes topology. Paper introduces a **surface-point mapping** so radiance/light samples survive changes across meshes of different topology. Rendered error must account for positional/normal mismatch and newly uncovered geometry. The PDF reports noise reductions over baseline configurations on evaluated scenes, but those numeric example results do not establish MGR performance.

**MGR-native:** **MGR Scene Continuity Renderer** maps coarse-vs-detailed surface correspondence across world/character LOD, preserving light history only when mappings pass location, orientation and visibility gates. Geometry identity/traversal remains authoritative, not the sample cache. **Tests:** orbit near/from far around Tevin's face and hands, 10× camera distance shifts in iKickItz world, fast LOD switching with light/shadows, moving/occluding limbs; measure pop, ghosting, image MSE and frame time. **Risk:** stale mapping produces smeared lighting; invalidation/reprojection confidence is mandatory. GPU-oriented; CPU reference test can validate mapping but not real-time claim.

## Method 4 — Agent-assisted reconstruction must modify actual editable geometry

**Read depth:** NVIDIA original GATOR 2026 project page method and demonstration descriptions; **site says code coming soon**, so only high-level method was inspectable. First classify images/camera/masks and available geometry; use generative prior to propose shape, then an agent examines actual images, masks, existing candidate and edits a mesh in Blender. Iterative edit/inspection improves controllability. Technical details of exact agent actions, loss functions, model weights, hidden system architecture, runtime and train data are not available from inspected public material, so cannot be claimed or reverse engineered from a video.

**MGR-native:** MGR Reconstruction Inspector can build a separate legal implementation: `ReferenceBundle → CandidateMesh → multi-angle Blender renders → difference regions → bounded edit proposal → tests → owner accept/reject`. It builds on existing MGR Visual Judge and Blender interface; objects must remain separately selectable. Specific to Tevin: verify both hands, chain attachment, coat/undershirt separation and a valid T-pose/A-pose + bending. **Tests:** image-vs-mesh residual triggers targeted geometry edits, no unrelated landmark/face/asset changes, 20+ varied poses and multi-view verification. **Hardware:** Blender editing + CPU quality math feasible; optional high-capacity neural proposal may require GPU. **License:** do not claim “NVIDIA released it open source”; code was listed pending on inspected page.

## Native product contracts

| MGR component | Inputs | Outputs / acceptance |
|---|---|---|
| MGR Light Memory | surface/light/camera state + candidate rays | temporally reliable lighting with reference error and reuse/invalidation receipt |
| MGR Material Mind | PBR baseline + reference photos/material graph | editable material + energy/color/view QA and cost |
| MGR Scene Continuity Renderer | geometric LOD map + motion/camera | stable transition with shading-history confidence and pixel-error/latency |
| MGR Reconstruction Inspector | owner image set/masks + original mesh | bounded repair proposals, Blender edit receipts, multi-view and rigging QA |

## Best build sequencing

1. Establish offline CPU correctness oracle: deterministic ray-light sampling toy, physically bounded PBR material tests, mesh LOD point association and image-vs-mesh mismatch map.
2. Plug into Blender headless renders and MGR Visual Judge; create stable renderer-independent QA receipts.
3. Add GPU acceleration only for measured bottlenecks; compare native implementations against true reference offline Blender frames rather than NVIDIA demo timing claims.
4. Treat RTXDI/NRD SDK usage as an external optional integration subject to exact license and GPU compatibility checks; do not make proprietary MGR Forge depend upon it.

## Acceptance and failure criteria

- **Lighting:** moving occluder and light scene must invalidate stale reservoirs and produce reference-bounded flicker/MSE; camera cut resets safely.
- **Materials:** compare diffuse, metal, dielectric, subsurface-like and iridescent sample sets at grazing angles. Passive-material energy budget flagged when violated.
- **LOD:** 8 camera distances, surface relocation and silhouette continuity; error and confidence logged across topology swaps, no persistent ghosting.
- **Agent geometry repair:** known ground-truth mesh with 5 planted defects, target fixes without altering locked approved geometry; render 12 camera poses and 20 articulation frames; include owner approval.
- **Licenses/hardware:** all external SDK/module/weights traced to exact revision, rights and hardware spec; CPU fallback never claims GPU-grade FPS.

## Explicit research maturity and gaps

**Inspected:** four selected projects/paper summaries; ReSTIR PDF and 2026 LoD PDF portions, neural appearance PDF/project, GATOR first-party page; official RTXDI license text. **Queued:** full derivation of reservoir unbiasedness/MIS, full neural appearance PDF and training details, 2026 LoD appendices, GATOR code after official release, NVIDIA source/SDK dependency audit, Windows GPU benchmarking, broader NVIDIA Research catalog including neural radiance cache, caustics and world modeling. Not a claim of reading every NVIDIA paper or implementing proprietary NVIDIA source.
