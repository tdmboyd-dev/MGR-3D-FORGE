"""Segmentation adapter contract, registry and honesty tests."""

import unittest

from forge.segmentation import (AdapterRegistry, ManualMaskAdapter, MaskResult,
                               SegmentationAdapter, SegmentationError,
                               UnavailableAdapter, build_default_registry,
                               describe_registry, EVIDENCE_LEVEL_INFERRED,
                               EVIDENCE_LEVEL_MANUAL, EVIDENCE_LEVEL_UNAVAILABLE,
                               SCHEMA)


class SegmentationContractTests(unittest.TestCase):
    def test_manual_adapter_is_always_available_and_never_claims_inference(self):
        adapter = ManualMaskAdapter()
        self.assertTrue(isinstance(adapter, SegmentationAdapter))
        self.assertTrue(adapter.available())
        self.assertEqual(adapter.evidence_level, EVIDENCE_LEVEL_MANUAL)
        result = adapter.segment("any.png", out_path="out.png")
        self.assertIsInstance(result, MaskResult)
        self.assertEqual(result.adapter, "manual-owner-mask")
        self.assertIsNone(result.confidence)
        self.assertEqual(result.evidence_level, EVIDENCE_LEVEL_MANUAL)
        self.assertIn("no model was invoked", " ".join(result.notes))

    def test_unavailable_adapter_refuses_to_segment(self):
        adapter = UnavailableAdapter("sam3", "model not installed")
        self.assertFalse(adapter.available())
        self.assertEqual(adapter.evidence_level, EVIDENCE_LEVEL_UNAVAILABLE)
        with self.assertRaises(SegmentationError):
            adapter.segment("any.png", out_path="out.png")

    def test_default_registry_contains_only_manual_adapter(self):
        registry = build_default_registry()
        self.assertEqual(registry.names(), ("manual-owner-mask",))
        self.assertEqual(registry.available_names(), ("manual-owner-mask",))
        described = describe_registry(registry)
        self.assertEqual(described["schema"], SCHEMA)
        self.assertFalse(described["neural_adapter_installed"])
        self.assertTrue(described["adapters"][0]["available"])

    def test_registry_rejects_duplicates_and_unknown_names(self):
        registry = AdapterRegistry()
        registry.register(ManualMaskAdapter())
        with self.assertRaises(ValueError):
            registry.register(ManualMaskAdapter())
        with self.assertRaises(KeyError):
            registry.get("nope")
        with self.assertRaises(SegmentationError):
            registry.require_available("nope")

    def test_registry_require_available_passes_for_manual(self):
        registry = build_default_registry()
        adapter = registry.require_available("manual-owner-mask")
        self.assertEqual(adapter.name, "manual-owner-mask")

    def test_mask_result_serializes_provenance(self):
        result = MaskResult(mask_path="m.png", adapter="manual-owner-mask",
                            evidence_level=EVIDENCE_LEVEL_MANUAL,
                            confidence=0.9, notes=("note",))
        payload = result.as_dict()
        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["mask_path"], "m.png")
        self.assertEqual(payload["confidence"], 0.9)
        self.assertEqual(payload["notes"], ["note"])

    def test_no_neural_adapter_is_claimed_available_by_default(self):
        registry = build_default_registry()
        described = describe_registry(registry)
        neural = [a for a in described["adapters"]
                  if a["evidence_level"] == EVIDENCE_LEVEL_INFERRED]
        self.assertEqual(neural, [])
        self.assertFalse(described["neural_adapter_installed"])


if __name__ == "__main__":
    unittest.main()
