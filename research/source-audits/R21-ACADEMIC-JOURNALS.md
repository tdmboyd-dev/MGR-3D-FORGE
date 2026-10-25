# R21 — MGR Academic Journal Evidence: Selected 3D/CV/Optics/Graphics/Biomechanics

**Research date:** 2026-10-25 · **Scope:** An intentionally selected sample of **eight peer-reviewed journal articles** across vision, perception, graphics, simulation and biomechanics. This is emphatically **NOT all journals, all papers or an exhaustive systematic review**. Official journal/author/public research sources are recorded in `research/external-provenance/R21-JOURNAL-SOURCES.md`. We inspected publisher/author abstracts and selected full paper material, not every experiment's raw data, algorithm implementation or supplementary asset.

## Executive native verdict

There is no scientific shortcut making a single 2D photo an exact unseen 3D human, a Gaussian-splat view an editable mesh, or a single pose a validated rig. The journal literature strongly supports a **representation-and-evidence architecture**: separate camera correspondence, image-based appearance, real 3D topology, physics-based movement, perceptual display quality and their respective uncertainty. Forge should synthesize them with observable rejection criteria before introducing expensive GPU training.

## Journal J1 — Lowe (2004), *International Journal of Computer Vision*: robust scale-invariant keypoints

**Finding:** Local image features built at scale extrema with orientation descriptors can support matching across scale/rotation and clutter.

**Mathematical insight:** Gaussian scale space `L(x,y,σ)=G(x,y,σ)*I(x,y)`; difference of Gaussians `D(x,y,σ)=L(x,y,kσ)-L(x,y,σ)` approximates scale-normalized Laplacian behavior. Descriptor correspondences require ratio and geometric verification, not raw nearest-neighbor acceptance.

**Production limitation:** Smooth skin, repetitive fabric patterns, view-dependent highlights, blur, occluded hands and AI-invented texture defeat naive descriptors. Feature matching proves corresponding image patches, not a unique 3D pose.

**MGR native:** **Correspondence Integrity Meter**. **Original test:** Blender synthetic checker, moving face and character turntable; positive/negative matches with known object IDs, per-camera scale, 3D ground-truth reprojection; report precision/recall and abstention on bad textures. **Feasibility:** CPU moderate; no proprietary training needed.

## Journal J2 — Hoffman/Girshick/Akeley/Banks (2008), *Journal of Vision*: vergence–accommodation conflict

**Finding:** Experimental stereoscopic display focus/vergence conflict can degrade visual performance and contribute to fatigue.

**Math:** Vergence distance is inferred from binocular geometry/disparity, while display focal accommodation is dictated by device optics. The effective mismatch can be represented by dioptric difference `ΔD=1/z_vergence - 1/z_focus` (meters). This is an explanatory metric, **not a universal medical threshold**.

**Limits:** Participant responses, lens design, individual vision and display configuration vary; no software setting abolishes all fixed-focus display conflicts.

**MGR native:** **Comfort-Safe Depth Director**. **Original test:** per-eye disparity and viewer-distance witness across near/far objects, headset-specific hardware review and opt-in comfort feedback; hardware required for full verification. **Feasibility:** simulated stereoscopy CPU; real comfort assessment demands headset, consent and user testing.

## Journal J3 — Kerbl et al. (2023), *ACM Transactions on Graphics*: 3D Gaussian splatting

**Finding:** Optimized anisotropic Gaussian scene primitives, calibrated images and visibility-aware splatting enable fast novel-view appearance rendering in demonstrated conditions.

**Math:** Gaussian influence `G(x)=exp[-½(x-μ)^T Σ^{-1}(x-μ)]`; Gaussian center `μ` and positive-definite covariance `Σ=RSS^TR^T` (appropriate parameterization) define anisotropic extent. Alpha accumulation along sorted fragments approximates radiance composition `C=Σ_i T_i α_i c_i`, with `T_i=∏_{j<i}(1-α_j)`.

**Limits:** Optimized splats may be nonphysical, view overfit, flicker, obscure transparency order and generally do **not** provide watertight surfaces, usable character skeletons or collision mesh. Reported realtime results depend on GPU/scene/resolution.

**MGR native:** **Appearance Cloud Witness**. **Original test:** 24+ Blender renders of owned room/portrait, held-out viewpoints and geometry, compare color metrics plus depth/occlusion/geometry availability; keep image-based reconstruction labeled separate from editable mesh. **Feasibility:** training GPU likely valuable; inference/CPU tiny witness is possible but not equal to realtime full scenes.

## Journal J4 — Radl et al. (2024), *ACM Transactions on Graphics*: sorted splatting/view consistency

**Finding:** View-consistent rendering needs attention to splat-depth sorting and popping; not every fast splat compositing strategy stays stable under camera change.

**Math:** With alpha composition, swapping order of two transparent elements changes resulting color generally, since `α_a c_a+(1-α_a)α_b c_b` differs from reversed order. Ordering/occlusion must be evaluated per view.

**Limits:** Better sorting does not turn a radiance field into a rigged mesh or guarantee correct extrapolation into unseen regions.

**MGR native:** **View-Pop Prosecutor**. **Original test:** 360° camera path past interleaved translucent splats; measure frame-to-frame pixel/depth discontinuity at stable geometry, flag temporal ghosting; compare sorted vs unsorted controls. **Feasibility:** synthetic CPU math and small scene, scalable rendering backend later.

## Journal J5 — Bender et al. (2014), *Computer Graphics Forum*: position-based dynamics simulation

**Finding:** Position-based methods enforce geometric constraints through repeated projections and can deliver stable interactive cloth/rope/soft-body approximations.

