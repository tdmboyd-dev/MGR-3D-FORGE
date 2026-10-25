# R20 — Apple ARKit Research-to-MGR Audit

**Stage:** `SOURCED / selective official API and example overview`, 2026-10-25. Official Apple ARKit pages on tracking, anchors, plane/mesh reconstruction, LiDAR scene depth, face tracking/blendshapes and permissions reviewed. No Apple mobile/visionOS device accessed, sample code executed or end-to-end framework source audit conducted. Provenance: `research/external-provenance/R19-R20-SOURCES.md`.

## Technique 1 — MGR Capture Confidence & Relocalization Guard

**Observed:** ARKit world tracking maps camera space into real physical space, reports camera tracking-state/reasons, and warns that detected planes may initially be inaccurate and change over time. World map relocalization may fail indefinitely in an unrelated environment.

**MGR-native design:** all spatial capture imports include `tracking_state`, `confidence_or_reason`, camera intrinsics/extrinsics, timestamp, coordinate convention, sensor source and unknown states. When tracking degrades, hold authoritative world transforms and label visual overlay degraded. On relocalization, reconcile anchor frames with explicit transform and error threshold before accepting a scene update.

**Tests:** low light, fast handheld motion, motion blur, textureless wall, repetitive patterns, moved furniture, moving camera after background app pause, teleport/relocalized wrong room and denied sensor access. Detect false spatial certainty rather than quietly reprojecting previously approved geometry.

## Technique 2 — MGR Scan-to-World Mesh Steward

**Observed:** ARKit LiDAR-capable reconstruction estimates surrounding physical geometry as mesh anchors, with plane-informed smoothing/classification. It is an **estimate** of observed surfaces, not a fully watertight/high-detail scan or a view of occluded regions.

**MGR-native design:** `Spatial Mesh Steward` aggregates sensor mesh chunks by source anchor/revision, tracks per-face class/confidence and invalidates stale chunks when environment changes. A separate artist pass may create clean architectural mesh from sampled geometry, preserving provenance and distinguishing invented/filled geometry from observed data. Output remains editable Blender scene meshes.

**Tests:** irregular floors, chairs occluding walls, shiny/mirror surfaces, thin poles, glass, noisy scans, changed room layout, duplicated/stale chunks, wrong scale, mesh hole, orientation, topology/nonmanifold cleanup. Independent ground-truth measurement before claims of scan accuracy. No claim that LiDAR is present on all Apple devices.

## Technique 3 — MGR Face Performance Bridge

**Observed:** `ARFaceAnchor` supplies face tracking transforms and expression blendshape coefficients; Apple's docs describe portable dictionaries of expression coefficients and a coarse face geometry. Face tracking availability changes with device/OS capabilities.

**MGR-native design:** MGR Living Rig canonical facial expression map accepts ARKit-style names through an optional adapter, maps into independent MGR FACS-like controls and preserves rig identity. The performance should be evaluated across side/front/three-quarter perspectives and under varying expression intensity, with no requirement to store raw identifiable face frames after consented conversion.

**Tests:** missing device support, eyelid/brow/jaw extremes, eye blink synchronization, lip closure and jaw separation, smile asymmetry, frozen face, head rotation versus face blendshape confusion, absent coefficient keys, consent revocation and identity drift. `ARFaceAnchor` expression values are not proof of a particular person's unique head geometry.

## Technique 4 — Grounded Surface Placement and Occlusion

**Observed:** ARKit plane detection and raycasting help map screen points to real-world surfaces; `sceneDepth` requires hardware-support checks. Depth and reconstruction can inform occlusion but carry sensor noise and dynamic updates.

**MGR-native design:** `MGR Ground Contact` adapts observed plane/mesh constraints into a world collision/proximity layer; visually rendered object shadows/occlusion are evaluated against the same explicit source surface while contact validity is separate. Feature negotiation determines whether raycast/depth are available, otherwise use manual user-approved placement with a `not scanned` flag.

**Tests:** raycast false hit, floating feet/props, floor slope, scene depth error, object behind occluder, moving table, location-based anchor orientation, sensor unavailable fallback and geometry-camera discrepancies. An accurate-looking flat image is not enough to verify true 3D contact.

## Technique 5 — MGR Cross-Device Anchor & Privacy Envelope

**Observed:** Apple ARKit/visionOS world sensing/anchors require relevant authorization and may persist spatial references across sessions on supported stacks. Sensor access and scope vary with platform/device/version; no guaranteed universal sync.

**MGR-native design:** `Spatial Evidence Envelope` records anchor identifier, relative reference frame, environment fingerprint without raw private map by default, tracking validity, consent purpose, retention, signed source receipt and per-device coordinate adapters. Imported anchors stay separate from canonical fantasy-world placements until transform proof passes.

**Tests:** permission denied/revoked, device swap, coordinate origin rebase, cloud offline, persisted anchor after app restart, anchoring to moved object, sharing revoked and deletion proof. Do not assume a visionOS-specific provider works unchanged in iOS ARKit.

## Device/runtime/legal boundary

ARKit capture features run on supported Apple hardware/framework versions; scene depth and mesh reconstruction require particular LiDAR/vision devices, and facial capabilities differ by platform/OS. Forge CPU schema, mesh repairs, rig quality and Blender renders can be backend-neutral; it cannot invoke unavailable ARKit sensors on the user's Windows machine. Apple SDK access and program terms apply to code/framework distribution; capture data may reveal faces, homes, rooms and identifiable behavior. Treat consent, platform permissions, sensitive storage and local conversion as first-class requirements. Apple documentation/source visibility does not authorize copying implementation.

## Concrete MGR admission test harness

1. Synthetic calibrated camera/plane/mesh/face/anchor streams validate schema, coordinate transforms, and unknown states without Apple hardware.
2. Pin device, Apple OS, ARKit session/configuration and exact authorization; run official sample only on supported device and inspect success/failure.
3. Reconstruct measured room planes and mesh; compare ground-truth physical dimensions, unknown holes and alignment drift.
4. Reimport mesh into Blender and validate topology, units, normals, scale, source fidelity and editable parts.
5. Stream facial coefficient clips into two differently proportioned rigs; compare expression and identity multi-view results, no exposure of unconsented face imagery.
6. Kill/restart session and move environment objects; verify anchor persist/relocalize/drop behavior and explicit loss receipt.

**Disposition:** `MGR-NATIVE` capture confidence, Scan-to-World Steward, facial performance bridge, grounded placement and spatial evidence envelope; `STUDY` ARKit implementation. Never describe Apple's LiDAR scan as full hidden-room reconstruction or conflate sensor depth with imaginary geometry knowledge.
