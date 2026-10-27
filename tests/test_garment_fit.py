"""Garment fitting contract tests."""

import unittest

from forge.garment_fit import FitResult, fit_garment, garment_coverage


class GarmentFitTests(unittest.TestCase):
    def test_fit_moves_garment_outward(self):
        body = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        garment = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        result = fit_garment(garment, body, offset=0.01)
        self.assertIsInstance(result, FitResult)
        self.assertEqual(len(result.fitted_positions), 6)
        # garment should move away from body
        self.assertAlmostEqual(result.fitted_positions[1], 0.01, places=5)
        self.assertAlmostEqual(result.mean_offset, 0.01, places=5)

    def test_fit_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            fit_garment([1.0, 2.0], [0.0, 0.0, 0.0])  # not triple
        with self.assertRaises(ValueError):
            fit_garment([0.0, 0.0, 0.0], [])  # empty body
        with self.assertRaises(ValueError):
            fit_garment([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], offset=-1)
        with self.assertRaises(ValueError):
            fit_garment([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], max_offset=0)

    def test_coverage_report(self):
        body = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.5, 0.5, 0.0]
        garment = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        cov = garment_coverage(garment, body)
        self.assertIn("coverage_ratio", cov)
        self.assertGreater(cov["covered_body_vertices"], 0)
        self.assertIn("limitations", cov)

    def test_coverage_rejects_empty(self):
        with self.assertRaises(ValueError):
            garment_coverage([], [0.0, 0.0, 0.0])
        with self.assertRaises(ValueError):
            garment_coverage([0.0, 0.0, 0.0], [])


if __name__ == "__main__":
    unittest.main()
