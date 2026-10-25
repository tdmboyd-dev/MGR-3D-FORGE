# S09 — External Technical Provenance and Research Depth

**Date:** 2026-10-25. **Scope:** Primary-author technical guides/specifications inspected to inform the independently authored, MGR-native product design at `research/chapters/S09-MODELING-SCULPT.md`. External names are recorded here for traceability only, not as MGR product names. Documentation inspection is not the same as executing, auditing or vendoring the source.

| Primary source | Exact reference | Documented observation | Inspection level and gaps | Native synthesis / proof demanded |
|---|---|---|---|---|
| Blender Foundation | https://docs.blender.org/manual/en/4.0/modeling/meshes/retopology.html | Retopology repairs/reorganizes topology after rough sculpt or remesh for downstream deformation. | Read official overview; exact installed-version operations and algorithm source not audited. | Distinguish silhouette refinement, remesh and animation-ready edge-flow verification. |
| Blender Foundation | https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/multiresolution.html | Multires lets an established base mesh be sculpted at additional subdivision levels; high-detail edits can be worked back to usable geometry/bakes. | Read current official manual; pin Blender runtime and verify sculpt displacement preservation. | MGR reversible sculpt stack plus high-to-low detail transfer. |
| Blender Foundation | https://docs.blender.org/manual/en/3.4/sculpt_paint/sculpting/tool_settings/remesh.html | Voxel remeshing generates dense, more uniform surface topology from form; this does not prove deforming edge loops. | Official technical manual only; benchmark voxel size, fine detail loss and open/multiple shell cases. | Stage-specific `form remesh` pass and separate retopo proof. |
| Blender Foundation | https://docs.blender.org/manual/en/5.4/modeling/meshes/uv/editing.html | Seams, island packing, pinning and chart decisions affect continuity and UV edits. | Official manual only; renderer-specific tangent/UDIM support not verified. | Per-corner UV islands, stretching, seams, margins, export checker fixtures. |
| Blender Foundation | https://docs.blender.org/manual/en/5.0/animation/shape_keys/workflow.html | Shape key authoring assumes stable topology; vertex additions/deletions later risk invalidation and remapping. | Official manual only; precision round trips and vertex compatibility still untested. | Morph/shape-key stable vertex-order gate. |
| Blender Foundation | https://docs.blender.org/manual/en/4.0/physics/cloth/settings/collisions.html | Cloth collision/self-collision controls are part of animated clothing evaluation. | Official manual, older release: compatibility must be checked on user installation. | Clothing pose-sweep, collision intent and forbidden penetration report. |
| Blender Foundation | https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/simulation/cloth_dynamics.html | Newer Geometry Nodes cloth dynamics is flagged experimental and its documented limitations include missing self-collision. | Version-specific snapshot; no claim this is preferred stable production solver. | Keep cloth backend swappable and validation backend-independent. |
| Khronos Group | https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc | glTF primitives encode mesh attributes, skinning, material slots and morph target deltas. | Official interchange specification reviewed; current exporter implementation and external readers not yet compared for S09. | Portable export checks by opening actual JSON/buffers and independent GLB import. |
| Khronos Group | https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/schema/mesh.primitive.schema.json | Per-primitive index/accessor and target attribute schema establish structural constraints. | JSON schema consulted; does not itself prove rendered likeness/material correctness. | Schema gate plus independent render/pose verification. |
| Pixar Animation Studios/OpenUSD | https://openusd.org/dev/user_guides/primvars.html | Mesh-scoped primvars support geometry-indexed texture and data interpolation semantics. | Official user guide reviewed; no MGR USD adapter exists yet. | Optional large scene/wardrobe metadata and UV interoperability lane. |
| Pixar Animation Studios/OpenUSD | https://openusd.org/dev/api/_usd_skel__schemas.html | Skeleton binding includes joint indices/weights and correspondence handling. | Official API/reference inspection only; no end-to-end renderer/USD integration. | Optional skeletal output contract with explicit per-vertex influences. |
| Prusa Research | https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135?product=core-one | Physical wall sizes, nozzle/print resolution and dimensional error differ from screen-smoothed mesh appearance. | Primary manufacturer practical guide, not universal physics; profile depends on specific printer, nozzle and material. | Separate printable-solid gate, thickness/cross-section fixtures and actual slicer analysis. |

## Cross-cutting findings that prevent premature completion claims

1. A dense detailed sculpt and an animation-ready low-poly skinned character are *different deliverables*; retopology, UV, weight painting and deformation tests connect them.
2. UVs cannot be validated by geometry positions alone; face-corner mapping can differ at seams and the target material/sampler must be checked.
3. A wardrobe manifest naming `coat`, `shirt`, `boot` etc. proves organization, not their ability to fit, deform or simulate. Check overlap and rigged attachment across time.
4. Image similarity after a camera/pose change is not an identity oracle: use common camera registration, 3D landmarks, depth/shape metrics and independent multi-angle renders.
5. A water-tight printable figurine is not necessarily a correct animated game character; open game meshes are not automatically invalid, while manufacturing requires positive volume and process-specific feature-size checks.
6. Source code, trained weights, scanned humans, demonstration models, textures and assets can have *different licenses*, even within the same upstream repository. Pin each before importing; none was copied into this research deliverable.

## Research gaps and execution triggers

- **Version fit:** discover installed Blender build and its sculpt/UV/export feature set; author reproducible headless `.blend` pipeline receipts.
- **Algorithm audit:** independently test remeshing, edge-manifold detection, UV chart packing/overlap tolerance and curvature-sensitive LOD; evaluate accuracy/performance on representative fixtures.
- **Anatomy:** secure licensed/owned proportion references and private subject/likeness approvals; no identity reference was accessed or stored here.
- **Production exchange:** render imported exported GLB with a second viewer/engine; compare morph/skin weights, UV tangent basis and material sample outputs.
- **Print profile:** obtain actual target printer/slicer/nozzle/material profile; verify physical thickness and warnings rather than hard-code a universal millimeter threshold.

**Evidence posture:** Primary reference review is complete for the targeted S09 research packet; third-party implementation audits, benchmark executions and the new production pipeline are still open and must receive independent receipts before any `BUILT`/`VERIFIED` claim.
