import json
import struct
import tempfile
import unittest
from pathlib import Path

from forge.cli import build
from forge.geometry import create_neighborhood
from forge.geometry import Mesh
from forge.glb import export_glb, inspect_glb
from forge.quality import validate_character_landmarks, validate_neighborhood
from forge.spec import WorldSpec
from forge.planner import plan_neighborhood
from forge.assets import AssetRegistry
from forge.quality import compare_character_identity
from forge.workflow import LocalJobStore, Step, approve_plan, resolve_plan
from forge.world import graph_for_world, shortest_road_path, overlaps_building
from forge.obj import export_obj
from forge.preview import render_world_svg
from forge.streaming import chunk_world, simple_building_lod, lod_for_distance
from forge.cinematic import camera_tour, interpolate_shots
from forge.recipes import ModelRecipe, inspect_recipe
from forge.meshqa import analyze_mesh, remove_bad_triangles
from forge.perception import scene_overview
from forge.interiors import generate_interiors
from forge.character import mannequin, build_mannequin, CHARACTER_MATERIALS
from forge.animation import arm_pose_clip, pose_landmarks
from forge.adapters import (AdapterCapabilities, ProceduralWorldAdapter,
                            UnavailableNeuralAdapter, select_adapter)
from forge.blender_bridge import blender_command, verify_blender, blender_render_command
from forge.benchmark import run_benchmark
from forge.environment import generate_parks, ENVIRONMENT_MATERIALS
from forge.receipt import verify_bundle


