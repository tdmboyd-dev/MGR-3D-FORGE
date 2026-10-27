"""SAM adapter gating and honesty tests (pass with or without SAM installed)."""

import os
import tempfile
import unittest
from pathlib import Path

from forge.sam_adapter import SamAdapter, describe_sam, register_sam_if_available
from forge.segmentation import AdapterRegistry, build_default_registry


class SamAdapterGatingTests(unittest.TestCase):
    def test_import_is_safe(self):
        adapter = SamAdapter()
        described = describe_sam()
        self.assertIn("available", described)
        self.assertIn("honesty", described)
        # available() must be consistent with describe_sam()
        self.assertEqual(adapter.available(), described["available"])

    def test_segment_refuses_when_unavailable(self):
        adapter = SamAdapter()
        if adapter.available():
            self.skipTest("SAM is available on this machine")
        with self.assertRaises(Exception):
            adapter.segment("nope.png", out_path="out.png")

    def test_register_is_no_op_when_unavailable(self):
        adapter = SamAdapter()
        if adapter.available():
            self.skipTest("SAM is available on this machine")
        registry = build_default_registry()
        before = registry.names()
        registered = register_sam_if_available(registry)
        self.assertFalse(registered)
        self.assertEqual(registry.names(), before)

    def test_weights_env_var_is_honored(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "sam_vit_b_01ec64.pth"
            fake.write_bytes(b"x" * 2_000_000)
            old = os.environ.get("MGR_SAM_WEIGHTS")
            os.environ["MGR_SAM_WEIGHTS"] = str(fake)
            try:
                adapter = SamAdapter()
                self.assertEqual(str(adapter._weights), str(fake))
            finally:
                if old is None:
                    os.environ.pop("MGR_SAM_WEIGHTS", None)
                else:
                    os.environ["MGR_SAM_WEIGHTS"] = old

    def test_mode_validation(self):
        adapter = SamAdapter(mode="garbage")
        self.assertEqual(adapter.mode, "center")
        adapter2 = SamAdapter(mode="auto")
        self.assertEqual(adapter2.mode, "auto")

    def test_default_registry_stays_manual_only(self):
        registry = build_default_registry()
        self.assertEqual(registry.names(), ("manual-owner-mask",))
        self.assertNotIn("sam", registry.names())

    def test_end_to_end_when_available(self):
        adapter = SamAdapter()
        if not adapter.available():
            self.skipTest("SAM not available")
        src = Path("artifacts/test_subject.png")
        if not src.is_file():
            self.skipTest("test subject missing")
        out = Path("artifacts/test_mask_e2e.png")
        result = adapter.segment(str(src), out_path=str(out))
        self.assertTrue(out.is_file())
        self.assertEqual(result.adapter, "sam")
        self.assertEqual(result.evidence_level, "MODEL_INFERRED_MASK")
        self.assertIsNotNone(result.confidence)

    def test_register_when_available(self):
        adapter = SamAdapter()
        if not adapter.available():
            self.skipTest("SAM not available")
        registry = AdapterRegistry()
        registry.register(__import__("forge.segmentation", fromlist=["ManualMaskAdapter"]).ManualMaskAdapter())
        registered = register_sam_if_available(registry)
        self.assertTrue(registered)
        self.assertIn("sam", registry.names())
        self.assertTrue(registry.get("sam").available())


    def test_segment_parts_when_available(self):
        adapter = SamAdapter()
        if not adapter.available():
            self.skipTest("SAM not available")
        src = Path("artifacts/test_subject.png")
        if not src.is_file():
            self.skipTest("test subject missing")
        out = Path("artifacts/test_parts")
        prompts = [{"name": "subject", "point": [128, 128]}]
        results = adapter.segment_parts(str(src), out_dir=str(out), prompts=prompts)
        self.assertEqual(len(results), 1)
        self.assertTrue(Path(results[0].mask_path).is_file())
        self.assertIsNotNone(results[0].confidence)
