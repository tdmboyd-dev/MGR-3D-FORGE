# S10 — MGR Native Living Rig & Motion System

**Status (2026-10-25):** 16-field sourced design packet, not implemented or production validated. Source links, licenses and provenance remain in `research/external-provenance/S10-ANIMATION-SOURCES.md`. MGR owns this capability description and proposed interfaces. A rig is **not** established merely by moving a mesh, detecting landmarks or generating a sequence of images.

## Executive MGR decision

Build a reproducible **MGR Living Rig**: a semantic skeleton, deformable skinned meshes, separate wearable assets, portable motion clips, contact/continuity guards, grounded locomotion and retargeted action library. First deliver a working Blender rig with export/reimport and visible deforming mesh; add model-driven body motion only when it beats deterministic baselines and meets consent/license/privacy gates. Preserve current landmarks as an initial test fixture, not a substitute for rigging.

## 1. Definition and capability tree

- Skeleton hierarchy: named joints/bones; rest pose, bind/inverse bind matrices, local and global transforms, units, anatomical constraints, twist axes and root bone.
- Skin deformation: mesh influences and normalized per-vertex weights, multi-bone blending, shape keys, corrective poses, hands/face, garment attachments and independently editable pieces.
- Controls: FK, IK, pole targets, foot roll, stretch limits, space switching, root motion, body/contact markers and layered control/driver systems.
- Motion: clips, easing, loop/cut states, blending, transitions, events, procedural gestures, physics-informed secondary motion, mocap ingestion, retargeting, cleanup and replay.
- Quality: structural proof, pose coverage, ground contact, skin stretch/volume loss, self-intersection, cloth clipping, identity/scale consistency, temporal smoothness and export correctness.

## 2. Production use

One approved character should walk, run, jump, sit, reach, emote, turn, hold props and perform world interactions with the same stable identity/garments across shots. Cinematics require editable authored performance, controls for facial acting, directed camera timing, contact with props and repeatable renders. Real-time use requires fast playback, animation LOD, state machines, interpolation and contact-aware transitions. Crowd characters may use a lower-cost skeleton/clip profile; a hero closeup needs hands, face and garment tests.

## 3. Standards and contracts

- `glTF 2.0`: joints, inverse-bind matrices, vertex `JOINTS_0`/`WEIGHTS_0`, animation samplers/channels and supported interpolation. Exporting a static GLB is not proof of valid skinning or moving mesh.
- `OpenUSD UsdSkel`: skeletons, skinned meshes and skeletal animations for studio exchange, with importer-specific fidelity tests.
- Blender armature/pose-bone/constraint data model. **Rest transforms vs evaluated pose matrices must not be confused.**
- Motion ingest candidates BVH, FBX, glTF, USD, proprietary sources: inspect scale, handedness, frame rate, coordinate system, joint channels, consent and licensing before adoption.
- MGR canonical schema proposal `mgr.forge.living-rig.v1`: semantic bone IDs, parent/rest transforms, mesh skin bindings, controls, garment slots, clip metadata, contact phases, source rights/consent, acceptance receipts. Maintain one explicit mapping per export target.

## 4. Research and scientific foundation

The foundational stack is forward kinematics (hierarchical transforms), inverse kinematics (constrained optimization), linear-blend skinning and advanced corrective/deformable methods, quaternion motion blending, time-continuous trajectory math (S05), contact-constrained locomotion and inverse dynamics where needed. Existing research shows standard linear blending can produce joint-volume artifacts; physics-based or velocity-aware deformations are research alternatives, **not automatically faster or more stable**. Motion transfer quality relies on joint correspondence *and* proportions, limits, coordinate systems, contact and semantic action timing. A pose image or 2D keypoints cannot uniquely determine hidden 3D depth or an unoccluded body.

## 5. Open implementations to study

- Blender armatures, pose constraints, Action/F-Curves, Geometry Nodes and dependency graph evaluation: authoring runtime and quality baseline.
- Godot Skeleton3D, SkeletonProfile, AnimationPlayer/AnimationTree: useful model for retargetable skeleton profile and playback states.
- Fairmotion: research candidate for motion loading, transforms, preprocessing and inspection, **not vendored or executed here**.
- Other runtime candidates: glTF Khronos samples/tutorials and OpenUSD official schemas. Take independent protocol lessons, not unreviewed code.
- The current `forge/animation.py` only returns landmark pose tracks and expressly marks `weight_painting_verified=False` and `skinned_animation_exported=False`; `forge/character.py` supplies mannequin geometry. These are appropriate fixtures but not complete deformable rigs.

## 6. AI models

Optional image/video pose tracking, monocular body reconstruction, rig prediction, motion diffusion/generation, text-to-motion, retarget optimization and audio-to-face models could speed drafts. Each output must clear pose/identity/contact rights and numerical tests. Proposed `ModelMotionAdapter` returns **proposal clips**, never silently overrides owner-approved bind pose or exports. Do not claim a model works locally, runs without GPU, knows accurate depth from one picture, has commercial rights or reaches studio quality without measured evidence. Start with authored/procedural clips and Blender controls.

