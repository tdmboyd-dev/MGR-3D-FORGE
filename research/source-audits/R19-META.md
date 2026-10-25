# R19 — Meta Reality Labs / Horizon OS Research-to-MGR Audit

**Stage:** `SOURCED / selective first-party API and research-repo review`, 2026-10-25. Official Horizon OS documentation, Movement SDK API descriptions and a Codec Avatar-related research repository landing page were reviewed; **no Quest device, sensor, sample runtime, model weights, source-depth audit or commercial license verified**. Detailed provenance: `research/external-provenance/R19-R20-SOURCES.md`.

## Technique 1 — MGR Depth Truth Compositor

**Observed:** Meta Horizon OS passthrough and Environment Depth describe spatial depth enabling real-world occlusion of virtual objects. Scene understanding can represent real surfaces, while depth and scene layouts offer different confidence and update behavior. Health/safety guidance notes that depth alone is not a substitute for physical boundary systems.

**MGR-native design:** World Visual Judge treats occlusion as a comparison between measured/estimated real-depth map and projected virtual-depth image. `MGR Depth Truth` records sensor source, uncertainty/missing pixels, timestamp, calibration, camera pose and whether occlusion is measured, estimated or artist-authored. No claim of hidden-object reconstruction: if a person is behind an occluder, actual invisible geometry remains UNKNOWN.

**Tests:** foreground person crossing virtual object, glass/reflective surfaces, textureless wall, missing depth map, bad confidence, tracking lag, camera shake, different capture resolution and incorrect foreground mask. Fail safe by simplifying/clearly labeling visualization rather than inventing unseen geometry. Measure temporal edge flicker, depth error, image quality and response latency on actual supported hardware.

## Technique 2 — Semantic Scene & Persistent Anchor Ledger

**Observed:** Meta scene understanding identifies room structure, and spatial anchors support a virtual object remaining fixed relative to a physical location, with local/cloud persistence paths. Anchor IDs and relocalization events matter across app sessions.

**MGR-native design:** World Forge owns an `Anchor Truth Ledger`: anchor reference frame, source feature/plane, transform covariance/confidence, consent, expiry, environment hash and revision. Portal/world anchor state can be reconstructed in a virtual scene and compared across sessions. Separate physical anchors from fictional world coordinates and never leak raw room maps across accounts by default.

**Tests:** relocalization loss, moved furniture, reused room name in different physical room, cloud unavailable, simultaneous users, revoked permissions, anchor drift and real-versus-virtual world coordinate mismatch. Verify persistence with real device power cycle/session restart before claiming it.

## Technique 3 — Embodied Avatar Tracking Mapper

**Observed:** Meta Movement SDK exposes body, face and eye tracking as separate capabilities, including abstracted face FACS/blendshape data and eye gaze. Some eye movement is intentionally smoothed for social presence and specific permissions/hardware support apply.

**MGR-native design:** `Living Rig` accepts a provider-neutral `CapturePoseFrame` containing joint confidence, normalized face-expression channels, gaze vectors, device calibration, timestamp and consent scope. Map sources to semantic rig controls and preserve separate hand/face/eye availability; missing streams are **unknown** rather than neutral/zero movement. Distinguish inferred body joints from directly tracked sensors.

**Tests:** face stream absent, impossible eye gaze, alternating tracking states, hand/face occlusion, joint-length variation, motion latency, poor calibration, permission denial, face/eye tracking revoked mid-session, retarget across two proportions and realistic gaze without jumpy pupil motion. Use consensual actors/fixtures and never infer a named identity from body patterns by default.

## Technique 4 — Privacy-Preserving Motion Transport

**Observed:** Meta Movement SDK references networked avatar/body tracking data workflows; live tracking has high update frequency while network conditions are variable. This does not prove a public turnkey avatar codec meets MGR's needs.

**MGR-native design:** Build an independent skeletal/expression packet format with quantization chosen by measured fidelity/latency, sequence numbers, source/device timestamps, identity policy and differential privacy controls where feasible. Transmit motion features rather than raw room camera imagery by default. Actor consent/retention and encryption are mandatory for identifiable capture.

**Tests:** packet loss 1–20%, delayed/reordered frames, time drift, malicious oversized pose, invalid quaternion, 50/100/200 ms network roundtrip simulations, missing face stream and consent revocation. Compare recovered motion with ground truth, foot sliding, pose latency and bandwidth, with frame/time synchronization under fixed clocks.

## Technique 5 — Neural Avatar Proposal with Strong Rights Gate

**Observed:** Meta-associated research `audio2photoreal` demonstrates a Codec Avatar research path driven from audio and includes datasets/code release descriptions. A research preview is not license clearance, production performance evidence or proof of arbitrary person fidelity.

**MGR-native design:** `MGR Character Performance` may accept optional neural face/body proposal clips for **authorized subjects only**. Canonical character geometry, deformation rig and editable independent wardrobe remain authoritative. The generated motion is judged with multi-view character identity, face/lip timing and exportable rig data, not a single image similarity score. Baseline authored FACS/phoneme control must remain usable without neural API or powerful GPU.

**Tests:** novel phonemes, accented speech, muted and noisy audio, unseen face angles, performer-specific likeness, lip desynchronization, temporal face warp, data rights rejection and GPU/no-GPU measured latency. Do not download Meta datasets or weights until each license, consent and redistribution condition is checked.

## Hardware, software and rights reality

Meta Horizon OS/Quest SDKs have device, system build, tracked-feature and permission dependencies; passthrough camera access may require specific supported headset models and OS versions. Movement body/face/eye availability cannot be asserted on a random Windows laptop or all Quest generations. Meta XR packages, Unity/Unreal adapters, open research source, datasets and human captures may carry distinct terms. Face, eye, body and room sensors are privacy-sensitive. Never move them into GitHub logs or public project assets. Keep opt-in, on-device processing when possible, minimal feature retention and full user revocation.

## Concrete MGR admission test harness

1. Use synthetic frame streams (`pose`, `face`, `gaze`, `depth`, `scene`, `anchor`) with timestamp and confidence to unit-test schema and provider-independent operators on CPU.
2. Run a real supported Quest device test only after exact SDK/device/permissions are known; record official feature support and denied-state behavior.
3. Compare depth occlusion to annotated scene/render samples under moved camera and high-motion actor.
4. Persist anchored object, restart/relocalize, lose session tracking and restore; measure spatial displacement.
5. Retarget captured performance to MGR rig while preserving contacts, face expression and character proportions; compare view-independent geometry and rendered output.
6. Benchmark motion transport quality under network impairment and device latency; revoke consent mid-capture and verify memory/log erasure policy.

**Disposition:** `MGR-NATIVE` Depth Truth, Anchor Ledger, CapturePoseFrame, privacy-preserving Motion Transport and licensed optional Character Performance adapter. `STUDY` Meta SDK implementation. Do not transplant Meta-branded APIs as product truth, claim hidden-depth omniscience, or represent research avatar output as a completed Tevin-style rig.
