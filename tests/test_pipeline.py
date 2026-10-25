from pathlib import Path
import json
import tempfile
import unittest

from forge.pipeline import run_pipeline
from forge.spec import WorldSpec


class PipelineTests(unittest.TestCase):
    def test_cpu_pipeline_retains_truthful_no_blender_status(self):
        with tempfile.TemporaryDirectory() as root:
            destination=Path(root)/"new-world"
            record=run_pipeline(WorldSpec(),destination)
            self.assertEqual(record["overall"],"PARTIAL_CPU_ONLY")
            self.assertEqual(record["stages"]["blender_import"]["status"],"NOT_RUN")
            self.assertTrue((destination/"world.glb").is_file())
            self.assertEqual(json.loads((destination/"pipeline.json").read_text())["overall"],"PARTIAL_CPU_ONLY")

    def test_refuse_overwriting_existing_work(self):
        with tempfile.TemporaryDirectory() as root:
            destination=Path(root)/"already"
            destination.mkdir()
            (destination/"notes.txt").write_text("preserve")
            with self.assertRaises(FileExistsError):
                run_pipeline(WorldSpec(),destination)
            self.assertEqual((destination/"notes.txt").read_text(),"preserve")

    def test_no_fake_visual_comparison_without_blender(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                run_pipeline(WorldSpec(),Path(root)/"fresh",visual_baseline=Path(root)/"reference.png")


if __name__=="__main__":
    unittest.main()