## 7. Datasets

- Synthetic MGR-owned fixtures: T/A pose, 24-or-more joint motion suite, asymmetric reach, crouch, fast 180° turns, gait/stair traversal, running, stops, jumps/landings, occluded/ambiguous single-image references, finger articulation and interacting with a prop.
- Candidate external research sets: AMASS, Human3.6M, LaFAN1 and CMU mocap. **Do not download, train on, embed or distribute until dataset-specific rights, participant consent, likeness, use case and redistribution are verified.** Training rights and clip reuse rights can differ.
- Include rig diversity: heights, proportions, skinning across body types, garment volumes, stylized non-human appendages, mobility and accessible motion.

## 8. Licensing/privacy

Keep imported code, rigs, motions, images, apparel, face and voice rights individually logged. An open repo license does not grant rights to its training weights, sample animations, underlying person or attached assets. Potentially sensitive mocap contains identifiable human body patterns; protect original captures and consent. Unity/Unreal ecosystem examples may come with separate marketplace and runtime conditions. External candidates require exact revision/version license checks before redistribution, commercial use or code vendoring; OpenPose is specifically **not safe to assume unrestricted commercial reuse**.

## 9. APIs/providers

External mocap/text-to-motion/auto-rig APIs and online animation catalogs are optional, noncanonical importers. Gate expenses; source files and provenance; allow local/manual Blender workflow without keys. Network providers cannot become hard dependencies for rig validation, export or existing procedural animation. No current price is asserted because paid tiers and generated-motion credits are time-variable and have not been scoped against production workloads.

## 10. Native MGR architecture and original differentiators

Propose `forge/living_rig.py` public validation contract, `forge/motion_retarget.py` for semantic mapping and transformation, `forge/contact_director.py` for floor/hand/prop constraints, and `forge/rig_quality.py` for scored receipts; actual placement must be confirmed against live package before implementation.

```python
# Proposed interface; SPECIFICATION ONLY, not existing executable code.
rig = LivingRig.from_blender(scene_object, profile="mgr.humanoid.v1")
report = rig.validate(rest_pose=True, weights=True, bounds=True)
clip = MotionRetarget.map_clip(source_clip, target_rig=rig, preserve_contacts=True)
tested = ContactDirector.solve(clip, floors=world_colliders, prop_anchors=anchors)
receipt = RigQuality.evaluate(rig, tested, views=["front", "side", "three_quarter"])
if receipt.production_passed:  # cannot pass if any required evidence missing
    export_asset(rig, tested)
```

Novel native targets:

1. **Contact Truth Ledger:** records planned versus observed foot/hand/finger/world contacts per frame; flags foot sliding, penetration and hand-to-prop distance errors.
2. **Identity/Proportion Continuity Lock:** compares rest geometry, skeleton dimensions, wearable constraints and image renders across clips, keeping camera-induced appearance changes separate from actual character changes.
3. **Pose Completeness Guard:** knows that hands/feet/fingers hidden outside an image or occluded are *unknown*, not validated; requests additional views or rig inspection.
4. **Motion Rehearsal Swarm:** deterministic action suite on varied floors, slopes, steps, speeds, props, wardrobe and FPS; captures machine-readable receipts and cinematic renders.
5. **Sculpt-to-Rig Trace:** binds each mesh region and garment to source asset IDs, skeleton revision, weights, correction shapekeys and tested pose range, so later edits trigger targeted rechecks.

## 11. Hardware/runtime

FK, small skeletons, contact metric checks and ordinary scripted keyframes can run CPU. Skin deformation for large crowds, collision-heavy clothing, physics, neural reconstruction and inference may need GPU acceleration. Windows Blender 5.x is an authoring/test candidate; local availability is not proof of scene-specific success. Record actual threads, CPU/GPU, RAM/VRAM, polygon/influence counts, frame timings, export size, model/download size and fallback quality. Target device is a product decision, not a universal benchmark.

## 12. Cost and velocity

- Free/local baseline: MGR-authored procedural clips and Blender, with human technical-art time for rigging, weights, controls and corrections. Compute/maintenance costs remain real.
- Main up-front expense is quality labor: deformation corrections at shoulder/hip/knee/face, separate wardrobe simulation, integration and independent export/reimport testing.
- Optional subscriptions and motion services must be evaluated with per-usable-approved-clip cost, failure/retry rate, account/API restrictions, rights, GPU rental and provider churn; headline generation cost can mislead.
- Speed path: ship an editable single-character rig and ten-clip acceptance scene first; only then add automated generation and larger crowds.

## 13. Failure modes and negative controls

