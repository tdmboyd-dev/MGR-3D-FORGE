import unittest

from forge.motion_truth import judge_motion_samples


class MotionTruthTests(unittest.TestCase):
    def test_constant_velocity_is_continuous(self):
        result=judge_motion_samples([(0,(0,0,0)),(1,(2,0,0)),(2,(4,0,0))])
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["max_measured_speed_mps"],2)
        self.assertEqual(result["max_measured_acceleration_mps2"],0)

    def test_teleport_spike_fails_limit(self):
        result=judge_motion_samples([(0,(0,0,0)),(1,(1,0,0)),(2,(101,0,0))])
        self.assertEqual(result["status"],"FAIL")
        self.assertIn("speed",[v["kind"] for v in result["violations"]])

    def test_abrupt_velocity_change_fails_acceleration(self):
        result=judge_motion_samples([(0,(0,0,0)),(1,(2,0,0)),(2,(-2,0,0))],
                                    max_speed_mps=100,max_acceleration_mps2=2)
        self.assertEqual(result["status"],"FAIL")
        self.assertIn("acceleration",[v["kind"] for v in result["violations"]])

    def test_duplicate_or_reversed_timestamps_rejected(self):
        for times in ((0,1,1),(2,1,3)):
            samples=[(time,(float(i),0,0)) for i,time in enumerate(times)]
            with self.subTest(times=times),self.assertRaises(ValueError):
                judge_motion_samples(samples)

    def test_nan_or_unbounded_samples_rejected(self):
        with self.assertRaises(ValueError):
            judge_motion_samples([(0,(0,0,0)),(1,(float("nan"),0,0)),(2,(2,0,0))])
        with self.assertRaises(ValueError):
            judge_motion_samples([(0,(0,0,0)),(1,(1,0,0)),(2,(2,0,0))],max_samples=2)


if __name__=="__main__":
    unittest.main()
