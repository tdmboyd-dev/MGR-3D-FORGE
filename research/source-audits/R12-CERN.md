# R12 — CERN Detector Visualization & Simulation Extraction for MGR Forge

**Research wave:** 2026-10-25. **Scope:** four selected first-party CERN/associated open physics-toolkit practices; **not** all CERN detectors, experiments, software, patents or research. A particle event display visualizes measured/simulated tracks and detector structures; **it does not model human-scale fluid/cloth worlds or license those datasets automatically**. Source/rights details appear in `research/external-provenance/R11-R12-SOURCES.md`.

## Four concrete technical techniques

| First-party scientific practice | Actual technical principle | MGR-native creation | Required benchmark |
|---|---|---|---|
| ROOT TGeoManager/TGeoChecker | Nested geometry hierarchy, navigator, overlap/intersection testing | **MGR Spatial Integrity Inspector** | Intentional overlaps/extrusions and traversal queries |
| ROOT REve + CMS iSpy | Show complex semantic geometry and separate time/event track layers interactively | **MGR Truth Overlay Theater** | Scene/event replay and pick/inspect identity |
| Geant4 visualization drivers | Physics transport state separated from multiple renderer backends | **MGR Physics Evidence Bus** | Identical physical trajectories across 2 render modes |
| Geant4 particle transport + CERN event corpus | Boundary/material interactions and Monte Carlo event simulation with reproducible configuration | **MGR Interaction Stress Laboratory** | Geometry boundary/energy checks and event trace provenance |

## 1. Make geometry navigable *and* mechanically self-consistent

**Inspected:** modern ROOT `TGeoManager` documentation and TGeoChecker API notes; ROOT Geometry user manual. Detector geometry is made of nested volumes with a global top frame and children; nested shapes should not extrude out of parents or overlap sibling volumes unless explicitly permitted. ROOT uses `TGeoNavigator` for path and boundary location queries and `TGeoChecker` for overlap sampling. Checking a render from one camera cannot reveal all illegal intersections. A broad/conservative collision pass can detect likely overlaps, while detailed triangle/volume tests refine; sample-based tests may miss very narrow defects unless coverage/resolution is reported.

**MGR-native:** Spatial Integrity Inspector traverses authored world and Tevin rig part hierarchies as typed volumes: `parent_id`, shape/collider mesh, transform, allowed_overlap_pairs, semantic material and source rights. **Acceptance:** insert 10 known defects—sibling box overlap, nested object outside parent, coincident boundary, zero/negative scale, disconnected prop, interior clothing penetration; detect and localize at least those authored fixtures. Record algorithm, precision, sample count and false positives; treat rendered look separately from physical geometry. **Hardware:** native broadphase, AABB and mesh sampling CPU-feasible; very large triangle intersections expensive and need LOD/hierarchy.

## 2. Separate event *truth* from camera/style

**Inspected:** modern ROOT `REve` event display documentation, `REveBoxSet`/calorimeter 3D classes and CERN CMS iSpy browser event display on Open Data Portal. REve is a 3D/web event visualization interface displaying selected object types and paths; CMS iSpy accepts `.ig` event collections and overlays physical collision tracks with detector context. This creates a useful workflow: immutable event payload → semantic layer selection → many camera projections → attributed operator inspection. An image of a scientific event is not the source data itself.

**MGR-native:** Truth Overlay Theater displays world simulation causality over final render: collider surface, trajectories, normals, bones/garments, camera rays, occlusion zones, damage/hit event and uncertain geometry. Director may toggle layers without changing saved physics state. **Acceptance:** a 50-event multi-camera shot, timestamp selection, stable object ID, layer filtering without state mutation, round-trip serialize/reload and matching event counts. **Hardware:** browser/client graphics for visualization, small events CPU parse; large detector-scale assets or elaborate live FX require measured GPU/transfer budget.

## 3. Output-independent simulation receipts

**Inspected:** Geant4 developer guide visualization introduction, Geant4 available driver documentation, executable integration page and example source. Geant4 physics transport and visualization are separate layers: OpenGL/Qt/OpenInventor and output-oriented backends such as DAWN differ but source simulation semantics can be shared. Driver availability depends on installed optional graphics dependencies and build configuration; Geant4 docs explicitly say some drivers are **not incorporated by default**. Visualization is downstream consumer of *simulation steps/events*, not the arbiter of numerical truth.

