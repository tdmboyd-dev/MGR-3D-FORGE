"""GPU planner: no money and no fictional live provider proof."""
import unittest
from datetime import date, timedelta
from forge.gpu_rental import plan_rental

JOBS = [{"id": "shape-3d", "seconds": 600, "min_vram_gb": 24}]


def offer(name="L40S", cost=1.2, days=0, capacity=48):
    return {"name": name, "provider": "example-quotes-only", "vram_gb": capacity,
            "hourly_usd": cost, "observed_at": (date.today()-timedelta(days=days)).isoformat(),
            "source_url": "https://example.com/quote"}


class GpuRentalTests(unittest.TestCase):
    def test_missing_prices_is_not_a_fake_quote(self):
        result = plan_rental(JOBS)
        self.assertEqual(result["status"], "UNPRICED")
        self.assertIsNone(result["selected_gpu"])
        self.assertFalse(result["rental_started"])
        self.assertFalse(result["provider_called"])

    def test_recent_quoted_offer_is_only_an_estimate(self):
        result = plan_rental(JOBS, offers=[offer("A", 1.2), offer("B", 0.8)])
        self.assertEqual(result["status"], "DRY_RUN_ESTIMATE")
        self.assertEqual(result["selected_gpu"]["name"], "B")
        self.assertEqual(result["total_estimated_cost"], 0.8)
        self.assertFalse(result["purchase_authorized"])

    def test_stale_or_unqualified_quotes_not_admitted(self):
        self.assertEqual(plan_rental(JOBS, offers=[offer(days=8)])["status"],
                         "NO_RECENT_ELIGIBLE_QUOTE")
        self.assertEqual(plan_rental(JOBS, offers=[offer(capacity=8)])["status"],
                         "NO_RECENT_ELIGIBLE_QUOTE")

    def test_rejects_bad_or_future_quotes(self):
        for bad in ({**offer(), "source_url": "http://example.com"},
                    {**offer(), "hourly_usd": -1},
                    {**offer(), "observed_at": (date.today()+timedelta(days=1)).isoformat()}):
            with self.subTest(quote=bad), self.assertRaises(ValueError):
                plan_rental(JOBS, offers=[bad])
