# Native image-to-3D surface repair — November 2, 2026

The original `forge.multiview` already had real orthographic silhouette space carving. This work repairs and extends that component. It does not add a competing reconstruction engine or claim arbitrary photograph-to-3D inference.

## Reproduced failures and correction

The old `forge.marching.surface_nets` connected any four mixed cells without checking whether their shared sample edge crossed the solid boundary. It also skipped boundary cells, so a completely filled capture volume produced an empty smooth mesh, and treated voxel-centre samples as corner samples, shifting coordinates by half a voxel.

`surface-before.txt` retains the original regression run: five tests, eight failing subtests, three errors. The corrected extractor emits an oriented quad only at a sign-changing shared edge, places vertices at the mean crossing midpoint of mixed cells, and adds an empty outside layer to close subjects touching the capture bounds. Samples use `(index + 0.5) * voxel_size`. Physical dimensions, occupancy shape/binary values, grid size, vertex count and face count have explicit bounds. Area-weighted unit normals come from emitted triangles.

`marching_cubes` remains a Python alias for compatibility. This is midpoint surface nets, not a Marching Cubes table implementation or Constrained Elastic SurfaceNets. `surface="marching-cubes-fan"` remains an old manifest compatibility value; use `surface_method="voxel-centre-midpoint-surface-nets"` to identify the actual algorithm.

The original reconstruct/export path now carves once. `prepare_reconstruction` builds and checks the actual mesh entirely in memory. Empty, degenerate, open or edge-ambiguous results fail before a persistent output directory exists. The export helper checks the generated GLB and prepares OBJ/MTL text before creating its destination. This preflight does not promise an atomic filesystem transaction if a later disk write fails; the native job owner must retain the failed job state.

## Checks and independent output

`core-final.txt`: **41/41 focused tests passed** in 5.220 seconds: 29 original multi-view tests plus 12 new core/preflight regressions. The new tests cover boundary closure and winding, true sign-edge face counts, calibrated position/translation, malformed/budget-refused input, no allocation on invalid meshes or failed GLB validation, one carve per export, exact PNG provenance, explicit mode selection, and recall versus true projected-footprint IoU.

The original fit field called recall "IoU". A footprint can extend outside a foreground mask even though its centre is inside. Compatibility fields `views[].hull_shadow_iou` and `fit.worst_view_iou` retain their old recall values, explicitly labeled by `fit.legacy_iou_field_is_recall`. Use `views[].voxel_projection.iou`, `.recall`, `.overfill_pixels`, `.missed_pixels` and `fit.worst_view_recall`. These measure occupied voxel footprints, **not** the final rounded triangle mesh. The 0.97 admission gate continues to measure mask completeness; it is not an arbitrary-image reconstruction accuracy guarantee.

The saved fixture is an original stepped vessel profile, specified as a union of boxes, with owner-authored front and left grayscale PNG pixels. Each horizontal slice is rectangular, so these two orthographic masks determine this particular solid at the sampled resolution. This is deliberately labeled synthetic calibrated ground truth. It is not a borrowed model or a claim that any two images determine an arbitrary object.

`calibrated-profile-final/analytic-ground-truth.json` records 11,488 carved and analytic voxels, zero overfill/missed voxels, and voxel IoU 1.0. The analytic/occupied-voxel volume is 4.20703125 m³.

`calibrated-profile-final/blender/blender-witness.json` records an actual independent Blender 5.2.2 LTS import of `hull.glb` and Workbench render:

- 3,778 vertices and 7,552 triangles in an editable imported mesh;
- zero boundary edges and zero nonmanifold edges;
- positive signed triangle-mesh volume 4.175981139596841 m³;
- reconstructed coordinate bounds `[-0.75, 0, -0.625]` to `[0.75, 3, 0.625]`, with zero recorded native-bounds readback error;
- GLB SHA-256 `049e7c0fd83e3d39d6c53f5e6216e9ac7a9ed3a7151a1b9ef52df363771d216d`.

The actual rounded surface volume is about 0.738% smaller than the analytic voxel solid. That difference is measured and retained, not hidden behind the voxel IoU. The preview `calibrated-profile-final/blender/mesh.png` was opened and visually inspected with the complete object in frame. The earlier import invocation failed because the fixture generator's test-helper import lacked the repository on `PYTHONPATH`; `blender-run.txt` preserves that failure. The first working camera clipped the object, retained under `calibrated-profile/blender`; the final script frames the full object. No weights, GPU server or paid provider were used.

