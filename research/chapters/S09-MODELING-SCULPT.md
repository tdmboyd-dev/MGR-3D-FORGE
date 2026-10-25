# S09 — MGR Native Form, Sculpt, Character and Wardrobe Fabrication

**Owner:** Money Grind Religion. **Research date:** 2026-10-25. **Research maturity:** PRIMARY TECHNICAL REFERENCE REVIEWED / contracts proposed. **Implementation maturity:** Existing procedural mannequin, detachable part inventory and basic mesh validation verified by code inspection; no claim of professional likeness, sculpt, retopology, fitted garment simulation, UV production or production-print verification. This chapter is the native product source of truth. Technical source URLs/attribution remain separately in `research/external-provenance/S09-MODELING-SOURCES.md`.

## Quick verdict

A genuinely professional 3D character cannot be produced by adding more boxes or increasing polygon count. The pipeline needs a coherent **shape-to-mesh-to-usable-character contract**: designed anatomy and silhouette, high-detail editable sculpt, deliberate low-resolution edge layout, stable UV/material coordinates, valid skeleton deformations, separable and properly fitted clothes, measurable render quality and variant-specific export tests. A visually pleasing still image does not prove any of those. The MGR breakthrough should be to make the entire character *revisable from plain English*, then let the engine show exactly which stage and which objective tests passed.

## 1. Definition and scope

Modeling converts an authored specification into explicit spatial surfaces (polygon meshes, parametric patches, subdivision surfaces or signed-distance/voxel fields). Sculpting edits surface form at high resolution; remeshing changes topology; **retopology** deliberately rebuilds edge connectivity for animation and baking. **UV unwrapping** maps 3D surface coordinates to 2D domains for image-backed materials; vertices may need duplicated UV corners at seams even when the 3D position is shared. A **shape key** changes compatible vertex positions without changing topology. **Modular wardrobe** is a set of independently editable, rig-compatible components with attachment, fit and collision metadata—not just names in a manifest. **Print preparation** is a distinct output contract: watertight closed shells, positive material volume, minimum physical feature thickness, correct unit scale, orientability and slicer verification.

## 2. Production use cases

- Tevin-style original character creation: correct complete hands, proportional arms and joints, identity-controlled silhouette, neutral T/A pose and facial motion range.
- Full modular wardrobe: body, hair, shirt, coat, trousers, boots, chain, rings and future wearables each authored and exported independently.
- Game characters: low/high LODs, moving joints, skinning, morph expressions, texture maps and collision capsules.
- Cinematic characters: fine pore/fabric detail, controlled subdivision and close-up topology, high-quality displacement/normal maps.
- World assets: hard-surface props, terrains, organic creatures, buildings and editable procedural variants.
- Physical objects: figurines/sculptures with **print-specific** meshes; these differ from hollow/open and one-sided game surfaces.

## 3. Standards and unambiguous interchange contracts

- MGR scene-space contract uses meters and Y-up, consistent with `forge/geometry.py`. Declare mesh transforms, scale and winding, and never silently change handedness.
- Production mesh schema should preserve indexed positions, corner normals/tangents, UV sets, per-face material groups, seams, vertex colors, blend shape deltas and skin joint indices/weights where used.
- glTF mesh primitives support material assignments, texcoord attributes, morph targets and skin joint weights. **Parts exported as individual GLBs are not automatically independently skinned.** Test the exported GLB's actual JSON/buffer attributes and an independent import.
- USD's mesh/primvar and skeleton schemas are an optional future interchange lane for complex shot assembly, variant inheritance and animation; do not conflate a research candidate with a verified current backend.
- Units for printing are explicit millimeters at export; source character scale remains meters and the conversion factor is recorded.

## 4. Scientific and artistic foundations

Geometry: polygon connectivity, surface orientation, manifoldness, normals, UV parameterization, surface curvature, subdivision and sampling. Anatomy: landmarks, proportions, muscle/articulation volumes, asymmetry, joint pivots, landmark persistence through poses. Visual truth: multi-angle orthographic/perspective presentation, silhouettes, shadow consistency and registered image/3D comparisons. Numerical proof: edge incidence, connected components, geometric degeneracy, self intersections, mesh-to-reference distances and uncertainty intervals. Perceptual identity is **not** proven by arbitrary-view pixel similarity; pose/rotation-aware comparison needs camera-normalized rendering and anatomical landmarks.

