"""Native job preflight refuses unusable inputs before persistent allocation."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge.geometry import Mesh
from forge.multiview import (export_prepared_reconstruction, export_reconstruction,
                            prepare_reconstruction)
from tests.test_multiview import mask_png, square_grid


class ReconstructionPreflightTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for axis in ('front', 'left'):
            (self.root / (axis+'.png')).write_bytes(mask_png(square_grid(16, 0, 16)))
        self.spec = {'base_dir': str(self.root), 'grid': 16,
                     'bounds': {'width': 2., 'height': 3., 'depth': 4.},
                     'views': [{'axis': axis, 'mask': axis+'.png'} for axis in ('front','left')]}

    def test_prepare_writes_nothing_and_preserves_exact_png_provenance(self):
        before = set(self.root.iterdir())
        mesh, manifest = prepare_reconstruction(self.spec, marching=True)
        self.assertEqual(set(self.root.iterdir()), before)
        self.assertGreater(len(mesh.indices), 0)
        self.assertEqual(manifest['surface_audit']['edges']['status'], 'PASS')
        self.assertEqual(manifest['mesh_bbox_min_m'], [-1.,0.,-2.])
        self.assertEqual(manifest['mesh_bbox_max_m'], [1.,3.,2.])
        self.assertEqual(manifest['source_provenance']['source_hashes'],
                         [hashlib.sha256((self.root/(axis+'.png')).read_bytes()).hexdigest()
                          for axis in ('front','left')])
        self.assertTrue(manifest['fit']['legacy_iou_field_is_recall'])
        result = export_prepared_reconstruction(mesh, manifest, self.root/'job')
        self.assertEqual(result['glb_path'].name, 'hull.glb')
        self.assertEqual(result['manifest_path'].name, 'reconstruction.json')
        self.assertTrue(result['manifest']['internally_consistent'])
        self.assertFalse('glb' in manifest)  # no mutation of prepared receipt

    def test_invalid_masks_and_shapes_refuse_without_allocating_output(self):
        cases = [None, [], {'views':[None]}, {**self.spec,'base_dir': []},
                 {**self.spec,'grid':97}, {**self.spec,'views':[{'axis':'front','mask':9}]},
                 {**self.spec,'bounds':{'width':float('nan'),'height':2,'depth':2}}]
        for spec in cases:
            with self.subTest(spec=repr(spec)), self.assertRaises(ValueError):
                prepare_reconstruction(spec)
        (self.root/'front.png').write_bytes(b'bad PNG')
        path = self.root/'spec.json'
        path.write_text(json.dumps(self.spec),encoding='utf-8')
        target = self.root/'refused'
        with self.assertRaises(ValueError):
            export_reconstruction(path,target,marching=True)
        self.assertFalse(target.exists())

    def test_bad_generated_mesh_never_allocates_a_job(self):
        mesh, manifest = prepare_reconstruction(self.spec,marching=True)
        mesh.indices = []
        target = self.root/'refused'
        with self.assertRaises(ValueError):
            export_prepared_reconstruction(mesh,manifest,target)
        self.assertFalse(target.exists())

    def test_serialization_refusal_never_allocates_a_job(self):
        mesh, manifest = prepare_reconstruction(self.spec,marching=True)
        target = self.root/'refused'
        with patch('forge.multiview.inspect_glb',return_value={'valid':False}):
            with self.assertRaises(ValueError):
                export_prepared_reconstruction(mesh,manifest,target)
        self.assertFalse(target.exists())

    def test_export_loads_and_carves_only_once(self):
        import forge.multiview as module
        path = self.root/'spec.json'
        path.write_text(json.dumps(self.spec),encoding='utf-8')
        with patch('forge.multiview.carve',wraps=module.carve) as carving:
            export_reconstruction(path,self.root/'job',marching=True)
        self.assertEqual(carving.call_count,1)

    def test_modes_are_explicit(self):
        for smooth,marching in [(True,True),('yes',False),(False,1)]:
            with self.subTest(smooth=smooth,marching=marching), self.assertRaises(ValueError):
                prepare_reconstruction(self.spec,smooth=smooth,marching=marching)

    def test_mask_completeness_is_not_mislabeled_as_actual_iou(self):
        rows=[[3 <= x < 14 for x in range(16)] for _ in range(16)]
        for axis in ('front','left'):
            (self.root/(axis+'.png')).write_bytes(mask_png(rows))
        _,manifest=prepare_reconstruction({**self.spec,'grid':8},marching=True)
        for view in manifest['views']:
            self.assertEqual(view['hull_shadow_iou'],1.)  # historical field is recall
            self.assertEqual(view['voxel_projection']['recall'],1.)
            self.assertLess(view['voxel_projection']['iou'],1.)
            self.assertGreater(view['voxel_projection']['overfill_pixels'],0)


if __name__ == '__main__':
    unittest.main()
