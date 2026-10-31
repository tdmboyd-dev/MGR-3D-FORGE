import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation


class DurableWorldJobs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.world = self.root/"world"
        build(WorldSpec(seed=7, columns=2, rows=2, buildings=2), self.world)
        self.studio = ForgeWorkstation(self.world, self.root/"workspace")
        manifest = json.loads((self.world/"manifest.json").read_text())
        self.edits = {"schema": "mgr.forge.world-edit.v1",
                      "asset_sha256": hashlib.sha256((self.world/"world.glb").read_bytes()).hexdigest(),
                      "buildings": [{k: b[k] for k in ("id", "center", "size", "material")}
                                    for b in manifest["buildings"]]}
        self.request_id = "time-owner-world-0001"

    def test_create_replay_after_restart_and_status(self):
        one = self.studio.command("/api/world-job", {"request_id": self.request_id, "edits": self.edits})
        self.assertEqual(one["status"], "MATERIALIZED")
        self.assertFalse(one["replayed"])
        self.assertFalse(one["independent_blender_verified"])
        repeat = self.studio.command("/api/world-job", {"request_id": self.request_id, "edits": self.edits})
        self.assertTrue(repeat["replayed"])
        self.assertEqual(one["world_sha256"], repeat["world_sha256"])
        other = ForgeWorkstation(self.world, self.root/"workspace")
        recovered = other.command("/api/world-job-status", {"request_id": self.request_id})
        self.assertEqual(recovered["world_sha256"], one["world_sha256"])
        self.assertEqual(len(list(other.jobs.iterdir())), 1)

    def test_wrong_payload_id_cannot_reuse_existing_job(self):
        self.studio.command("/api/world-job", {"request_id": self.request_id, "edits": self.edits})
        altered = {**self.edits, "buildings": []}
        with self.assertRaises(ValueError):
            self.studio.command("/api/world-job", {"request_id": self.request_id, "edits": altered})
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 1)

    def test_tampered_world_cannot_replay(self):
        result = self.studio.command("/api/world-job", {"request_id": self.request_id, "edits": self.edits})
        path = self.studio.valid_job(result["job_id"])/"edited"/"world.glb"
        path.write_bytes(b"tampered")
        with self.assertRaises(RuntimeError):
            self.studio.command("/api/world-job-status", {"request_id": self.request_id})

    def test_incomplete_request_is_not_built_again(self):
        self.studio.command("/api/world-job", {"request_id": self.request_id, "edits": self.edits})
        ledger = self.studio.workspace/"world-requests.json"
        doc = json.loads(ledger.read_text())
        doc[self.request_id]["status"] = "STARTED"
        ledger.write_text(json.dumps(doc))
        reopened = self.studio.command("/api/world-job", {"request_id": self.request_id, "edits": self.edits})
        self.assertEqual(reopened["status"], "NEEDS_RECONCILIATION")
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 1)

    def test_bad_edits_do_not_create_job(self):
        with self.assertRaises(ValueError):
            self.studio.command("/api/world-job", {"request_id": "bad", "edits": self.edits})
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 0)
