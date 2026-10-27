"""GPU lifecycle and billing tests (pure CPU)."""

import time
import unittest

from forge.gpu_lifecycle import (
    BillingLedger, InstanceManager, InstanceRecord, UserAccount,
)


class InstanceManagerTests(unittest.TestCase):
    def test_register_and_get(self):
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time())
        mgr.register(rec)
        self.assertEqual(mgr.get("i1").instance_id, "i1")
        self.assertEqual(len(mgr.running()), 1)

    def test_duplicate_raises(self):
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time())
        mgr.register(rec)
        with self.assertRaises(ValueError):
            mgr.register(InstanceRecord("i1", "runpod", "A10", 0.5, time.time()))

    def test_terminate(self):
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time() - 100)
        mgr.register(rec)
        mgr.terminate("i1")
        self.assertEqual(mgr.get("i1").status, "terminated")
        self.assertEqual(len(mgr.running()), 0)

    def test_double_terminate_raises(self):
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time() - 100)
        mgr.register(rec)
        mgr.terminate("i1")
        with self.assertRaises(ValueError):
            mgr.terminate("i1")

    def test_total_cost(self):
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time() - 7200)
        mgr.register(rec)
        mgr.terminate("i1")
        self.assertGreater(mgr.total_cost(), 0)

    def test_shadow_available_seconds(self):
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time())
        mgr.register(rec)
        spare = mgr.shadow_available_seconds("i1")
        self.assertGreaterEqual(spare, 0)
        self.assertLessEqual(spare, 3600)

    def test_unknown_instance_raises(self):
        mgr = InstanceManager()
        with self.assertRaises(KeyError):
            mgr.get("nope")


class BillingLedgerTests(unittest.TestCase):
    def test_allocate_and_pool_status(self):
        ledger = BillingLedger()
        acct = ledger.allocate_pool("alice", 5.0)
        self.assertEqual(acct.pool_hours, 5.0)
        status = ledger.pool_status("alice")
        self.assertEqual(status["remaining_pool_hours"], 5.0)

    def test_charge_deducts_pool(self):
        ledger = BillingLedger()
        ledger.allocate_pool("alice", 5.0)
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time() - 3700)
        mgr.register(rec)
        mgr.terminate("i1")
        receipt = ledger.charge("alice", rec)
        self.assertEqual(receipt["user_id"], "alice")
        self.assertGreater(receipt["billed_hours"], 0)
        self.assertLess(ledger.pool_status("alice")["remaining_pool_hours"], 5.0)

    def test_insufficient_pool_raises(self):
        ledger = BillingLedger()
        ledger.allocate_pool("alice", 0.5)
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time() - 7200)
        mgr.register(rec)
        mgr.terminate("i1")
        with self.assertRaises(ValueError):
            ledger.charge("alice", rec)

    def test_receipts_filter_by_user(self):
        ledger = BillingLedger()
        ledger.allocate_pool("alice", 10.0)
        ledger.allocate_pool("bob", 10.0)
        mgr = InstanceManager()
        r1 = InstanceRecord("i1", "runpod", "A10", 0.5, time.time() - 3700)
        r2 = InstanceRecord("i2", "runpod", "A10", 0.5, time.time() - 3700)
        mgr.register(r1); mgr.register(r2)
        mgr.terminate("i1"); mgr.terminate("i2")
        ledger.charge("alice", r1)
        ledger.charge("bob", r2)
        self.assertEqual(len(ledger.receipts("alice")), 1)
        self.assertEqual(len(ledger.receipts("bob")), 1)
        self.assertEqual(len(ledger.receipts()), 2)

    def test_total_billed(self):
        ledger = BillingLedger()
        ledger.allocate_pool("alice", 10.0)
        mgr = InstanceManager()
        rec = InstanceRecord("i1", "runpod", "A10", 0.5, time.time() - 3700)
        mgr.register(rec)
        mgr.terminate("i1")
        ledger.charge("alice", rec)
        self.assertGreater(ledger.total_billed("alice"), 0)
        self.assertEqual(ledger.total_billed("nobody"), 0.0)

    def test_negative_allocation_raises(self):
        ledger = BillingLedger()
        with self.assertRaises(ValueError):
            ledger.allocate_pool("alice", -1)


if __name__ == "__main__":
    unittest.main()
