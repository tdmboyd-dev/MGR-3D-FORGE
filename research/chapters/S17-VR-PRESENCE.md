# S17 — MGR Presence Engine: Stereoscopy, Embodied Cameras and Comfortable VR

**Owner:** MGR · **Date:** 2026-10-25 · **Status:** Scoped primary-source research; **not** headset-tested production VR. Primary-source ledger is `research/external-provenance/S17-VR-SOURCES.md`.

## MGR-native verdict

A visually impressive 3D render and a comfortable six-degrees-of-freedom (6DoF) world are fundamentally different deliverables. Forge should first maintain a physically consistent, navigable world and add an **optional immersive interface** that respects the headset's real-time runtime, per-eye projections, tracked head pose, display deadlines, room boundary and comfort settings. Do not make VR the prerequisite for building characters/worlds: CPU Blender stills and desktop navigation must remain independently functional.

## 1 — Definition and scope

- Stereoscopy: each eye sees a distinct perspective, providing binocular disparity; it does not invent missing geometry.
- 6DoF: tracked translations along three axes and rotations around three axes; rotational-only 3DoF is not equivalent.
- Presence: subjective feeling of being situated in a simulated environment, affected by viewpoint consistency, head tracking, scale, hands, audio, interactivity and stable latency. It is not captured by one photorealistic screenshot.
- XR runtime: device-specific system handling poses, frame prediction/compositing, display optics and supported controller/hand paths. Rendering application and runtime divide responsibilities.
- Optical display: lens distortion, field of view, inter-pupillary separation, resolution/degree, persistence and eye-relief/fit can limit realism independent of scene detail.

## 2 — Full production workflow

1. Produce metrically coherent geometry and collision surfaces; declare origin, gravity, scale, reachable and nonreachable regions.
2. Device probe: runtime, headset displays/view count, refresh, render target, position tracking and supported input extensions.
3. Enter XR session and allocate runtime-compatible swapchains; query predicted display time and view poses each frame.
4. Render per-eye images using supplied view/FOV, submit layers to compositor; allow runtime optical distortion/timewarp mechanisms.
5. Map controller/head/hand poses to the same world origin; implement tracking-loss states and safe re-centering.
6. Navigate with comfortable defaults (teleport/snap turn) and opt-in controlled smooth locomotion.
7. Test latency, missed frames, temporal artefacts, user reach/ergonomics, accessibility and real-room safety before deployment.

## 3 — Standards and contracts

- OpenXR is the primary native runtime interoperability contract; WebXR is an optional browser-facing XR adapter where actual device/browser support exists.
- Reference spaces `VIEW`, `LOCAL`, `STAGE` etc. have distinct origins/lifetimes; pose values need timestamps and validity flags. Never use a stale head pose as ground truth.
- Clock domain and runtime `predictedDisplayTime` must be preserved; camera/view poses should reflect the runtime's predicted presentation time.
- Hand joint location is an optional negotiated extension, not a universal feature. Controller actions are not interchangeable with hand skeletal data.
- Use app-frame vs runtime-compositor vs display latency terminology precisely, and explicitly log the portion actually measurable by an app.

## 4 — Key research foundations

- Stereo disparity depends on each-eye projection, eye baseline and point depth; inter-eye images must use their proper view/projection, not duplicated monocular cameras.
- Visual–vestibular mismatch can cause cybersickness when the virtual camera accelerates/rotates without matching bodily motion.
- Vergence–accommodation conflict: conventional fixed-focus stereo displays suggest a 3D convergence distance that differs from the optical focusing distance. Published psychophysics shows potential fusion/fatigue problems; **software alone cannot eliminate hardware's fixed-focus conflict**.
- Motion-to-photon latency combines sensing, simulation, rendering, queues, compositing, scanout and optical emission. Consistent low latency and stable frame times matter, not just mean FPS.
- Late latching/pose prediction can reduce view/controller lag; runtime reprojection helps but cannot repair arbitrarily broken frames and fast animated objects.

## 5 — Implementation and research families

- Khronos OpenXR core spec and official SDK/Guide: runtime lifecycle, frame wait/begin/end, swapchains, layers, actions, reference spaces and extension discovery.
- W3C WebXR spec: browser XR session, frames, views and reference spaces; used when a browser can genuinely enter immersive mode, with permission and secure context.
- Meta official developer engineering references: operational frame budgets, missed-frame behavior, late latching, comfort and locomotion choices. Policies/hardware refresh options can change by device/runtime.
- Peer-reviewed vision studies: binocular display and accommodation mismatch; experimental evidence constrains user-comfort claims.

