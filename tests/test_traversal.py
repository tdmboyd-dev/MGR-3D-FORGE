import unittest

from forge.geometry import create_neighborhood
from forge.spec import WorldSpec
from forge.traversal import rehearse_road_walk


class WorldTraversalTests(unittest.TestCase):
    def setUp(self):
        _,self.world=create_neighborhood(WorldSpec(columns=4,rows=4,buildings=8))
        ids=[building["id"] for building in self.world["buildings"]]
        self.start,self.goal=ids[0],ids[-1]

    def test_road_agent_reaches_goal_without_building_contact(self):
        result=rehearse_road_walk(self.world,self.start,self.goal)
        self.assertEqual(result["status"],"PASS_OFFLINE_ROAD_GRAPH")
        self.assertGreaterEqual(len(result["frames"]),1)
        self.assertGreaterEqual(result["duration_s"],0)
        self.assertTrue(all(result["frames"][i]["time_s"]<=result["frames"][i+1]["time_s"]
                            for i in range(len(result["frames"])-1)))

    def test_same_building_zero_distance(self):
        result=rehearse_road_walk(self.world,self.start,self.start)
        self.assertEqual(result["distance_m"],0)
        self.assertEqual(len(result["frames"]),1)

    def test_invalid_inputs_and_budgets_fail(self):
        with self.assertRaises(ValueError):
            rehearse_road_walk(self.world,self.start,self.goal,speed_mps=0)
        with self.assertRaises(ValueError):
            rehearse_road_walk(self.world,self.start,self.goal,max_samples=1)
        with self.assertRaises(KeyError):
            rehearse_road_walk(self.world,"made-up-building",self.goal)


if __name__=="__main__":
    unittest.main()
