from pathlib import Path
import tempfile
import unittest

from forge.code_architect import FileChange
from forge.repair import repair_until_pass


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def test_fail_revert_then_succeed(self):
        target=self.root/"geometry.txt"
        def propose(attempt, error):
            return [FileChange("geometry.txt", "bad" if attempt==1 else "fixed")]
        def validate():
            return target.read_text()=="fixed"
        outcome=repair_until_pass(self.root,propose=propose,validate=validate,max_attempts=2)
        self.assertTrue(outcome.passed)
        self.assertEqual([x["status"] for x in outcome.receipts],["REVERTED","PASS"])
        self.assertEqual(target.read_text(),"fixed")

    def test_exhaustion_keeps_workspace_clean(self):
        outcome=repair_until_pass(self.root,
            propose=lambda attempt,error:[FileChange("bad.txt","bad")],
            validate=lambda:False,max_attempts=2)
        self.assertFalse(outcome.passed)
        self.assertFalse((self.root/"bad.txt").exists())
        self.assertEqual(outcome.attempts,2)

    def test_reject_unbounded_attempts(self):
        with self.assertRaises(ValueError):
            repair_until_pass(self.root,propose=lambda *_:[],validate=lambda:True,max_attempts=500)


if __name__=="__main__":
    unittest.main()
