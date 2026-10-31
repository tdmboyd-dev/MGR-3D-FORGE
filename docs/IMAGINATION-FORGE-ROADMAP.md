# MGR Imagination Forge — from prompt to original geometry
**Decision:** 2026-10-31. **Canonical status:** `docs/HANDOFF.md`. This is the technical blueprint, not a second handoff.

## Product meaning and honest boundaries
MGR 3D Forge must be a standalone full 3D creation product with Tevin as one optional client via MGR-API-MCP. It must NOT be an asset-selection kiosk, a bundled Meshy/Tripo subscription, or a dependency of underbuilt Creation OS. The desired creative ceiling is ambitious: surprise-worthy new species, characters, faces, clothing, worlds and VFX that can be iterated, modified and owned. There is no objective way to prove that a result is "never-before-experienced" across all humans; originality must be assessed by diverse generations, similarity screening, visual quality and actual human critique.

Three complementary sources of geometry are intentionally distinct:
1. **Native procedural imagination:** actually constructs its own triangles using parameterized DNA, rules, mutation and composition. Does not require any bought/downloaded stock model or web inference. Current `forge/imagination.py` generates 1–12 creatures from prompt traits and seeded mutations, picks with a measurable heuristic, writes real GLB + genome/variant/evidence JSON. Current quality is stylized primitives, not photoreal. This is CODED and CPU tested. Physical plausibility, body topology continuity, UVs, displacement maps, rig and look fidelity remain open.
2. **Morph field:** `forge/morph_engine.py` deforms vertex positions with length, height, width and bounded twist, preserving indices, rebuilding normals and refusing degenerate triangles. It is non-destructive and reusable by other Forge renderers; it is **not** a mature facial blendshape, muscle/skin deformation, clothing drape or arbitrary topology fusion system. Tested against generated creature geometry.
3. **Neural generative backends:** optional open-weight 3D shape and texturing models run in **isolated** GPU containers if the exact checkpoint, dependencies, rights, VRAM and owner-approved compute are verified. The registry `forge/data/generative_engines.json` is a candidate catalog only; only the MGR-native procedural backend is installed/runnable today. Never fake neural inference from code or source links.

## Master-level creation director (next scope, not present)
`INTENT → SPECIES/CHARACTER/WORLD DNA → MULTIPLE CONCEPT DESIGNS → MULTI-VIEW REFERENCE GENERATION → 3D GEOMETRY INFERENCE/ASSEMBLY → MORPH/SCULPT/RETOPOLOGY → PBR/UV/FUR/HAIR → RIG & MOTION → BLENDER/GAME ENGINE → VISUAL/ANATOMY QA → ITERATE → STORE VERSIONED OUTPUT`

- Generate multiple distinct plans, not just one text prompt. Deliberately mix unusual yet coherent features, e.g. a glass-armored aquatic dragon with pressure-adapted wings. Preserve prompts/seeds/settings and lock features that the owner approves.
- Use similarity/reference checks to avoid near-duplicates of stored designs and third-party copyrighted characters; be candid that global novelty cannot be guaranteed. A real visual scoring model can compare reference views/anatomy, while geometry/rig tests catch structural failures.
- Build **MGR Morph DNA 2.0** for humans with landmark-aware/part-aware shapes, morph targets, facial expressions and body blendshapes, then skin/cloth/hair/fur. Do not stretch existing disconnected mannequins and call that a production human.
- Creature genetics needs independent skeleton archetypes (biped, quadruped, bird, winged, serpent, arachnid), constraints and retarget maps so horns/wings/tails become functional deforming anatomy.
- World invention needs biome/architecture/scene-grammar synthesis, semantic layout, navigable collisions, procedural shaders and editable layers. It must not be limited to copying Kenney town kits.
- A genuine fully autonomous job needs per-stage retry/cancel/reconcile, cost/resource budgets, documentable partial failures, saved result access, user correction, and artifacts passed through Blender and target engine.
- Safe asset reuse can accelerate creation but must never cap creativity. Preserve and pin selected officially licensed kit releases, not indiscriminately download millions of objects or assume a GitHub license covers imported media.

## Open AI/model candidates (not installed)
- **Microsoft TRELLIS.2:** https://github.com/microsoft/TRELLIS.2 ; image-to-3D PBR, 4B, MIT code/model described; official hardware: Linux NVIDIA with >=24GB VRAM, dependencies have separate licenses. Good image-to-3D candidate.
- **TencentARC Pixal3D:** https://github.com/TencentARC/Pixal3D ; code/weights MIT per publisher NOTICE; multiview code released Sep 2026. Exact GPU/camera and dependency compatibility need a pilot.
- **Microsoft TRELLIS original:** https://github.com/microsoft/TRELLIS ; text/image-to-3D and localized edits; inspect pinned checkpoints and GPU resource needs before install.
- **VAST-AI-Research TripoSR:** https://github.com/VAST-AI-Research/TripoSR ; single-image reconstruction; code and separately hosted weights need version/license review.
- **Tencent Hunyuan3D 2.1:** https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1 ; ~10GB shape / ~21GB texture / ~29GB combined reported; **restricted community license**, territorial and commercial conditions; cannot default to MGR unrestricted backend.
- **MakeHuman/MPFB:** https://www.makehumancommunity.org/mpfb/index.html ; human morph tooling. Software and core assets have separate licenses; third-party packs differ. Not inherently a prompt-to-3D neural engine.