## 6 — Geometry, optics and equations

- Frame budget is approximately `1000 / refresh_hz` milliseconds: 72 Hz ≈13.89 ms; 90 Hz ≈11.11 ms; 120 Hz ≈8.33 ms **per refresh**, with application headroom below this for compositor/system demands.
- Per-eye view and asymmetric frustum come from runtime, which also handles/display-maps optical distortion. Hardcoding lens coefficients from another headset can cause spatial mismatch.
- A user's eye position can change by real head translation; 2D equirectangular or stereo video without correct parallax cannot offer arbitrary 6DoF.
- Reprojection cannot reconstruct independent hidden geometry in a newly exposed viewpoint; disocclusion needs real scene data or explicitly inferred content.

## 7 — MGR-owned witness data

- Metric checker room, waist-height table, doorway, horizon grid, near/far parallax objects, finger-sized UI targets, reachable object, collision wall and floor marker.
- Tracked synthetic replay with head rotation and translation, snap turn, joystick locomotion, disocclusion, fast crossing object, hand grasp/release and tracking loss.
- Night/smoke/FX scene measuring per-eye transparency ordering, temporal ghosting and readability in high/low luminance.
- Maintain baseline device profile and user comfort survey only with consent; no raw hand/head/eye recordings retained beyond justified task needs.

## 8 — Licensing, platform and human-data considerations

- The OpenXR/WebXR standards explain interoperability, not licenses to distribute proprietary vendor runtimes, headset drivers or sample assets. Review SDK and individual sample file licenses.
- Tracking data may reveal sensitive behavior; permission, on-device minimization and retention boundaries are mandatory.
- VR comfort issues can include nausea, disorientation, collisions and falls; use visible physical-boundary guidance, pause/recenter functions and no forced physical movement. Do not claim medically guaranteed comfort.

## 9 — APIs, adapters and session states

- Native adapter behind `XRRuntime`: probe, initialize, begin session, frame prediction, locate views/inputs, acquire image, submit, focus/suspend, exit, cleanup.
- Browser adapter behind `WebXRRuntime`: supported/unsupported decision, permission failure, reference-space setup, XR animation loop and input source events.
- Shared scene renderer gets `world_snapshot`, `eye_view`, `eye_projection`, `predicted_display_time`, `render_budget_ms` and optional hand/controller streams. Never allow untrusted scene scripts direct access to hardware sensor storage.

## 10 — Original MGR-native capabilities and contract

**Presence Truth Ledger:** logs exactly which tracking, stereo and timing claims hardware supports. **World-to-Body Anchor:** maps authored avatars/props to stable physical-scale reach without changing canonical geometry. **Ghost Frame Prosecutor:** correlates dropped frames with motion ghosts and disocclusion. **Comfort Director:** selectable locomotion/head-relative UX and exposure/time limits. **Hands of Reality:** tracked/inferred hands visibly tagged with confidence and fallback to controllers. **Beyond-Lens Studio:** creative scene effects tested for per-eye consistency, not 2D fake depth.

```json
{
  "xr_session_id": "mgr-xr-session", "runtime": "detected-not-assumed",
  "device": {"view_count": 2, "refresh_hz": null, "supports_6dof": false, "hand_tracking": false},
  "reference_space": "LOCAL", "world_scale_meters_per_unit": 1,
  "frame": {"predicted_display_time": null, "left_view_id": "left", "right_view_id": "right", "app_cpu_ms": null, "app_gpu_ms": null, "dropped": null},
  "comfort": {"locomotion": "teleport", "turning": "snap", "boundary_required": true},
  "proof": {"per_eye_parallax": "unverified", "tracking_loss": "unverified", "status": "device-not-tested"}
}
```

## 11 — Hardware/runtime boundaries

- No headset: can test stereo math, rendering and lifecycle mocks but **cannot** certify optical distortion, measured motion-to-photon latency, real 6DoF head tracking, hand occlusion or comfort. The Windows Blender installation is insufficient to pass these gates alone.
- A headset's tracking cameras/IMUs, compositor and drivers determine capabilities. Some devices support controller-only tracking, optional hands or additional eye tracking; enumerate at runtime.
- Mobile standalone XR has harder thermal, battery, memory and frame budgets than desktop offline Cycles. Performance must be measured *on device* after warmup and during sustained load.

