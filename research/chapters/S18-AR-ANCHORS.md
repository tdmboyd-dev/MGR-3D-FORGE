# S18 — MGR Reality Bridge: spatial anchors and mixed-world truth

**Decision:** Keep MGR worlds as stable, device-independent authored space, and attach them to physical environments through a separate **Reality Bridge** with measured tracking quality. Make every physical placement reversible, re-localizable and inspectable. Local-first tracking and on-device occlusion should work without mandatory cloud location storage; optional shared/location-based anchors are gated by credentials, consent and supported hardware.

**Status 2026-10-25:** 16-domain implementation specification, not a tested phone/headset product. References and external rights are in [S18 external sources](../external-provenance/S18-AR-SOURCES.md). No real sensor/headset tests were run in this research task.

## 1. Definition: AR versus mixed reality

Augmented reality overlays virtual objects on camera passthrough or optical see-through, tracked relative to physical space. Mixed reality adds robust interaction, occlusion and spatial understanding: a virtual creature passes behind a real table, reacts to physical floors, and maintains plausible contact as the viewer walks around. It is not enough for a sticker to follow one camera angle. An anchor is a **time-varying best estimate** of physical space, not an eternal absolute coordinate.

## 2. Coordinate systems and math foundations

Represent every transform as a 4×4 homogeneous matrix with explicit `parent_frame`, units, handedness, timestamp and covariance/quality. Spaces include camera sensor, device/head, session/local tracking origin, floor/stage, physical-map anchor, geospatial ENU/ECEF and MGR-world actor. Compose transforms in a defined order, never interchange camera-to-world and world-to-camera silently. Camera image intrinsics/distortion connect tracked 3D features to pixels. Head pose, eye projection and per-frame prediction must target the actual display time to reduce jitter and apparent lag.

## 3. What live tracking actually requires

Camera frames plus IMU acceleration/angular rate yield visual-inertial odometry and tracking; optional LiDAR/ToF/depth improves scene understanding. Features/planes/meshes let the app register furniture, floors, walls and objects. SLAM estimates the moving camera while incrementally creating/updating a spatial map, with loop closure/relocalization correcting earlier drift. Device motion and environment changes mean scene estimates can jump; the app must treat corrections as events and avoid teleporting objects or physics unexpectedly.

## 4. Full production path

Start MGR scene and scale truth → request minimum camera/motion permission → start platform tracker → query supported capabilities/sensors → establish session origin and quality → detect surfaces/mesh → ask user to select safe placement region → bind semantic MGR actor group to one spatial anchor → render with device-calibrated view/projection → use real-world depth/mesh for occlusion and collision proxies → update transforms based on tracking confidence → re-localize after interruption → optionally persist/shared-anchor by explicit consent → capture metrics and permission-safe QA artifacts. If tracking falls below threshold, pause hazardous interactions and display clear guidance.

## 5. Distinct spatial anchor classes

| MGR-native class | Meaning | Failure recovery |
|---|---|---|
| `LOCAL_SESSION` | Anchor valid within tracked session's map | Resolve again or invite user to reposition on restart |
| `RELOCALIZED_MAP` | Recovered using known environment features | Validate transform residual and re-attach only if sufficiently confident |
| `SHARED_GROUP` | Multiple opted-in devices resolve common local mapping | Compare inter-device alignment and clock/network synchronization |
| `GEOSPATIAL` | Geographic frame plus visual localization | Fall back to coarse GPS/warning if coverage/precision inadequate |
| `HAND_BODY` | Temporary tracked joint/body pose frame | Expire on loss of hand/body tracking; never silently persist as fixed wall placement |
| `AUTHORING` | Synthetic anchor fixture for desktop/headless testing | Test transform logic; cannot substitute real device sensor acceptance |

## 6. Mapping geometry, depth and occlusion

Plane detection supplies approximate extent and orientation; never treat initial plane detection as exact floor CAD. Scene mesh/point depth is sparse/noisy/movable; confidence and freshness must travel with every surface tile. For occlusion, compare real-scene depth and virtual projected depth in one calibrated camera frame, with confidence-aware edge filtering and temporal smoothing. For physical collision, derive coarse tested proxies rather than copying every noisy triangle; collision assumptions and virtual appearance must agree. Transparent windows, moving people, mirrors, dark corners and furniture rearrangement require degraded quality states.