Missing/deformed hand; arm length inconsistency; bone-parent cycle; joint inversion; unnormalized/missing weights; skin collapses at elbow/knee; floating foot; foot skate; heel passing through ground; knee hyperextension; arm through torso; hair/coat body collision; T/A rest pose mismatch; clipped finger; duplicate skeleton root; root motion applied twice; retarget wrong twist/axis/scale; pole-vector flip; discontinuous animation transition; teleport interpolated across cuts; non-deterministic procedural seeds; occluded view falsely called correct; 2D likeness maintained while hidden backside geometry is broken; GLB has valid node animation but no deforming skin; exported and Blender-native pose differ.

## 14. Evaluation metrics and rubric

**Structural:** bones have acyclic parents, finite transforms, consistent rest/bind matrices; vertex weight sums within epsilon; no unbound deformation mesh; required semantic bones present; no zero-length critical chain.

**Temporal:** frame/clip continuity of joint position/rotation and root velocity; speed/accel/jerk distributions; stable contact phases; true loop closure; deterministic playback at sampled timestamps independent of render frame rate.

**Physical/perceptual:** peak and RMS planted-foot velocity (local world units/s), toe/heel penetration depth, hand-prop error, bone-length variance, joint-limit violation count, mesh/wardrobe self-penetration, rendered silhouette and landmark visibility for multi-angle poses. Face/emotion quality additionally requires human visual approval and consistent expressive blend shapes where applicable.

**Portability:** exact bone names, joints, skin weights, rest and animated transforms, root motion and garment attachment after Blender→glTF/USD→independent importer→render. Include per-target supported-feature matrix; a lossy export cannot be marked an unchanged roundtrip.

No arbitrary scoring threshold claims production sufficiency; thresholds come from representative baseline scenes and owner quality evaluation, with numeric tolerances locked before final sign-off.

## 15. System placement and migration

`forge/animation.py` is an input producer/kinematic control fixture. The proposed Living Rig owns rest/bind/skin semantics; Motion Retarget produces semantic clips; Contact Director adjusts executable motion; Rig Quality and Visual Judge consume evaluated world transforms and independent rendered views. Blender bridge authors and evaluates the actual rig; exports become artifacts with evidence receipts. The director/camera layer coordinates timing without rewriting skeleton ownership. Add feature flags/schema versions and leave old landmark interfaces intact until a tested migration.

## 16. Acceptance suite — all required before production claim

1. Build a deformable character mesh with named, parented skeleton, proper rest pose and normalized skin weights; inspect evaluated Blender scene and `.blend` file.
2. Show preserved bone lengths and bounded joint angles for T, A, crouch, overhead reach, squat, stride and 180° turn. Feet, hands and fingers must remain present and in frame for full-body renders.
3. Validate shoulder, elbow, hip, knee and neck deformation from multiple viewpoints with shape correction where needed; test mesh volume/silhouette under extreme poses.
4. Model separate coat, shirt, pants, boots, hair and jewelry attachment references; confirm wardrobe deformation and no unacceptable clipping during all stress clips. Hair/fabric simulation must not be claimed without executing a solver.
5. Reproduce ten canonical actions and retarget three significantly different body proportions without broken constraints, contact or skeletal scale.
6. Floor/contact tests across level ground, slope, stair, stop/start, jump/land, moving platform and prop grab; compare plant speed, penetration and IK solution stability.
7. Transition walk→run→stop and reach→turn with timed blending, root-motion continuity and deterministic results at 24/30/60 render FPS on fixed motion timestamps.
8. Reject malicious/broken clip metadata: NaN quaternion, non-normalized rotation, unknown bone, missing binding, corrupt hierarchy, joint spikes, zero-duration timestamp, duplicate clips, wrong handedness and self-intersecting garment.
9. Export animated skinned glTF and USD candidate; independently import/render and compare the **deforming mesh**, joint transforms and timings, logging unsupported properties separately.
10. Visual Judge checks same character at changed angle/pose/camera/light using anatomical/skeleton identity and multi-view checks, not brittle pixel equality; deliberate different-character and missing-hand negatives must fail.
11. Profile CPU/GPU timing and memory for hero and crowd rigs on actual hardware, with budgets for target engine and renderer; fallback execution tested.
12. Legal/production sign-off: verify rights, identity/consent, asset provenance, exact environment, determinism, complete artifacts, receipts and owner approval.

### Implement now versus later

**Immediately buildable:** structural schema checks, named bone map and coverage report, pose stress fixtures, weight checks, finite matrix checks, landmark visibility checks, contact distance/foot-skate metrics, deterministic replay receipts. **Needs actual Blender/target-runtime proof:** skinned deforming rig, fully separated wardrobe, robust IK, cloth/hair, export integrity and photoreal visual quality. **Research-stage experiments:** automated AI rig prediction, retargeted motion generation, differentiable/volumetric deformation and no-GPU neural pipeline.

### Research confidence and recommendation

Primary spec/manual coverage is sufficient to **specify** an initial MGR-native rig pipeline and acceptance gates, but not enough to certify automation, commercial model reuse, engine interoperability or high-end output. Avoid declaring production completion until the full 12-point suite passes on genuine assets and recorded Windows Blender/independent game-engine results. Prioritize core rig→deform→pose→contact→export before any AI-generated cinematic volume.
