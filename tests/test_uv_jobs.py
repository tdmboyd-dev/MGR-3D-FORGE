"""Real UV authoring through original Studio request/journal/history owners."""
import base64
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from forge.cli import build
from forge.geometry import Mesh
from forge.glb import export_glb
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation
from tests.test_imported_morph import fixture as textured_fixture
from tests.test_uv_authoring import fixture
from forge.uv_authoring import validate_uv_glb


def request(raw,**changes):
    return {'request_id':'original-uv-atlas-001','glb_base64':base64.b64encode(raw).decode(),
            'expected_sha256':hashlib.sha256(raw).hexdigest(),'atlas_size':2048,'padding':2,**changes}


class UVJobsTests(unittest.TestCase):
    def setUp(self):
        temporary=TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name);self.world=self.root/'world'
        build(WorldSpec(seed=7,columns=2,rows=2,buildings=2),self.world)
        self.studio=ForgeWorkstation(self.world,self.root/'workspace')
        self.original=fixture(attributes=True);self.request=request(self.original)

    def create(self,payload=None):return self.studio.command('/api/uv-create',payload or self.request)
    def status(self):return self.studio.command('/api/uv-status',{'request_id':self.request['request_id']})

    def test_planar_pairs_layout_is_saved_and_bound_to_request(self):
        payload = {**self.request, 'layout': 'planar-pairs'}
        first = self.create(payload)
        self.assertEqual(first['layout'], 'planar-pairs')
        self.assertEqual(first['method'], 'padded-planar-pairs-uv-atlas')
        self.studio = ForgeWorkstation(self.world, self.root/'workspace')
        self.assertEqual(self.status()['asset_sha256'], first['asset_sha256'])
        self.assertTrue(self.create(payload)['replayed'])
        with self.assertRaises(ValueError):
            self.create()

    def test_actual_uv_job_replays_after_restart_and_reopens_with_source_verification(self):
        first=self.create();self.assertEqual(first['status'],'MATERIALIZED');self.assertFalse(first['replayed'])
        job=self.studio.valid_job(first['job_id'])
        self.assertEqual((job/'original-upload.glb').read_bytes(),self.original)
        self.assertEqual((job/'uv/original.glb').read_bytes(),self.original)
        model=(job/'uv/uv-mapped.glb').read_bytes()
        self.assertEqual(first['asset_sha256'],hashlib.sha256(model).hexdigest())
        self.assertEqual(json.loads((job/'uv/uv-receipt.json').read_text())['chart_count'],24)
        self.assertTrue((job/'uv/diagnostic-checker.png').is_file())
        self.studio=ForgeWorkstation(self.world,self.root/'workspace')
        before={p.relative_to(job):p.read_bytes() for p in job.rglob('*') if p.is_file()}
        repeat=self.create();self.assertTrue(repeat['replayed'])
        self.assertEqual(repeat['asset_sha256'],first['asset_sha256'])
        self.assertEqual(self.status()['job_id'],first['job_id'])
        verification=self.studio.command('/api/request-verify',{'kind':'uv','request':self.request})
        self.assertTrue(verification['input_verified'])
        history=self.studio.command('/api/saved-jobs',{'kind':'uv'})
        self.assertEqual(history['total'],1);self.assertFalse(history['items'][0]['artifact_verified'])
        reopened=self.studio.command('/api/saved-job-reopen',{'kind':'uv','request_id':self.request['request_id']})
        self.assertEqual(reopened['asset_sha256'],first['asset_sha256'])
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)
        self.assertEqual(before,{p.relative_to(job):p.read_bytes() for p in job.rglob('*') if p.is_file()})

    def test_existing_uv_textured_and_invalid_settings_refuse_without_allocation(self):
        invalid=[request(textured_fixture()),{**self.request,'expected_sha256':'0'*64},
                 {**self.request,'padding':True},{**self.request,'padding':0},
                 {**self.request,'atlas_size':300},{**self.request,'extra':'not approved'}]
        for payload in invalid:
            with self.subTest(keys=list(payload)),self.assertRaises(ValueError):self.create(payload)
            self.assertEqual(list(self.studio.jobs.iterdir()),[])
            self.assertFalse((self.studio.workspace/'uv-requests.json').exists())
        self.assertEqual(self.create()['status'],'MATERIALIZED')

    def test_changed_parameters_or_original_bytes_cannot_reuse_saved_identity(self):
        first=self.create()
        other=fixture()
        for payload in [{**self.request,'padding':3},{**self.request,'atlas_size':1024},request(other)]:
            with self.subTest(change=payload['expected_sha256']),self.assertRaises(ValueError):self.create(payload)
            with self.assertRaises(ValueError):
                self.studio.command('/api/request-verify',{'kind':'uv','request':payload})
        self.assertEqual(self.status()['asset_sha256'],first['asset_sha256'])
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)

    def test_request_original_model_and_receipt_tamper_refuse_replay_status_and_reopen(self):
        saved=self.create();job=self.studio.valid_job(saved['job_id'])
        for name in ['asset-request.json','original-upload.glb','uv/uv-mapped.glb','uv/uv-receipt.json','uv/diagnostic-checker.png']:
            with self.subTest(name=name):
                path=job/name;original=path.read_bytes();path.write_bytes(original+b'changed')
                try:
                    with self.assertRaises(RuntimeError):self.status()
                    with self.assertRaises(RuntimeError):self.create()
                    with self.assertRaises(RuntimeError):
                        self.studio.command('/api/saved-job-reopen',{'kind':'uv','request_id':self.request['request_id']})
                finally:path.write_bytes(original)
        self.assertEqual(self.status()['asset_sha256'],saved['asset_sha256'])
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)

    def test_large_shared_index_mesh_reopens_with_actual_multi_megabyte_chart_receipt(self):
        mesh=Mesh()
        mesh.positions=[0,0,0,1,0,0,0,1,0];mesh.normals=[0,0,1]*3
        mesh.indices=[0,1,2]*10_000
        raw=export_glb([mesh],materials=[('owned shared-index stress fixture',[.3,.4,.5,1])])
        self.assertLess(len(raw),900_000)
        result=self.create(request(raw))
        self.assertEqual(result['status'],'MATERIALIZED')
        job=self.studio.valid_job(result['job_id'])
        size=(job/'uv/uv-receipt.json').stat().st_size
        self.assertGreater(size,1_000_000);self.assertLess(size,8_000_000)
        self.studio=ForgeWorkstation(self.world,self.root/'workspace')
        self.assertEqual(self.create(request(raw))['asset_sha256'],result['asset_sha256'])
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)

    def test_oversized_serialized_preflight_receipt_refuses_before_allocation(self):
        prepared=validate_uv_glb(self.original)
        # Explicit fault injection of an excessive native receipt, without a
        # synthetic GLB/provider success standing in for the real creator.
        prepared['unexpected_excessive_native_metadata']='x'*8_000_000
        with patch('forge.uv_authoring.validate_uv_glb',return_value=prepared):
            with self.assertRaisesRegex(ValueError,'receipt|manifest|budget'):
                self.create()
        self.assertEqual(list(self.studio.jobs.iterdir()),[])
        self.assertFalse((self.studio.workspace/'uv-requests.json').exists())


if __name__=='__main__':unittest.main()
