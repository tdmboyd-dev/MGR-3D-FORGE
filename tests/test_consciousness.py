import unittest

from forge.consciousness import scene_facts, scene_query
from forge.geometry import create_neighborhood
from forge.spec import WorldSpec


class SceneConsciousnessTests(unittest.TestCase):
    def setUp(self):
        _, self.world = create_neighborhood(WorldSpec(rows=3, columns=3, buildings=5))

    def test_generated_facts_stable_and_grounded(self):
        first = scene_facts(self.world)
        self.assertEqual(first, scene_facts(self.world))
        self.assertEqual(len(first["objects"]), 5)
        self.assertTrue(all(x["evidence"] == "generated-scene-geometry" for x in first["objects"]))

    def test_specific_object_and_qualified_route(self):
        ids = [b["id"] for b in self.world["buildings"]]
        result = scene_query(self.world, building_id=ids[0], route_to=ids[-1])
        self.assertEqual(result["object"]["id"], ids[0])
        self.assertIn("not navmesh verified", result["route_evidence"])

    def test_no_invented_entities(self):
        with self.assertRaises(KeyError):
            scene_query(self.world, building_id="no-such-building")
        with self.assertRaises(ValueError):
            scene_query(self.world, route_to="unknown")

    def test_bad_geometry_fails_closed(self):
        self.world["buildings"][0]["size"] = [1, 0, 1]
        with self.assertRaises(ValueError):
            scene_facts(self.world)


if __name__ == "__main__":
    unittest.main()
