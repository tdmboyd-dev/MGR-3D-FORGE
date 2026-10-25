import unittest

from forge.geometry import create_neighborhood
from forge.glb import export_glb
from forge.obj import export_obj
from forge.spec import WorldSpec
from forge.asset_parity import audit_export_parity


class ExportParityTests(unittest.TestCase):
    def setUp(self):
        self.meshes, _ = create_neighborhood(WorldSpec(name="Witness", columns=3, rows=3, buildings=3, seed=8964))
        self.glb = export_glb(self.meshes)
        self.obj, self.mtl = export_obj(self.meshes)

    def test_matching_glb_and_obj_geometry(self):
        result = audit_export_parity(self.glb, self.obj)
        self.assertEqual(result["status"], "PASS")
        self.assertGreater(result["glb_triangles"], 0)

    def test_wrong_vertex_location_detected(self):
        lines = self.obj.splitlines()
        first = next(i for i, line in enumerate(lines) if line.startswith("v "))
        lines[first] = "v 9999 0 0"
        self.assertEqual(audit_export_parity(self.glb, "\n".join(lines))["status"], "FAIL")

    def test_missing_face_detected(self):
        lines = self.obj.splitlines()
        first = next(i for i, line in enumerate(lines) if line.startswith("f "))
        lines.pop(first)
        self.assertEqual(audit_export_parity(self.glb, "\n".join(lines))["status"], "FAIL")

    def test_rejects_bad_face_indices_and_nonfinite_vertices(self):
        for bad in (self.obj + "f 1//1 2//2 999999//9\n",
                    self.obj + "v nan 0 0\n"):
            with self.assertRaises(ValueError):
                audit_export_parity(self.glb, bad)

    def test_rejects_nonfinite_tolerance(self):
        with self.assertRaises(ValueError):
            audit_export_parity(self.glb, self.obj, tolerance_m=float("nan"))


if __name__ == "__main__":
    unittest.main()
