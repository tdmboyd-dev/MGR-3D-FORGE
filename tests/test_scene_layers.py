import unittest
import json
import tempfile
from pathlib import Path

from forge.scene_layers import compose_scene_layers
from forge.cli import main


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

    def test_cli_materializes_receipt_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)
            source=path/"layers.json"
            result=path/"scene.json"
            source.write_text(json.dumps({"layers":[self.base]}),encoding="utf-8")
            self.assertEqual(main(["compose-scene","--layers",str(source),"--out",str(result)]),0)
            self.assertEqual(json.loads(result.read_text(encoding="utf-8"))["objects"]["/world/rock"]["kind"],"mesh")
            with self.assertRaises(FileExistsError):
                main(["compose-scene","--layers",str(source),"--out",str(result)])

    def test_cli_rejects_unexpected_input_envelope(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)
            source=path/"layers.json"
            source.write_text(json.dumps({"layers":[self.base],"dangerous":True}),encoding="utf-8")
            with self.assertRaises(ValueError):
                main(["compose-scene","--layers",str(source),"--out",str(path/"scene.json")])


if __name__ == "__main__":
    unittest.main()
