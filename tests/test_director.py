import math
import unittest

from forge.director import compile_director_reel, ease_fraction, sample_motion
from forge.blender_bridge import blender_director_inspect_command,blender_director_frames_command
from pathlib import Path
import tempfile


REEL={"shots":[
    {"id":"arrival","subject_id":"house1","camera":[30,20,15],
     "look_at":[0,4,0],"hold_seconds":2.0},
    {"id":"reveal","subject_id":"house2","camera":[-15,22,12],
     "look_at":[5,3,0],"hold_seconds":1.0},
]}


class NativeDirectorTests(unittest.TestCase):
    def test_nonoverlapping_shot_cuts(self):
        reel=compile_director_reel(REEL)
        self.assertEqual(reel["frame_end"],72)
        self.assertEqual(reel["shots"][0]["start_frame"],1)
        self.assertEqual(reel["shots"][0]["end_frame"],48)
        self.assertEqual(reel["shots"][1]["start_frame"],49)
        self.assertEqual(reel["shots"][1]["end_frame"],72)

    def test_frame_rate_and_motion_contract_validation(self):
        for kwargs in ({"fps":0},{"fps":121},{"transition":"teleport"}):
            with self.assertRaises(ValueError):
                compile_director_reel(REEL,**kwargs)

    def test_easing_curve_preserves_endpoints(self):
        for mode in ("linear","smoothstep","smootherstep"):
            self.assertEqual(ease_fraction(0,mode=mode),0)
            self.assertEqual(ease_fraction(1,mode=mode),1)
            vals=[ease_fraction(i/100,mode=mode) for i in range(101)]
            self.assertEqual(vals,sorted(vals))

    def test_motion_samples_stable_and_smooth(self):
        result=sample_motion([0,0,0],[12,6,-3],samples=11)
        self.assertTrue(result["endpoints_preserved"])
        self.assertEqual(result["samples"][0],[0,0,0])
        self.assertEqual(result["samples"][-1],[12,6,-3])
        # Smooth easing moves less near the endpoints than the middle.
        diffs=[math.dist(a,b) for a,b in zip(result["samples"],result["samples"][1:])]
        self.assertLess(diffs[0],diffs[4])
        self.assertLess(diffs[-1],diffs[5])

    def test_invalid_motion_rejected(self):
        with self.assertRaises(ValueError):
            sample_motion([0,0,0],[float("inf"),0,0])
        with self.assertRaises(ValueError):
            sample_motion([0,0,0],[1,2,3],samples=1)
        with self.assertRaises(ValueError):
            ease_fraction(float("nan"))

    def test_directed_camera_dolly_has_movement_and_correct_timeline(self):
        reel={"shots":[{**REEL["shots"][0],"camera_end":[25,20,15],"movement":"smooth-dolly"}]}
        result=compile_director_reel(reel)
        self.assertEqual(result["shots"][0]["camera_end"],[25,20,15])

    def test_invalid_dolly_rejected(self):
        shot={**REEL["shots"][0],"camera_end":[30,20,15],"movement":"smooth-dolly"}
        with self.assertRaises(ValueError):
            compile_director_reel({"shots":[shot]})

    def test_blender_director_command_requires_real_scene(self):
        with tempfile.TemporaryDirectory() as directory:
            blend=Path(directory)/"actual.blend"
            blend.write_bytes(b"placeholder")
            command=blender_director_inspect_command("blender",blend,Path(directory)/"out.json")
            self.assertIn("blender_director_inspect.py"," ".join(command))
            with self.assertRaises(ValueError):
                blender_director_inspect_command("blender",Path(directory)/"missing.blend",Path(directory)/"out.json")

    def test_timeline_render_command_validates_new_output(self):
        with tempfile.TemporaryDirectory() as directory:
            blend=Path(directory)/"scene.blend"
            blend.write_bytes(b"placeholder")
            cmd=blender_director_frames_command("blender",blend,Path(directory)/"new",Path(directory)/"report.json")
            self.assertIn("blender_director_frames.py"," ".join(cmd))
            with self.assertRaises(FileExistsError):
                blender_director_frames_command("blender",blend,Path(directory),Path(directory)/"report.json")


if __name__=="__main__":
    unittest.main()
