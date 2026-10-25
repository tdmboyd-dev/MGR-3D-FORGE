import unittest

from forge.geometry import Mesh
from forge.surface_truth import inspect_surface_edges


class SurfaceTruthTests(unittest.TestCase):
    def test_closed_box_edge_candidate(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,3,4)
        result=inspect_surface_edges(mesh)
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["boundary_edges"],0)
        self.assertEqual(result["nonmanifold_edges"],0)
        self.assertEqual(result["triangles"],12)

    def test_hole_is_detected(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,3,4)
        mesh.indices=mesh.indices[:-3]
        result=inspect_surface_edges(mesh)
        self.assertEqual(result["status"],"FAIL")
        self.assertEqual(result["boundary_edges"],3)

    def test_duplicate_face_is_nonmanifold(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,3,4)
        mesh.indices.extend(mesh.indices[:3])
        result=inspect_surface_edges(mesh)
        self.assertEqual(result["status"],"FAIL")
        self.assertEqual(result["nonmanifold_edges"],3)

    def test_bad_index_rejected(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,3,4)
        mesh.indices[0]=99_000
        with self.assertRaises(ValueError):
            inspect_surface_edges(mesh)

    def test_triangle_budget_is_enforced(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,3,4)
        with self.assertRaises(ValueError):
            inspect_surface_edges(mesh,max_triangles=10)


if __name__=="__main__":
    unittest.main()