## 5. Open implementation families and specific lessons

| Family | Lesson | Status and MGR decision |
|---|---|---|
| Blender modeling/sculpt system | Subdivision/multires, voxel/dynamic remesh and manual retopology form distinct operations; a dense sculpt is not a usable deforming base mesh | Official docs reviewed; use installed Blender through the native controlled bridge, do not clone its entire source |
| Blender UV/editor and shape key system | Seam-aware unwrap and stable vertex IDs are central to reproducible texture and facial expressions | Official docs reviewed; create a native specification plus controlled Blender tests |
| Blender cloth simulation | Cloth must be evaluated over frames, with collision/contact checks; Geometry Nodes cloth simulation remains experimental in latest docs, with noted missing self-collision | Official docs reviewed; select stable supported backend per installed version, verify independently |
| Khronos glTF format | Portable triangles/materials/skin/morph contracts for real-time use | Official specification reviewed; use as output acceptance oracle, not as a promise of all cinematic features |
| OpenUSD geom/skel | Primvars, geometry sets and skin binding express advanced asset assemblies | Official schemas reviewed; optional scene/wardrobe interchange research, not yet integrated |
| Prusa print engineering | Slicer/tooling constraints (feature thickness, resolution, shrinkage) differ from on-screen smoothing | Manufacturer primary technical guide reviewed; require print-profile-specific acceptance |

Source names and links belong only in the provenance ledger, keeping feature labels fully MGR-native.

## 6. Neural models and generative tools

Neural image-to-mesh, text-to-mesh, multiview diffusion and mesh-reconstruction models can supply **candidate** shapes or texture maps. Their output is not inherently watertight, rigged, topologically sensible, likeness-faithful or commercially licensed. Every adapter needs explicit input provenance, model+weights license, version, memory budget, expected topology class, uncertain details warning, export format and objective validators. **No generative model or GPU is necessary for basic CPU mesh generation, topology analysis, procedural wardrobe parts, UV coordinate transforms or GLB validation.** High-end learned synthesis and detailed GPU renders may require significant VRAM and time; benchmark before selecting hardware.

## 7. Data and reference strategy

Use owned synthetic baseline meshes first: deterministic jointed figures; cubes, cylinders, rings and shells with known edge counts; manifold and nonmanifold fixtures; authored UV chart checker patterns; multi-camera render fixtures; cloth contact stress poses; slicer-sized thickness calibration blocks. For owner-provided identity images, maintain a private reference store outside this public repository and record only non-identifying manifest IDs/hashes. Reference photos require consent, rights and private handling. Public anatomy/scan datasets are only candidates until licenses, identities, commercial rights and allowed derivatives have been audited.

## 8. Licensing and provenance

Mathematical concepts and independent algorithms may be implemented natively. Copying snippets, sculpt brushes, character base meshes, assets, scans, clothing patterns, neural weights or benchmark images can carry different license limits. Audit source code, example assets and weights **separately** at pinned revisions. Never package private likeness/owner references in public fixtures. Maintain supplier/provider fields in machine receipts if externally generated content is admitted.

## 9. Interfaces and tool adapters

Proposed native contracts: `FormRecipe` (purpose, height/units, anatomical landmarks, front/side/depth silhouette), `SculptStack` (ordered editable operations with seed/version), `TopologyProof` (mesh edge and deformation contract), `UVProof` (coverage, overlap policy, stretch), `RigBindProof` (influences and poses), `WardrobeFitProof` (garment-to-body clearance and intended contact), `OutputProfile` (`game`, `cinematic`, `print`) and a signed/hashed visual-quality receipt. Blender scripting is a swappable execution backend, not the source-of-truth. Optional engine/slicer/AI adapters must use explicit capabilities and tested version guards.

## 10. MGR-native design — Form Intelligence pipeline

