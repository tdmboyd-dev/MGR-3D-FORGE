"""Initial journal failures cannot leak disposable allocations or duplicate owned jobs."""
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge.cli import build
from forge.creation_asset_jobs import KINDS
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation
from forge.world_jobs import _atomic_json,_index
from tests.test_multiview import mask_png,square_grid
from tests.test_imported_morph import fixture


class CreationAdmissionTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name)
        build(WorldSpec(seed=4,columns=2,rows=2,buildings=2),self.root/'world')
        self.studio=ForgeWorkstation(self.root/'world',self.root/'workspace')
        mask=base64.b64encode(mask_png(square_grid(8,0,8))).decode()
        raw=fixture()
        self.requests={
            'reconstruction':{'request_id':'admission-reconstruct-0001','front_png_base64':mask,'side_png_base64':mask,
                              'bounds':{'width':2,'height':2,'depth':2},'grid':8,'surface':'smooth'},
            'morph':{'request_id':'admission-morph-0001','glb_base64':base64.b64encode(raw).decode(),
                     'expected_sha256':hashlib.sha256(raw).hexdigest(),'morph':{'height':1.2}}}

    def create(self,kind):return self.studio.command('/api/'+kind+'-create',self.requests[kind])

    def test_uncommitted_failure_removes_only_its_fresh_empty_allocation(self):
        for kind in self.requests:
            with self.subTest(kind=kind):
                before=set(self.studio.jobs.iterdir())
                with patch('forge.creation_asset_jobs._atomic_json',side_effect=OSError('disk failed before admission')):
                    with self.assertRaisesRegex(OSError,'disk failed before admission'):self.create(kind)
                self.assertEqual(set(self.studio.jobs.iterdir()),before)
                self.assertFalse((self.studio.workspace/KINDS[kind][0]).exists())
                result=self.create(kind)
                self.assertEqual(result['status'],'MATERIALIZED')
                self.assertEqual(len(set(self.studio.jobs.iterdir())-before),1)

    def test_committed_then_error_preserves_original_job_and_never_reallocates(self):
        for kind in self.requests:
            with self.subTest(kind=kind):
                before=set(self.studio.jobs.iterdir())
                def commit_then_fail(path,rows):
                    _atomic_json(path,rows)
                    raise OSError('commit happened but acknowledgement failed')
                with patch('forge.creation_asset_jobs._atomic_json',side_effect=commit_then_fail):
                    with self.assertRaisesRegex(OSError,'acknowledgement failed'):self.create(kind)
                allocated=set(self.studio.jobs.iterdir())-before
                self.assertEqual(len(allocated),1)
                journal=self.studio.workspace/KINDS[kind][0]
                saved=journal.read_bytes()
                row=json.loads(saved)[self.requests[kind]['request_id']]
                self.assertEqual(row['status'],'STARTED')
                self.assertEqual(next(iter(allocated)).name,row['job_id'])
                replay=self.create(kind)
                self.assertEqual(replay['status'],'NEEDS_RECONCILIATION')
                self.assertEqual(replay['job_id'],row['job_id'])
                self.assertTrue(replay['replayed'])
                self.assertEqual(journal.read_bytes(),saved)
                self.assertEqual(set(self.studio.jobs.iterdir())-before,allocated)

    def test_unknown_or_corrupt_admission_preserves_allocated_work(self):
        for mode in ('unreadable','invalid-row','populated'):
            with self.subTest(mode=mode):
                # Each independent case uses a fresh ID and no readable journal.
                request={**self.requests['reconstruction'],'request_id':'ambiguous-'+mode+'-0001'}
                before=set(self.studio.jobs.iterdir())
                def fail(path,rows):
                    if mode=='unreadable':path.write_text('{interrupted',encoding='utf8')
                    elif mode=='invalid-row':_atomic_json(path,{'broken':None})
                    else:
                        job=self.studio.jobs/rows[request['request_id']]['job_id']
                        (job/'original-work.txt').write_text('preserve original work',encoding='utf8')
                    raise OSError('initial journal outcome unknown')
                with patch('forge.creation_asset_jobs._atomic_json',side_effect=fail):
                    with self.assertRaisesRegex(OSError,'outcome unknown'):
                        self.studio.command('/api/reconstruction-create',request)
                allocated=set(self.studio.jobs.iterdir())-before
                self.assertEqual(len(allocated),1)
                journal=self.studio.workspace/KINDS['reconstruction'][0]
                if journal.exists():journal.unlink()  # isolated corrupt fixture, never production state

    def test_unreadable_recovery_journal_preserves_original_admission_error_and_job(self):
        calls=0
        def read(studio,ledger):
            nonlocal calls
            calls+=1
            if calls>1:raise PermissionError('original journal cannot be read')
            return _index(studio,ledger)
        def failed_write(path,rows):
            path.write_text('{}',encoding='utf8')
            raise OSError('initial admission error')
        with patch('forge.creation_asset_jobs._index',side_effect=read),patch('forge.creation_asset_jobs._atomic_json',side_effect=failed_write):
            with self.assertRaisesRegex(OSError,'initial admission error'):self.create('reconstruction')
        self.assertEqual(calls,2)
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)

    def test_other_request_owning_the_allocated_job_prevents_removal(self):
        def committed_owner(path,rows):
            row=rows[self.requests['reconstruction']['request_id']]
            _atomic_json(path,{'different-original-request-0001':row})
            raise OSError('admission identity uncertain')
        with patch('forge.creation_asset_jobs._atomic_json',side_effect=committed_owner):
            with self.assertRaisesRegex(OSError,'identity uncertain'):self.create('reconstruction')
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)


if __name__=='__main__':unittest.main()