## 12 — Cost tiers and optional hardware

CPU/headless stereo witness generation: no new hardware purchase. Browser/desktop emulator smoke checks: minimal external cost but not VR certification. True VR acceptance requires a compatible real headset, runtime and a device capable of presenting the target scene; defer hardware purchases until an approved user requirement selects the target. Do not silently route private camera/hand telemetry to external services.

## 13 — Critical failure and adversarial cases

1. Both eyes get the same projection (fake 3D). 2. Swapped eye images or inconsistent eye baseline. 3. World rendered at toy/giant scale. 4. Camera/head pose one or more frames stale. 5. Application misses refresh repeatedly. 6. Unexpected teleport/forced smooth acceleration. 7. Tracking loss causes object/jitter jump. 8. Runtime boundary ignored and player collides with real furniture. 9. One-eye compositing/transparent FX mismatch. 10. Controller and hand spaces mixed. 11. UI too small/too close causing discomfort and unreadable text. 12. Static 360° panorama fraudulently advertised as 6DoF. 13. Hand tracking extension called without support. 14. High render quality overheats mobile device and throttles. 15. Extra artificial camera shake ruins comfort. 16. Photosensitive effects/intense flashing deployed without appropriate risk review and controls.

## 14 — Quantitative acceptance matrix

| Gate | Instrument | Acceptance basis |
|---|---|---|
| Runtime discovery | Actual OpenXR/WebXR enumeration | Supported/unsupported features accurately reported; no fabricated hands/eye tracking |
| Stereo geometry | Synthetic indexed per-eye witness | View/FOV and disparity match reference math, without swapped images |
| 6DoF poses | Runtime head trajectory recording | Correct translation/rotation scale, reference frames and tracking validity |
| Controller/hands | Runtime joints/actions replay | Dropouts/reacquisition safe, controllers fallback, no false joints |
| Frame timing | Device frame stats and wall-clock logs | Sustained target refresh and accepted dropped/missed frame envelope defined per device |
| Latency | Hardware-assisted end-to-end measurement when available | Full measurement method and uncertainty documented; app-only timing not mislabeled as photon latency |
| Distortion/color | Real headset through-lens test | Per-eye alignment, chromatic/lens artefacts and comfort review |
| Locomotion | User comfort/accessibility protocol | Teleport/snap settings available, no forced acceleration, exit/recenter always accessible |
| Safety | Guardian/boundary/tracking-loss rehearsal | Pause/recover/physical bounds and falls/collision mitigations verified |
| Endurance | 30+ minute device-specific warmed session | Sustained performance, memory and thermal trends tracked without hidden regressions |

Pass thresholds remain device- and user-population-specific. Synthetic stereo renders can pass a simulation gate while hardware/comfort gates remain explicitly blocked.

## 15 — Placement and phased implementation

1. Keep desktop world creation, S02/S07 physical reference rendering and S12 camera truth as baseline.
2. Add MGR-native stereo/six-axis pose and reference-space validation **without requiring hardware**.
3. Build replaceable OpenXR native adapter and a WebXR browser adapter only when target platform selected.
4. Add comfort director and tracking-loss states before enabling unrestricted locomotion.
5. Run real device frames, thermal/latency and per-eye tests; version hardware/runtime profiles and isolate platform-specific failures.
6. Connect director cameras/Fx to per-eye QA so cinema effects have consistent VR variants (or are disabled when unsafe).

## 16 — Acceptance / completeness boundary

**Research:** 16 documented fields and primary evidence ledger. **Implementation:** not evidenced by this file. **Desktop stereo prototype:** passes simulated stereo/pose tests. **VR production:** only accepted after actual runtime/headset per-eye rendering, measured sustained frames, tracked 6DoF, safe hand/controller handling, optical/view verification, tracking-loss recovery and comfort/safety evaluation. If the current lab lacks headset access, status must be **hardware verification pending**, never 100%.

**Recommendation:** put **World-to-Body Anchor + Ghost Frame Prosecutor + Comfort Director** in the build queue, but do not delay core Forge character/world authoring or misrepresent Blender-only tests as immersive-headset proof.