**MGR-native:** Physics Evidence Bus records every important native event `(scene_revision, time_step, entity_id, pre/post_transform, material, collider_id, contact_impulse, effect_id)` and publishes independent adapters to Blender preview, game overlay and director log. **Acceptance:** same deterministic fixture through two renderers has matching physics state digest, contact timeline and entity IDs, even when shaders/compositing differ; deliberately change camera lighting only and prove no physics receipt change. Beware cross-solver floating-point differences; exact byte parity only under same deterministic backend, with tolerances across others.

## 4. Boundary/material interaction as an auditable chain

**Inspected:** Geant4 official project overview, Getting Started developer guide, upstream basic `B1` example source header and ROOT geometry/navigation docs. Geant4 is a research particle transport toolkit for detailed particle-matter interactions. Its conceptual chain—defined world volumes, materials, incident particles, stochastic interactions, tracking and energy deposits—suggests **a verification discipline**, not a reason to add a heavy particle detector simulator into the first Tevin animation pipeline.

**MGR-native:** Interaction Stress Laboratory generates authored collisions/rays/projectiles/spell beams through layered surfaces with material responses and event accounting. Core math for a simple ballistic projectile remains classical rigid-body dynamics; particle tracks and electromagnetic interactions use completely different physical assumptions. For an energy deposition rule `E_in = E_out + E_deposited + E_other` within declared boundaries, test conservation at the resolution of a chosen simplified model, but do not claim Geant4-grade validity of magical/fire simulations. **Acceptance:** known analytic ray/plane or sphere intersections, repeated seeds, controlled materials/shielding, flux counting, hit/miss event integrity and error logs. **Hardware:** basic rays/contacts CPU, detailed Monte Carlo transport can be high cost; no GPU inference required for the proposed toy tests.

## Rights and source maturity

- **ROOT:** official ROOT site states LGPL-2.1-or-later, with redistribution/linking obligations; pinned version and dependency notice audit required before embedding modules.
- **Geant4:** license is its custom **Geant4 Software License 1.0**, not an assumed MIT/Apache/GPL; read its exact terms for modifications, redistribution and acknowledgment of scientific use.
- **CERN Open Data:** usage is **record-specific**. The inspected CMS example JSON event records list CC0 1.0; other datasets can have different rights, attribution, embargo or access policy. We have **not downloaded** a detector model or event corpus.
- Scientific geometry/event concepts can be studied and implemented natively; the original tools' code, sample events and visual branding remain subject to their own rights.

## MGR acceptance matrix

| Gate | Fixture | Minimum meaningful proof |
|---|---|---|
| Hierarchical geometry | 10 planted overlap/extrusion defects | Defect IDs + bounds + severity, documented miss-rate methodology |
| Event observability | 50 contacts/trajectory events, 4 cameras | Deterministic IDs/time/physics values across UI filters |
| Simulation/render split | Identical physics run, two renderer backends | Same physical receipt, different legal appearance allowed |
| Material response | Ray/solid layers with known entry/exit | Recorded hits, material transitions and conservation budget |
| Asset rights | CC0-like synthetic authored event and restricted sample | Rights gate admits only cleared cases |
| Cost | Run on owner's actual Windows Blender machine | CPU time, RAM, draw calls and frame latency reported, not guessed |

## Best native implementation sequencing

Start with geometry containment/overlap checks and immutable event logs; both are high-value, no-GPU required correctness foundations. Then add multi-view event visualization/scene overlays. Add specialized ray/material diagnostic fixtures after ordinary rigid-body contact tests pass. ROOT/Geant4 SDK embedding is optional and **not justified** without benchmark/licensing evidence for an MGR production requirement.

## What remains unverified

No ROOT/Geant4/CMS iSpy source was installed or executed, no detector geometry dataset downloaded, no full library source audit, no commercial counsel review, no Windows Blender integration and no empirical missed-overlap benchmark in this batch. Full CERN experiments/event display archive, detector precision algorithms and Geant4 Monte Carlo validation are pending. These four selected lessons are useful without claiming CERN physics accuracy for MGR fantasy effects.
