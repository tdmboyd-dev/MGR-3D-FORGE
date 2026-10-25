from pathlib import Path
import tempfile
import unittest

from forge.view_identity import AssetView, compare_asset_views, compare_view_silhouettes
from tests.test_visualqa import png_bytes


def canvas(coords, *, width=18, height=18):
    return [[(255,255,255) if (x,y) in coords else (0,0,0)
             for x in range(width)] for y in range(height)]


class ViewIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def write(self,name,coords):
        path=self.root/name
        path.write_bytes(png_bytes(canvas(coords)))
        return path

    def test_same_approved_asset_across_pose_and_camera(self):
        asset="a"*64
        old=AssetView("character-1",asset,"b"*64,"T","front")
        new=AssetView("character-1",asset,"b"*64,"walk","side")
        report=compare_asset_views(old,new)
        self.assertEqual(report["verdict"],"SAME_VERIFIED_SOURCE_ASSET")
        self.assertTrue(report["different_pose"])
        self.assertTrue(report["different_camera"])

    def test_same_name_different_source_is_not_proof_of_character_difference(self):
        a=AssetView("character-1","a"*64,None)
        b=AssetView("character-1","b"*64,None)
        self.assertEqual(compare_asset_views(a,b)["verdict"],"DIFFERENT_SOURCE_ARTIFACTS")
        self.assertEqual(compare_asset_views(a,AssetView("character-1",None,None))["verdict"],
                         "IDENTITY_UNDETERMINED")

    def test_translated_same_shape_appearance_consistent(self):
        shape={(1,1),(2,1),(3,1),(1,2),(1,3)}
        shifted={(x+8,y+7) for x,y in shape}
        report=compare_view_silhouettes(self.write("original.png",shape),
                                        self.write("shifted.png",shifted))
        self.assertEqual(report["verdict"],"APPEARANCE_CONSISTENT")
        self.assertFalse(report["identity_proven"])

    def test_image_plane_rotation_is_not_asset_identity_proof(self):
        shape={(1,1),(2,1),(3,1),(1,2),(1,3)}
        turned={(5-y,x+5) for x,y in shape}
        report=compare_view_silhouettes(self.write("first.png",shape),
                                        self.write("rotated.png",turned))
        self.assertEqual(report["verdict"],"APPEARANCE_CONSISTENT")
        self.assertFalse(report["identity_proven"])

    def test_different_silhouette_or_blank_does_not_claim_identity(self):
        a=self.write("a.png",{(1,1),(1,2),(1,3),(1,4)})
        b=self.write("b.png",{(1,1),(2,1),(3,1),(4,1),(2,2),(3,2)})
        report=compare_view_silhouettes(a,b)
        self.assertFalse(report["identity_proven"])
        blank=self.write("blank.png",set())
        self.assertEqual(compare_view_silhouettes(a,blank)["verdict"],"INSUFFICIENT_FOREGROUND")


if __name__=="__main__":
    unittest.main()
