# Creation-system evidence and native adaptation decisions

Date: 2026-11-02. Owner-directed comparison: Meshy, Tripo, Higgsfield, Unreal,
Hyper3D, Hi3D, Artlist.io (owner clarified the earlier “Artist”), and SAM 3D.
This is external provenance, not an MGR product specification or proof of
provider execution. The owner's direction is to learn useful methods and build
original native capabilities without making large model hosting or rented GPUs
a prerequisite.

## Evidence boundary and method

This pass reads current official public documentation, official repositories'
README/API examples, and selected existing Forge source. Vendor descriptions
below are **documented capabilities or claims**, not our measured results.
No paid task, account login, credential read, weight download, model install,
license acceptance, private backend inspection, asset upload, or inference was
performed by this research pass. Reading a model's architecture does not recover
its trained knowledge or establish a CPU replacement with equal fidelity.

The parent investigation owns separately retained REA browser observations.
Those records must retain their own exact targets, evidence IDs and limits;
this documentation pass does not fabricate REA IDs or call docs browsing
decompilation. Public browser captures can establish controls and client
behavior; they cannot reveal proprietary model weights or server algorithms.

Forge source examined here: `forge/imagination.py`, `forge/glb.py`,
`forge/materials.py`, `forge/meshqa.py`, `forge/repair.py`,
`forge/generative_backends.py`, and `forge/adapters.py`. Additional path
references below identify existing owners; they are not claims that every
algorithm in the whole repository was audited in this pass. Source may change
during the build; the final verification receipt pins the accepted version.

## Official-source ledger

