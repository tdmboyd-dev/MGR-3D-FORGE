import json
from pathlib import Path
import tempfile
import unittest

from forge.creation_memory import CreationMemory


class CreationMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.memory=CreationMemory(self.tmp.name)

    def test_revision_continuity_and_owner_lock(self):
        first=self.memory.record("sample-character",properties={"height_m":1.84,"outfit":"coat"},locked_keys=["height_m"],author="owner")
        second=self.memory.record("sample-character",properties={"height_m":1.84,"outfit":"shirt"},author="owner",expected_head=first["head"])
        self.assertEqual(len(second["history"]),2)
        self.assertEqual(self.memory.read("sample-character"),second)
        with self.assertRaises(PermissionError):
            self.memory.record("sample-character",properties={"height_m":2.0,"outfit":"shirt"},author="agent",expected_head=second["head"])

    def test_stale_revision_rejected(self):
        first=self.memory.record("world-1",properties={"season":"fall"},author="owner")
        with self.assertRaises(ValueError):
            self.memory.record("world-1",properties={"season":"winter"},author="agent")
        self.assertEqual(self.memory.read("world-1")["head"],first["head"])

    def test_detect_tamper(self):
        self.memory.record("world-2",properties={"water":False},author="owner")
        path=Path(self.tmp.name)/"world-2.json"
        record=json.loads(path.read_text())
        record["history"][0]["properties"]["water"]=True
        path.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            self.memory.read("world-2")

    def test_reject_invalid_identity_and_values(self):
        with self.assertRaises(ValueError):
            self.memory.record("../../escape",properties={},author="owner")
        with self.assertRaises(ValueError):
            self.memory.record("valid",properties={"scale":float("nan")},author="owner")


if __name__=="__main__":
    unittest.main()
