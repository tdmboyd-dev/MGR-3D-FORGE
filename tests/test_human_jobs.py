"""Human lip-sync worker reuses ForgeStudio job/rights/reconciliation boundaries."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation
from forge.human_jobs import start_human_lipsync_job,human_lipsync_job_status

TIMINGS={"schema":"mgr.forge.phoneme-timeline.v1","actor_id":"mgr-test-human",
  "language":"en-US","duration_ms":1000,
  "phonemes":[{"phoneme":"M","start_ms":0,"end_ms":150},
              {"phoneme":"AA","start_ms":150,"end_ms":550},
              {"phoneme":"OW","start_ms":550,"end_ms":1000}]}

class NoRunThread:
 def __init__(self,**kw):pass
 def start(self):pass

class HumanStudioTests(unittest.TestCase):
 def setUp(self):
  temp=TemporaryDirectory();self.addCleanup(temp.cleanup)
  self.root=Path(temp.name)
  self.world=self.root/"world"
  build(WorldSpec(seed=20,columns=2,rows=2,buildings=2),self.world)
  self.studio=ForgeWorkstation(self.world,self.root/"workspace",blender="blender")
  self.request={"request_id":"mgr-human-lipsync-0001","timings":TIMINGS,"fps":24}

 def test_starts_one_job_and_replay_after_restart_needs_reconciliation(self):
  with patch("forge.human_jobs.threading.Thread",NoRunThread):
   a=start_human_lipsync_job(self.studio,self.request)
  self.assertEqual(a["status"],"RUNNING")
  self.assertFalse(a["replayed"])
  b=start_human_lipsync_job(self.studio,self.request)
  self.assertEqual(b["status"],"RUNNING")
  self.assertTrue(b["replayed"])
  after=ForgeWorkstation(self.world,self.root/"workspace")
  pending=human_lipsync_job_status(after,self.request["request_id"])
  self.assertEqual(pending["status"],"NEEDS_RECONCILIATION")
  self.assertEqual(len(list(after.jobs.iterdir())),1)
  with self.assertRaisesRegex(ValueError,"altered"):
   start_human_lipsync_job(self.studio,{**self.request,"fps":30})
  self.assertEqual(len(list(after.jobs.iterdir())),1)

 def test_invalid_parameters_do_not_allocate_jobs(self):
  for wrong in (
   {"request_id":"bad"},
   {"timings":{**TIMINGS,"phonemes":[{"phoneme":"INVALID","start_ms":0,"end_ms":100}]}},
   {"fps":0},
   {"dangerous":"exec"},
  ):
   with self.subTest(wrong=wrong),self.assertRaises(ValueError):
    start_human_lipsync_job(self.studio,{**self.request,**wrong})
  self.assertEqual(len(list(self.studio.jobs.iterdir())),0)

 def test_completed_receipt_requires_real_glb_and_independent_blender(self):
  from forge.human_jobs import _readback
  with patch("forge.human_jobs.threading.Thread",NoRunThread):
   created=start_human_lipsync_job(self.studio,self.request)
  job=self.studio.valid_job(created["job_id"])
  row={"status":"MATERIALIZED","job_id":created["job_id"],
       "fingerprint":"a"*64,"sha256":"f"*64}
  with self.assertRaises(RuntimeError):
   _readback(self.studio,self.request["request_id"],row,replayed=True)