## 7. Platform adapter strategy

MGR `SpaceAdapter` exposes `start_session`, `get_frame_pose`, `get_camera_intrinsics`, `get_depth`, `enumerate_planes`, `get_scene_mesh`, `create_anchor`, `resolve_anchor`, `persist_anchor`, `remove_anchor`, `get_tracking_state` and `stop_session`. Capability discovery is mandatory: some devices provide plane detection but no mesh, depth or cloud anchoring; portable XR headset input/render standards alone do not mandate phone-style RGB passthrough or global maps. Maintain explicit adapters for supported Apple/Google/headset environments, not vendor SDK imports inside core MGR scene contracts. Every adapter records SDK/runtime version and user permission state.

## 8. MGR-native original inventions

1. **Reality Bridge**: connects MGR world frames to timestamped physical-frame observations without contaminating canonical authoring coordinates.
2. **Anchor Family**: one parent anchor for a coherent nearby object group; children retain relative precision when tracking adjusts instead of individually drifting apart.
3. **Drift Witness**: marks anchor corrections, uncertainty change and observed residual from previous known placements; rechecks when the map relocates.
4. **Occlusion Truth Mat**: renders real/virtual depth correspondence and confidence, surfacing edges that lie incorrectly in front of furniture or bodies.
5. **Safety Envelope**: separates visual FX from physical hazard boundaries; warnings for obstructed stairs, exits and moving vehicles, and disables unsafe interaction when tracking weak.
6. **Physical Set DNA**: records permission-safe descriptors of floor/table/wall zones as semantic placement targets without storing unnecessary raw footage.
7. **World-to-Room Director**: automatically scales/spaces a fantasy world prop set around available real environment, respecting passage clearances and viewing distance.
8. **Revisit Contract**: on return, reports match confidence and changed furnishings and asks the user to confirm major realignment.
9. **Shared Scene Consensus**: compares peer anchor graph alignment and rejects divergent transforms before shared gameplay state.

These are proposed owned components, **not implemented claims**.

## 9. Scene-authoring and game relationships

World assets from Forge need metrically verified dimensions, pivot points, collider bounds, world-light direction, animation roots and multiple LODs. A large imaginary creature can be scaled to fit a room, but that transform must be intentional and communicated; it must not alter the original asset proportions. Interactive actors may be rooted to physical planes or floating world frames with rules. Indoor portals and world transitions use explicit anchored scene instances; multiplayer server state is authoritative while each client owns its local camera/tracking map.

## 10. Models, scanning, and sensor data

Learned plane/depth/semantic mapping can estimate surfaces that RGB images only partly constrain. Treat depth inferred from a single image as uncertain relative geometry unless physically calibrated, and never equate beautiful segmentation with survey-grade measurements. Capture real scene mesh/depth only with permission, process on device by default, omit faces/bystanders and private household details from logs, and support retention deletion. No pretrained model or map dataset is admitted to core in this research. Optional outside image maps require direct licensed service access.

## 11. Latency and hardware realities

Tracking requires real device cameras/IMU for actual AR; synthetic fixtures can test frame logic but cannot prove stable anchors. Rendering virtual worlds in real time needs a suitable graphics device; realistic shadows, depth occlusion and hand tracking compete for CPU/GPU/power/thermal budget. High-quality depth may require supported hardware, though some devices estimate depth without LiDAR. Budget motion-to-photon latency, frame time, sensor bandwidth, mapping memory, camera heat/power, network anchor resolve delay and tracking recovery time. Never hardcode a universal millimeter accuracy number.

## 12. Cost and privacy operation

Local anchors minimize cloud dependency and per-use map-service fees. Persistent/shared/geospatial anchors may require a provider project, billing, quotas, connectivity and private visual feature maps; their policies and price can change. Capture of room scans or geolocation can expose personally sensitive information even absent user identity. Require precise permission prompts, encryption at rest/transit, access-controlled sharing, retention TTL, revocation and full purge verification. Disable mapping upload by default. A server might store an opaque anchor ID while the client handles tracking; it should not silently store camera video.

## 13. Failure modes and safety consequences

