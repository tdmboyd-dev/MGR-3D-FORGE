import unittest

from forge.scene_layers import compose_scene_layers


class SceneLayerTests(unittest.TestCase):
    def setUp(self):
        self.base = {"id": "terrain", "objects": {
            "/world/rock": {"kind": "mesh", "material": "basalt", "visible": True},
            "/world/tree": {"kind": "mesh", "material": "pine"}}}

    def test_stronger_layer_overrides_field_without_losing_other_fields(self):
        result = compose_scene_layers([self.base, {"id": "art", "objects": {
            "/world/rock": {"material": "moss"}}}])
        self.assertEqual(result["objects"]["/world/rock"],
                         {"kind": "mesh", "material": "moss", "visible": True})
        self.assertEqual(result["field_sources"]["/world/rock"]["material"], "art")
        self.assertEqual(result["field_sources"]["/world/rock"]["kind"], "terrain")

    def test_tombstone_and_reintroduction(self):
        result = compose_scene_layers([self.base, {"id": "trim", "objects": {
            "/world/tree": None}}, {"id": "regrow", "objects": {
            "/world/tree": {"kind": "mesh", "material": "oak"}}}])
        self.assertEqual(result["objects"]["/world/tree"]["material"], "oak")
        self.assertEqual(result["field_sources"]["/world/tree"]["kind"], "regrow")

    def test_output_deterministic_without_mutating_inputs(self):
        baseline = repr(self.base)
        a = compose_scene_layers([self.base])
        b = compose_scene_layers([self.base])
        self.assertEqual(a, b)
        a["objects"]["/world/rock"]["material"] = "edited"
        self.assertEqual(repr(self.base), baseline)
        self.assertNotEqual(a, b)

    def test_rejects_bad_paths_duplicate_ids_and_nonfinite(self):
        for layers in ([self.base, self.base],
                       [{"id": "x", "objects": {"../escape": {"kind": "mesh"}}}],
                       [{"id": "x", "objects": {"/r": {"kind": "mesh", "metadata": {"nan": float("nan")}}}}],
                       [{"id": "x", "objects": {"/r": {"material": "bare"}}}],
                       [{"id": "x", "objects": {"/r": {"kind": "mesh", "visible": 1}}}],
                       [{"id": "x", "objects": {"/r": {"kind": "mesh", "transform": [0] * 15}}}]):
            with self.subTest(layers=layers), self.assertRaises(ValueError):
                compose_scene_layers(layers)

    def test_nested_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            compose_scene_layers([{"id": "x", "objects": {"/r": {"kind": "mesh", "script": "code"}}}])


if __name__ == "__main__":
    unittest.main()
