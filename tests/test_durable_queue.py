"""Durable job queue tests."""

import json
import tempfile
import time
import unittest
from pathlib import Path

from forge.durable_queue import DurableJobQueue, JobSpec, JobState


class DurableQueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "queue"
        self.q = DurableJobQueue(self.root)

    def test_enqueue_and_claim(self):
        spec = JobSpec(job_id="j1", kind="test", payload={"x": 1})
        state = self.q.enqueue(spec)
        self.assertEqual(state.status, "queued")
        claimed = self.q.claim_next()
        self.assertIsNotNone(claimed)
        spec2, state2 = claimed
        self.assertEqual(spec2.job_id, "j1")
        self.assertEqual(state2.status, "running")
        self.assertEqual(state2.attempt, 1)

    def test_claim_empty_returns_none(self):
        self.assertIsNone(self.q.claim_next())

    def test_complete(self):
        spec = JobSpec(job_id="j2", kind="test")
        self.q.enqueue(spec)
        self.q.claim_next()
        state = self.q.complete("j2", {"result": 42})
        self.assertEqual(state.status, "done")
        self.assertEqual(state.result, {"result": 42})
        self.assertEqual(self.q.counts()["done"], 1)
        self.assertEqual(self.q.counts()["running"], 0)

    def test_fail_requeues(self):
        spec = JobSpec(job_id="j3", kind="test", max_attempts=3)
        self.q.enqueue(spec)
        self.q.claim_next()
        state = self.q.fail("j3", "transient error")
        self.assertEqual(state.status, "queued")
        self.assertEqual(state.attempt, 1)

    def test_fail_exhausts_attempts(self):
        spec = JobSpec(job_id="j4", kind="test", max_attempts=1)
        self.q.enqueue(spec)
        self.q.claim_next()
        state = self.q.fail("j4", "permanent error")
        self.assertEqual(state.status, "failed")
        self.assertEqual(self.q.counts()["failed"], 1)

    def test_recover_interrupted(self):
        spec = JobSpec(job_id="j5", kind="test", max_attempts=3)
        self.q.enqueue(spec)
        self.q.claim_next()
        # simulate crash: move back to running manually
        # (claim_next already moved to running; just call recover)
        recovered = self.q.recover_interrupted()
        self.assertIn("j5", recovered)
        # should be re-queued
        self.assertEqual(self.q.status("j5").status, "queued")

    def test_update_progress(self):
        spec = JobSpec(job_id="j6", kind="test")
        self.q.enqueue(spec)
        self.q.claim_next()
        self.q.update_progress("j6", 0.5)
        state = self.q.status("j6")
        self.assertAlmostEqual(state.progress, 0.5)

    def test_status_lookup(self):
        spec = JobSpec(job_id="j7", kind="test")
        self.q.enqueue(spec)
        self.assertEqual(self.q.status("j7").status, "queued")
        self.assertIsNone(self.q.status("nonexistent"))

    def test_counts(self):
        self.q.enqueue(JobSpec(job_id="a", kind="t"))
        self.q.enqueue(JobSpec(job_id="b", kind="t"))
        self.assertEqual(self.q.counts()["queued"], 2)
        self.q.claim_next()
        self.assertEqual(self.q.counts()["running"], 1)
        self.assertEqual(self.q.counts()["queued"], 1)

    def test_duplicate_enqueue_raises(self):
        self.q.enqueue(JobSpec(job_id="dup", kind="t"))
        with self.assertRaises(ValueError):
            self.q.enqueue(JobSpec(job_id="dup", kind="t"))

    def test_complete_missing_raises(self):
        with self.assertRaises(ValueError):
            self.q.complete("nope", {})

    def test_fail_missing_raises(self):
        with self.assertRaises(ValueError):
            self.q.fail("nope", "err")


if __name__ == "__main__":
    unittest.main()