**Math:** A constraint `C(x)=0` is locally corrected by `Δx_i = -[w_i∇_{x_i}C / Σ_j w_j ||∇_{x_j}C||²] C(x)` in a simplified mass-weighted projection step; practical solvers address damping, collisions and solver ordering. The expression is a standard conceptual correction, not verbatim method coverage for every variant.

**Limits:** Few solver iterations, changing timestep, compliance and collision ordering distort stiffness and realism; visually plausible physics need not conserve true energy or physical material parameters.

**MGR native:** **Costume Contact Stabilizer**. **Original test:** coat, shirt, chain/rope, cape and ground collision witness across timestep/iteration grid; count penetrations, stretch error, oscillation decay and frame-time. **Feasibility:** tiny CPU solver feasible; production garments still require validated collision meshes and adaptation.

## Journal J6 — Delp et al. (2007), *IEEE Transactions on Biomedical Engineering*: OpenSim human movement

**Finding:** Musculoskeletal models couple bodies, joints, musculotendon actuators and movement simulation to reason about forces and coordination.

**Math:** For articulated rigid-body dynamics, `M(q) q̈ + C(q,q̇) + g(q) = τ + J(q)^T λ` schematically balances generalized inertia, velocity effects, gravity, muscle/controller forces and contact; model validity rests on mass/inertia/constraint data.

**Limits:** Aesthetic game rigs are not anatomically calibrated biomechanical models; forces estimated from unmeasured bodies are model hypotheses, not diagnoses.

**MGR native:** **Anatomy Motion Guardian**. **Original test:** independent TEVIN skeletal joint ranges, foot contacts, floor support, hand reach and center-of-mass paths; compare conservation/contact checks using an MGR-authored mannequin. **Feasibility:** modest CPU inverse kinematics; full muscle simulation deferred.

## Journal J7 — Rajagopal et al. (2016), *IEEE Transactions on Biomedical Engineering*: full-body gait model validation

**Finding:** Published 3D musculoskeletal gait modeling can compare predicted joint moments/muscle activity to measured ground-truth biomechanics rather than relying on looks.

**Math:** A movement model can minimize task residuals `J=Σ_t ||q_model(t)-q_target(t)||_W² + λ||u(t)||²` subject to joint/muscle/contact dynamics. This is a generalized MGR validation objective, **not a claim the paper uses exactly this expression**.

**Limits:** Original study's anthropometric parameterization/populations and test configuration cannot simply transfer to a fictional avatar; full-body ranges differ by actor.

**MGR native:** **Gait Truth Continuity**. **Original test:** ground reaction and foot-lock witness, 10-cycle walk/run with pelvis/foot trajectories, bone length and self-intersection metrics; compare against a permitted mocap reference only if license allows. **Feasibility:** owned procedural walk loop and geometry checks CPU-feasible.

## Journal J8 — Hedman et al. (2023), *ACM Transactions on Graphics*: memory-efficient radiance field view synthesis

**Finding:** Volumetric neural appearance may be baked into an efficient representation for interactive view synthesis, reducing runtime burden under paper-specific conditions.

**Math:** Rays integrate color with density/opacity `C(r)=∫ T(t) σ(r(t)) c(r(t),d) dt`, `T(t)=exp[-∫_0^t σ(r(s))ds]`. Compression/baking changes sampling/storage but does not magically create semantic object surfaces.

**Limits:** Captured or optimized view synthesis cannot be assumed metrically correct under novel lighting, editable geometry, animation/collisions or unseen disoccluded angles.

**MGR native:** **Pocket World View**. **Original test:** same owned room in mesh, splat and baked radiance forms; compare memory, loading, held-out image PSNR/SSIM and collision/shape capability claims. **Feasibility:** CPU tiny analytic prototype possible; production training/render requires measured device budgets.

## Combined MGR engine design lessons

1. **Evidence modes:** direct observation, geometrically recovered, physics-simulated, artist-invented. Store separately; confidence calibration is modality-specific.
2. **Truth overlays:** show hand/limb silhouette, occlusion, bone continuity, material/lighting, contact and unseen-depth uncertainty, not a single “98% matching” score.
3. **Fidelity ladder:** editable mesh/rig base → real-time representation optional → cinematic physics/light quality; do not make expensive appearance models determine scene truth.
4. **Adaptive math first:** CPU-only correspondence, pose, normal/depth/ID, PBD witness and analytic optics can catch costly failures before full GPU render.
5. **Human-data caution:** literature body datasets, medical recordings, scanned faces and eye/comfort tests have consent, privacy and license constraints.

## Reproducibility checklist / honest completion boundary

| Evidence | Gate |
|---|---|
| Citation authenticity | Original journal/author citation with title, year and subject, plus exact license/data availability check |
| Implementation lineage | Record separately authored MGR source; never claim journal paper grants source code/models |
| Synthetic baseline | Owned Blender scenes with known depth, occlusion, transforms, material, frame times, bone identity |
| Numeric tests | Camera reprojection, feature inliers, eye disparity, gaussian order, solver collision, joint limit, temporal stability |
| Uncertainty | Abstain on unseen geometry/low parallax; report numerical conditioning, variance and missing evidence |
| Data ethics | License/consent review for real humans, captured datasets and any code trained on restricted material |
| Benchmark honesty | Per-device/frame-size/samples, time/memory and original vs reproduced setup separated |

**No study in this sample was fully replicated here.** Documentary research packet: complete for these eight selections. Production implementation, quantitative empirical baselines and broader journal review remain open work; avoid labeling the entire academic literature “100% read.”
