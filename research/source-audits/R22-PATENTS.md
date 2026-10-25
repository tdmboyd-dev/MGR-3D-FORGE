# R22 — MGR original 3D invention with a patent-risk evidence gate

**Decision:** Research patents to uncover engineering directions and potential legal restrictions, while keeping MGR features **independently authored** and making *claim-level legal review* an explicit release gate for high-overlap technology. The fact that a method is described publicly, published in a paper, covered by an open-source repository or familiar from an existing game **does not** prove it is patent-free. This audit is preliminary technical triage, not patent clearance or legal advice.

**Snapshot:** 2026-10-25. Seven representative US publication groups identified. Public IDs, preliminary status and primary lookup pointers are quarantined in [R22 patent provenance](../external-provenance/R22-PATENT-SOURCES.md). Individual patents can have continuations and family members with different claim scope. No exact claim chart or counsel opinion exists.

## Five+ research themes and MGR-native build choices

| Technology risk theme | Examples in patent ledger | Useful MGR native capability | Independent design / verification route |
|---|---|---|---|
| Runtime mesh LOD and streamed geometry | P1 grid-guided mesh LOD; P2 game-time LOD creation | **Perception Budgeter** + **Horizon Truth** | Design device-independent error-driven precomputed mesh levels, tested pixel error and GPU-time budget. Do not mechanically reproduce an individual claim's ordered grid/mesh operations. Final approach requires lawyer claim analysis, not an engineer's assertion of non-infringement. |
| Reconstructing geometry via learned radiance depth | P3 NeRF→depth→mesh | **Capture Truth** + **Metric Surface Proof** | Start conventional measured multiview photogrammetry/SfM and tested cross-view triangulation plus deterministic mesh QA. Learned fields may be optional alternative only after claims/license review; independently designed algorithm is not automatically legally safe. |
| Gaussian representation from point clouds with mask adjustment | P4 masked Gaussian rendering | **Appearance Proxy Atlas** | Use traditional mesh+texture proxy first for interactive world views; treat Gaussian render as separately gated candidate. Validate multi-angle appearance and geometry independently. Avoid assuming all Gaussian primitives are patent-free or all implementations infringe. |
| Dynamic Gaussian video/world motion | P5 spatiotemporal Gaussian embeddings | **Motion Continuity Clock** | Native skeletal animation, collision-driven transforms and frame-to-frame scene graph for character/FX; separate visual radiance animation candidate with counsel review. |
| Single-image hypothetical 3D reconstruction | P6 radiance-based inferred image depth | **Visibility Quilt** and **Inference Labels** | Distinguish observed multi-view measurements vs generative guesses, require held-out orbit/camera tests; conventional parametric modeling/artist design is an independent path. |
| Object-centric geometry/material/light disentangling | P7 neural decomposition | **Part DNA**, **Material Truth**, **Director Light Rig** | Build authored object hierarchy, shader/material nodes and independently known light rigs. Evaluate fit/identity across camera and lighting changes; gate matching protected claim sequences. |

## Full search methodology for the next legal-grade pass

1. Define specific planned commercial product workflows **before searching**: text/image→game mesh, camera capture→editable CAD mesh, streaming LOD runtime, character rig/body wardrobe, neural scene render, mixed-reality anchors and offline fabrication.
2. Search USPTO public database and Patent Center by terms, CPC/IPC classes (e.g. G06T/G06V/G06F relevant subgroups), assignees, inventors, related applications and backward/forward citations. Review **independent claims** and dependent claim extensions, not merely titles.
3. For each potentially relevant document, check exact filed application, US grant/amendments/terminal disclaimer/fees, prior-art citations, continuations/divisionals and patent term adjustments. Do not rely only on Google `Active` labels.
4. Expand family and legal-event search in EPO Espacenet/INPADOC and actual target countries. A PCT `WO` publication is an application path, not a worldwide enforceable patent.
5. Map *each proposed implementation step* to each legally operative claim element in a confidential claim chart, including alternatives; commission professional patent counsel for FTO in the launch jurisdictions. Document date, reviewer and decision.
6. Maintain continuous watch for newly published applications and relevant litigation/licensing changes; a snapshot cannot stay “cleared” forever.

## MGR-native defensive product architecture