| Target and primary source | What the official source establishes | Transferable principle and evidence limit |
|---|---|---|
| [Meshy Text to 3D](https://docs.meshy.ai/en/api/text-to-3d) | Separate geometry preview and texture refinement tasks; the refinement refers to an accepted preview. | Inspect silhouette before committing to surface detail. API documentation, not a trial of generated output. |
| [Meshy Remesh](https://docs.meshy.ai/en/api/remesh) | Existing models can be remeshed with topology and target face-count controls. The requested face count is an aim, not an exact guarantee. | Geometry budget and topology are explicit production decisions. Do not treat high face count as semantic or visual correctness. |
| [Tripo H3.1 developer reference](https://developers.tripo3d.ai/en/models/v3-1) | Distinct geometry and texture seeds, UV export, material generation, face limits, quad output, and generated parts. Some parameter combinations exclude each other. | Freeze geometry while revising materials; preserve part identities and exact capabilities. Documentation does not prove the models are locally installed or give Forge trained generation ability. |
| [Tripo feature guide](https://www.tripo3d.ai/help/getting-started/what-features-does-tripo-have) | A modular workflow spanning generation, segmentation, retopology, texturing, rigging/animation and DCC transfer. | Every stage needs visible outputs and independent checks. Its quality/speed adjectives remain vendor claims. |
| [Hyper3D Rodin Gen-2.5](https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5) | Text/image input, triangle/quad selection, output formats, dimensional conditioning and distinct material modes. HighPack changes texture resolution rather than geometry. | Separate shape resolution, topology, material response and texture resolution. A larger texture is not more geometric detail. No generation or billing was exercised. |
| [Higgsfield Cinema Studio build account](https://higgsfield.ai/blog/how-we-built-cinema-studio) | A filmmaking interface over interchangeable video models, with camera, optics and focal-length choices curated through creative review. | Make artistic controls affect an observable result and compare shots. A rendered video is not proof of an editable 3D mesh, UV set or reusable rig. |
| [Unreal PCG framework](https://dev.epicgames.com/documentation/unreal-engine/procedural-content-generation-framework-in-unreal-engine) and [PCG overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-overview) | Editable spatial generation graphs, point/attribute operations, component ownership, debug inspection and iterative generation. | Retain editable scene relationships, reproducible seeds, placement constraints and intermediate diagnostics. This pass did not run Unreal or import a Forge result into it. |
| [Hi3D official API platform](https://platform.hi3d.ai/) | Official indexed page identifies Sparc3D/Ultra3D-backed image-to-3D generation. Direct fetch timed out in this pass; indexed content is partial. | Plausible match for the owner's Hi3D wording; preserve the fetch limitation. Do not substitute the unrelated Hunyuan3D name. |
| [Hi3D 1.0 official release page](https://www.hi3d.ai/hi3d-1-0-open-source) | Describes the earlier Sparc3D release and links separately to code, weights and a demo; describes newer geometry/texture tiers. | Code availability, weight availability, exact rights and live fidelity are separate questions. No linked release, weights, deployment or quality claim was independently qualified. |
| [Artlist 3D generation how-to](https://help.artlist.io/hc/en-us/articles/39755194637597-Artlist-AI-Tools-Generating-3D-Models) | One user library fronts several generation models, with text/image input, quality selection, orbit/zoom and model-dependent exports. It explicitly says rigging/animation/texture prompts are unavailable in that 3D flow. | A unified library is a useful interface, not evidence of one proprietary geometry algorithm. Keep downstream edit/rig ability visible rather than assuming a generated asset has it. |
| [Meta SAM 3D overview](https://ai.meta.com/sam3d) | Separate object and body models; object shape/pose precede detail/texture refinement; body estimation separates skeletal and surface representations. | Separate observed mask/keypoints, estimated pose and invented hidden shape. Keep each reconstructed object independently editable. Architecture description, not a CPU implementation recipe with equal learned priors. |
| [SAM 3D Objects official repository](https://github.com/facebookresearch/sam-3d-objects) | Image plus selected mask is a first-class inference input; examples use fixed seeds and support posed objects and shared scene context. Code/checkpoints carry the SAM License. | Keep selected regions, coordinate frames and source attribution through export. No checkpoint was downloaded or executed; exact licensing has not been approved for vendoring. |
| [SAM 3D Body official repository](https://github.com/facebookresearch/sam-3d-body) and [installation guide](https://github.com/facebookresearch/sam-3d-body/blob/main/INSTALL.md) | Body recovery accepts optional masks/keypoints; examples and installation require model checkpoint access. The representation separates skeleton and surface. | Native interactive fitting can use explicit owner measurements/keypoints and an existing parametric body. That bounded method cannot claim SAM's learned single-image recovery. |

Hunyuan3D is a distinct system, considered only as a cross-check after finding
it behind Artlist's model selector. Its [official 2.1 source
README](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) separates shape and
PBR paint pipelines and lists substantial GPU memory requirements. It is not
the chosen interpretation of “Hi3D,” and its hosting is not the solution selected
for this owner-directed CPU-native build.

## Why the existing native creature output has a low ceiling

These are source observations at the beginning of this cycle, before the
parent's new native repairs:

1. `imagination.py::_meaning` reduces prompts to membership in a small token
   vocabulary. It does not parse negation, detailed requested anatomy, material
   semantics or exact feature counts. A fluent request is therefore much richer
   than the constraint system actually used to build its mesh.
2. `creature_meshes` creates body/head ellipsoids, beam-based limbs/tail/horns,
   small eye volumes and doubled flat wing triangles. They are real original
   geometry, but they are not an anatomically sculpted, continuously joined
   surface. More variants of these same rules do not create broad semantic
   understanding.
3. `_score` ranks a deterministic complexity heuristic. More legs/horns/armor
   can improve its score without improving the requested silhouette, anatomy,
   deformation, texture coherence or visual appeal. Its existing comments
   correctly deny that the score proves creativity.
4. `glb.py::export_glb` emits positions and normals plus material factors;
   the examined exporter does not emit UV coordinates, image textures or
   tangent-space detail maps. `materials.py` provides useful scalar PBR
   contracts, but scalar roughness/base color alone is not a full textured
   skin/scale/fabric surface pipeline.
5. `meshqa.py::analyze_mesh` catches invalid indices and degenerate triangles.
   Its passing result does not establish closed topology, self-intersection
   freedom, plausible anatomy, consistent deformation or attractive render.
6. `generative_backends.py` deliberately performs preflight/planning, and
   `adapters.py::UnavailableNeuralAdapter.run` refuses unavailable inference.
   A registry of models is not an active generator. This honesty should remain.

These observations explain a bounded part of the quality gap. They are not a
whole-product defect count, benchmark against paid services or claim that
every world/human/FX path has the same limitations.

## Native decisions and acceptance

| Decision | Original MGR work and existing owner | Required proof; current research status |
|---|---|---|
| **ADAPT: explicit creation constraints** | Extend the original prompt-to-genome path in `imagination.py`; enforce exclusions/counts rather than merely detecting words. Keep deterministic seeds. | Contradictory/unsupported input handling, exact requested anatomy tests, saved request/genome correspondence and unchanged replay rules. Parent owns implementation/qualification. |
| **ADAPT: better local geometry before larger mesh counts** | Replace crude beam silhouettes where appropriate with bounded tapered jointed/radial geometry inside the existing creature construction path. Reuse `morph_engine.py` and current rig ownership. | Finite/nondegenerate geometry, silhouette and joint attachment checks, stable identity, independent Blender reopen, same-camera baseline/candidate renders and explicit remaining continuity limits. Parent owns implementation/qualification. |
| **ADOPT: staged inspect/revise/reopen** | Reuse original job journals, native status readers and artifact hashes. The new Saved Creations navigation is the parent's implementation in this cycle. | Actual authenticated browser reopen after restart, exact downloaded bytes, no duplicate generation, interrupted/corrupt state visible. Not a separate asset database. |
| **ADAPT NEXT: native surface production** | Extend the existing mesh/export/material owners with UV-aware procedural scale/skin/fabric maps, separated geometry/material seeds and explicit texture lineage. | UV coverage/seams and tangent tests; normals/roughness/metallic maps independently inspected in Blender under multiple lights; no baked lighting masquerading as physical material. Specified only in this research; not built by this pass. |
| **ADAPT NEXT: selected-region and keypoint fitting** | Build on `segmentation.py`, `unclothe_3d.py`, `reference_pack.py`, `character.py`, `garment_fit.py`, `rectify.py` and current silhouette reconstruction; accept explicit owner masks/views/measurements. | Calibrated reference fixture, projected silhouette/keypoint error, uncertainty labels on hidden geometry, saved source/coordinate frame and editable output. Do not relabel a relief/visual hull as learned 3D recovery. |
| **ADAPT NEXT: scene relationship and motion acceptance** | Reuse scene-layer/world/camera/perception/rig owners for object IDs, placement constraints, camera presets, joint ranges and independent motion frames. | No unwanted overlap, stable coordinates, reopened scene and observed deformation over clips. Unreal and cinematic examples inform principles; no proprietary code port or new scene authority. |
| **DEFER: hosted learned generation** | Preserve existing replaceable adapters and rights gates; no provider or local giant-model dependency added to this CPU-native cycle. | Would need separate explicit model rights, resource budget and actual inference/output acceptance. Owner's no-large-model-hosting direction governs current work. |
| **REJECT: inferred parity or hidden-surface certainty** | Do not market simple rules as equivalent learned reconstruction or claim unseen anatomy is measured. | A public demonstration, documentation feature, source name or passing structural GLB test cannot establish that claim. |

The no-large-model direction is compatible with substantial native improvements:
better explicit shape constraints, original parametric surfaces, procedural
materials, fit controls, pose tools, scene composition and reliable recovery.
It does not by itself solve arbitrary single-image semantic reconstruction.
Keep that distinction visible while finishing each usable native stage.

## Reproducible next comparison

Use one owner-approved brief and fixed seeds; preserve the old GLB and render
before changing construction rules. Record requested anatomy/material/style,
actual genome, geometry counts/bounds, negative constraint cases, independently
reopened Blender facts and fixed-camera renders under at least two lights.
Evaluate silhouette, surface quality, articulation, editability, file size and
recovery separately. Measure runtime on the same machine. Provider comparison
requires actual independently obtained licensed output; documentation alone
does not create a numeric quality or speed result.

This file records research findings and proposals only. Delivered changes,
exact source pins, executed tests, REA evidence and remaining work belong in
the existing `docs/HANDOFF.md`, feature register and final build evidence.
