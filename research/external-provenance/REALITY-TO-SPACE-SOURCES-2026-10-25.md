# Technical source provenance — reality to space

Sourced 2026-10-25. This file records legal/technical external foundations. MGR's original capability specification is `research/MGR-REALITY-TO-SPACE-MASTER-MAP.md`. Entries below were read as official documentation/reference overviews, **not** full source-tree audits or code reuse. Version/license checks remain necessary before importing code.

| Topic | Primary source | Evidence / MGR engineering consequence | Verification depth |
|---|---|---|---|
| Monocular/stereo vision | NCBI Webvision, https://www.ncbi.nlm.nih.gov/books/NBK11512/ | Motion parallax and binocular signals contribute depth; single image depth is ambiguous. Use observable cues and explicit confidence. | Official scientific overview |
| Spatial orientation | NCBI Bookshelf, https://www.ncbi.nlm.nih.gov/books/NBK518976/ | Human depth perception integrates monocular/binocular and motion cues. Prevent one-cue certainty. | Medical overview |
| Pinhole camera geometry | OpenCV calibration/reconstruction, https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html | 3D world point → 2D pixel via intrinsics/extrinsics and scale; validate MGR `camera_project` and avoid invented Z. | Official API + math overview |
| Machine slices | Ultimaker CuraEngine, https://github.com/Ultimaker/CuraEngine/wiki/Slicing | Intersect triangles with planes, connect segments into layer polygons. First MGR section output deliberately stops before contour welding/toolpaths. | Upstream architectural wiki; core code not audited |
| Slicer runtime | CuraEngine internal notes, https://github.com/Ultimaker/CuraEngine/wiki/Internals | Layer polygons, topology/holes/normals are core to print paths. Need geometry QA before hardware. | Upstream architecture overview |
| 3D print interchange | PrusaSlicer I/O docs, https://help.prusa3d.com/category/input-output_209 | STL is geometry; 3MF stores project and settings; G-code controls print execution. No image-to-3D conversion implied. | Official product docs |
| Virtual game worlds | Unreal Engine World Partition release docs, https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5.0-release-notes?application_version=5.0 | Cells, data layers and automatic loading bound runtime world scale. Study chunk/visibility residency. | Official product architecture |
| Virtualized geometry | Unreal Nanite docs, https://dev.epicgames.com/documentation/unreal-engine/nanite-virtualized-geometry-in-unreal-engine | Visibility-related work, compressed fine-grained streaming and detail at pixel scale. Not license to copy vendor source. | Official product architecture |
| Virtualized shadows | Unreal Virtual Shadow Maps docs, https://dev.epicgames.com/documentation/unreal-engine/virtual-shadow-maps-in-unreal-engine | Page/tile allocation based on visible depth and detail. MGR Light/Shadow Judge should test screen-space relevance and budgets. | Official product architecture |
| GPU drawing pipeline | Vulkan official tutorial, https://docs.vulkan.org/tutorial/latest/03_Drawing_a_triangle/02_Graphics_pipeline_basics/00_Introduction.html | Geometry primitives become fragments and depth-buffer tests reject obscured pixels. | Official API tutorial |
| GPU raster specification | Vulkan specification, https://docs.vulkan.org/spec/latest/chapters/primsrast.html | Defines projection-to-framebuffer occupancy/depth rules. | Published standard |
| Direct3D console/PC graphics | Microsoft Direct3D guide, https://learn.microsoft.com/en-us/windows/win32/direct3d/ | GPU vertex/pixel/compute pipeline, not CPU-only execution. MGR must distinguish build CPU path from real-time rendering. | Official platform docs |
| AR spatial tracking | Apple ARKit world tracking, https://developer.apple.com/documentation/arkit/understanding-world-tracking | Visual-inertial odometry and anchors align real and virtual spaces, with drift and mapping uncertainty. | Official platform docs |
| Neural/field-based display | NVIDIA Research light-field visualizations, https://research.nvidia.com/labs/amri/projects/g2lf/ | Gaussian/sparse field rendering is a representation option, not inherently editable/watertight collision geometry. | Research project overview |

## Research integrity

- No proprietary Fortnite/PlayStation reverse engineering, hidden source extraction, SDK entitlement bypass or console firmware modification performed or proposed.
- Public Unreal docs show architectural lessons, **not access to Fortnite's confidential production build**.
- A slicer consumes 3D mesh and emits planned toolpaths; this is distinct from neural single-image model inference.
- Remaining research: current OpenXR/VR/SLAM stack comparisons; physically based CAD/CSG and anatomy; full engine code path review; open license status; actual slicer and target-engine execution; multi-view/uncertainty benchmarking.
