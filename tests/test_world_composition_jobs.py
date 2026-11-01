"""Existing ForgeWorkstation composition jobs, replay, auth and resource caps."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation
from forge.world_composition_jobs import start_world_composition,world_composition_status

class NoRun:
    def __init__(self,**kw):pass
    def start(self):pass

class WorldCompositionJobTests(unittest.TestCase):
    def setUp(self):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root=Path(folder.name)
        world=root/"world"
        build(WorldSpec(seed=81,columns=2,rows=2,buildings=3),world)
        self.studio=ForgeWorkstation(world,root/"studio")
        self.request={"request_id":"mgr-world-composed-0001",
                      "biome_request_id":"mgr-world-biome-00001"}
        x=self.studio.command("/api/biome-create",{
            "request_id":self.request["biome_request_id"],
            "biome":"forest","seed":41,"resolution":18
        })
        self.assertEqual(x["status"],"MATERIALIZED")

    def test_same_id_replay_and_restart_reconcile(self):
        with patch("forge.world_composition_jobs.threading.Thread",NoRun):
            started=start_world_composition(self.studio,self.request)
        self.assertEqual(started["status"],"RUNNING")
        self.assertEqual(started["replayed"],False)
        again=start_world_composition(self.studio,self.request)
        self.assertEqual(again["status"],"RUNNING")
        self.assertTrue(again["replayed"])
        restarted=ForgeWorkstation(self.studio.world,self.studio.workspace)
        state=world_composition_status(restarted,self.request["request_id"])
        self.assertEqual(state["status"],"NEEDS_RECONCILIATION")
        self.assertEqual(len(list(self.studio.jobs.iterdir())),2)
        with self.assertRaisesRegex(ValueError,"MATERIALIZED"):
            start_world_composition(self.studio,{**self.request,"biome_request_id":"not-this-source"})

    def test_invalid_and_unmaterialized_biome_refused_before_job(self):
        for changed in ({"request_id":"bad"},{"biome_request_id":"invalid"},
                        {"extra":"arbitrary"}):
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                start_world_composition(self.studio,{**self.request,**changed})
        with self.assertRaises(ValueError):
            start_world_composition(self.studio,{**self.request,
                                 "biome_request_id":"mgr-not-created-0001"})
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)

    def test_heavy_blender_slot_does_not_allocate_duplicate_job(self):
        self.assertTrue(self.studio.heavy_worker_slot.acquire(blocking=False))
        busy=start_world_composition(self.studio,self.request)
        self.assertEqual(busy["status"],"BUSY")
        self.assertEqual(len(list(self.studio.jobs.iterdir())),1)
        self.studio.heavy_worker_slot.release()
