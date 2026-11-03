# Imported static GLB morph — native implementation and independent proof

The original morph engine deformed generated Forge meshes. Imported character intake preserved a model as a candidate but supplied no native deformation of its original geometry. `forge/imported_morph.py` closes that specific gap: it applies the existing six-control Forge field to the original static GLB's vertices across all source parts in world space, preserving hierarchy and original source bytes.

The implementation appends transformed float32 positions, normals and tangents to the original binary payload. It retains original indices, UVs, images, materials, names, hierarchy and transforms. Normals use the analytic inverse-transpose derivative; tangents follow the forward derivative and retain handedness. A derived revision contains `original.glb`, `morphed.glb` and a hash-bound `morph-receipt.json`. Existing revision folders refuse overwrite. Source SHA mismatches refuse before allocation.

## Executed proof

`python scripts/verify_imported_morph.py --out artifacts/imported-morph-verification-final-20261102`

Result: `ACTUAL_STATIC_MORPH_ACCEPTANCE_PASS`. This builds an original owned CPU-authored two-part static GLB with UVs and an embedded 2x2 image, creates its morph revision, then launches a separate Blender 5.2.2 LTS process. Blender imports both files, records independent object/triangle/UV/material/image-pixel facts, measures bounds against the creator's receipt and renders both with the same camera and lights using CPU Cycles. Both actual images were opened and visually inspected: the source parts are upright boxes; the derived parts stretch, bend and twist while preserving the source texture and separate parts.

- Source GLB SHA-256: `3e94a29c238d12718f55973795501bd82d89a8620263372c2e3ccade5362f21b`.
- Derived GLB SHA-256: `a38db2b4923cd86daf29d7b4f2fe5df266bf912e802f1963af4bee574d6cf25d`.
- Both imports: 2 named parts, 48 vertices, 24 triangles; identical UV loop hashes, material assignments and decoded embedded-image pixel hash.
- Independent imported bounds match the native before/after world bounds after glTF-to-Blender axis conversion.
- Actual 700x500 before/after PNGs and separate Blender witness are retained here. Raw GLBs, `.blend` files and logs remain in the ignored local artifacts directory above.

## Native integration checks

`python -m unittest tests.test_imported_morph tests.test_creation_asset_jobs -v`

The focused log is retained as `tests.txt` (expanded to 68 related tests). The core's 11 tests exercise preservation, shared world coordinates, source binding, overwrite refusal, deterministic bytes, explicit unsupported inputs, hierarchy/transforms, budgets, nonlinear derivative normals/tangents, interleaved attributes and read-only affine/shear world-position observation. The adapter's 7 tests execute real PNG/GLB creators through `ForgeWorkstation.command`, restart and replay exact saved work, navigate original saved history, verify input identity, reject source/request/artifact/receipt tampering, refuse invalid input before job/journal allocation, preserve failed executions without retry and preserve saved replay at journal capacity. These adapter tests cover the actual command/native persistence path; browser rendering, HTTP authorization and shared-edge/MCP acceptance are separate parent-owned checks.

## Explicit limits and next work

This is a static source-preserving deformation path, not completion of all morph capabilities. Skins, animation, existing shape targets, differently transformed instances of one mesh, multiple scenes, compressed geometry, external buffers/images and unsupported geometry extensions explicitly refuse. No input rig or animation is stripped to make an unsupported file appear accepted. Global length/height/width/twist/bend/taper is not semantic face/body fitting, topology editing or learned image reconstruction. Large deformations can stretch existing textures. Self-intersection is not fully solved. Rig-aware revisions need a separate bind-pose, skin and animation-preservation design plus independent deformed-rig verification. The current owned fixture proves an actual GLB import and deformation with preserved texture/parts; it does not establish quality for arbitrary production assets, owner likeness, photoreal art or target-engine acceptance.

No provider generation, model download, hosted GPU or paid operation was used. The native creator does not mark its own output independently verified; the separate Blender witness records that narrower external proof. Owner art acceptance and rig deformation verification remain false.
