"""Actual native appendage geometry, winding, rig alignment and morph checks."""
from collections import Counter
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from forge.geometry import Mesh
from forge.imagination import (_append_tapered_tube, creature_meshes,
                               create_original_creature, genome_candidates)
from forge.creature_rig_recipe import creature_bones, creature_leg_landmarks
from forge.meshqa import analyze_mesh
from forge.morph_engine import morph_point
from forge.smooth import smooth_normals


class CreatureAppendageTests(unittest.TestCase):
    def test_tube_has_closed_oriented_surface_and_smaller_tip(self):
        mesh=Mesh()
        _append_tapered_tube(mesh,((0,0,0),(2,0,0)),(.4,.1))
        self.assertTrue(analyze_mesh(mesh)["passed"])
        points=[tuple(round(v,9) for v in mesh.positions[i:i+3])
                for i in range(0,len(mesh.positions),3)]
        directed=Counter()
        edges=Counter()
        for offset in range(0,len(mesh.indices),3):
            a,b,c=(points[index] for index in mesh.indices[offset:offset+3])
            for first,last in ((a,b),(b,c),(c,a)):
                directed[first,last]+=1
                edges[tuple(sorted((first,last)))]+=1
        self.assertTrue(all(value==2 for value in edges.values()))
        self.assertTrue(all(directed[b,a]==value for (a,b),value in directed.items()))
        for x,radius in ((0,.4),(2,.1)):
            ring=[p for p in set(points) if p[0]==x and math.hypot(p[1],p[2])>0]
            self.assertEqual(len(ring),12)
            for p in ring:self.assertAlmostEqual(math.hypot(p[1],p[2]),radius,places=8)
        # Signed volume verifies outward winding, not merely paired edges.
        volume=0
        for offset in range(0,len(mesh.indices),3):
            a,b,c=(points[index] for index in mesh.indices[offset:offset+3])
            volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+
                     a[1]*(b[2]*c[0]-b[0]*c[2])+
                     a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        self.assertGreater(volume,0)

    def test_collapsed_nonfinite_unbounded_and_invalid_radius_refuse_before_mutation(self):
        for points,radii,steps in (
                (((0,0,0),(0,0,0)),(.1,.1),12),
                (((0,0,0),(1,0,0)),(.1,0),12),
                (((0,0,0),(math.inf,0,0)),(.1,.1),12),
                (((0,0,0),(1,0,0)),(.1,.1),100),
                (((0,0,0),(1,0,0),(0,0,0)),(.1,.1,.1),12)):
            mesh=Mesh()
            with self.subTest(points=points,radii=radii,steps=steps),self.assertRaises(ValueError):
                _append_tapered_tube(mesh,points,radii,steps=steps)
            self.assertEqual(mesh.positions,[])

    def test_two_segment_leg_mesh_uses_exact_rig_joint_and_common_morph(self):
        genome=genome_candidates("a horned winged forest creature",21,1)[0]
        calls=[]
        def capture(mesh,points,radii,**kwargs):
            calls.append(tuple(points))
            return _append_tapered_tube(mesh,points,radii,**kwargs)
        with patch("forge.imagination._append_tapered_tube",side_effect=capture):
            meshes=creature_meshes(genome)
        extent=max(y for mesh in meshes for y in mesh.positions[1::3])
        morph={"bend_degrees":21,"twist_degrees":-16,"height":1.3,"width":.8}
        bones=creature_bones(genome,morph=morph,axis_extent=extent)["skeleton"]
        for index,landmarks in enumerate(creature_leg_landmarks(genome)):
            self.assertEqual(calls[index],landmarks)
            upper=next(b for b in bones if b["name"]==f"leg_{index+1:02}_upper")
            lower=next(b for b in bones if b["name"]==f"leg_{index+1:02}_lower")
            actual=[upper["head"],upper["tail"],lower["tail"]]
            expected=[list(morph_point(p,morph,axis_extent=extent)) for p in calls[index]]
            self.assertEqual(actual,expected)
            self.assertEqual(upper["tail"],lower["head"])

    def test_smooth_surface_preserves_triangle_geometry_and_wings_keep_opposite_faces(self):
        mesh=Mesh()
        _append_tapered_tube(mesh,((0,0,0),(1,.2,0),(2,0,0)),(.3,.2,.1))
        smooth=smooth_normals(mesh)
        self.assertLess(len(smooth.positions),len(mesh.positions))
        self.assertEqual(len(smooth.indices),len(mesh.indices))
        def triangles(source):
            return [tuple(source.positions[i*3:i*3+3]) for i in source.indices]
        self.assertEqual(triangles(mesh),triangles(smooth))
        self.assertTrue(analyze_mesh(smooth)["passed"])
        for i in range(0,len(smooth.normals),3):
            self.assertAlmostEqual(math.sqrt(sum(n*n for n in smooth.normals[i:i+3])),1)
        with TemporaryDirectory() as temp:
            result=create_original_creature("a winged horned creature with a long tail",
                                             Path(temp)/"creature",variants=1,
                                             morph={"bend_degrees":20,"twist_degrees":15})
            self.assertGreater(result["glb_quality"]["triangles"],1000)
            self.assertFalse(result["rigged"])
            self.assertFalse(result["independently_blender_verified"])

    def test_tailless_and_bounded_eye_counts_materialize_exact_requested_parts(self):
        base=genome_candidates("a forest creature",7,1)[0]
        with_tail=creature_meshes(base)
        tailless={**base,"tail_length":0,"eye_count":0}
        without_tail=creature_meshes(tailless)
        self.assertLess(len(without_tail[0].indices),len(with_tail[0].indices))
        self.assertFalse(without_tail[3].indices)
        self.assertFalse(any(b["role"]=="tail" for b in creature_bones(tailless)["skeleton"]))
        one=creature_meshes({**tailless,"eye_count":1})[3]
        for count in (2,3,8):
            eye_mesh=creature_meshes({**tailless,"eye_count":count})[3]
            self.assertEqual(len(eye_mesh.indices),len(one.indices)*count)
            self.assertTrue(analyze_mesh(eye_mesh)["passed"])
        with self.assertRaises(ValueError):creature_meshes({**base,"eye_count":9})

    def test_tailless_wingless_rig_has_real_existing_leg_or_head_animation_target(self):
        base=genome_candidates("a forest creature",7,1)[0]
        for legs,expected in ((4,["leg_01_upper","leg_02_upper"]),(0,["head"])):
            recipe=creature_bones({**base,"tail_length":0,"wing_pairs":0,"legs":legs})
            self.assertEqual(recipe["preview_animation_bones"],expected)
            actual_names={bone["name"] for bone in recipe["skeleton"]}
            self.assertTrue(set(recipe["preview_animation_bones"])<=actual_names)

    def test_shared_limb_root_is_inside_actual_original_torso_surface(self):
        for prompt in ("a winged forest beast","a giant spider creature","a biped forest creature"):
            for genome in genome_candidates(prompt,19,5):
                length,width,bodyh,high=(genome[key] for key in
                        ("body_length","body_width","body_height","standing_height"))
                cy=high+bodyh*.4
                for root,_,_ in creature_leg_landmarks(genome):
                    ellipsoid=(root[0]/(length*.54))**2+((root[1]-cy)/bodyh)**2+(root[2]/width)**2
                    self.assertLess(ellipsoid,1,"limb attachment must intersect authored torso")


if __name__=="__main__":unittest.main()
