# MGR World Flight Runtime — Delivery Contract

Owner: MGR. 2026-10-25. This defines a **user-facing working experience** with a measurable acceptance gate; green unit checks alone are insufficient.

## Bounded end-to-end user workflow

1. Author a world spec (for example `examples/neighborhood.json`).
2. `forge.cli build` outputs actual GLB geometry and integrity-checked scene metadata.
3. `forge.cli world-flight` validates the GLB hash and embeds the real geometry plus manifest in **one offline HTML file**. No account, CDN, API payment or local server required.
4. Open the HTML in a WebGL2 desktop browser. GPU triangles are drawn with authored base materials and light shading. W/A/S/D moves, E/Q changes height, arrow keys turn and dragging adjusts view.
5. HUD shows live FPS/camera coordinates/collision stops. Ground-plane movement checks building bounds.
6. Rebuild the world with a different seed or layout; corrupt sources and output overwrites are rejected.

## Acceptance gates

| Gate | Proof required |
|---|---|
| Packaging | Actual hashed GLB included; no external runtime URLs; invalid input rejected |
| Syntax/tests | `node --check viewer/runtime.js`; positive and negative package tests |
| Browser rendering | WebGL2 context; draw calls; nonblank screenshot; positive measured FPS |
| Interaction | Camera moves, rotation works, building bounds reject movement |
| Offline | The same saved page reopens without network |
| Platform | Actual Windows GPU/browser execution and independent second browser/render backend |

## Important current limits

- This is a real WebGL2 rendering program for **generated static neighborhoods**, not a photoreal game engine or cinematic asset editor.
- GLB subset: float3 positions/normals, uint32 triangle indices and PBR baseColorFactor. No skinned characters, textures, node transforms, animations or extensions in this viewer yet.
- Building collision is a horizontal bounds check each frame. The native swept contact module is not yet connected to this JS path; rapid movement may jump a thin obstacle under unusual frame time.
- Bundles cap GLB at 40 MB. Large-scale streaming still requires active geometry paging, LOD/instancing, an I/O service and GPU memory accounting.
- Full Forge production requires Tevin owner-approved assets, a substantial editing UI, high-quality light/material/FX, independent visual review, navigation and game-world acceptance.

Technical specification references are isolated in `research/external-provenance/MGR-LIVE-WORLD-STANDARDS.md`.