class ForgeTests(unittest.TestCase):
    def test_spec_rejects_excess_count(self):
        with self.assertRaises(ValueError):
            WorldSpec(rows=2, columns=2, buildings=5)

    def test_spec_rejects_extra_json_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text('{"rows": 4, "evil": true}')
            with self.assertRaises(ValueError):
                WorldSpec.from_json(path)

    def test_seed_deterministic(self):
        spec = WorldSpec()
        meshes1, world1 = create_neighborhood(spec)
        meshes2, world2 = create_neighborhood(spec)
        self.assertEqual(world1, world2)
        self.assertEqual(export_glb(meshes1), export_glb(meshes2))

    def test_new_seed_changes_geometry(self):
        first = create_neighborhood(WorldSpec(seed=8964))[1]
        second = create_neighborhood(WorldSpec(seed=8965))[1]
        self.assertNotEqual(first["buildings"], second["buildings"])

    def test_world_qa(self):
        _, scene = create_neighborhood(WorldSpec())
        self.assertTrue(validate_neighborhood(scene)["passed"])
        self.assertEqual(len(scene["buildings"]), 10)

    def test_large_world_no_missing_lots(self):
        _, scene = create_neighborhood(WorldSpec(columns=40, rows=25, buildings=1000))
        self.assertTrue(validate_neighborhood(scene)["passed"])
        self.assertEqual(len({tuple(b["lot"]) for b in scene["buildings"]}), 1000)

    def test_glb_export_roundtrip(self):
        meshes, scene = create_neighborhood(WorldSpec())
        result = inspect_glb(export_glb(meshes))
        self.assertTrue(result["valid"])
        self.assertEqual(result["triangles"], scene["triangle_count"])
        self.assertEqual(result["vertices"], scene["vertex_count"])

    def test_glb_rejects_corrupt_index(self):
        meshes, _ = create_neighborhood(WorldSpec())
        data = bytearray(export_glb(meshes))
        data[0:4] = b"BADD"
        with self.assertRaises(ValueError):
            inspect_glb(data)

    def test_glb_rejects_short_chunk(self):
        meshes, _ = create_neighborhood(WorldSpec())
        data = export_glb(meshes)[:-4]
        with self.assertRaises(ValueError):
            inspect_glb(data)

    def test_box_face_normals_point_outward(self):
        mesh = Mesh()
        mesh.box(0, 0, 0, 2, 3, 4)
        centers = []
        for index in range(0, len(mesh.positions), 12):
            x = sum(mesh.positions[index + j] for j in (0,3,6,9)) / 4
            y = sum(mesh.positions[index + j] for j in (1,4,7,10)) / 4
            z = sum(mesh.positions[index + j] for j in (2,5,8,11)) / 4
            centers.append((x, y - 1.5, z))
        for i, vector in enumerate(centers):
            normal = mesh.normals[i * 12:i * 12 + 3]
            self.assertGreater(sum(a * b for a, b in zip(normal, vector)), 0)

    def test_build_manifest_and_file(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = build(WorldSpec(), Path(temp))
            self.assertTrue((Path(temp) / "world.glb").is_file())
            self.assertTrue((Path(temp) / "world.obj").is_file())
            self.assertTrue((Path(temp) / "world.mtl").is_file())
            self.assertTrue((Path(temp) / "navigation.json").is_file())
            self.assertTrue((Path(temp) / "preview.svg").is_file())
            self.assertTrue((Path(temp) / "world_lod1.glb").is_file())
            self.assertTrue((Path(temp) / "chunks.json").is_file())
            self.assertTrue((Path(temp) / "camera_tour.json").is_file())
            self.assertTrue((Path(temp) / "spatial_overview.json").is_file())
            self.assertTrue((Path(temp) / "interiors.glb").is_file())
            self.assertTrue((Path(temp) / "interiors.json").is_file())
            self.assertTrue((Path(temp) / "parks.glb").is_file())
            self.assertTrue((Path(temp) / "parks.json").is_file())
            self.assertEqual(manifest["execution"]["external_api_calls"], 0)
            self.assertFalse(manifest["execution"]["blender_verified"])
            saved = json.loads((Path(temp) / "manifest.json").read_text())
            self.assertEqual(saved["artifact"], manifest["artifact"])
            self.assertTrue(verify_bundle(Path(temp))["passed"])

    def test_world_bundle_detects_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            build(WorldSpec(),Path(temp))
            (Path(temp)/"parks.json").write_text("tampered")
            with self.assertRaises(ValueError):
                verify_bundle(Path(temp))

    def test_obj_has_same_triangle_count_as_glb(self):
        meshes, world = create_neighborhood(WorldSpec())
        obj, material = export_obj(meshes)
        self.assertEqual(sum(line.startswith("f ") for line in obj.splitlines()),
                         world["triangle_count"])
        self.assertEqual(sum(line.startswith("newmtl ") for line in material.splitlines()), 6)

    def test_obj_refuses_unsafe_mtl_path(self):
        with self.assertRaises(ValueError):
            export_obj([], mtl_name="../private.mtl")

    def test_svg_preview_is_deterministic_and_safe(self):
        _, world = create_neighborhood(WorldSpec())
        a = render_world_svg(world)
        self.assertEqual(a, render_world_svg(world))
        self.assertEqual(a.count('<polygon '), 1 + len(world["roads"]) + len(world["buildings"]) * 3)
        self.assertIn('not a GLB render', a)

    def test_svg_preview_rejects_oversize(self):
        _, world = create_neighborhood(WorldSpec())
        with self.assertRaises(ValueError):
            render_world_svg(world, width=100000)

    def test_chunks_cover_every_building_once(self):
        _, world = create_neighborhood(WorldSpec(rows=13, columns=9, buildings=91))
        data = chunk_world(world, chunk_lots=4)
        listed = [bid for chunk in data["chunks"] for bid in chunk["building_ids"]]
        self.assertEqual(sorted(listed), sorted(b["id"] for b in world["buildings"]))
        self.assertEqual(len(listed), len(set(listed)))

    def test_simple_lod_reduces_triangle_count(self):
        _, world = create_neighborhood(WorldSpec())
        lod = inspect_glb(export_glb(simple_building_lod(world)))
        self.assertEqual(lod["triangles"], len(world["buildings"]) * 12)
        self.assertLess(lod["triangles"], world["triangle_count"])

    def test_lod_distance_boundaries(self):
        self.assertEqual([lod_for_distance(x) for x in (0,79,80,249,250)], [0,0,1,1,2])
        with self.assertRaises(ValueError):
            lod_for_distance(float("nan"))

    def test_spec_rejects_nonfinite_ground(self):
        with self.assertRaises(ValueError):
            WorldSpec(lot_size=float("inf"))

    def test_camera_tour_is_actual_3d_not_video(self):
        _, world = create_neighborhood(WorldSpec())
        tour = camera_tour(world)
        self.assertEqual(len(tour["shots"]), 10)
        self.assertFalse(tour["requires_generated_video"])
        self.assertEqual(len({shot["subject_id"] for shot in tour["shots"]}), 10)
        self.assertEqual(tour, camera_tour(world))

    def test_camera_interpolation_and_boundaries(self):
        _, world = create_neighborhood(WorldSpec())
        shots = camera_tour(world)["shots"]
        halfway = interpolate_shots(shots[0], shots[1], 0.5)
        self.assertEqual(halfway["camera"][0],
                         round((shots[0]["camera"][0]+shots[1]["camera"][0])/2, 6))
        with self.assertRaises(ValueError):
            interpolate_shots(shots[0], shots[1], 1.5)

    def test_model_recipe_fails_closed_on_license_and_gpu(self):
        recipe = ModelRecipe(id="candidate", package_id="model-xyz", version="1.0",
                             sha256="a"*64, license_id="restricted", runtime="python",
                             requires_gpu=True, estimated_vram_gb=24,
                             source_url="https://example.org/model")
        result = inspect_recipe(recipe, available_vram_gb=0)
        self.assertFalse(result["ready"])
        self.assertIn("license not approved", result["reasons"])
        self.assertIn("insufficient GPU VRAM", result["reasons"])
        self.assertFalse(result["execute"])

    def test_model_recipe_rejects_unpinned_hash(self):
        with self.assertRaises(ValueError):
            ModelRecipe(id="bad", package_id="p", version="1", sha256="unverified",
                        license_id="MGR-native", runtime="python", requires_gpu=False,
                        estimated_vram_gb=0, source_url="https://example.org/model")

    def test_world_meshes_have_nonzero_triangles(self):
        meshes, _ = create_neighborhood(WorldSpec())
        self.assertTrue(all(analyze_mesh(mesh)["passed"] for mesh in meshes))

    def test_mesh_repair_drops_degenerate_and_invalid_indices(self):
        mesh = Mesh()
        mesh.box(0, 0, 0, 1, 1, 1)
        mesh.indices.extend([0,0,0, 0,1,9999])
        self.assertFalse(analyze_mesh(mesh)["passed"])
        cleaned, receipt = remove_bad_triangles(mesh)
        self.assertEqual(receipt["removed_triangles"], 2)
        self.assertEqual(receipt["remaining_triangles"], 12)
        self.assertTrue(analyze_mesh(cleaned)["passed"])

    def test_mesh_repair_rejects_nonfinite_vertices(self):
        mesh = Mesh(positions=[float("nan"),0,0], normals=[0,1,0], indices=[])
        with self.assertRaises(ValueError):
            remove_bad_triangles(mesh)

    def test_spatial_overview_evidence_labels(self):
        _, world = create_neighborhood(WorldSpec())
        result = scene_overview(world, camera=(0,100,0))
        self.assertEqual(len(result["observations"]), len(world["buildings"]))
        self.assertTrue(all(o["evidence"] == "generated-scene-geometry"
                            and o["real_world_verified"] is False for o in result["observations"]))
        self.assertEqual(result, scene_overview(world, camera=(0,100,0)))

    def test_spatial_overview_detects_occlusion(self):
        _, world = create_neighborhood(WorldSpec(rows=2, columns=2, buildings=4))
        left = {"id":"near", "center":[0,0,0], "size":[4,10,4], "lot":[0,0]}
        right = {"id":"far", "center":[0,0,12], "size":[4,10,4], "lot":[0,1]}
        world["buildings"] = [left,right]
        result = scene_overview(world, camera=(0,3,-10))
        far = next(o for o in result["observations"] if o["id"] == "far")
        self.assertFalse(far["visible_center"])
        self.assertEqual(far["occluded_by"], ["near"])

    def test_spatial_overview_rejects_nonfinite_camera(self):
        _, world = create_neighborhood(WorldSpec())
        with self.assertRaises(ValueError):
            scene_overview(world, camera=(float("inf"), 1, 1))

    def test_interior_mesh_and_provenance(self):
        _, world = create_neighborhood(WorldSpec())
        meshes, plan = generate_interiors(world)
        self.assertEqual(len(plan["room_sets"]), 10)
        self.assertEqual(sum(item["count"] for item in plan["room_sets"]), 20)
        self.assertTrue(all(not item["reference_observed"] and not item["owner_approved"]
                            for item in plan["room_sets"]))
        self.assertTrue(all(analyze_mesh(mesh)["passed"] for mesh in meshes))
        self.assertTrue(inspect_glb(export_glb(meshes))["valid"])

    def test_interior_geometry_deterministic(self):
        _, world = create_neighborhood(WorldSpec())
        first, plan1 = generate_interiors(world)
        second, plan2 = generate_interiors(world)
        self.assertEqual(export_glb(first), export_glb(second))
        self.assertEqual(plan1,plan2)

    def test_beam_geometry_faces_and_export(self):
        beam=Mesh()
        beam.beam((0,0,0),(1,1,0),0.2)
        self.assertEqual(len(beam.indices)//3,12)
        self.assertTrue(analyze_mesh(beam)["passed"])
        for idx in range(0,len(beam.positions),12):
            center=[sum(beam.positions[idx+j*3+axis] for j in range(4))/4
                    for axis in range(3)]
            outward=[center[0]-0.5,center[1]-0.5,center[2]]
            normal=beam.normals[idx:idx+3]
            self.assertGreater(sum(a*b for a,b in zip(outward,normal)),0)
        with self.assertRaises(ValueError):
            Mesh().beam((0,0,0),(0,0,0),0.2)

    def test_generic_character_both_poses_have_complete_hands(self):
        for pose in ("T","A"):
            parts,landmarks,quality=mannequin(pose)
            self.assertTrue(quality["passed"])
            self.assertIn("left_hand",parts)
            self.assertIn("right_hand",parts)
            self.assertLess(landmarks["left_hand"][0],-0.8)
            self.assertGreater(landmarks["right_hand"][0],0.8)
            self.assertTrue(all(analyze_mesh(mesh)["passed"] for _,mesh in parts.values()))

    def test_character_exports_detachable_components(self):
        with tempfile.TemporaryDirectory() as temp:
            result=build_mannequin(Path(temp),"T")
            self.assertFalse(result["tevin_identity_verified"])
            self.assertEqual(len(list((Path(temp)/"parts").glob("*.glb"))),
                             len(result["editable_parts"]))
            self.assertTrue(inspect_glb((Path(temp)/"mannequin.glb").read_bytes())["valid"])
            for path in (Path(temp)/"parts").glob("*.glb"):
                self.assertTrue(inspect_glb(path.read_bytes())["valid"])

    def test_material_export_validates_mesh_count(self):
        with self.assertRaises(ValueError):
            export_glb([Mesh()],materials=CHARACTER_MATERIALS)

    def test_pose_track_preserves_anatomy(self):
        clip=arm_pose_clip(samples=15)
        self.assertEqual(len(clip["frames"]),15)
        base=clip["frames"][0]["landmarks"]
        for frame in clip["frames"]:
            self.assertTrue(compare_character_identity(base,frame["landmarks"],tolerance=0.001)["passed"])
        self.assertFalse(clip["skinned_animation_exported"])

    def test_a_pose_matches_procedural_character(self):
        _,expected,_=mannequin("A")
        self.assertEqual(expected,pose_landmarks(1))
        with self.assertRaises(ValueError):
            pose_landmarks(1.5)

    def test_adapter_selects_free_native_world(self):
        chosen=select_adapter("world-massing",[UnavailableNeuralAdapter(),ProceduralWorldAdapter()])
        self.assertEqual(chosen.capabilities.name,"mgr-cpu-world")
        with tempfile.TemporaryDirectory() as temp:
            result=chosen.run(WorldSpec(),Path(temp))
            self.assertTrue(result["quality"]["passed"])

    def test_adapter_refuses_unavailable_neural(self):
        with self.assertRaises(LookupError):
            select_adapter("image-to-mesh",[UnavailableNeuralAdapter()])

    def test_adapter_remote_requires_explicit_budget_and_approval(self):
        class TestRemote:
            capabilities=AdapterCapabilities("remote-sim",("image-to-mesh",),True,0.5,False,True)
            def run(self, spec, output):
                raise RuntimeError("test adapter intentionally not executable")
        with self.assertRaises(LookupError):
            select_adapter("image-to-mesh",[TestRemote()],allow_network=True,budget_usd=1)
        chosen=select_adapter("image-to-mesh",[TestRemote()],allow_network=True,
                              budget_usd=1,approved_step_ids=["remote-sim"])
        self.assertEqual(chosen.capabilities.name,"remote-sim")

    def test_blender_bridge_has_explicit_proof_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/"real.glb"
            meshes,_=create_neighborhood(WorldSpec())
            source.write_bytes(export_glb(meshes))
            command=blender_command("blender",source,Path(temp)/"report.json")
            self.assertIn("--background",command)
            self.assertIn("--python",command)
            with self.assertRaises(RuntimeError):
                verify_blender(source,Path(temp)/"report.json",blender_binary="nonexistent-blender-mgr-test")
            render=blender_render_command("blender",source,Path(temp)/"preview.png",Path(temp)/"preview.json")
            self.assertIn("blender_render.py",render[4])

    def test_character_missing_hand(self):
        landmarks = {name: [0, i, 0] for i, name in enumerate((
            "head", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hand", "right_hand", "left_hip",
            "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"))}
        del landmarks["right_hand"]
        result = validate_character_landmarks(landmarks)
        self.assertFalse(result["passed"])
        self.assertIn("missing or invalid right_hand", result["errors"])

    def test_bounded_prompt_planner(self):
        plan = plan_neighborhood("Build 37 houses in a futuristic neighborhood")
        self.assertEqual(plan.spec.buildings, 37)
        self.assertEqual(plan.external_cost_usd, 0)
        self.assertEqual(plan.method, "cpu-procedural")

    def test_planner_refuses_unbounded_request(self):
        with self.assertRaises(ValueError):
            plan_neighborhood("1001 buildings")

    def test_asset_registry_deduplicates_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            store = AssetRegistry(Path(temp))
            first = store.add(b"mesh-contents", owner="MGR", license_id="MGR-native")
            second = store.add(b"mesh-contents", owner="MGR", license_id="MGR-native")
            self.assertEqual(first, second)
            contents, _ = store.get(first["sha256"])
            self.assertEqual(contents, b"mesh-contents")
            (Path(temp) / first["relative_path"]).write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                store.get(first["sha256"])

    def test_asset_provenance_required(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                AssetRegistry(Path(temp)).add(b"asset", owner="", license_id="MIT")

    def test_character_identity_proportion_drift(self):
        points = {
            "head": [0, 2.1, 0],
            "left_shoulder": [-0.5, 1.8, 0], "right_shoulder": [0.5, 1.8, 0],
            "left_elbow": [-0.9, 1.35, 0], "right_elbow": [0.9, 1.35, 0],
            "left_wrist": [-1.1, 0.9, 0], "right_wrist": [1.1, 0.9, 0],
            "left_hand": [-1.2, 0.8, 0], "right_hand": [1.2, 0.8, 0],
            "left_hip": [-0.3, 1.0, 0], "right_hip": [0.3, 1.0, 0],
            "left_knee": [-0.3, 0.55, 0], "right_knee": [0.3, 0.55, 0],
            "left_ankle": [-0.3, 0.1, 0], "right_ankle": [0.3, 0.1, 0],
        }
        self.assertTrue(compare_character_identity(points, points)["passed"])
        changed = {k: list(v) for k, v in points.items()}
        changed["left_wrist"][0] += 3
        self.assertFalse(compare_character_identity(points, changed)["passed"])

    def test_workflow_dependency_order(self):
        plan = resolve_plan([Step("export", "glb", ("geometry",)),
                             Step("geometry", "cpu")])
        self.assertEqual([step.id for step in plan], ["geometry", "export"])

    def test_workflow_rejects_cycles(self):
        with self.assertRaises(ValueError):
            resolve_plan([Step("a", "x", ("b",)), Step("b", "x", ("a",))])

    def test_workflow_rejects_missing_dependencies(self):
        with self.assertRaises(ValueError):
            resolve_plan([Step("a", "x", ("missing",))])

    def test_free_local_plan_auto_allowed(self):
        result = approve_plan([Step("cpu", "procedural")])
        self.assertTrue(result["allowed"])
        self.assertEqual(result["estimated_usd"], 0)

    def test_paid_plan_needs_budget_and_explicit_approval(self):
        steps = [Step("neural", "remote", estimated_usd=0.8, network_access=True)]
        with self.assertRaises(PermissionError):
            approve_plan(steps)
        with self.assertRaises(PermissionError):
            approve_plan(steps, budget_usd=1.0)
        self.assertTrue(approve_plan(steps, budget_usd=1.0,
                                     approved_step_ids=["neural"])["allowed"])

    def test_plan_rejects_nan_cost_and_budget(self):
        with self.assertRaises(ValueError):
            Step("bad","remote",estimated_usd=float("nan"))
        with self.assertRaises(ValueError):
            approve_plan([Step("cpu","local")],budget_usd=float("nan"))

    def test_benchmark_receipt_small(self):
        result=run_benchmark((10,))
        self.assertEqual(result["external_api_calls"],0)
        self.assertEqual(result["results"][0]["status"],"PASS")

    def test_parks_fill_empty_lots_with_real_geometry(self):
        _,world=create_neighborhood(WorldSpec(rows=4,columns=4,buildings=10))
        meshes,parks=generate_parks(world)
        self.assertEqual(len(parks["parks"]),6)
        self.assertEqual(parks["tree_count"],18)
        self.assertTrue(inspect_glb(export_glb(meshes,materials=ENVIRONMENT_MATERIALS))["valid"])
        self.assertTrue(all(analyze_mesh(mesh)["passed"] for mesh in meshes))

    def test_parks_reproducible(self):
        _,world=create_neighborhood(WorldSpec())
        self.assertEqual(generate_parks(world)[1],generate_parks(world)[1])

    def test_license_gate_requires_explicit_approval(self):
        restricted = Step("model", "local", license_id="restricted-license")
        with self.assertRaises(PermissionError):
            approve_plan([restricted])
        self.assertTrue(approve_plan([restricted], approved_step_ids=["model"])["allowed"])

    def test_workflow_restart_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            steps = [Step("create", "cpu"), Step("export", "glb", ("create",))]
            store = LocalJobStore(Path(temp))
            store.create("job-1", steps)
            with self.assertRaises(ValueError):
                store.checkpoint("job-1", completed_id="export")
            store.checkpoint("job-1", completed_id="create")
            # New store instance simulates process restart.
            restarted = LocalJobStore(Path(temp))
            self.assertEqual(restarted.read("job-1")["completed_ids"], ["create"])
            restarted.checkpoint("job-1", completed_id="export", state="complete")
            self.assertEqual(restarted.read("job-1")["state"], "complete")

    def test_workflow_job_id_no_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                LocalJobStore(Path(temp)).create("../out", [])

    def test_world_road_graph_size_and_symmetric_links(self):
        _, world = create_neighborhood(WorldSpec(rows=3, columns=4, buildings=12))
        graph = graph_for_world(world)
        self.assertEqual(len(graph), 20)
        for node, data in graph.items():
            for adjacent in data["neighbors"]:
                self.assertIn(node, graph[adjacent]["neighbors"])

    def test_route_between_distant_buildings(self):
        _, world = create_neighborhood(WorldSpec(rows=2, columns=2, buildings=4))
        by_lot = {tuple(b["lot"]): b["id"] for b in world["buildings"]}
        route = shortest_road_path(world, by_lot[(0, 0)], by_lot[(1, 1)])
        self.assertEqual(len(route["intersection_ids"]), 3)
        self.assertEqual(len(route["waypoints"]), 3)
        self.assertEqual(route, shortest_road_path(world, by_lot[(0, 0)], by_lot[(1, 1)]))

    def test_collision_hits_building_not_road(self):
        _, world = create_neighborhood(WorldSpec(rows=1, columns=1, buildings=1))
        b = world["buildings"][0]
        x, _, z = b["center"]
        self.assertEqual(overlaps_building(world, x, 1, z), [b["id"]])
        self.assertEqual(overlaps_building(world, x, 50, z), [])
        self.assertEqual(overlaps_building(world, 1000, 1, 1000), [])

    def test_collision_rejects_nonfinite(self):
        _, world = create_neighborhood(WorldSpec())
        with self.assertRaises(ValueError):
            overlaps_building(world, float("nan"), 0, 0)


if __name__ == "__main__":
    unittest.main()
