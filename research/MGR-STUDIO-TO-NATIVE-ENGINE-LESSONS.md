# MGR Production Secrets → Native Forge Quality Systems

Date: 2026-10-25. **Not a new competing source of truth.** This is the cross-domain implementation sheet feeding the canonical `MGR-REALITY-TO-SPACE-MASTER-MAP.md`, `docs/BUILD-REGISTER.md` and `docs/PROGRESS-LOG.md`. Outside research/rights live exclusively in `external-provenance/STUDIO-ENGINE-PRIMARY-SOURCES-2026-10-25.md`.

**Implementation wave:** all ten rows below now have *scoped CPU proof/guard functions* in `forge/studio_quality.py`, real unit/negative tests in `tests/test_studio_quality.py`, and an `studio-proof` CLI receipt. This does **not** upgrade any row's missing professional Blender/live engine acceptance. 24 separate source-family audits are tracked in `research/SOURCE-INTELLIGENCE-QUEUE.md`, preserving each source's exact inspected depth and rights.

## What the 20 foundations teach — and what studio engineering adds

Scientific foundations explain depth, geometry, simulation, imaging, mathematics and the physical meaning of a world. Studio and engine research answers the harder shipping question: **how to make those truths editable, directable, visually beautiful, performant and stable across thousands of shots/players/poses.** The winning MGR architecture uses both.

| MGR-native production capability | Actual user value | Engineering experiment needed before a PASS claim | 20-domain bridge | Current truth |
|---|---|---|---|---|
| **MGR Material Reality Witness** | Tevin's skin, chains, hair, coats and magical surfaces react consistently to light | Render measured/simple BRDF reference balls under fixed HDR light; save scene-linear EXR + per-material deltas, validate roughness/metallic energy behavior | S02+S07 | Research specified; generic PBR Blender render passed, measurements open |
| **MGR Adaptive Light Orchestra** | Movie-scale scenes with hundreds of motivated moving lights and VFX | Compare unbiased low-light-count reference with many-light sampling; per-light variance/noise, stable temporal frame and time budget | S02+S07+S15 | Research only |
| **MGR Flesh & Translucence Lab** | Skin, ears, marble, wax, crystal and monster tissue gain believable inner light | Compare offscreen reference views under transmissive/backlit lights and skin-tone landmarks; preserve mobile fallback | S01+S02+S07+S19 | Research only |
| **MGR Surface Anatomy Guardian** | Sculpted characters retain smooth silhouettes without seam cracks or broken joints | Compare base cage to subdivided limit surface at silhouette, UV seam, screen-space curvature, mirrored edge and rig motion | S03+S09+S10 | Basic topology edge-audit tested; full subdivision open |
| **MGR Living Hair Director** | Hair, braids, fur, capes and flowing props obey style and shot intent | Multi-shot curve/cloth simulation with contact, roots, collision, inertia and continuity under T/A/action poses | S06+S09+S10+S19 | Modular geometry/rig prototype only |
| **MGR Layered World DNA** | A scene can be changed collaboratively without erasing approved content | Compose source scene + override layers + variant references, roundtrip exact IDs/materials and rollback change, corruption tests | S08+S09+S11 | JSON revision/memory partial; full scene-layer interop open |
| **MGR Horizon Truth Streaming** | Huge world feels persistent when turning, entering rooms or teleporting | Four-cell and 64-cell traversals with real load/unload, collider ownership, peak resident bytes and frame p99 | S08+S15 | CPU distance-based **plan** coded/tested, not loaded |
| **MGR Visual-Surface Reconciler** | Fine geometry doesn't vanish or crack between levels of detail | Compare adjacent chunk seams, silhouette error in pixels, material continuity and near/far transitions on target renderer | S03+S07+S08 | Generic LOD and edge checks; perceptual transitions open |
| **MGR Cross-View Reality Judge** | Detect Tevin hands/face/clothes changing identity as camera rotates or poses change | Calibrated 5-view capture, landmarks/occlusion labels, actual skeleton and surface overlap; do NOT treat raw image pixel similarity as identity | S01+S04+S10+S12+S13 | Native calibrated stereo + visual same-frame checks; semantic pose invariance open |
| **MGR Atmosphere Memory** | Fog, magic, portals, smoke, weather stay consistent across shots and worlds | Compare temporal volume densities/light scattering and memory over camera travel; cache/revision and budget tests | S02+S06+S07+S11 | Cycles uniform/procedural cloud volumes Windows tested; continuous FX open |

## The deeper source-code / talk / paper audit contract

For any technique selected for implementation, follow **all** steps before adding it as production-ready:

1. Read primary paper or authoritative engine implementation, not marketing screenshots. Record exact publication, repository commit/engine version and technical assumptions.
2. Extract math/data structures, precision, GPU/CPU allocation, known limitations, real asset ownership and code/data/model license separately.
3. Build the **smallest MGR-native independent test scene** that measures its claimed advantage. Add a negative case intentionally designed to break it.
4. Run a fast preview and physically grounded reference where applicable; compare geometry, camera depth, illumination, temporal coherence, memory and render/frame time.
5. Test with generic assets first, then modular character/wardrobe, then real approved character or world fixture. Do not confuse a visually good sample with acceptance.
6. Record a machine-generated receipt, owner approval requirement and supported hardware. Only after the receipt passes may the implementation register move from PARTIAL to VERIFIED.

## Non-negotiable priorities after 20-domain research packets

1. **Character truth:** Tevin's real base model, hands, skull/face silhouette, bone weights, detached garments and view/pose continuity. Controlled multiview captures and owner likeness approval.
2. **World truth:** actual navigation/collisions, streaming, depth, occlusion, interior/exterior continuity and measured interactive target performance.
3. **Studio quality:** reference/material captures, lights, skin/hair, FX volume temporal coherence, composition and final shots.
4. **Cross-platform production:** measured CPU/GPU capacity, optional legally usable neural workers, engine export and versioned scene/asset state.
5. **Research gap recovery:** expand SIGGRAPH/Pixar/Disney/GDC candidates per *applicable implementation*, cite a particular paper/lecture/source file, and run parity tests—no arbitrary claim that reading a catalog = mastering a studio pipeline.

**Decision:** MGR Forge should own the geometry/scene identity, judges, approvals, revision history, native orchestration and art direction. Blender and selected runtime/model backends can be replaceable execution workers. This builds an original creation platform with measurable proofs, not a repackaging of a studio's proprietary stack.