1. **MGR Shape Intent:** convert prompt, design sheet or owned images into labeled dimensions, material categories, silhouette constraints and pose targets. Preserve what is unknown.
2. **MGR Full Body Truth:** proportional landmark graph for head, torso, shoulders, elbows, wrists, each hand and finger, hip, knees, ankles and foot extremities, with a camera-framing margin gate. A missing hand is a hard failure.
3. **MGR Volumetric Draft:** deterministic body volumes or signed-distance union/difference, with controls for stature, limb thickness, head shape and stylization, while keeping editable components.
4. **MGR Sculpt Memory:** operation history with high/low form scales; reversible layers, symmetry policy, high-resolution displacement source and retained base mesh. Sculpt detail need not imply a giant game mesh.
5. **MGR Flow Weaver:** remesh for form, then retopologize for deforming joints: wrist/finger loops, elbows, shoulders, hips, knees, lips and eyelids where needed. This is a separate operation from voxel remesh. Preserve approved silhouette within tolerance.
6. **MGR UV Cartographer:** seam charts, per-corner UV indexing, checker validation, UDIM strategy when target supports it, island margins, normalized density and distorted-area receipt; bake high-resolution form onto low-resolution assets with ray cage controls.
7. **MGR Surface Compiler:** tangent-space normal, color, roughness, metalness, opacity/displacement maps appropriate to target renderer, with texture color-space metadata and sample material checks.
8. **MGR Bone & Expression Bridge:** stable bind pose and anatomical pivot graph; 4+ influences when allowed, per-vertex normalized skinning, facial morph support and deformation poses. Freeze or remap vertex topology before shape keys and weights.
9. **MGR Detachable Wardrobe:** separate coat/shirt/pants/boots/hair/jewelry meshes with material slots and garment-specific skeleton/skinning or physical simulation, garment rest states and swap compatibility. Clip/penetration scan across stress poses.
10. **MGR Reality Preview:** rotating, zoomable, multi-camera turntable and side-by-side reference registered against the same pose; produce geometry, seam, skin and material heatmaps rather than one flattering beauty image.
11. **MGR Shape Passport:** versioned lineage for neutral mesh→sculpt→retopo→UV→rig→garments→LOD/print, per-stage receipts, asset hashes, provenance, owner-approval flag and repeatable golden fixtures.
12. **MGR Three-Output Gate:** game exports must pass budget/skinning/UV/material checks; cinematic outputs pass close-up displacement/lighting/continuity; print outputs pass closed-volume, thickness, scale and slicer proof. No single generic “mesh passed” result can substitute for these gates.

## 11. Hardware and runtime

- CPU-first: primitive/parametric modeling, medium-poly editing, edge topology checks, deterministic remeshing experiments, UV chart QA and small-scale baking can run locally.
- Larger high-resolution sculpt, complex cloth, high-resolution textures and rendering can exceed RAM/VRAM; use explicit adjustable face/texture/frame budgets and queue receipts before taking resources.
- Slicing and print validation typically run as separate software steps and do not need to be treated as generative model inference.
- The installed Windows Blender version, available add-ons and actual GPU capabilities must be detected on the user's machine; do not assume Blender rendering or compute capability from a passed CLI object-inspection test.

## 12. Cost and schedule engineering

Avoid recurring 3D-model API charges for basic modeling/validation. The fastest credible path is an independently editable native procedural baseline, Blender-assisted retopology/UV/rig pipeline and automated acceptance with a few representative hero test models. Need time and VRAM benchmarks before dollar forecasts. Design once, reuse neutral/rest mesh, skeleton, attachment semantic IDs and UV contracts across outfits and visual styles. Do not spend expensive render cycles before geometry, hand coverage and deformation gates pass.

## 13. Failure modes, detection and controls

| Failure | Observable defect | Gate |
|---|---|---|
| Cropped/missing arms or fingers | Landmark or render-frame intersection missing | 3D landmark completeness plus 6-view framing |
| Dense sculpt but bad animation | Pinching/collapse at elbow, knees and face | Retopology topology and 12-pose deformation sweep |
| Vertex IDs mutate after retopo | Shape keys/weights become invalid | Stable mesh topology version, remap proof or rebuild |
| Unusable UVs | Checker stretch, flipped islands, texture bleed | UV signed-area, chart stretch and padding fixtures |
| Clothing merged into body | Cannot swap or animate garments | Component mesh IDs, separate bindings and import test |
| Clothing penetrates body | Coats/pants intersect moving body | Collision scan on contact-exempt vs forbidden regions |
| Zero-thickness print | Slicer holes, no physical shell | Closed oriented manifoldness and thickness by printer profile |
| False likeness/quality claim | Generic silhouette labeled owner-approved | Explicit approval and identity evidence gate |
| Renderer-specific pass only | GLB looks different or morphs drop | Independent import/render and morph/skin inspection |

