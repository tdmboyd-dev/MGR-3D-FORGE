# Native CPU UV authoring with preserved source revisions

`forge/uv_authoring.py` adds actual UV creation for a bounded untextured static GLB. The original generated exporter supplied no UV layout. This path uses every original triangle as an individual planar chart, preserves its intrinsic proportions and orientation, packs it into a unique padded atlas cell and writes a real float32 `TEXCOORD_0` accessor. It does not merely assign a checker or claim source preservation as UV creation.

Seams require duplicated vertices and remapped active indices. Every supported vertex attribute is duplicated consistently, including normalized vertex colors; existing tangents are recomputed for the new UV field. The original GLB and complete original BIN payload remain byte-for-byte intact, while the active geometry uses appended attribute/index buffers. World triangles, triangle order, material assignments, part names, hierarchy and transforms remain preserved. UV authoring refuses existing UVs/textures, skins, animation, original shape targets, unsupported extensions, excessive budgets and float32-collapsed islands before persistent allocation.

The output is a new revision containing `original.glb`, `uv-mapped.glb`, `uv-receipt.json` and an original `diagnostic-checker.png`. Existing output folders refuse overwrite. The checker is diagnostic QA, with no claim of native texture art, painting or baking.

## Executed verification

```
python -m unittest tests.test_uv_authoring -v
python scripts/verify_uv_atlas.py --out artifacts/uv-atlas-verification-final-20261102
```

Thirteen focused tests pass: seven native core and six original Studio job integration checks. They inspect actual GLB accessor data and triangle correspondence, all supported attribute duplication, normalized colors, recomputed tangent orthogonality/handedness, float32 island areas/range/padding/nonoverlap, exact immutable source bytes, deterministic output, hash mismatch refusal and unsupported-source refusal before output allocation. A real small source with 10,000 shared-index triangles and 1,001 aliased color attributes is rejected by a conservative expansion budget before any output bytearray can be allocated; otherwise it would amplify beyond 120 MB. The source BIN, all duplicated attributes/UVs/indices and conservative metadata overhead are included in that budget.

The Studio integration suite executes actual native UV jobs and verifies replay/restart/history/reopen/request binding, changed input refusal, existing-UV refusal before allocation and request/source/GLB/receipt/checker tamper refusal. A real 10,000-triangle shared-index fixture successfully saves and reopens with a receipt larger than 1 MB but inside the UV-specific 8 MB limit. A separately labeled oversized native-preflight-receipt fault injection refuses before job/journal allocation. These tests initially reproduced a real old 1 MB status-reader mismatch; the original adapter owner repaired that bound and added pre-allocation serialization checks. All thirteen now pass; see `tests.txt` and `job-tests.txt`.

The separate Blender 5.2.2 LTS process returned `INDEPENDENT_UV_ATLAS_IMPORT_CHECKER_RENDER_PASS`. It imported the actual original and UV revision, independently compared world-space triangle/material/name inventories and inspected actual imported UV coordinates. It measured 24 nonzero, nonoverlapping islands inside the unit UV square on the original two parts. It applied the diagnostic checker only inside the separate Blender scene, rendered with CPU Cycles and saved a diagnostic `.blend`. The actual PNG was opened and inspected: checker coordinates follow every face, with the expected visible per-triangle seams. The delivered GLB's original material definitions remain unchanged.

- Derived GLB SHA-256: `f244b1ec1bbcc7ff88ce93a26a04f1d799a2695cd069efcaa184007fa8c8be24`.
- Source counts: 48 vertices, 24 triangles, two named parts/materials.
- Revision counts: 72 vertices, the same 24 triangles, two named parts/materials.
- Native atlas: 2048-square coordinate layout, two-pixel padding, five cells per row.
- Exact byte regeneration from final native source matched the independently imported artifact.

Safe native/Blender receipts, source hashes, focused log and actual checker render are retained here. Raw GLBs, diagnostic `.blend` and subprocess log remain in the ignored local artifact directory above. The native receipt keeps independent verification false; the separate Blender witness owns that external proof.

## Scope and limitations

This is a deterministic, fully seamed atlas, not semantic chart unwrapping or a distortion/texel-density optimizer. Every triangle becomes an island, so seams and vertex expansion are intentional. The method is appropriate as a real editable CPU starting layout and diagnostic/export contract, not a claim of a film/game texture workflow. The source cap is 16,384 triangles, with explicit resolution/padding fit checks and float32 area refusal. Atlas sizes are 256/512/1024/2048/4096, padding one to sixteen pixels. Existing UV/textured inputs refuse instead of silently replacing authored work. Further work includes chart merging, seam selection, packing efficiency, user-selected texel density, baking and original texture/material authoring. No provider, model download, GPU hosting, owner art approval or target-engine acceptance is claimed.

## Native API / use

`author_uv_atlas(source, output, expected_sha256=..., atlas_size=2048, padding=2)` creates the revision. `atlas_glb_bytes(blob, ...)` returns derived bytes and the same native receipt without file writes; `validate_uv_glb(blob, ...)` executes the identical pure preflight and returns the receipt. CLI/Studio/shared-edge adapters are tracked separately by their original owners; this core report does not assert those integrations merely because a function exists.
