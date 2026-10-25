from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from forge.code_architect import FileChange, WorkspaceFileJob


class CodeArchitectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.job = WorkspaceFileJob(self.root)

    def test_multi_file_unattended_apply_then_rollback(self):
        existing = self.root / "existing.txt"
        existing.write_text("before", encoding="utf-8")
        digest = sha256(b"before").hexdigest()
        changes = [FileChange("existing.txt", "after", digest),
                   FileChange("folder/new.txt", "new")]
        receipt = self.job.apply("job-1", changes)
        self.assertEqual(receipt["status"], "applied")
        self.assertEqual(existing.read_text(), "after")
        self.assertEqual((self.root / "folder/new.txt").read_text(), "new")
        self.job.rollback("job-1")
        self.assertEqual(existing.read_text(), "before")
        self.assertFalse((self.root / "folder/new.txt").exists())

    def test_out_of_scope_paths_and_symlink_blocked(self):
        for path in ("../outside", "/tmp/other", "folder/../../outside", "C:/Users/a", "a\\b"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.job.preview([FileChange(path, "no")])
        outside = Path(self.tmp.name).parent
        (self.root / "jump").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(PermissionError):
            self.job.preview([FileChange("jump/escape.txt", "no")])

    def test_precondition_collision_and_budget(self):
        (self.root / "locked.txt").write_text("old")
        with self.assertRaises(ValueError):
            self.job.apply("bad-precondition", [FileChange("locked.txt", "overwrite")])
        with self.assertRaises(ValueError):
            self.job.preview([FileChange("a", "one"), FileChange("a", "two")])
        with self.assertRaises(ValueError):
            WorkspaceFileJob(self.root, max_bytes=2).preview([FileChange("a", "big")])

    def test_rollback_refuses_to_overwrite_later_edit(self):
        self.job.apply("first", [FileChange("a.txt", "one")])
        (self.root / "a.txt").write_text("changed elsewhere")
        with self.assertRaises(ValueError):
            self.job.rollback("first")
        self.assertEqual((self.root / "a.txt").read_text(), "changed elsewhere")


if __name__ == "__main__":
    unittest.main()