## "Unlimited" is a usage and ownership decision
No per-request cloud API credits for local CPU modeling and locally installed open weights, but **hardware, time, VRAM, license, concurrent-job, disk and storage limits remain**. Meshy API explicitly rate-limits concurrent and per-second jobs and charges credits. Self-hosted model execution is closer to owner-controlled capacity, provided weight/dependency licenses permit it and GPUs have enough memory.

**Package policy:** install only tested dependencies into isolated environments for their corresponding backend, pinned to a SHA/version with source and weight hashes. Never `pip install` every internet 3D package into Forge's core Python runtime; doing so can break the CPU builder and contaminate licenses. No 24+ GB model checkpoint was downloaded or GPU rented in this wave. Heavy file mirrors need a separate owned object store and a second verified backup.

## Proof this wave
- `python -m unittest -q tests.test_imagination tests.test_morph_engine tests.test_generative_backends` verifies candidate determinism, bounded prompts, real GLB, morph quality, registry and fail-closed optional backends.
- Actual seeded stylized creature `invented-dragon/creature.glb` SHA `fb03416fbe7f7d92d8507dc2864881185a41e45cdddcd20fa924a6165c276fa0`, 8 candidate genomes, local CPU/no neural inference, imported on Windows Blender 5.2.2 with **1 mesh, 2,528 faces, 5 materials**, saved editable `.blend` file. Independent reopening/render evidence in `invented-dragon/blender-proof.json` on owner's PC when completed; visual and owner-art QA still open.
- Metadata-only model registry, no installed optional neural backends. This isn't equivalent to Meshy, Tripo or high-end multiview realism. It is the first MGR-native creation and morph foundation toward that objective.

## Acceptance roadmap
1. Visual and independent Blender and Godot tests of generated creature; inspect rendered geometry honestly and repair obvious silhouette defects.
2. Add actual editable creature anatomy parameters for legs, tails, wings, eyes, fur, horn geometry and connection fidelity; support arbitrary imported meshes and export morph targets (not just one fused GLB).
3. Build AI provider plugin interface with captured latency, VRAM, real license, weights hash, cost and failure receipts; pilot one generative backend in approved GPU environment.
4. Build prompt → image/multiview → textured detailed mesh with repair/UV/retopo/rig/animation and real visual acceptance.
5. Turn human/creature creation into a user-facing Studio flow where a person can generate, compare variants, morph, revise and save without Tevin.
6. Connect that same isolated Forge job through authenticated MGR API/MCP for Tevin and Creation OS; no second router or mandatory coordinator.


## Master-level target: exceed a single Meshy/Tripo generator (2026-10-31 owner expansion)

**Owner outcome:** In either the standalone Forge Studio or via Tevin through MGR-API-MCP, create, regenerate, morph, rig, animate, edit and reuse a human, fantasy animal, hybrid creature, vehicle, prop or world with consistent anatomy/style and saved provenance. Source asset packs are optional ingredients, not a creativity ceiling. "No one has ever experienced" is artistic ambition, not an objectively testable claim.

### Four cooperating creation modes

| Mode | Owner result | Technical route | Actual status |
|---|---|---|---|
| Forge Native Imagine | Invent new base shapes and configurable DNA, no commercial credits | seeded procedural meshes, anatomy rules, topology, boolean/voxel modifiers, design lineage | Stylized creature GLB **locally verified**; rough aesthetic |
| Forge Morph DNA | Precisely transform geometry, joints, clothes, skin textures and articulation without body parts breaking | *shared* non-destructive geometry/bone deformation field; semantic vertex groups; blendshape and corrective shape-key system | Shared stretch/twist kernel **tested**; facial/cloth morph and arbitrary topology open |
| Forge Multi-Model Shape Lab | High-detail creative original meshes not derived from stored pack selections | independently hosted Pixal3D, TRELLIS.2, licensed controllable generation, side-by-side variants, PBR/UV/retopo | Profiles only; **no third-party weights installed or neural inference** |
| Forge Motion & Skeleton Intelligence | Auto-detect anatomy, create bone hierarchy and weights, edit bone morphology and retarget motions | native DNA skeleton templates, Blender skinner, later UniRig/AniGen, optional licensed Rigify/Rigger/CaptureForge | Native Blender 19-bone weighted creature prototype imported and animated; professional art rig open |