## 14. Quantitative evaluation (pre-register targets)

Report objective measurements per profile: silhouette landmark reprojection error, extremity visibility, triangle count, component/part count, edge manifoldness, degenerate face count, normal/winding consistency, measured UV island overlap and stretch, material/texture coverage, skin influence normalization, pose penetration volume and fraction of bad frames, deformation volume preservation, rendered difference across fixed cameras, export size/import failures, print shell watertightness and minimum-wall pass. Thresholds depend on purpose and resolution: retain numeric configuration with provenance rather than inventing a universal “Hollywood standard.” At minimum gate all invalid/NaN coordinates, index errors, missing hands, missing expected detachable components and claimed printability without slicer evidence at zero tolerance.

## 15. Repository fit and upgrade path

Current evidence from code inspection:

- `forge/character.py`: honest anonymous T/A mannequin with hands, body parts, independent coat, shirt, trousers, boots, hair and chain assets, GLB exports and landmark receipts. **Not a production sculpt, anatomical Tevin likeness or proof of proper rigged clothing.**
- `forge/wardrobe.py`: editable part taxonomy/attachment metadata; explicitly acknowledges rigid weights and no cloth/fit proof.
- `forge/meshqa.py`: finite vertices, index validity and zero-area triangle checks; does **not** check manifoldness, self-intersections, topology, UV charts or printable shells.
- `forge/geometry.py`: deterministic CPU geometry primitives, not arbitrary digital sculpting.

Build increments: `forge/form_intelligence.py` (recipe/landmarks/procedural bodies), `forge/topology_truth.py` (incidence/euler/orientability/components), `forge/uv_truth.py` (per-corner charts/QA), `forge/wardrobe_fit.py` (part/pose fit), `forge/print_truth.py` (shell/thickness/slicer adapter), plus `.blend`/GLB golden fixtures through `forge/blender_bridge.py`. Add fixtures and local tests before claiming any lane complete. Integrate receipts into the existing pipeline; do not create conflicting product authorities or duplicate approval systems.

## 16. Acceptance tests and honest completion criteria

**Core geometry:** A cube has closed manifold edge incidence; open cube fails print but may be valid game mesh; bowtie/nonmanifold mesh and inverted winding are rejected for printing. Degenerate/NaN triangles fail safely. Rescaling checks explicit meters→millimeters.

**Anatomy:** Test T/A and 12 animation poses; hands, fingers, palms, elbows, wrists, knees and soles remain full, correctly connected, independently visible in front, side, rear and elevated shots. Fail a deliberately missing hand, short forearm and camera-cropped hand. Generic mannequin does not pass owner likeness approval.

**Sculpt-retopo:** Given controlled high/low meshes, compare shape deviation using sampled nearest-surface distances; joint loops must deform without severe collapse in elbow/knee/wrist challenge poses. Log vertex count and deformation error; avoid pretending a voxel remesh automatically produces clean topology.

**UV/material:** Checkerboard render across seam/island fixtures, intentional mirrored-island overlap declared, otherwise forbidden overlap rejected. Validate 0..1 charts unless profile explicitly allows UDIM/tile repetition. Tangent-space normal consistency and texture-color-space intent must survive import.

**Garments:** Prove outfit parts retain stable names, independent geometry and transform/rig attachment after GLB round trip; detect unwanted cloth/body penetration over a turntable and pose sweep. Treat deliberate contact and layered garment overlap separately from errors. Ring and chain must be separate parts if selected in recipe.

**Print:** Sphere, hollow sculpt with wall thickness, nonmanifold shell and interpenetrating solids exported to slicer through explicit millimeter conversion. Assert reported slicer volume/feature warnings before marking print-ready. Numerical watertightness alone is insufficient for manufacturability.

**Independent Blender/engine verification:** Pin installed Blender version; run headless creation/open/export, independently reimport GLB, compare part count, unit scale, normals, skin weights, morphs, named UV and material maps. Capture native renders and a machine-generated acceptance receipt containing hashes, camera matrices, thresholds and measured outcomes.

**Current status:** S09 specification and primary-source research are written; **the substantial new modeling/sculpt, retopology, UV and print gates described here are NOT BUILT or VERIFIED yet**. Production completion is achieved only after the above executable tests pass on local Windows Blender and at least one independent target importer/slicer as appropriate.
