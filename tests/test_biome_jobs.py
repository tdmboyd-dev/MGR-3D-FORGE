import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation

class BiomeJobTests(unittest.TestCase):
 def setUp(self):
  self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
  self.world=self.root/"world"
  build(WorldSpec(seed=7,columns=3,rows=3,buildings=3),self.world)
  self.studio=ForgeWorkstation(self.world,self.root/"jobs-workspace")
  self.request={"request_id":"mgr-biome-test-00001","biome":"alien","seed":9,"resolution":24}

 def test_create_hash_replay_and_reopen(self):
  before=hashlib.sha256((self.world/"world.glb").read_bytes()).hexdigest()
  result=self.studio.command("/api/biome-create",self.request)
  self.assertEqual(result["status"],"MATERIALIZED")
  self.assertEqual(result["source_world_sha256"],before)
  self.assertFalse(result["replayed"])
  self.assertGreater(result["triangles"],100)
  self.assertEqual(hashlib.sha256((self.world/"world.glb").read_bytes()).hexdigest(),before)
  saved=self.studio.valid_job(result["job_id"])/"biome"/"biome.glb"
  self.assertEqual(hashlib.sha256(saved.read_bytes()).hexdigest(),result["biome_sha256"])
  replay=self.studio.command("/api/biome-create",self.request)
  self.assertTrue(replay["replayed"])
  self.assertEqual(replay["biome_sha256"],result["biome_sha256"])
  other=ForgeWorkstation(self.world,self.root/"jobs-workspace")
  recovered=other.command("/api/biome-status",{"request_id":self.request["request_id"]})
  self.assertEqual(recovered["biome_sha256"],result["biome_sha256"])
  self.assertEqual(len(list(other.jobs.iterdir())),1)

 def test_wrong_body_conflicts_invalid_inputs_and_corruption(self):
  for change in ({"request_id":"bad"},{"biome":"ultra?"},{"seed":-1},{"resolution":100}):
   with self.subTest(change=change),self.assertRaises(ValueError):
    self.studio.command("/api/biome-create",{**self.request,**change})
  self.assertEqual(len(list(self.studio.jobs.iterdir())),0)
  result=self.studio.command("/api/biome-create",self.request)
  with self.assertRaisesRegex(ValueError,"changed source"):
   self.studio.command("/api/biome-create",{**self.request,"seed":11})
  saved=self.studio.valid_job(result["job_id"])/"biome"/"biome.glb"
  saved.write_bytes(b"tampered")
  with self.assertRaises(RuntimeError):
   self.studio.command("/api/biome-status",{"request_id":self.request["request_id"]})