- Canonical `CreationContract` defines *what* MGR promises (geometry truth, silhouette fidelity, complete parts, smooth streaming), not how a named outside company specifically achieves it.
- `AlgorithmRegistry` records independent authored implementation, mathematical derivation, provenance, source-license admission, version, tests and patent-risk ticket.
- `ImplementationVariants` permits alternate algorithms for the same contract (mesh proxy vs point cloud; measured stereo vs learned inference; frame-authored vs trained dynamic appearance) without rewriting caller products.
- `ClaimRiskGate` states `UNREVIEWED`, `SCREENED`, `COUNSEL_REVIEW`, `CLEARED_FOR_SCOPE`, `LICENSE_REQUIRED`, or `BLOCKED`. “Screened” cannot silently become “cleared.”
- `EvidenceBoundary` keeps user datasets, model-weight licenses, third-party source terms and patent risk as **four separate** approvals.

## Concrete stop and escalation rules

| Event | Build behavior |
|---|---|
| Prototype uses basic public mathematics/CPU mesh checks | Continue in dedicated Forge workspace with provenance and tests; mark patent FTO unassessed |
| Research identifies a related published patent application | Document exact application and assess specific claim risk; do not assume grant or automatic infringement |
| MGR implementation appears to match every step of an active independent claim in a target country | Stop *commercial release of that feature path* pending counsel, license or approved alternative; related unrelated build work can continue |
| Want to include third-party source or model weights | Separate open-source license and training data review; do not treat publication as authorization |
| Need restricted database, private patent file or paid prosecution record | Use authorized official access; do not bypass paywalls or access controls |
| Counsel approves scoped release | Record jurisdictions, product/build version, implementation choice, analysis date and monitoring interval; changes reopen gate |

## Hardware, tests and business cost

Patent search itself needs no giant GPU; heavy render/model implementations do. Keep low-cost classical reference paths and benchmark GPU alternatives separately. Engineering acceptance uses scene pixel error, geometric manifold/accuracy, animation stability, frame-time p95/p99, dataset provenance and deterministic reconstruction tests. Legal acceptance independently requires claim review and applicable territorial rights—not a passing unit test. Budget attorney time and possible commercial licensing before public sales rather than retrofitting architecture after deployment.

## High-value ideas not dependent on copying protected internals

1. **Truth-preserving geometry ladder**: same canonical body/room object holds multiple verified representations (sketch → measured sparse points → watertight mesh → rigged actor → printable solid), with confidence and review trail.
2. **Budgeted active exploration**: choose next camera view or cell load by expected decrease in uncertainty and estimated run cost, with independent test fixtures.
3. **Pose-invariant identity DNA**: hold verified anatomy/wardrobe/material ID steady through camera and motion changes, audited by geometry and render evidence.
4. **World memory cells**: semantic objects, physics/collision, render proxies and history stored separately to avoid giant recompiles.
5. **Explainable appearance illusion**: layer effects/light/postprocessing while maintaining transparent collision, topology and provenance truth.

These are **MGR design directions**, not opinions that corresponding implementations necessarily avoid all patents. A skilled independent implementation can still implicate a patent claim; the correct move is specific claim analysis and counsel signoff where warranted.

## Acceptance for this audit and build sequence

| Gate | Required artifact | Status |
|---|---|---|
| P-A | 5+ exact relevant published/granted records with country/type/source/status caveat | **DONE: 7 initial publication groups** |
| P-B | USPTO and EPO primary search/status workflow | **DONE: workflow defined; exact prosecution not independently verified** |
| P-C | Native algorithm variants with source/patent/data separate gates | **DONE: architecture specification** |
| P-D | Full claim chart per proposed production algorithm | **OPEN: patent counsel / final implementation required** |
| P-E | Foreign jurisdiction family/legal-event audit | **OPEN** |
| P-F | Counsel-reviewed FTO for actual shipping features and jurisdictions | **OPEN** |
| P-G | Continuous monitoring and documented ownership | **OPEN** |

**Next engineering order:** complete the classical geometry/scene runtime contracts (S03/S08/S13), register actual algorithm choices/versions, run negative QA, then escalate high-overlap patent families for *claim-by-claim* review before monetized deployment. Do not block every Forge build on an unreviewed broad patent search, and do not declare any feature patent-cleared from this packet.
