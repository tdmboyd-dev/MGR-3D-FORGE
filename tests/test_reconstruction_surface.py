"""Image-derived occupancy must become bounded, oriented, actual surfaces."""
from collections import Counter
import math
import unittest

from forge.marching import surface_nets
from forge.meshqa import analyze_mesh


def field(size, predicate):
    return [[[int(predicate(x, y, z)) for x in range(size)]
             for z in range(size)] for y in range(size)]


def signed_volume(mesh):
    total = 0.0
    for offset in range(0, len(mesh.indices), 3):
        a, b, c = [mesh.positions[index * 3:index * 3 + 3]
                   for index in mesh.indices[offset:offset + 3]]
        total += (a[0] * (b[1] * c[2] - b[2] * c[1]) +
                  a[1] * (b[2] * c[0] - b[0] * c[2]) +
                  a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return total


def sign_changes(occupancy):
    size = len(occupancy)
    def value(x, y, z):
        return occupancy[y][z][x] if all(0 <= i < size for i in (x, y, z)) else 0
    count = 0
    for y in range(size):
        for z in range(size):
            for x in range(-1, size):
                count += value(x, y, z) != value(x + 1, y, z)
    for x in range(size):
        for z in range(size):
            for y in range(-1, size):
                count += value(x, y, z) != value(x, y + 1, z)
    for x in range(size):
        for y in range(size):
            for z in range(-1, size):
                count += value(x, y, z) != value(x, y, z + 1)
    return count


class ReconstructionSurfaceTests(unittest.TestCase):
    def assert_closed_outward(self, mesh):
        self.assertTrue(analyze_mesh(mesh)['passed'])
        self.assertGreater(len(mesh.indices), 0)
        directed = Counter()
        for offset in range(0, len(mesh.indices), 3):
            a, b, c = mesh.indices[offset:offset + 3]
            for first, last in ((a, b), (b, c), (c, a)):
                directed[first, last] += 1
        self.assertTrue(all(count == 1 and directed[last, first] == 1
                            for (first, last), count in directed.items()))
        self.assertGreater(signed_volume(mesh), 0)
        for offset in range(0, len(mesh.normals), 3):
            self.assertAlmostEqual(math.sqrt(sum(v*v for v in mesh.normals[offset:offset + 3])), 1)

    def test_full_frame_subject_is_capped_at_all_capture_boundaries(self):
        occupancy = field(8, lambda x, y, z: True)
        mesh = surface_nets(occupancy, (2., 3., 4.), 8)
        self.assert_closed_outward(mesh)
        self.assertEqual(len(mesh.indices) // 3, sign_changes(occupancy) * 2)
        self.assertEqual([min(mesh.positions[i::3]) for i in range(3)], [-1., 0., -2.])
        self.assertEqual([max(mesh.positions[i::3]) for i in range(3)], [1., 3., 2.])

    def test_interior_measured_box_has_no_half_voxel_translation(self):
        occupancy = field(16, lambda x, y, z: 4 <= x < 12 and 4 <= y < 12 and 4 <= z < 12)
        mesh = surface_nets(occupancy, (2., 2., 2.), 16)
        self.assert_closed_outward(mesh)
        for observed, expected in zip([min(mesh.positions[i::3]) for i in range(3)], [-.5, .5, -.5]):
            self.assertAlmostEqual(observed, expected)
        for observed, expected in zip([max(mesh.positions[i::3]) for i in range(3)], [.5, 1.5, .5]):
            self.assertAlmostEqual(observed, expected)

    def test_only_true_sign_changing_grid_edges_emit_faces(self):
        occupancy = field(10, lambda x, y, z: (1 <= y < 9 and
            ((1 <= x < 9 and 1 <= z < 4) or (1 <= x < 4 and 1 <= z < 9))))
        mesh = surface_nets(occupancy, (2., 2., 2.), 10)
        self.assert_closed_outward(mesh)
        self.assertEqual(len(mesh.indices) // 3, sign_changes(occupancy) * 2)

    def test_voxel_center_translation_moves_the_mesh_exactly_one_step(self):
        first = field(12, lambda x, y, z: 2 <= x < 7 and 2 <= y < 7 and 2 <= z < 7)
        second = field(12, lambda x, y, z: 3 <= x < 8 and 2 <= y < 7 and 2 <= z < 7)
        a, b = (surface_nets(o, (3., 3., 3.), 12) for o in (first, second))
        self.assert_closed_outward(a)
        self.assert_closed_outward(b)
        self.assertAlmostEqual(min(b.positions[0::3]) - min(a.positions[0::3]), .25)
        self.assertAlmostEqual(signed_volume(a), signed_volume(b))

    def test_invalid_occupancy_bounds_and_budget_refuse_before_output(self):
        valid = field(4, lambda x, y, z: True)
        for occupancy, bounds, size in (([], (2., 2., 2.), 4),
                (valid, (2., 2., 2.), True), (valid, (2., float('nan'), 2.), 4),
                (valid, (2., 0., 2.), 4), (valid, (2., 2., 2.), 97),
                (field(4, lambda x,y,z:True)[:-1], (2., 2., 2.), 4)):
            with self.subTest(bounds=bounds, size=size), self.assertRaises(ValueError):
                surface_nets(occupancy, bounds, size)
        wrong = field(4, lambda x,y,z:True)
        wrong[0][0][0] = 2
        with self.assertRaises(ValueError):
            surface_nets(wrong, (2., 2., 2.), 4)
