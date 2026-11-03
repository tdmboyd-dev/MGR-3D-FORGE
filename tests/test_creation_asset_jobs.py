"""Real uploaded-byte journeys across Studio, native creators and saved history."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge.cli import build
from forge.creation_asset_jobs import KINDS
from forge.glb import inspect_glb
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation
from tests.test_imported_morph import fixture, pack, unpack
from tests.test_multiview import mask_png, square_grid


def encoded(raw):
    return base64.b64encode(raw).decode('ascii')


class CreationAssetJobsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.world = self.root/'world'
        build(WorldSpec(seed=7, columns=2, rows=2, buildings=2), self.world)
        self.studio = ForgeWorkstation(self.world, self.root/'workspace')
        self.png = mask_png(square_grid(16, 2, 14))
        self.glb = fixture()
        self.requests = {
            'reconstruction': {'request_id': 'original-image-job-001',
                'front_png_base64': encoded(self.png), 'side_png_base64': encoded(self.png),
                'bounds': {'width': 2., 'height': 3., 'depth': 4.}, 'grid': 8, 'surface': 'smooth'},
            'morph': {'request_id': 'original-morph-job-001', 'glb_base64': encoded(self.glb),
                'expected_sha256': hashlib.sha256(self.glb).hexdigest(), 'morph': {'height': 1.3, 'bend_degrees': 14}},
        }

    def create(self, kind, request=None):
        return self.studio.command('/api/'+kind+'-create', request or self.requests[kind])

    def status(self, kind):
        return self.studio.command('/api/'+kind+'-status', {'request_id': self.requests[kind]['request_id']})

    def test_both_real_creators_persist_replay_restart_history_and_exact_binding(self):
        originals = {}
        for kind in self.requests:
            with self.subTest(kind=kind):
                request = self.requests[kind]
                missing = self.studio.command('/api/request-verify', {'kind': kind, 'request': request})
                self.assertEqual(missing['status'], 'NOT_FOUND')
                self.assertFalse(missing['input_verified'])
                result = self.create(kind)
                self.assertEqual(result['status'], 'MATERIALIZED')
                self.assertFalse(result['replayed'])
                self.assertFalse(result['model_inference_used'])
                job = self.studio.valid_job(result['job_id'])
                _, directory, model, receipt = KINDS[kind]
                raw = (job/directory/model).read_bytes()
                self.assertTrue(inspect_glb(raw)['valid'])
                self.assertEqual(result['asset_sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(result['asset_bytes'], len(raw))
                self.assertTrue((job/directory/receipt).is_file())
                if kind == 'morph':
                    self.assertEqual((job/'original-upload.glb').read_bytes(), self.glb)
                    self.assertEqual((job/directory/'original.glb').read_bytes(), self.glb)
                    self.assertNotEqual(raw, self.glb)
                else:
                    self.assertEqual((job/'front.png').read_bytes(), self.png)
                    self.assertEqual((job/'side.png').read_bytes(), self.png)
                    doc = json.loads((job/directory/receipt).read_text())
                    self.assertEqual(doc['surface_audit']['edges']['status'], 'PASS')
                originals[kind] = result
        self.studio = ForgeWorkstation(self.world, self.root/'workspace')
        before = {p.relative_to(self.studio.jobs): p.read_bytes() for p in self.studio.jobs.rglob('*') if p.is_file()}
        for kind, saved in originals.items():
            with self.subTest(restart=kind):
                repeat = self.create(kind)
                self.assertTrue(repeat['replayed'])
                for key in ('job_id', 'asset_sha256', 'asset_bytes', 'source_sha256'):
                    self.assertEqual(repeat[key], saved[key])
                    self.assertEqual(self.status(kind)[key], saved[key])
                verified = self.studio.command('/api/request-verify', {'kind': kind, 'request': self.requests[kind]})
                self.assertTrue(verified['input_verified'])
                reopened = self.studio.command('/api/saved-job-reopen', {'kind': kind, 'request_id': saved['request_id']})
                self.assertEqual(reopened['asset_sha256'], saved['asset_sha256'])
                history = self.studio.command('/api/saved-jobs', {'kind': kind})
                self.assertEqual(history['total'], 1)
                self.assertFalse(history['items'][0]['artifact_verified'])
                self.assertEqual(history['items'][0]['job_id'], saved['job_id'])
        after = {p.relative_to(self.studio.jobs): p.read_bytes() for p in self.studio.jobs.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 2)

    def test_changed_inputs_cannot_reuse_a_request_id_or_verify_existing_output(self):
        for kind in self.requests:
            with self.subTest(kind=kind):
                self.create(kind)
                changed = copy.deepcopy(self.requests[kind])
                if kind == 'morph': changed['morph']['height'] = 1.4
                else: changed['bounds']['height'] = 3.1
                with self.assertRaises(ValueError): self.create(kind, changed)
                with self.assertRaises(ValueError):
                    self.studio.command('/api/request-verify', {'kind': kind, 'request': changed})
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 2)

    def test_actual_unsupported_geometry_and_empty_silhouette_refuse_before_allocation(self):
        doc, binary = unpack(self.glb)
        doc['skins'] = [{'joints': [0]}]
        unsupported = pack(doc, binary)
        bad_morph = {**self.requests['morph'], 'glb_base64': encoded(unsupported),
                     'expected_sha256': hashlib.sha256(unsupported).hexdigest()}
        empty = mask_png(square_grid(16, 0, 0))
        bad_reconstruction = {**self.requests['reconstruction'], 'front_png_base64': encoded(empty)}
        for kind, request in [('morph', bad_morph), ('reconstruction', bad_reconstruction)]:
            with self.subTest(kind=kind), self.assertRaises(ValueError): self.create(kind, request)
            self.assertFalse((self.studio.workspace/KINDS[kind][0]).exists())
        self.assertEqual(list(self.studio.jobs.iterdir()), [])
        # Invalid input does not burn the stable identity; corrected bytes work.
        for kind in self.requests: self.assertEqual(self.create(kind)['status'], 'MATERIALIZED')

    def test_invalid_uploads_hash_controls_and_schema_allocate_no_job(self):
        cases = [('morph', {'expected_sha256': '0'*64}),
                 ('morph', {'morph': {'height': float('nan')}}),
                 ('morph', {'glb_base64': '!not base64!'}),
                 ('reconstruction', {'front_png_base64': encoded(b'bad PNG')}),
                 ('reconstruction', {'grid': True}),
                 ('reconstruction', {'surface': 'invented'}),
                 ('reconstruction', {'bounds': {'width': 0, 'height': 3, 'depth': 4}}),
                 ('reconstruction', {'unapproved': True})]
        for kind, changes in cases:
            with self.subTest(kind=kind, changes=repr(changes)), self.assertRaises(ValueError):
                self.create(kind, {**self.requests[kind], **changes})
        self.assertEqual(list(self.studio.jobs.iterdir()), [])
        self.assertEqual(list(self.studio.workspace.glob('*-requests.json')), [])

    def test_tampered_request_source_model_and_receipt_cannot_reopen_or_replay(self):
        for kind in self.requests:
            result = self.create(kind)
            job = self.studio.valid_job(result['job_id'])
            _, directory, model, receipt = KINDS[kind]
            source = 'original-upload.glb' if kind == 'morph' else 'front.png'
            for relative in ('asset-request.json', source, directory+'/'+model, directory+'/'+receipt):
                with self.subTest(kind=kind, file=relative):
                    path = job/relative
                    saved = path.read_bytes()
                    path.write_bytes(saved+b'changed')
                    try:
                        with self.assertRaises(RuntimeError): self.status(kind)
                        with self.assertRaises(RuntimeError): self.create(kind)
                        with self.assertRaises((ValueError, RuntimeError)):
                            self.studio.command('/api/request-verify', {'kind': kind, 'request': self.requests[kind]})
                    finally: path.write_bytes(saved)
                    self.assertEqual(self.status(kind)['status'], 'MATERIALIZED')
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 2)

    def test_failed_execution_is_preserved_and_never_silently_retried(self):
        for kind in self.requests:
            module = 'forge.imported_morph.morph_imported_glb' if kind == 'morph' else 'forge.multiview.export_prepared_reconstruction'
            with self.subTest(kind=kind), patch(module, side_effect=RuntimeError('witness execution failure')):
                with self.assertRaisesRegex(RuntimeError, 'witness execution failure'): self.create(kind)
            journal = self.studio.workspace/KINDS[kind][0]
            saved = journal.read_bytes()
            result = self.create(kind)
            self.assertEqual(result['status'], 'NEEDS_RECONCILIATION')
            self.assertTrue(result['replayed'])
            self.assertEqual(journal.read_bytes(), saved)
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 2)

    def test_full_journal_refuses_new_work_but_keeps_exact_saved_replay(self):
        for kind in self.requests:
            result = self.create(kind)
            journal = self.studio.workspace/KINDS[kind][0]
            rows = json.loads(journal.read_text())
            rows.update({f'capacity-{kind}-{i:04}': {'status': 'STARTED', 'job_id': 'a'*24} for i in range(999)})
            journal.write_text(json.dumps(rows))
            saved = journal.read_bytes()
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'journal full'):
                self.create(kind, {**self.requests[kind], 'request_id': 'over-capacity-original-001'})
            self.assertEqual(journal.read_bytes(), saved)
            self.assertEqual(self.create(kind)['asset_sha256'], result['asset_sha256'])
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 2)


    def test_corrupt_saved_row_requires_reconciliation_without_allocating(self):
        request = self.requests['morph']
        request_id = request['request_id']
        journal = self.studio.workspace / KINDS['morph'][0]
        damaged = json.dumps({request_id: None})
        journal.write_text(damaged, encoding='utf8')
        for route, body in (
            ('/api/morph-create', request),
            ('/api/morph-status', {'request_id': request_id}),
            ('/api/request-verify', {'kind': 'morph', 'request': request}),
        ):
            with self.subTest(route=route), self.assertRaisesRegex(RuntimeError, 'reconciliation required'):
                self.studio.command(route, body)
        self.assertEqual(journal.read_text(encoding='utf8'), damaged)
        self.assertEqual(list(self.studio.jobs.iterdir()), [])


if __name__ == '__main__':
    unittest.main()

