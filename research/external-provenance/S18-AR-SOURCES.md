# S18 external provenance — mixed reality and spatial anchors

Captured 2026-10-25. External references inform, but do not name or own, MGR-native product contracts in `research/chapters/S18-AR-ANCHORS.md`. Primary vendor/standards documentation was inspected; **no physical headset, phone sensor or proprietary SDK ran in this research wave**. Exact availability depends on device OS, sensors, location, permission, network and SDK release.

| Primary source | URL | Verified technical lesson | Rights and implementation limits |
|---|---|---|---|
| Khronos OpenXR 1.1 ratified spec | https://registry.khronos.org/OpenXR/specs/1.1-khr/html/xrspec.html | Reference spaces, transforms and runtime-mediated XR sessions. | Open standard; extension support and deployment runtimes vary; read-only spec inspection. |
| Khronos OpenXR extensions | https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html | Additional vendor spatial-anchor/spatial-entity capabilities can extend core. | All-extension document is **not itself entirely ratified**; each extension availability must be queried. |
| Apple world tracking | https://developer.apple.com/documentation/arkit/understanding-world-tracking | Camera/inertial motion tracking places virtual content relative to world; planes initially inaccurate and may shift as observations accumulate. | Proprietary SDK/platform rules; no Apple device run. |
| Apple plane tracking | https://developer.apple.com/documentation/arkit/tracking-and-visualizing-planes | Horizontal/vertical physical planes have live-updating anchors, bounds and transforms. | Platform permission and supported device. |
| Apple scene reconstruction | https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction | Supported devices can return estimated polygonal environment meshes, with LiDAR/smoothing and imperfect real-world surfaces. | Sensor hardware constraints; recon mesh is an estimate not survey-grade CAD. |
| Apple geo tracking | https://developer.apple.com/documentation/ARKit/ARGeoTrackingConfiguration | Visual localization can place geographic anchors using imagery matched to georeferenced environment. | Geography/coverage and vendor terms constrain use. |
| Google ARCore anchors | https://developers.google.com/ar/develop/anchors | Anchor poses update as tracking improves; independent anchors can adjust independently and cause drift between nearby virtual objects. | Android/iOS SDK-specific support, permission and quota; cannot guarantee perfect stability. |
| Google cloud anchors | https://developers.google.com/ar/develop/cloud-anchors | Cloud persistence/sharing hosts spatial feature maps and allows devices to resolve same place. | Uploads mapping/visual information; privacy/consent, credentials, quota, lifecycle and usage terms. |
| Google cloud anchors NDK | https://developers.google.com/ar/develop/c/cloud-anchors/developer-guide | Hosting includes visual data + pose; resolving uses visual feature recognition and hosted unique IDs. | Sensitive mapped-space data; user opt-in necessary. |
| Google geospatial AR | https://developers.google.com/ar/develop/geospatial | Site coverage relies on visual positioning/location imagery; geographic anchor scale and precision depend on coverage. | Geospatial service dependence, connectivity, local safety/privacy rules. |
| Google ARCore depth | https://developers.google.com/ar/develop/depth | Depth imagery helps virtual objects respect real-object occlusion and physical contact. | Availability by supported device and optional depth sensor; confidence varies. |
| Microsoft spatial anchors | https://learn.microsoft.com/en-us/windows/mixed-reality/design/spatial-anchors | Local anchors stabilize holograms relative to mapped physical space; use gaze ray and spatial mesh for placement. | HoloLens-focused docs; device/runtime version constraints. |
| Microsoft coordinate systems | https://learn.microsoft.com/en-us/windows/mixed-reality/design/coordinate-systems | Spatial maps and coordinate frames can reset or become invalid, losing anchor placements. | Re-localization and failure policies required, no durability guarantee. |

## Source-to-product boundary

- No third-party branded world-tracking service or API is required for MGR's canonical scene graph; sensors are accessed only through platform adapters.
- OpenXR is valuable for portable XR rendering/input spaces, but core conformance **does not guarantee** camera passthrough, scene mesh, global geospatial resolution or cloud anchors.
- Platform visual positioning may use proprietary map imagery. Do not scrape/rehost maps or claim access without an authorized API and valid credentials.
- Spatial mapping may capture bystanders, family homes, workplace layouts and precise location. Require local-first defaults, explicit consent and deletion controls before any cloud sharing.
- No product claims about sub-centimeter precision or universal persistence should be made without repeated device measurements over environmental changes.
