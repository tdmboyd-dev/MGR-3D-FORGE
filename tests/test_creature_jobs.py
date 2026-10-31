"""Tests actual original creature output and replay-safe Studio job controller."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation

class CreatureJobsTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        build(WorldSpec(seed=9,columns=2,rows=2,buildings=2),self.root/"world")
        self.studio=ForgeWorkstation(self.root/"world",self.root/"workspace")
        self.payload={"request_id":"forge-creative-001","prompt":"invent an ancient winged crystal beast",
                      "seed":31,"variants":4,"morph":{"length":1.13,"twist_degrees":9}}

    def test_real_glb_replays_without_recreating_and_restarts(self):
        a=self.studio.command("/api/creature-create",self.payload)
        self.assertEqual(a["status"],"MATERIALIZED")
        self.assertFalse(a["replayed"])
        self.assertGreater(a["triangles"],300)
        self.assertFalse(a["model_inference_used"])
        file=self.studio.valid_job(a["job_id"])/"creature"/"creature.glb"
        self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),a["creature_sha256"])
        same=self.studio.command("/api/creature-create",self.payload)
        self.assertTrue(same["replayed"])
        self.assertEqual(a["creature_sha256"],same["creature_sha256"])
        other=ForgeWorkstation(self.root/"world",self.root/"workspace")
        after=other.command("/api/creature-status",{"request_id":self.payload["request_id"]})
        self.assertEqual(after["creature_sha256"],a["creature_sha256"])
        self.assertEqual(len(list(other.jobs.iterdir())),1)

    def test_changed_request_id_cannot_be_reused(self):
        self.studio.command("/api/creature-create",self.payload)
        with self.assertRaisesRegex(ValueError,"reused"):
            self.studio.command("/api/creature-create",{**self.payload,"prompt":"invent different creature"})
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)

    def test_malformed_prompts_fail_before_job_creation(self):
        for changed in ({"request_id":"bad"},{"seed":-1},{"variants":100},
                        {"morph":{"unbounded_axis":50}},{"prompt":"x"}):
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                self.studio.command("/api/creature-create",{**self.payload,**changed})
        self.assertEqual(len(list(self.studio.jobs.iterdir())),0)
        self.assertEqual(self.studio.command("/api/creature-status",
                          {"request_id":self.payload["request_id"]})["status"],"NOT_FOUND")

    def test_tamper_and_incomplete_job_are_not_silent_success(self):
        result=self.studio.command("/api/creature-create",self.payload)
        file=self.studio.valid_job(result["job_id"])/"creature"/"creature.glb"
        file.write_bytes(b"tampered")
        with self.assertRaises(RuntimeError):
            self.studio.command("/api/creature-status",{"request_id":self.payload["request_id"]})
