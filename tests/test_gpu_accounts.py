"""GPU account management tests (pure CPU, no credentials)."""

import os
import tempfile
import unittest
from pathlib import Path

from forge.gpu_accounts import AccountStore, GpuAccountManager, ProviderCredential


class AccountStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = AccountStore(Path(self.tmp.name))

    def test_register_user(self):
        acct = self.store.register_user("alice")
        self.assertEqual(acct.user_id, "alice")
        self.assertFalse(acct.is_founder)
        # idempotent
        acct2 = self.store.register_user("alice")
        self.assertEqual(acct2.user_id, "alice")

    def test_register_founder(self):
        acct = self.store.register_user("founder", is_founder=True)
        self.assertTrue(acct.is_founder)

    def test_add_credential(self):
        self.store.register_user("alice")
        cred = ProviderCredential(provider="runpod", api_key="sk-test-1234", account_id="acc1")
        acct = self.store.add_credential("alice", cred)
        self.assertEqual(len(acct.credentials), 1)
        self.assertEqual(acct.credentials[0].provider, "runpod")

    def test_add_credential_replaces_duplicate(self):
        self.store.register_user("alice")
        c1 = ProviderCredential(provider="runpod", api_key="key1", account_id="acc1")
        c2 = ProviderCredential(provider="runpod", api_key="key2", account_id="acc1")
        self.store.add_credential("alice", c1)
        self.store.add_credential("alice", c2)
        acct = self.store.get_user("alice")
        self.assertEqual(len(acct.credentials), 1)
        self.assertEqual(acct.credentials[0].api_key, "key2")

    def test_remove_credential(self):
        self.store.register_user("alice")
        cred = ProviderCredential(provider="runpod", api_key="key1", account_id="acc1")
        self.store.add_credential("alice", cred)
        removed = self.store.remove_credential("alice", "runpod", "acc1")
        self.assertTrue(removed)
        acct = self.store.get_user("alice")
        self.assertEqual(len(acct.credentials), 0)

    def test_remove_nonexistent_returns_false(self):
        self.store.register_user("alice")
        self.assertFalse(self.store.remove_credential("alice", "runpod", "nope"))

    def test_persistence(self):
        self.store.register_user("alice")
        cred = ProviderCredential(provider="vast", api_key="secret-key-9999", account_id="a1")
        self.store.add_credential("alice", cred)
        # reload from disk
        store2 = AccountStore(self.store.root)
        acct = store2.get_user("alice")
        self.assertIsNotNone(acct)
        self.assertEqual(len(acct.credentials), 1)
        self.assertEqual(acct.credentials[0].api_key, "secret-key-9999")

    def test_credentials_encrypted_at_rest(self):
        self.store.register_user("alice")
        cred = ProviderCredential(provider="runpod", api_key="super-secret-key", account_id="a1")
        self.store.add_credential("alice", cred)
        raw = self.store.path.read_bytes()
        # the raw file should not contain the plaintext key
        self.assertNotIn(b"super-secret-key", raw)

    def test_list_users(self):
        self.store.register_user("alice")
        self.store.register_user("bob")
        self.assertEqual(self.store.list_users(), ["alice", "bob"])

    def test_masked_credential(self):
        cred = ProviderCredential(provider="runpod", api_key="sk-12345678", account_id="a1")
        masked = cred.masked()
        self.assertEqual(masked["api_key"], "***5678")
        self.assertEqual(masked["provider"], "runpod")


class GpuAccountManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = AccountStore(Path(self.tmp.name))
        self.mgr = GpuAccountManager(self.store)

    def test_register_and_connect(self):
        acct = self.mgr.register("alice")
        self.assertEqual(acct.user_id, "alice")
        acct = self.mgr.connect_provider("alice", "runpod", "sk-test-key-1234", account_id="acc1")
        self.assertEqual(len(acct.credentials), 1)

    def test_connect_rejects_short_key(self):
        self.mgr.register("alice")
        with self.assertRaises(ValueError):
            self.mgr.connect_provider("alice", "runpod", "short")

    def test_connect_rejects_unknown_provider(self):
        self.mgr.register("alice")
        with self.assertRaises(ValueError):
            self.mgr.connect_provider("alice", "unknown", "sk-test-key-1234")

    def test_disconnect(self):
        self.mgr.register("alice")
        self.mgr.connect_provider("alice", "runpod", "sk-test-key-1234", account_id="acc1")
        removed = self.mgr.disconnect_provider("alice", "runpod", "acc1")
        self.assertTrue(removed)
        acct = self.store.get_user("alice")
        self.assertEqual(len(acct.credentials), 0)

    def test_allocate_pool(self):
        self.mgr.register("alice")
        acct = self.mgr.allocate_pool("alice", 5.0)
        self.assertEqual(acct.pool_hours, 5.0)

    def test_allocate_negative_raises(self):
        self.mgr.register("alice")
        with self.assertRaises(ValueError):
            self.mgr.allocate_pool("alice", -1)

    def test_select_account(self):
        self.mgr.register("alice")
        self.mgr.connect_provider("alice", "runpod", "sk-test-key-1234", account_id="acc1")
        result = self.mgr.select_account("alice")
        self.assertEqual(result["status"], "SELECTED (dry run, no rental)")
        self.assertEqual(result["selected_provider"], "runpod")

    def test_select_account_no_credentials_raises(self):
        self.mgr.register("alice")
        with self.assertRaises(ValueError):
            self.mgr.select_account("alice")

    def test_select_account_unknown_user_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.select_account("nobody")

    def test_founder_shadow_pool(self):
        self.mgr.register("founder", is_founder=True)
        self.mgr.allocate_pool("founder", 10.0)
        self.mgr.contribute_shadow_hours("founder", 3.0)
        pool = self.mgr.founder_shadow_pool()
        self.assertEqual(pool["founder_accounts"], 1)
        self.assertAlmostEqual(pool["available_shadow_hours"], 3.0)

    def test_contribute_shadow_hours(self):
        self.mgr.register("founder", is_founder=True)
        self.mgr.allocate_pool("founder", 10.0)
        result = self.mgr.contribute_shadow_hours("founder", 3.0)
        self.assertEqual(result["contributed_hours"], 3.0)

    def test_contribute_more_than_pool_raises(self):
        self.mgr.register("founder", is_founder=True)
        self.mgr.allocate_pool("founder", 2.0)
        with self.assertRaises(ValueError):
            self.mgr.contribute_shadow_hours("founder", 5.0)

    def test_consume_shadow_hours(self):
        self.mgr.register("founder", is_founder=True)
        self.mgr.allocate_pool("founder", 10.0)
        self.mgr.contribute_shadow_hours("founder", 3.0)
        result = self.mgr.consume_shadow_hours("alice", 1.0)
        self.assertEqual(result["consumed_shadow_hours"], 1.0)
        self.assertAlmostEqual(result["remaining_shadow_hours"], 2.0)

    def test_consume_insufficient_shadow_raises(self):
        self.mgr.register("founder", is_founder=True)
        self.mgr.allocate_pool("founder", 10.0)
        with self.assertRaises(ValueError):
            self.mgr.consume_shadow_hours("alice", 5.0)

    def test_consume_no_founder_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.consume_shadow_hours("alice", 1.0)

    def test_describe(self):
        self.mgr.register("alice")
        desc = self.mgr.describe()
        self.assertEqual(desc["user_count"], 1)
        self.assertIn("honesty", desc)


if __name__ == "__main__":
    unittest.main()
