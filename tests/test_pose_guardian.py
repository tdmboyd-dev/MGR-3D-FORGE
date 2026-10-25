import copy
import unittest

from forge.pose_guardian import REQUIRED_BONES, validate_pose_frames


def fixture():
    bones={name:{"head":[0.0,1.0,0.0],"tail":[0.2,1.0,0.0]} for name in REQUIRED_BONES}
    for side in ("left", "right"):
        bones[f"{side}_forearm"]={"head":[0.2,1.0,0.0],"tail":[0.4,1.0,0.0]}
        bones[f"{side}_hand"]={"head":[0.4,1.0,0.0],"tail":[0.5,1.0,0.0]}
    parts={"MGR_hand":{"vertices":8,"weighted_vertices":8,"armature_modifier":True}}
    frames=[{"frame":1,"bones":bones,"parts":parts},
            {"frame":12,"bones":copy.deepcopy(bones),"parts":copy.deepcopy(parts)}]
    # Shift the second frame's entire skeleton (rig translation preserves every joint).
    for bone in frames[1]["bones"].values():
        bone["head"][2] += .25
        bone["tail"][2] += .25
    return frames


class PoseGuardianTests(unittest.TestCase):
    def test_valid_connected_animation_passes(self):
        result=validate_pose_frames(fixture())
        self.assertEqual(result["status"],"PASS",result["errors"])
        self.assertAlmostEqual(result["maximum_hand_motion_m"],.25)

    def test_missing_hand_fails(self):
        frames=fixture()
        del frames[1]["bones"]["left_hand"]
        self.assertEqual(validate_pose_frames(frames)["status"],"FAIL")

    def test_joint_gap_fails(self):
        frames=fixture()
        frames[1]["bones"]["left_forearm"]["head"][0] += .2
        self.assertIn("disconnected joint", " ".join(validate_pose_frames(frames)["errors"]))

    def test_bone_stretch_fails(self):
        frames=fixture()
        frames[1]["bones"]["head"]["tail"][0] += .1
        self.assertIn("bone length changed", " ".join(validate_pose_frames(frames)["errors"]))

    def test_weightless_mesh_fails(self):
        frames=fixture()
        frames[0]["parts"]["MGR_hand"]["weighted_vertices"]=7
        self.assertIn("skin coverage", " ".join(validate_pose_frames(frames)["errors"]))

    def test_frozen_animation_fails(self):
        frames=fixture()
        frames[1]=copy.deepcopy(frames[0])
        frames[1]["frame"]=12
        self.assertIn("animation frozen", " ".join(validate_pose_frames(frames)["errors"]))

    def test_mixed_weight_sleeve_accepts_normalized_blend(self):
        frames=fixture()
        for frame in frames:
            frame["parts"]["MGR_left_elbow_sleeve"]={"vertices":8,"weighted_vertices":8,
                "armature_modifier":True,"dual_weight_vertices":8,"max_weight_sum_error":0.0}
        self.assertEqual(validate_pose_frames(frames)["status"],"PASS")

    def test_unblended_or_unnormalized_sleeve_fails(self):
        frames=fixture()
        for frame in frames:
            frame["parts"]["MGR_left_elbow_sleeve"]={"vertices":8,"weighted_vertices":8,
                "armature_modifier":True,"dual_weight_vertices":0,"max_weight_sum_error":0.0}
        self.assertIn("mixed bone weights"," ".join(validate_pose_frames(frames)["errors"]))
        for frame in frames:
            frame["parts"]["MGR_left_elbow_sleeve"]["dual_weight_vertices"]=8
            frame["parts"]["MGR_left_elbow_sleeve"]["max_weight_sum_error"]=.3
        self.assertIn("not normalized"," ".join(validate_pose_frames(frames)["errors"]))

    def test_invalid_numbers_fail_closed(self):
        frames=fixture()
        frames[0]["bones"]["left_hand"]["tail"][1]=float("nan")
        self.assertEqual(validate_pose_frames(frames)["status"],"FAIL")
        with self.assertRaises(ValueError):
            validate_pose_frames(frames,joint_tolerance_m=float("nan"))


if __name__=="__main__":
    unittest.main()
