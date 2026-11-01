"""Prove repo handbook points to current original source, not imaginary components."""
import ast,json,re
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class SourceHandbookTests(unittest.TestCase):
    def test_baseline_static_inventory_is_complete_and_sha_versioned(self):
        source=json.loads((ROOT/"evidence/audits/2026-10-31-baseline-static-inventory.json").read_text(encoding="utf8"))
        self.assertEqual(source["tracked_file_count"],405)
        self.assertEqual(len(source["all_tracked_file_sha256_bytes_and_parse_classifications"]),405)
        self.assertEqual(len(source["errors"]),0)
        self.assertEqual(source["baseline_git_commit"],"310badac0661422fd1415b9d3baa52fed7127391")
        for entry in source["all_tracked_file_sha256_bytes_and_parse_classifications"]:
            self.assertRegex(entry["sha256"],r"^[0-9a-f]{64}$")
            self.assertTrue(entry["path"])
            self.assertGreaterEqual(entry["bytes"],0)
    def test_module_index_covers_actual_tracked_python_without_imaginary_file(self):
        inv=json.loads((ROOT/"evidence/audits/2026-10-31-baseline-static-inventory.json").read_text(encoding="utf8"))
        actual=sorted(x["path"] for x in inv["all_tracked_file_sha256_bytes_and_parse_classifications"]
                      if x["path"].startswith("forge/") and x["path"].endswith(".py"))
        handbook=(ROOT/"docs/ACTUAL-FORGE-MODULE-MAP-2026-10-31.md").read_text(encoding="utf8")
        for path in actual:
            self.assertIn(path,handbook)
        self.assertNotIn("| "+chr(96)+"forge/fantasy.py"+chr(96),handbook)
        self.assertFalse((ROOT/"forge/fantasy.py").exists())
    def test_all_actual_cli_subcommands_documented(self):
        tree=ast.parse((ROOT/"forge/cli.py").read_text(encoding="utf8"))
        names=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=="add_parser" and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
                names.add(node.args[0].value)
        self.assertEqual(len(names),60)
        handbook=(ROOT/"docs/FORGE-ENGINEERING-HANDBOOK.md").read_text(encoding="utf8")
        for name in names:
            self.assertIn("| "+chr(96)+name+chr(96)+" |",handbook)
        self.assertIn("MGR-API-MCP",handbook)
        self.assertIn("NOT",handbook)
    def test_187_rights_gated_candidates_are_not_187_installed_models(self):
        data=json.loads((ROOT/"research/external-provenance/BEAST-3D-RESEARCH-UNIVERSE-2026-10-31.json").read_text(encoding="utf8"))
        self.assertEqual(data["target_count"],187)
        self.assertEqual(len(data["targets"]),187)
        self.assertEqual(data["new_rea_runs"],0)
        self.assertEqual(sum(x["assets_downloaded"] is True for x in data["targets"]),0)
        self.assertEqual(sum(x["research_state"]=="SOURCED_PRIMARY_PUBLIC_DOCS_NOT_END_TO_END_READ" for x in data["targets"]),3)
        for entry in data["targets"]:
            self.assertTrue(entry["source_locator"])
            self.assertFalse(entry["production_ready"])
            self.assertEqual(entry["rea_execution_state"],"NOT_RUN")
    def test_one_handoff_and_source_based_howto_exist(self):
        required=["docs/HANDOFF.md","docs/FORGE-ENGINEERING-HANDBOOK.md",
                  "docs/HOW-TO-MORPH-RIG-LIPSYNC.md",
                  "docs/HOW-TO-SOURCE-VAULT-REA.md",
                  "docs/HOW-TO-INTEGRATION-VERIFY-RECOVER.md",
                  "docs/ACTUAL-FORGE-MODULE-MAP-2026-10-31.md",
                  "evidence/audits/2026-10-31-baseline-summary.md"]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue((ROOT/path).is_file())
        head=(ROOT/"docs/HANDOFF.md").read_text(encoding="utf8")
        self.assertIn("FORGE-ENGINEERING-HANDBOOK",head)
