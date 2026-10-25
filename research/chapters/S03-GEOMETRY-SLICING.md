# S03 — MGR Geometric Truth: space, solids, sections, and print intelligence

**Decision:** Own the geometry *contracts, validation, inference labels, conversion rules and test suite*. Use deterministic CPU geometry first. Keep high-precision CAD, third-party repair libraries and physical printer toolpaths behind optional, licensed, version-pinned adapters. This capability supports character construction, separable wardrobe, interactive worlds, machine-readable scenes and physically printable assets; printing itself is a distinct machine-validation lane.

**Status (2026-10-25):** research + implementable specification. Forge already contains foundational `forge/spatial_truth.py` (`slice_mesh_at_height` returns raw segments; stereo ray geometry) and `forge/meshqa.py` mesh checks. Existing code is **not** a polygon stitcher, BRep kernel, exhaustive topology verifier or G-code generator. No implementation in this packet is claimed complete and no independent hardware benchmark was run for this research.

## 1. What it means, and why Forge needs it

3D is stored using several incompatible descriptions of shape. MGR needs a truthful translation layer rather than declaring every triangle soup a solid. A triangle mesh is enough to draw a surface, but it may contain holes, duplicate points and inward-facing triangles. A fabrication-ready solid additionally needs closed and consistent boundaries, positive measurable thickness, manufacturing tolerances and machine-specific suitability. A 2D image may constrain visible surface appearance but **cannot uniquely establish the hidden back of a 3D object**.

## 2. Representation and data schema

| Form | Geometry truth | Best MGR use | Main loss on conversion |
|---|---|---|---|
| Indexed triangle mesh | Vertex positions + indexed faces + normals/UVs/attributes | Real-time worlds, costumes, final exports | No exact radius, hole or CAD feature history |
| Boundary representation solid | Topological vertex/edge/wire/face/shell/solid and analytic curves/surfaces | Precise props, product dimensions, booleans | Tessellation loses analytic precision |
| Signed-distance/implicit field | Distance/inside-outside query over space | Sculpt unions, terrain caves, remeshing, collision | Sampling resolution can erase thin features |
| Voxel/volume | Discrete 3D cells/density | Smoke, occupancy, terrain, visual effects | Memory grows cubically with resolution |
| Point cloud/surfels | Samples with positions, optional normals/colors | Scans and reconstruction evidence | Often has no closed surface or watertight topology |
| Scene hierarchy | Mesh instances, transforms, materials and semantic groups | Worlds, independently animated clothes | Flattening loses identity and editability |

All MGR contracts must declare `schema`, `coordinate_system`, `up_axis`, `units`, `object_id`, `source_observation`, `confidence`, `transform`, `topology_report`, `precision_policy` and `provenance_ref`. Define canonical internal **meters, right-handed XYZ, Y-up** (matching the existing `slice_mesh_at_height` horizontal Y plane); exporters convert explicit units and axes. A `pose` is an animated transform/skeleton state, not a different character identity.

## 3. Actual end-to-end production paths

**A. Character/game asset:** concept + multi-view observations → owned mesh/sections → topology cleanup and quad-retopo → distinct body/hair/coat/shirt/trousers/boots/jewelry → skeleton and deformation validation → UV/materials/LODs/collision → GLB or target engine import → inspect from all angles and poses. Skinning checks are mandatory even when still-image QA passes.

**B. World:** terrain and structure generators → scene graph with object semantics → CSG/geometry operations for roads, caves, interiors → watertight collision where required → navmesh, portals and dynamic obstacles → streaming/LODs/occlusion → gameplay camera walkthrough → repeatable screenshots, collision and traversal tests. A visible building facade is not proof its interior exists.

**C. Printer:** dimensioned parametric solid or scanned mesh → BRep or manifold mesh repair → 3MF/mesh interchange with units → layer-plane sectioning → segment stitching into ordered closed contours (outer boundaries, holes, islands) → offset shells and supports/infill → machine/profile-specific toolpaths and G-code → printer simulator/preview and physical safety validation. A sliced picture by itself cannot control a printer.

## 4. Mathematics worth implementing natively

- Robust orientation predicates (2D/3D signed determinants), line-plane and triangle-plane intersection, triangle-triangle contact, point-in-polygon/solid, barycentric coordinates, normals, curvature and bounding-volume hierarchies.
- Mesh connectivity: half-edge or winged-edge adjacency, connected shells, face winding, boundary cycles, Euler characteristic and orientability. Watertight, manifold, non-self-intersecting, consistently oriented and positive-volume are **different** properties, all independently tested.
- Computational shape: constructive-solid-geometry union/subtract/intersect; polygon arrangement and winding rules; signed-distance Boolean combinations; constrained triangulation; simplification preserving seams and silhouette; remeshing and surface projection.
- Stable geometry tolerances: use unit-aware epsilon and robust predicates, never an undocumented universal equality threshold. Explicitly classify coplanar/tangential/ambiguous intersections instead of silently discarding them.
- Physics-facing shapes: triangle mesh for static visuals/collision, convex hull/decomposition for dynamic bodies, SDF for volumetric proximity. Game-engine representation and printer solid can share inputs while demanding different acceptance gates.

