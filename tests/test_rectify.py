"""Perspective-to-orthographic rectification tests."""

import unittest

from forge.rectify import homography, apply_homography, rectify_mask


class RectifyTests(unittest.TestCase):
    def test_identity_homography(self):
        src = [(0, 0), (10, 0), (10, 10), (0, 10)]
        dst = [(0, 0), (10, 0), (10, 10), (0, 10)]
        H = homography(src, dst)
        self.assertIsNotNone(H)
        for p in src:
            self.assertAlmostEqual(apply_homography(H, *p)[0], p[0], places=6)
            self.assertAlmostEqual(apply_homography(H, *p)[1], p[1], places=6)

    def test_scale_homography(self):
        src = [(0, 0), (10, 0), (10, 10), (0, 10)]
        dst = [(0, 0), (20, 0), (20, 20), (0, 20)]
        H = homography(src, dst)
        self.assertIsNotNone(H)
        pt = apply_homography(H, 5, 5)
        self.assertAlmostEqual(pt[0], 10, places=6)
        self.assertAlmostEqual(pt[1], 10, places=6)

    def test_rectify_identity_preserves_mask(self):
        mask = [[255 if (10 <= x < 20 and 10 <= y < 20) else 0
                 for x in range(30)] for y in range(30)]
        quad = [(10, 10), (20, 10), (20, 20), (10, 20)]
        out = rectify_mask(mask, (30, 30), (30, 30), quad, quad)
        # center should still be 255
        self.assertEqual(out[15][15], 255)
        self.assertEqual(out[0][0], 0)

    def test_degenerate_returns_none(self):
        # collinear points
        src = [(0, 0), (1, 0), (2, 0), (3, 0)]
        dst = [(0, 0), (1, 0), (2, 0), (3, 0)]
        H = homography(src, dst)
        self.assertIsNone(H)

    def test_wrong_count_raises(self):
        with self.assertRaises(ValueError):
            homography([(0, 0)], [(0, 0)])


if __name__ == "__main__":
    unittest.main()
