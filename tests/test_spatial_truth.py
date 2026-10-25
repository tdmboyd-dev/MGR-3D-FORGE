"""Perspective ambiguity and printable-style mesh section evidence."""

import math
import json
from pathlib import Path
import tempfile
import unittest

from forge.geometry import Mesh
from forge.spatial_truth import camera_project,pixel_to_ray,slice_mesh_at_height,triangulate_parallel_views,triangulate_oriented_views
from forge.cli import main


class SpatialTruthTests(unittest.TestCase):
    def test_same_pixel_can_represent_multiple_depths(self):
        # This disproves treating a monocular pixel as proof of unique 3D.
        p=camera_project((1,2,4),focal_px=400)
        q=camera_project((3,6,12),focal_px=400)
        self.assertEqual(p,q)
        self.assertEqual(p,(100,200))

    def test_inverse_ray_aligns_with_source_direction_not_depth(self):
        ray=pixel_to_ray((100,200),focal_px=400)
        norm=math.sqrt(1**2+2**2+4**2)
        for found,want in zip(ray,(1/norm,2/norm,4/norm)):
            self.assertAlmostEqual(found,want)

    def test_projection_rejects_invalid_camera(self):
        for point,focal in [((0,0,0),100),((0,0,-1),100),((float("nan"),0,1),100),((0,0,1),0),((0,0,1),float("inf"))]:
            with self.subTest(point=point,focal=focal),self.assertRaises(ValueError):
                camera_project(point,focal_px=focal)

    def test_box_sections_change_with_height(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,4,2)
        middle=slice_mesh_at_height(mesh,height_m=2)
        self.assertEqual(len(middle),8)  # each side quad triangulated in two
        self.assertEqual(slice_mesh_at_height(mesh,height_m=5),[])
        self.assertTrue(all(all(abs(v)<=1 for pt in line for v in pt) for line in middle))

    def test_cross_sections_are_reproducible(self):
        mesh=Mesh()
        mesh.box(2,1,-3,2,4,2)
        a=slice_mesh_at_height(mesh,height_m=3)
        self.assertEqual(a,slice_mesh_at_height(mesh,height_m=3))
        self.assertTrue(a)

    def test_slicer_rejects_untrusted_geometry_or_budget(self):
        mesh=Mesh()
        mesh.box(0,0,0,2,2,2)
        with self.assertRaises(ValueError):
            slice_mesh_at_height(mesh,height_m=1,max_triangles=1)
        mesh.indices[0]=99_999
        with self.assertRaises(ValueError):
            slice_mesh_at_height(mesh,height_m=1)

    def test_spatial_proof_cli_persists_truth(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"proof.json"
            self.assertEqual(main(["spatial-proof","--out",str(path)]),0)
            data=json.loads(path.read_text())
            self.assertTrue(data["same_pixel_different_depth"])
            self.assertEqual(data["depths_m"],[4,12])
            self.assertEqual(len(data["cross_section_segments"]),8)
            self.assertEqual(data["surface_edge_audit"]["status"],"PASS")
            for actual,expected in zip(data["stereo_calibrated_example"]["point_m"],(0,1,4)):
                self.assertAlmostEqual(actual,expected,places=6)
            for actual,expected in zip(data["oriented_stereo_example"]["point_m"],(0,1,4)):
                self.assertAlmostEqual(actual,expected,places=6)
            with self.assertRaises(FileExistsError):
                main(["spatial-proof","--out",str(path)])

    def test_stereo_recovers_known_point_from_two_views(self):
        world=(0,1,4)
        first=(-1,0,0)
        second=(1,0,0)
        a=camera_project((world[0]-first[0],world[1],world[2]),focal_px=400)
        b=camera_project((world[0]-second[0],world[1],world[2]),focal_px=400)
        result=triangulate_parallel_views(a,b,camera_a=first,camera_b=second,focal_px=400)
        for got,want in zip(result["point_m"],world):
            self.assertAlmostEqual(got,want,places=6)
        self.assertEqual(result["baseline_m"],2)
        self.assertLess(result["ray_separation_m"],.000001)

    def test_stereo_rejects_zero_parallax(self):
        with self.assertRaises(ValueError):
            triangulate_parallel_views((100,0),(100,0),camera_a=(0,0,0),camera_b=(1,0,0),focal_px=400)

    def test_stereo_rejects_mismatched_correspondences(self):
        with self.assertRaises(ValueError):
            triangulate_parallel_views((100,0),(-100,100),camera_a=(-1,0,0),camera_b=(1,0,0),focal_px=400)

    def test_stereo_rejects_backwards_point(self):
        with self.assertRaises(ValueError):
            triangulate_parallel_views((-100,0),(100,0),camera_a=(-1,0,0),camera_b=(1,0,0),focal_px=400)

    def test_rotated_camera_recovers_point_not_parallel(self):
        identity=((1,0,0),(0,1,0),(0,0,1))
        rotated=((0,0,1),(0,1,0),(-1,0,0))
        result=triangulate_oriented_views((100,100),(0,200),camera_a=(-1,0,0),
                                          camera_b=(-2,0,4),rotation_a=identity,
                                          rotation_b=rotated,focal_px=400)
        for actual,want in zip(result["point_m"],(0,1,4)):
            self.assertAlmostEqual(actual,want,places=6)
        self.assertEqual(result["reprojection_errors_px"],[0,0])

    def test_rotated_camera_rejects_reflection_and_scale(self):
        identity=((1,0,0),(0,1,0),(0,0,1))
        for invalid in (((-1,0,0),(0,1,0),(0,0,1)),
                        ((2,0,0),(0,1,0),(0,0,1))):
            with self.subTest(rotation=invalid),self.assertRaises(ValueError):
                triangulate_oriented_views((100,100),(0,200),camera_a=(-1,0,0),
                    camera_b=(-2,0,4),rotation_a=identity,rotation_b=invalid,focal_px=400)


if __name__=="__main__":
    unittest.main()