## 5. External research translated into owned capability

The robust geometric-kernel literature and CAD systems establish that meshes, BRep, booleans, repairs and sectional contours are separate solved subproblems. A production slicer additionally handles support, material, printer settings and machine commands. The MGR lesson is to **compose transparent stages and preserve evidence**, not copy another software's source or label an image as a manufactured object. Source details and copyrights are recorded exclusively in [S03 external provenance](../external-provenance/S03-GEOMETRY-SOURCES.md); this chapter is the MGR-native design authority.

## 6. Repository and algorithm candidates

First ship a small Python core with deterministic predicates and fixed fixtures for mesh validation, sections and contour building. An optional C++/Python native library can accelerate million-triangle work when evidence justifies it. CAD precision deserves its own adapter; a separate printer runner may invoke an **installed approved slicer** as an external process without mixing its source into Forge. Selection gates: proven license, version pin, reproducible install, time/memory limits, tests against corrupted geometry and rollback. No external candidate is currently admitted as a bundled Forge dependency under this research.

## 7. Models, training and data

Geometry truth should not depend on a hallucination-prone generative model. Any future vision-to-shape model may propose `INFERRED` mesh regions, surface normals, missing edges, thickness or likely object parts; the deterministic layer marks and tests them. Start with generated analytic fixtures, hand-authored properly licensed reference models, and consented MGR assets. Real-world print-model failure corpora and analytic CAD corpora are promising research benchmarks but require **per-asset rights verification** before download, training, redistribution or commercial shipping. No training run or accuracy number is claimed.

## 8. Licensing and intellectual-property gates

Architecture and mathematical ideas can be independently implemented; literal source code, pretrained weights, named examples and datasets carry licenses. Some production slicer source and geometric modules impose GPL/AGPL or commercial licensing; a general upstream name is not proof that every internal module shares permissive terms. If a component must be integrated, record exact upstream SHA, dependency tree, licenses and legal approval. Keep external provenance out of public MGR source-of-truth feature names except where attribution is legally or technically required.

## 9. APIs and hardware integration

Expose *local* versioned functions rather than paid-provider calls:

```python
inspect_mesh(mesh, *, units="m", policy="game") -> MeshTruth
section_mesh(mesh, *, plane, epsilon_policy) -> SectionTruth
stitch_contours(section, *, topology_policy) -> ContourTruth
evaluate_solid(mesh_or_brep, *, policy="print") -> SolidTruth
convert_geometry(asset, *, target="glb", preserve_parts=True) -> ConversionReport
```

These are proposed interfaces, **not existing callable Forge functions**. Machine operations need separate `compile_print_job(approved_solid, signed_printer_profile)`, with no default hardware send command. For cloud orchestration each stage records input/output hashes, deterministic settings, visible warnings and capped cost.

## 10. Native MGR product invention: Geometric Truth Core

Build one verification spine with named contracts:

1. **MGR MeshTruth** — indices, finiteness, degenerate/duplicate faces, winding, boundaries, seams, component identities.
2. **MGR SectionTruth** — plane pose, line segments, coplanar classifications, topology uncertainties.
3. **MGR ContourTruth** — closed ordered rings, nested holes, island groups, winding, contour tolerance, explicit disconnected components.
4. **MGR SolidTruth** — closed/oriented/self-intersection/thickness/volume checks; clear `visual_only`, `game_ready`, `cad_precise`, `print_candidate` labels.
5. **MGR Multi-View Truth** — observer camera, visible geometry, occlusions and inferred regions, with verification against a novel pose/view.
6. **MGR Part DNA** — body/coat/boots/hair/accessories stay independently addressable through LOD/export, collision and rig updates.
7. **MGR World Anatomy** — buildings, surfaces, interior/exterior, traversable regions, collision fields and streaming cells have verifiable links.
8. **MGR Fabrication Boundary** — print profile, machine/material, output preview and manual authorization are outside visual-render acceptance.

Never silently promote `INFERRED` geometry to `OBSERVED` geometry. Maintain immutable observation and review history when repair algorithms invent missing faces. A geometric repair that changes appearance must trigger multiview review.

## 11. Compute and GPU requirements

Basic mesh inspection, adjacency, plane slicing, simple booleans and contour stitching run on CPUs. Naively intersecting `T` triangles against `L` layers costs `O(T×L)` checks; Y-range buckets/BVH and per-layer active triangle sets substantially reduce practical work. GPU compute can accelerate batch work but is **not necessary** to validate an ordinary asset or make section contours. High-resolution neural reconstruction, neural rendering and photoreal path tracing are different compute-intensive problems. Benchmark exact hardware rather than promise “GPU-free everything.” Bound triangle count, workspace memory, runtime and mesh decompression bombs.