### Specific measurable development gates

- **Gate A — engineering trust:** one source of truth, pinned license scope *for each copied subfolder*, reproducible source hashes and checkpoint model cards, dependency-isolated installs, rollback/timeout/duplicate/restart tests. A free README is not a commercial release.
- **Gate B — editable rigged native foundation:** generate DNA + eight variants → edit morph → map same transform across mesh **and bones** → build 19+ bones and weights → keyframe real deforming motion → export GLB → reopen on second Blender 5.2 process → preview/render → record bone counts, vertex motion and SHA. This is now a local prototype **not beauty/skin quality accepted**.
- **Gate C — true neural 3D pilot:** set up one legally permitted, pinned open-weight Pixal3D/TRELLIS.2 backend in isolated GPU environment with weight/license hashes; image/multiview → GLB → exact camera-match, surface/PBR checks → 3D mesh metrics and license receipt. No floating "latest" installs or auto-GPU spend.
- **Gate D — advanced artistic iteration:** generate multiple *distinct* concept/style options, compare to target refs across front/left/right/back, refine real 3D mesh rather than just rerender the image. Add sculpture/morph/retopology/texture correction, visual critic, anatomy/UV/LOD/mesh leak checks and approval-conditioned retry.
- **Gate E — arbitrary character families:** diverse human faces, skin color/undertones, hair/locs, clothing/body morphs, expressions/52 ARKit controls; biped/quadruped/bird/aquatic/serpent/insect/hybrid creature rigs; preserve head/facial identity under changes. Rigged model must survive posing and animation with no broken mesh.
- **Gate F — world intelligence:** procedural terrain and biome synthesis, architecture grammar, object/camera/light/navigation/physics, streamed editable layers, and partial scene edit without regeneration of unrelated content.
- **Gate G — standalone end-to-end experience:** Studio user prompts → local/cloud verified workflow → variant browser → direct mesh and rig controls → saved/restored project → Blender and Godot play → secure Tevin/MCP same job path. Creation OS may orchestrate *multiple* factories but is not an ordinary Forge job prerequisite.
- **Gate H — competitor comparative evidence:** on same approved briefs/reference images, measure image match from 4 cameras, mesh topology and watertightness, PBR/UV, anatomy/preservation, bone weights and animation failures, character/world editing, actual completion/cost/compute, and human panel quality score. Compare to Meshy/Tripo/Higgsfield only with current legitimate benchmark outputs and permission. Don't declare higher quality without side-by-side pass.

### Research implementation priority

1. **Native reusable core (zero API credits):** Blender Python `bpy`, Forge CPU generation/morph, rig templates, model/asset cache, supported exports, glTF validators, real render QA. Unlimited requests are limited by PC, storage and concurrent work, not cloud credits.
2. **Separate GPL Blender tool lane:** Rigify, Rigger, CaptureForge and MakeHuman/MPFB where exact license and add-on versions permit; maintain separate source/notices so the standalone MGR core isn't silently relicensed.
3. **Separate permissive-weight GPU lane:** Pixal3D and TRELLIS.2 first, then AniGen/UniRig subject to exact subdirectory, dependency and checkpoint rights. AniGen `extensions/CUBVH/LICENSE_NVIDIA` is noncommercial; exclude it from any commercial inference install until actually demonstrated not needed and legal conditions cleared.
4. **Research-only/conditional:** Adobe RigAnything (Adobe research-only); MeshAnything V2 (S-Lab noncommercial); Meta SAM 3D checkpoints (SAM License); Tencent Hunyuan (territory/usage conditions); proprietary Higgsfield CLI (MIT client, not free weights). **No unrestricted embedded release of these.**
5. **Performance and hardware:** first inspect existing Blender/CPU. GPU planner works in dry-run with pinned quote evidence, but no provider launch/billing. Only request a pay-per-use GPU when model weights are permitted, a workload demands it and user authorizes spend.

**New MGR-native proposed upgrades:**
- **Creation Genome Ledger** — reversible sequence of each character mesh/rig morph, keeping locked identity portions when new designs are spawned.
- **Shape Tournament** — seed many original form/geometry candidates, evaluate with surface/anatomy/style metrics and visual human preference, then merge approved traits into a new source-backed creation (never a hidden asset selector).
- **MorphRig Continuity** — change body, wings, hands, tails and clothing while re-solving bone positions/weights, preventing leg/hair/wing breakage and republishing all prior motion clips with regression checks.
- **World Design Seeds** — save editable environmental DNA and variations, reconstruct worlds without losing continuity and rights information.

See `research/external-provenance/NEXT-GEN-MORPH-RIGGING-2026-10-31.md` for pinned source SHA, **exact folder/license** and weight/provider distinctions. Current status lives only in `docs/HANDOFF.md`; no new handoff created.