- Anchor jitter/slow drift; sudden map relocalization moves an object through a table or user.
- Each separately anchored piece shifts by a different amount, breaking a castle or character skeleton apart.
- Plane extent updates after placement; physically real door/edge becomes falsely blocked by virtual collision.
- Dynamic furniture/person interpreted as permanent mesh; reflective glass, darkness, repetitive wallpaper, sunlight change and low texture hurt tracking.
- Real depth missing near glass/hair causes virtual objects to appear in front of occluders.
- Device loses internet, lacks LiDAR/depth, lacks VPS coverage or receives denied camera permission; feature must degrade clearly.
- Shared peers have different coordinate-origin or scaling, yielding disagreements about hitboxes/locations.
- Obscuring walkway/stairs with immersive overlays raises physical safety risk, even if renderer passes visual tests.

## 14. Evaluation and quantitative tests

Store frame timestamps, sensor confidence, valid tracking fraction, position/rotation drift over repeated fixed-anchor observations, inter-anchor relative error, relocalization time, plane/mesh point residual, depth coverage/confidence, occlusion precision/recall at labeled contact edges, frame-time percentiles, heat/battery metrics, user-perceived anchor slip and cross-device frame disagreement. Use surveyed marker/checkerboard/AprilTag positions and physically measured distances as independent truth where allowed. Separate simulated transform-unit tests from measured phone/headset results. Never claim high precision based on a simulator.

## 15. MGR integration and contracts

S18 consumes S03 geometric solids/sections and S13 camera truth, S08 living-world actors/gameplay and director/camera tools. It adds physical-frame tracking data on top without rewriting MGR spatial identity or event ledger. Represent `AnchorTruth` with `{id, class, physical_frame, mgr_parent_actor, transform_m, covariance, tracking_state, timestamp, observation_ref, rights_scope, expiry, version}`. Spatial mesh tiles carry their own timestamps, uncertainty and geometry QA reports. Anchor groups are independently testable. A device adapter must be replaceable with a synthetic fixture for regular CI, while final certification runs on named physical devices.

## 16. Acceptance gates / build order

| Gate | Scenario | Required evidence | State |
|---|---|---|---|
| A1 | Synthetic camera, world and anchor transforms | Correct round-trip transform/units/axis conventions | OPEN |
| A2 | One parent with 12 child props | Correction to parent preserves child relative placements | OPEN |
| A3 | Dynamic sensor capability matrix | Missing depth/mesh/cloud support yields explicit fallback | OPEN |
| A4 | Horizontal/vertical planes on real device | Correct detected pose, width, angle with independently measured residual | DEVICE TEST OPEN |
| A5 | Walk around object and return | Quantified anchor drift and recovery from device loss | DEVICE TEST OPEN |
| A6 | Tracking map reset | No phantom anchor persistence or unacknowledged teleport | OPEN |
| A7 | Real desk blocks virtual creature | Occlusion order correct over multiple camera angles and edge motion | DEVICE TEST OPEN |
| A8 | Transparent/reflective surfaces | Uncertain depth flagged; no false certainty | OPEN |
| A9 | One-hour active AR session | p50/p95/p99 frames, battery, temperature and tracking stability measured | DEVICE TEST OPEN |
| A10 | Two real devices sharing one scene | Matched placements within stated measured tolerances; partition/rejoin handling | DEVICE/CLOUD TEST OPEN |
| A11 | Location anchor with no coverage/network | Clear degraded mode, no fake precise fix | OPEN |
| A12 | Private room recording denied | No camera/map upload; purge/TTL verified under opt-in/out | OPEN |
| A13 | MGR cinematic fantasy prop in room | Scale, camera exposure/light and collision safety survive motion | OPEN |
| A14 | Headset/phone portability | MGR actor identity/geometry preserved through different adapters | DEVICE TEST OPEN |

**Build order:** A1–A3 independent core/simulator → local device tracking A4–A6 → geometry/depth A7–A9 → optional collaborative/geospatial A10–A11 → privacy/cross-device release gates A12–A14. The platform-dependent gates must stay open until appropriate hardware, permissions and service access are available. No destructive filesystem, room/video capture or cloud mapping outside dedicated Forge authority.

**Bottom line:** MGR can own a world-aware AR layer, but physical reality is dynamic and imperfectly sensed. The native advantage is *honest geometry, confidence, stability and safety*, not pretending camera tracking never drifts.