## 12. Cost and operational tradeoffs

The native Python baseline has no per-call vendor API fee; its costs are development, testing and local CPU time. Precision CAD modules and commercial/AGPL dependencies may add license/compliance expense. If print automation is later added, material/printer maintenance, safety validation and machine configuration are nonoptional. An inexpensive image-to-mesh output with unresolved topology often costs more downstream artist and QA time than a verified structured mesh.

## 13. Known breakpoints to design against

- Nonmanifold edges, multiple shells, internal faces, holes, T-junctions, slivers, duplicated faces, self-intersection and inverted normals.
- Tiny features vanishing under tessellation, floating-point scale changes, unit mismatch, coplanar ambiguities, exact vertex-plane hits and touching contours.
- Correct 2D silhouette from one view but false thickness or impossible hidden anatomy; fake limbs/hands behind foreground; clothing fused to body; bones or skin weights failing on rotation.
- Z-fighting and material seams in games; collision meshes not matching visible geometry; navmesh traversability errors.
- Printing without checking overhang, thickness, material shrinkage, slicing profile, support and printer-specific physical constraints.

## 14. Measurement and visual evaluation

Store machine-readable reports: `bad_index_count`, `nonfinite_vertex_count`, `degenerate_area_count`, `boundary_edge_count`, `nonmanifold_edge_count`, `face_orientation_conflicts`, `self_intersections`, `component_count`, signed `volume_m3`, `minimum_wall_thickness_m` when measurable, `contour_open_count`, per-layer ring/holes count, generated/approved region coverage and tolerance assumptions. For reconstructed objects report multi-view silhouette intersection-over-union, symmetric Chamfer/Hausdorff distance when ground-truth meshes exist, normal-angle deviation, and rig/clothing penetration across poses. A perceptual pixel match cannot substitute for topology or 3D identity.

## 15. Integration placement

Extend the existing geometry/QA lane anchored by `forge/spatial_truth.py` and `forge/meshqa.py` without modifying their contracts blindly. Keep section-to-contour and BRep conversion separate modules, with tests in `tests/`. Character assembly and wardrobe use Part DNA; world builders use terrain solids, collision/navmesh and streaming; exporters require GLB/3MF part preservation checks. Blender is an optional graphical/manual headless verifier rather than the only implementation path. Any build registration should cite the implementer’s actual code/test evidence, not treat this research as shipped functionality.

## 16. Repeatable acceptance matrix and order of build

| Gate | Input | Required result | Status |
|---|---|---|---|
| G1 plane segment truth | Unit cube sliced at mid-height | Finite correct intersections, explicit coordinate units and plane transform | Existing raw segment prototype; regression suite required |
| G2 contour topology | Cube section, donut cross-section, two disconnected cubes | Closed ordered loops, interior hole and independent island counts | **OPEN** |
| G3 degenerate safety | Coplanar face, touching tip, zero-area face, near-parallel plane | Classified ambiguity and bounded output, never fake closed contour | **OPEN** |
| G4 real mesh QA | Corrupt indices, nonmanifold Y junction, inverted shell, self-intersecting solid | Distinct flags; correct invalidation; no silent repair | Existing basic mesh QA; comprehensive checks **OPEN** |
| G5 precision & transforms | Millimeters→meters→3MF/GLB, rotated/up-axis switched asset | Stable dimensions/tolerances; original part identities intact | **OPEN** |
| G6 geometric scaling | 10k, 100k and 1M triangle legal meshes across many sections | Measured wall time, peak RAM and no uncontrolled explosion | **OPEN, hardware-dependent** |
| G7 living character | A/T-pose and 10 extreme poses with distinct wardrobe/hair/boots | No missing hands, intersections beyond threshold or merged wearables | **OPEN** |
| G8 game-world truth | Building with traversable interior and collision test route | Visual/collider/navmesh agree; full orbital/free camera QA | **OPEN** |
| G9 3D-print interchange | Valid solids + labeled multi-part 3MF with units | Independent slicer opens correct component count/dimensions, preview surfaces/errors | **OPEN** |
| G10 safe fabrication | Target printer/material profile | Independent slicer G-code preview plus explicit human approval; no unsanctioned send | **OPEN** |

**Build sequence:** (1) normalized mesh contract and comprehensive QA; (2) robust section and contour topology; (3) remesh/repair evidence; (4) scene/part preservation and multi-view verification; (5) optional CAD and 3MF adapters; (6) live printer path only after full machine safety review. Deliver vertically across character, world and physical-print sample fixtures; no benchmark is accepted without exact machine/settings/version and recorded pass criteria.

**Verification honesty:** these ten gates are forward acceptance criteria, not ten passing tests. The named open items are not complete merely because the research packet exists. The immediate usable outcome is a representation-aware implementation specification and license-gated source map.