## Core API / native job integration

```python
from forge.multiview import prepare_reconstruction, export_prepared_reconstruction

spec = {
    "base_dir": PRIVATE_STAGED_MASK_DIRECTORY,
    "grid": 32,
    "bounds": {"width": 2.0, "height": 3.0, "depth": 2.0},
    "views": [
        {"axis": "front", "mask": "front.png", "threshold": 128},
        {"axis": "left", "mask": "left.png", "threshold": 128},
    ],
}
mesh, manifest = prepare_reconstruction(spec, marching=True)  # no files written
result = export_prepared_reconstruction(mesh, manifest, NEW_OUTPUT_DIRECTORY)
```

The trusted caller controls staged files and output location; do not expose arbitrary server filesystem paths in an upload API. Preserve the exact staged PNG bytes with the native job so hashes are replayable. Preparation does not reread them during export. Existing `export_reconstruction(spec_path, output, smooth=False, marching=False)` remains the file/CLI wrapper.

Stable result keys are `manifest`, `manifest_path`, `glb_path`; stable output names are `hull.glb`, `hull.obj`, `hull.mtl`, `reconstruction.json`. Manifest source receipts include each mask filename, SHA-256, dimensions, threshold, coverage and interpretation; `source_provenance.source_hashes` identifies actual input bytes, and `glb.sha256/bytes` identifies output. `mesh_bbox_min_m/max_m` and `surface_audit` describe actual emitted geometry separately from the occupied voxel hull.

Inputs are 8-bit non-interlaced grayscale, RGB or RGBA PNG masks up to 256 pixels per axis and 4 MB each. Foreground means luminance multiplied by alpha is at least threshold (default 128), so a transparent white pixel is empty and an opaque black pixel is also empty. Grid is 8–96; physical width/height/depth are 0.01–100 metres. At least one front/back and one left/right view are required. Supply **camera-seen** back/right masks; those axes are mirrored by the existing native carver. The top PNG row corresponds to the top of the Y-up capture volume. White background photographs require segmentation and calibrated framing first.

Choose one mode: default voxel boundary quads, `smooth=True` (averaged normals on those same geometric faces), or `marching=True` (rounded surface-nets geometry). The old `taubin-averaged-normals` smoothing compatibility label does not mean Taubin vertex relocation occurs.

To reproduce the saved fixture on a fresh evidence destination, adjust the single `root` variable in `generate_fixture.py` and run it with the repository on `PYTHONPATH`. To independently inspect it:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python scripts/verify_reconstruction_blender.py -- HULL_DIRECTORY NEW_PROOF_DIRECTORY
```

Existing proof and reconstruction directories are never overwritten.

## Proof limits and remaining product work

This core acceptance scope has 8/8 applicable checks supported: reproduced old failure, boundary/orientation correction, coordinate calibration, bounded refusal, preallocation failure handling, exact input/output receipts, regression tests and independent receiver import/render. It does not score all Forge, image reconstruction quality in general, UI/MCP integration, provider parity or production.

Occluded concavities, perspective camera calibration, realistic color texture/UV capture, learned hidden geometry, single-photograph semantic object reconstruction and likeness remain outside this patch. Surface-nets corner rounding is explicit. Edge closure and positive fixture volume do not certify arbitrary mesh self-intersection freedom or print readiness. Studio/native-job/API/MCP admission, persistence and reopening are owned by the parent integration task and require their own evidence. This child did not run the parent combined full repository suite or publish Git changes.

## Primary algorithm references and implementation boundary

The implementation is original Python over the existing native `Mesh` type, not copied third-party source. The sign-changing-edge / dual-cell relationship is consistent with the primary discussion of [dual contouring](https://people.engr.tamu.edu/schaefer/research/techreport02408.pdf). [MERL's Constrained Elastic SurfaceNets publication](https://www.merl.com/publications/TR99-24) is a related surface-net family reference; its constrained elastic relaxation is **not** implemented or claimed here. No source-level feature inference about commercial image generators was required for this repair. The explicitly requested REA skill routes complete owned-source analysis through normal repository tools; no binary decompilation is claimed for this core work.
