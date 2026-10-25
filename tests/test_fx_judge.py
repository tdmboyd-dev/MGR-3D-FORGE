"""MGR-native atmosphere render evidence and fail-closed comparison tests."""

import json
from pathlib import Path
import tempfile
import unittest

from forge.fx_judge import judge_atmosphere
from tests.test_visualqa import png_bytes


class AtmosphereJudgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        self.control=root/"control.png"
        self.fog=root/"fog.png"
        self.control.write_bytes(png_bytes([[(0,0,0),(0,0,0)]]))
        self.fog.write_bytes(png_bytes([[(60,50,40),(70,60,50)]]))
        self.a=root/"control.json"
        self.b=root/"fog.json"
        self.base={"status":"PASS","source":"effect.glb","camera":"MGR_FX_Camera",
                   "render_engine":"CYCLES","render_device":"CPU","compositor_glare":"Fog Glow",
                   "point_light_count":2,"emission_socket_colors":[[.5,.5,.5]],
                   "volume_density":0,"volume_shader":None}
        self.candidate=dict(self.base,volume_density=.075,
                            volume_shader="ShaderNodeVolumePrincipled",volume_style="cloud")
        self.save()

    def save(self):
        self.a.write_text(json.dumps(self.base))
        self.b.write_text(json.dumps(self.candidate))

    def test_real_pixel_delta_and_density(self):
        receipt=judge_atmosphere(self.control,self.fog,self.a,self.b)
        self.assertEqual(receipt["status"],"PASS")
        self.assertEqual(receipt["candidate_style"],"cloud")
        self.assertGreater(receipt["rgb_mae_8bit"],3)

    def test_identical_pixels_fail_quality_gate(self):
        receipt=judge_atmosphere(self.control,self.control,self.a,self.b)
        self.assertEqual(receipt["status"],"FAIL")

    def test_unmatched_camera_refused(self):
        self.candidate["camera"]="untrusted-other-camera"
        self.save()
        with self.assertRaises(ValueError):
            judge_atmosphere(self.control,self.fog,self.a,self.b)

    def test_missing_physical_medium_refused(self):
        self.candidate["volume_shader"]=None
        self.save()
        with self.assertRaises(ValueError):
            judge_atmosphere(self.control,self.fog,self.a,self.b)

    def test_unbounded_or_nan_acceptance_refused(self):
        for value in (-1,0,float("nan"),256,True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                judge_atmosphere(self.control,self.fog,self.a,self.b,minimum_rgb_mae=value)


if __name__=="__main__":
    unittest.main()
