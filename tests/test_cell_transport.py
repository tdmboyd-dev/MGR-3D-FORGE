import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from forge.cell_transport import MGRCellTransport
from forge.cli import main


class CellTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = {}
        for key, data in (("a", b"aaaa"), ("b", b"bbbb"), ("c", b"cccc")):
            (self.root / f"{key}.glb").write_bytes(data)
            self.manifest[key] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

    def plan(self, active, prefetch=(), evict=()):
        return {"status": "PLAN_ONLY", "active": list(active), "prefetch": list(prefetch), "evict": list(evict)}

    def test_real_disk_cache_and_repeat_no_extra_read(self):
        transport = MGRCellTransport(self.root, self.manifest, memory_budget_bytes=8)
        result = transport.apply_plan(self.plan(["a"], ["b"]))
        self.assertEqual(result["loaded"], ["a", "b"])
        self.assertEqual(result["disk_reads"], 2)
        self.assertEqual(transport.apply_plan(self.plan(["a"]))["disk_reads"], 2)
        self.assertEqual(transport.apply_plan(self.plan(["c"], evict=["b"]))["resident_bytes"], 8)

    def test_prefetch_does_not_evict_active(self):
        transport = MGRCellTransport(self.root, self.manifest, memory_budget_bytes=4)
        result = transport.apply_plan(self.plan(["a"], ["b"]))
        self.assertEqual(result["resident"], ["a"])
        self.assertEqual(result["skipped"], ["b"])

    def test_two_active_cells_exceeding_budget_are_not_false_loaded(self):
        transport = MGRCellTransport(self.root, self.manifest, memory_budget_bytes=4)
        result = transport.apply_plan(self.plan(["a", "b"]))
        self.assertEqual(result["loaded"], ["a"])
        self.assertEqual(result["resident"], ["a"])
        self.assertEqual(result["skipped"], ["b"])

    def test_corrupt_disk_file_fails_closed(self):
        (self.root / "a.glb").write_bytes(b"zzzz")
        transport = MGRCellTransport(self.root, self.manifest, memory_budget_bytes=8)
        result = transport.apply_plan(self.plan(["a"]))
        self.assertEqual(result["status"], "PARTIAL_FAILURE")
        self.assertEqual(result["resident_bytes"], 0)
        self.assertIn("integrity", result["faults"]["a"])

    def test_missing_cell_is_explicit_fault(self):
        transport = MGRCellTransport(self.root, self.manifest, memory_budget_bytes=8)
        result = transport.apply_plan(self.plan(["absent"]))
        self.assertEqual(result["faults"]["absent"], "UNKNOWN_CELL")

    def test_bad_manifest_or_plan_rejected(self):
        with self.assertRaises(ValueError):
            MGRCellTransport(self.root, {"../escape": self.manifest["a"]})
        transport = MGRCellTransport(self.root, self.manifest)
        with self.assertRaises(ValueError):
            transport.apply_plan(self.plan(["a", "a"]))

    def test_cli_runs_real_io_and_writes_receipt(self):
        registry = self.root / "registry.json"
        plan = self.root / "plan.json"
        output = self.root / "transport-report.json"
        registry.write_text(json.dumps(self.manifest), encoding="utf-8")
        plan.write_text(json.dumps(self.plan(["a"], ["b"])), encoding="utf-8")
        self.assertEqual(main(["load-cells", "--root", str(self.root),
                               "--manifest", str(registry), "--plan", str(plan),
                               "--budget-bytes", "8", "--out", str(output)]), 0)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["disk_reads"], 2)
        self.assertEqual(report["resident_bytes"], 8)
        with self.assertRaises(FileExistsError):
            main(["load-cells", "--root", str(self.root), "--manifest", str(registry),
                  "--plan", str(plan), "--out", str(output)])

    def test_cli_failed_integrity_returns_nonzero_with_receipt(self):
        registry = self.root / "registry.json"
        plan = self.root / "plan.json"
        output = self.root / "tamper-report.json"
        registry.write_text(json.dumps(self.manifest), encoding="utf-8")
        plan.write_text(json.dumps(self.plan(["a"])), encoding="utf-8")
        (self.root / "a.glb").write_bytes(b"xxxx")
        self.assertEqual(main(["load-cells", "--root", str(self.root),
                               "--manifest", str(registry), "--plan", str(plan),
                               "--out", str(output)]), 1)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "PARTIAL_FAILURE")


if __name__ == "__main__":
    unittest.main()
