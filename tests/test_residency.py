import unittest

from forge.streaming import plan_chunk_residency


class ResidencyTests(unittest.TestCase):
    def setUp(self):
        self.cells={"chunks":[
            {"id":"origin","world_origin":[0,0,0]},
            {"id":"east","world_origin":[100,0,0]},
            {"id":"far","world_origin":[500,0,0]},
        ]}

    def test_nearby_active_and_distant_prefetch(self):
        result=plan_chunk_residency(self.cells,(0,1,0),active_radius_m=25,prefetch_radius_m=120)
        self.assertEqual(result["active"],["origin"])
        self.assertEqual(result["prefetch"],["east"])
        self.assertEqual(result["status"],"PLAN_ONLY")

    def test_distant_cell_is_evicted_and_never_claimed_loaded(self):
        result=plan_chunk_residency(self.cells,(0,0,0),previously_resident=("far","origin"))
        self.assertEqual(result["evict"],["far"])
        self.assertNotIn("far",result["active"])

    def test_budget_is_deterministic_at_equal_distance(self):
        equal={"chunks":[{"id":"z","world_origin":[1,0,0]},
                         {"id":"a","world_origin":[-1,0,0]}]}
        result=plan_chunk_residency(equal,(0,0,0),active_radius_m=2,max_active=1)
        self.assertEqual(result["active"],["a"])
        self.assertEqual(result["prefetch"],["z"])

    def test_invalid_chunk_registry_or_radius_rejected(self):
        for registry in ({"chunks":[{"id":"dup","world_origin":[0,0,0]},
                                     {"id":"dup","world_origin":[1,0,0]}]},
                         {"chunks":[{"id":"bad","world_origin":[float("nan"),0,0]}]}):
            with self.assertRaises(ValueError):
                plan_chunk_residency(registry,(0,0,0))
        with self.assertRaises(ValueError):
            plan_chunk_residency(self.cells,(0,0,0),active_radius_m=200,prefetch_radius_m=100)


if __name__=="__main__":
    unittest.main()
