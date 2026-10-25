import unittest

from forge.dynamics import first_motion_contact


class MotionContactTests(unittest.TestCase):
    def setUp(self):
        self.boxes = [{"id": "wall", "bounds": [2, -1, 2.2, 1]}]

    def test_continuous_sweep_catches_thin_wall_without_sampling(self):
        result = first_motion_contact((0, 0), (10, 0), 0.3, self.boxes)
        self.assertEqual(result["status"], "CONTACT")
        self.assertEqual(result["hit"]["position_xz"], [1.7, 0])
        self.assertEqual(result["hit"]["approx_normal_xz"], [-1, 0])

    def test_parallel_segment_clear(self):
        self.assertEqual(first_motion_contact((0, 3), (10, 3), 0.3, self.boxes)["status"], "CLEAR")

    def test_start_inside_reports_immediate_contact(self):
        result = first_motion_contact((2.1, 0), (8, 0), 0.1, self.boxes)
        self.assertEqual(result["hit"]["fraction"], 0)

    def test_earliest_collision_wins_order_independently(self):
        earlier = {"id": "closer", "bounds": [1, -1, 1.1, 1]}
        a = first_motion_contact((0, 0), (10, 0), 0, [*self.boxes, earlier])
        b = first_motion_contact((0, 0), (10, 0), 0, [earlier, *self.boxes])
        self.assertEqual(a, b)
        self.assertEqual(a["hit"]["obstacle_id"], "closer")

    def test_invalid_bounds_and_nonfinite_rejected(self):
        for obs in ([{"id": "bad", "bounds": [2, 0, 1, 1]}],
                    [{"id": "bad", "bounds": [float("nan"), 0, 1, 1]}]):
            with self.assertRaises(ValueError):
                first_motion_contact((0, 0), (1, 1), 0.1, obs)
        with self.assertRaises(ValueError):
            first_motion_contact((0, 0), (float("inf"), 1), 0.1, self.boxes)


if __name__ == "__main__":
    unittest.main()
