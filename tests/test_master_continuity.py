"""Protect the owner-approved research plan from silent handoff/target drift.

This test checks documentation integrity only; it does not claim to inspect
all sources or implement/accept the proposed 3D engines.
"""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/external-provenance/BEAST-3D-RESEARCH-UNIVERSE-2026-10-31.json"

class MasterContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(SOURCE.read_text(encoding="utf8"))
    def test_sources_have_distinct_ids_and_over_one_hundred_distinct_names(self):
        entries=self.registry["targets"]
        self.assertGreaterEqual(len(entries),150)
        self.assertEqual(self.registry["target_count"],len(entries))
        self.assertEqual(len({x["id"] for x in entries}),len(entries))
        self.assertGreaterEqual(len({x["name"].lower() for x in entries}),100)
        self.assertEqual(sum(e["research_state"]=="QUEUED_UNVERIFIED" for e in entries),184)
        self.assertEqual(sum(e["research_state"]=="SOURCED_PRIMARY_PUBLIC_DOCS_NOT_END_TO_END_READ" for e in entries),3)
        self.assertTrue(all(e["rea_execution_state"]=="NOT_RUN" for e in entries))
        self.assertTrue(all(e["production_ready"] is False for e in entries))
        self.assertEqual(self.registry["new_rea_runs"],0)

    def test_targets_keep_exact_authorization_and_license_gate(self):
        required={"id","name","family","source_locator","source_path","owner_system",
                  "license_state","authorized_method","next_action"}
        for item in self.registry["targets"]:
            with self.subTest(name=item["name"]):
                self.assertTrue(required.issubset(item))
                self.assertTrue(item["source_locator"].startswith("https://") or (item["source_locator"].startswith("forge/") and item["license_state"]=="OWNED"))
                self.assertEqual(item["authorized_method"],
                                 "PUBLIC_DOCUMENTATION_ONLY_UNTIL_EXACT_RIGHTS_REVIEW")
                self.assertTrue(item["license_state"])
                self.assertFalse(item["assets_downloaded"])

    def test_one_current_handoff_master_plan_and_feature_ids(self):
        paths=["docs/HANDOFF.md","docs/BUILD-REGISTER.md","docs/PROGRESS-LOG.md",
               "docs/MASTER-FORGE-PROGRAM-2026-10-31.md",
               "research/external-provenance/BEAST-3D-RESEARCH-UNIVERSE-2026-10-31.json"]
        for path in paths:
            self.assertTrue((ROOT/path).is_file(),path)
        handoff=(ROOT/"docs/HANDOFF.md").read_text(encoding="utf8")
        self.assertIn("Current master program/continuity registration",handoff)
        self.assertIn("MASTER-FORGE-PROGRAM-2026-10-31.md",handoff)
        reg=(ROOT/"docs/BUILD-REGISTER.md").read_text(encoding="utf8")
        for i in range(129,139):
            self.assertEqual(reg.count("| F"+str(i)+" |"),1)
        self.assertIn("F01–F144",reg)
        master=(ROOT/"docs/MASTER-FORGE-PROGRAM-2026-10-31.md").read_text(encoding="utf8")
        for phrase in ("MGR Rambler","Forge Creator plugin","REA self-study",
                       "Creation OS","source", "not"):
            self.assertIn(phrase,master)
