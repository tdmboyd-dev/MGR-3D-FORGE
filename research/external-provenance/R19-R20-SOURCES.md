# R19–R20 external provenance — Meta Reality Labs and Apple ARKit

Checked 2026-10-25. Primary developer documentation and first-party research-repo overviews only. **Level:** `DOC` = selected official docs/API pages reviewed, `REPO-OVERVIEW` = primary research repo description located, `RUN` = executed sample/device test (**none**), `SOURCE-DEEP` = complete implementation/dependency/license/test audit (**none**). Links do not imply code or model adoption.

## R19 Meta Horizon OS / Reality Labs

| Official source | Verified scope | Evidence depth / native relevance |
| --- | --- | --- |
| [Horizon OS passthrough](https://developers.meta.com/vr/essentials/horizon-os-passthrough/) | Passthrough, environment depth, scene understanding and anchors are separate immersive components | DOC; feeds independent depth/scene/anchor contracts. |
| [Horizon OS immersive features](https://developers.meta.com/vr/essentials/horizon-os-immersive-features/) | Room models, anchoring virtual objects to physical environment | DOC; supports Anchor Truth Ledger concept. |
| [Horizon OS platform overview](https://developers.meta.com/vr/essentials/horizon-os/) | Mixed-reality feature and device-specific app memory limits | DOC; actual headset memory and app feature tier unknown. |
| [Meta Depth safety](https://developers.meta.com/vr/design/mr-health-depth/) | Depth-occlusion limitations and health/safety concerns | DOC; safeguards are not replaceable by depth alone. |
| [Meta scene understanding design](https://developers.meta.com/vr/design/mr-design-scene/) | Scene semantics and depth occlusion, camera/context limitations | DOC; no hidden-object reconstruction proven. |
| [Meta passthrough camera API](https://developers.meta.com/vr/documentation/spatial-sdk/spatial-sdk-pca-overview/) | Computer-vision capture path on named supported headsets/OS versions | DOC; **not** universally available to arbitrary app/device. |
| [Meta spatial anchors](https://developers.meta.com/vr/documentation/unreal/unreal-local-spatial-anchors/) | Local/cloud persistence and anchor UUID concepts | DOC Unreal-path; native cross-session test not run. |
| [Meta Movement SDK OpenXR overview](https://developers.meta.com/vr/documentation/native/android/move-overview/) | Body, face, eye tracking abstraction | DOC; native capture adapter candidate. |
| [Meta Movement OpenXR API](https://developers.meta.com/vr/documentation/native/android/move-api/) | Permission-gated face/eye features and tracking API boundaries | DOC; privacy/feature negotiation mandatory. |
| [Meta Movement face tracking](https://developers.meta.com/vr/documentation/unity/move-face-tracking/) | Abstract FACS-like facial expression channels | DOC Unity path; no direct MGR backend. |
| [Meta Movement Unity sample overview](https://developers.meta.com/vr/documentation/unity/unity-sample-movement/) | Body/face retarget, networked avatars and motion synthesis examples | DOC sample description only, not built/read end-to-end. |
| [Meta audio2photoreal research repo](https://github.com/facebookresearch/audio2photoreal) | Research code/dataset described for photoreal Codec Avatars from audio | REPO-OVERVIEW; **model weights, dataset consent, terms, runtime and full code not audited**. Study only. |

**Meta restrictions/unknowns:** Meta Quest/Horizon OS SDK, third-party Unity/Unreal plugin, SDK entitlement, OS version, device SKU, sensor permissions and Meta research model/dataset terms are distinct. Face/eye/body motion and room scans are sensitive. A public research release is not blanket commercial avatar/voice/face permission. No user Quest device or SDK installation verified. Camera/passthrough usage must honor official permissions, safety restrictions and user consent. Do not publish raw capture, calibration, private home layout, or biometric streams to public Forge.

## R20 Apple ARKit / visionOS

| Official source | Verified scope | Evidence depth / native relevance |
| --- | --- | --- |
| [Understanding world tracking](https://developer.apple.com/documentation/arkit/understanding-world-tracking) | Camera pose alignment, raycasting, tracking quality and planes changing over time | DOC; confidence and relocalization gate. |
| [Managing session life cycle/tracking quality](https://developer.apple.com/documentation/arkit/managing-session-life-cycle-and-tracking-quality) | Session failure/relocalization and map mismatch risks | DOC; unknown/lost states. |
| [Tracking and visualizing planes](https://developer.apple.com/documentation/arkit/tracking-and-visualizing-planes) | Plane anchors added and revised during AR session | DOC sample overview only, sample code not run. |
| [Scene reconstruction](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction?changes=_6&language=objc) | Polygonal mesh estimate and plane smoothing | DOC; Scan-to-World source uncertainty. |
| [ARMeshAnchor](https://developer.apple.com/documentation/arkit/armeshanchor) | Environment expressed as mesh anchors | DOC; mesh chunks and revision scheme. |
| [Visualize reconstructed scene](https://developer.apple.com/documentation/arkit/visualizing-and-interacting-with-a-reconstructed-scene) | LiDAR depth and mesh classification example | DOC sample overview only; no device run. |
| [Scene depth semantics](https://developer.apple.com/documentation/arkit/arconfiguration/framesemantics-swift.struct/scenedepth) | Scene depth requires LiDAR-capable/support-checked device | DOC; explicit feature gate. |
| [ARFaceAnchor](https://developer.apple.com/documentation/arkit/arfaceanchor) | Facial position/orientation/expression and blendshapes | DOC; semantic face clip adapter. |
| [ARFaceAnchor blendshapes](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapes?changes=l_9__8&language=objc) | Portable coefficients for expression controls | DOC; coefficients not raw identity/geometry proof. |
| [Tracking/visualizing faces](https://developer.apple.com/documentation/arkit/tracking-and-visualizing-faces) | Coarse face mesh and expression animation sample; platform support varies | DOC sample overview, not SOURCE/RUN. |
| [Combining face/world tracking](https://developer.apple.com/documentation/arkit/combining-user-face-tracking-and-world-tracking) | Face expression transform can be anchored to world | DOC; fused coordinate receipt candidate. |
| [ARKit world-sensing authorization](https://developer.apple.com/documentation/arkit/arkitsession/authorizationtype/worldsensing) | Authorization for world-sensing features | DOC; permission workflow required. |
| [visionOS world anchors](https://developer.apple.com/documentation/visionOS/tracking-points-in-world-space) | Anchored points across sessions on relevant devices | DOC; cannot assume same implementation for iPhone ARKit. |

**Apple restrictions/unknowns:** Frameworks, App Store/Apple Developer Program agreements, hardware feature support, OS/version, world-sensing permissions and privacy requirements apply. LiDAR and facial tracking capabilities vary by actual supported device. Reconstructed geometry is an estimate, can change, and cannot reveal hidden/unobserved structures. No Apple physical device or current SDK version tested. Raw faces and scanned rooms remain private unless explicitly consented.

## Native synthesis and test evidence table

| Independent MGR design | Meta input lesson | Apple input lesson | Truth test required |
| --- | --- | --- | --- |
| Depth Truth compositor | Environment depth and passthrough occlusion | LiDAR sceneDepth/mesh anchors | Measured occlusion against annotated moving near/far objects; unknown masks handled. |
| Spatial Anchor Ledger | Persistent local/cloud anchors | World tracking and session relocalization | Restart, drift, moved furniture, wrong room, revoked auth. |
| Living Rig performance bridge | Body, face, eye/FACS and networked avatar ideas | FaceAnchor blendshape expression controls | Retarget to own rig with pose/contact, side views, latency and consent. |
| Scan-to-World mesh steward | Room semantic labels/scene layout | ARMeshAnchor and classified LiDAR mesh | Ground-truth scale, holes, stale chunks, Blender editability. |
| Spatial Evidence envelope | Device permission and sensor scope | World-sensing authorization and session tracking states | Revocation, minimization, privacy and cross-device state truth. |

**Follow-up source-depth gate:** choose a specific headset/iOS device and framework version, inspect actual SDK repo/package tree, manifest, license, example source, tests, binary dependencies and maintenance; execute official sample with denied permissions and compare real captured data to independently measured geometry. Until then these are educational architecture audits, **not end-to-end reverse engineering and not proof of device-connected Forge features**.
