"""Acceptance tests for recovered CPU-only packing, shadow and budget use."""
import unittest
from forge.gpu_packer import pack_jobs


def job(identity, seconds, vram=24, shadow=False):
    return {"id":identity, "seconds":seconds, "min_vram_gb":vram, "shadow":shadow}


class GpuPackerTests(unittest.TestCase):
    def test_serial_schedule_and_block_calculation(self):
        result=pack_jobs([job("human",120),job("creature",3600,36)],block_hours=1)
        self.assertEqual(result["totals"]["blocks"],2)
        self.assertEqual(result["totals"]["min_vram_gb"],36)
        self.assertEqual(result["placements"][1]["start_seconds"],3600)
        self.assertEqual(result["totals"]["unused_seconds"],3480)

    def test_decreasing_packing_recovers_spaces_that_naive_queue_wastes(self):
        result=pack_jobs([job("tiny",900),job("large",2500),job("medium",2000),
                          job("small",1100)],block_hours=1)
        # Block 1 = 2500+1100, Block 2 = 2000+900: two blocks, not four.
        self.assertEqual(result["totals"]["blocks"],2)
        self.assertEqual(result["totals"]["unused_seconds"],700)
        self.assertEqual(result["totals"]["placed"],4)

    def test_shadow_fills_existing_unbilled_time_only(self):
        result=pack_jobs([job("main",2000),job("shadow-fit",1200,shadow=True),
                          job("shadow-no-fit",1800,shadow=True)],block_hours=1)
        self.assertEqual(result["totals"]["blocks"],1)
        self.assertEqual(result["totals"]["shadow_used_seconds"],1200)
        self.assertEqual(result["unplaced_shadow"],["shadow-no-fit"])
        self.assertEqual(result["totals"]["unused_seconds"],400)

    def test_only_shadow_jobs_never_allocate_money(self):
        result=pack_jobs([job("shadow",600,shadow=True)])
        self.assertEqual(result["totals"]["blocks"],0)
        self.assertEqual(result["unplaced_shadow"],["shadow"])
        self.assertEqual(result["totals"]["min_vram_gb"],0)

    def test_multiblock_job_reserves_nonoverlapping_timeline(self):
        result=pack_jobs([job("long",4000),job("short",1000)])
        self.assertEqual(result["totals"]["blocks"],2)
        a,b=next(x for x in result["placements"] if x["id"]=="long"),next(x for x in result["placements"] if x["id"]=="short")
        self.assertTrue(b["start_seconds"]>=a["end_seconds"])
        self.assertEqual(result["totals"]["unused_seconds"],2200)

    def test_fails_closed_on_bad_jobs(self):
        good={"id":"x","seconds":60,"min_vram_gb":24}
        for jobs in ([],[good,good],[{**good,"seconds":-1}],
                     [{**good,"min_vram_gb":float("nan")}],
                     [{**good,"secret":"not allowed"}],
                     [{**good,"shadow":1}]):
            with self.subTest(jobs=jobs),self.assertRaises(ValueError):
                pack_jobs(jobs)

    def test_rejects_invalid_billing_block(self):
        with self.assertRaises(ValueError):
            pack_jobs([job("a",60)],block_hours=0)
