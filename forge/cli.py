"""Offline CLI: python -m forge.cli build --out /path/to/output."""

import argparse
import hashlib
import json
from pathlib import Path

from .geometry import create_neighborhood
from .glb import export_glb, inspect_glb
from .quality import validate_neighborhood
from .planner import plan_neighborhood
from .spec import WorldSpec
from .obj import export_obj
from .world import graph_for_world
from .preview import render_world_svg
from .streaming import chunk_world, simple_building_lod
from .cinematic import camera_tour
from .perception import scene_overview
from .consciousness import scene_facts
from .visualqa import compare_pngs
from .view_identity import compare_view_silhouettes, compare_asset_views, AssetView
from .traversal import rehearse_road_walk
from .interiors import generate_interiors
from .character import build_mannequin
from .blender_bridge import verify_blender, blender_render_command, blender_facts_command, blender_rig_command, blender_pose_render_command, blender_pose_inspect_command, blender_cinematic_command, blender_material_inspect_command, blender_director_inspect_command, blender_director_frames_command
from .environment import generate_parks, ENVIRONMENT_MATERIALS
from .receipt import file_receipt, verify_bundle
from .materials import MGR_MATERIAL_PRESETS
from .shot_design import validate_shot_reel, lighting_recipe, validate_camera_clearance


def build(spec: WorldSpec, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    meshes, manifest = create_neighborhood(spec)
    qc = validate_neighborhood(manifest)
    if not qc["passed"]:
        raise RuntimeError(f"scene QA failed: {qc['errors']}")
    payload = export_glb(meshes, name=spec.name,
        pbr_overrides={1:MGR_MATERIAL_PRESETS["asphalt"],
                       2:MGR_MATERIAL_PRESETS["weathered-brick"],
                       3:MGR_MATERIAL_PRESETS["matte-stone"],
                       4:MGR_MATERIAL_PRESETS["painted-metal"]})
    glb_qc = inspect_glb(payload)
    glb_path = output / "world.glb"
    manifest_path = output / "manifest.json"
    glb_path.write_bytes(payload)
    obj_data, mtl_data = export_obj(meshes)
    (output / "world.obj").write_text(obj_data, encoding="utf-8")
    (output / "world.mtl").write_text(mtl_data, encoding="utf-8")
    roads_data = graph_for_world(manifest)
    (output / "navigation.json").write_text(
        json.dumps({"schema": "mgr.forge.road-graph.v1", "nodes": roads_data},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "preview.svg").write_text(render_world_svg(manifest), encoding="utf-8")
    chunks = chunk_world(manifest)
    (output / "chunks.json").write_text(
        json.dumps(chunks, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tour=camera_tour(manifest)
    manifest["cinematic_reel_quality"]=validate_shot_reel(tour)
    manifest["cinematic_camera_clearance"]=validate_camera_clearance(manifest,tour)
    if manifest["cinematic_camera_clearance"]["status"]!="PASS":
        raise RuntimeError("generated camera intersects authored building geometry")
    (output / "camera_tour.json").write_text(
        json.dumps(tour, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "lighting.json").write_text(
        json.dumps(lighting_recipe(),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (output / "spatial_overview.json").write_text(
        json.dumps(scene_overview(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "scene_facts.json").write_text(
        json.dumps(scene_facts(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    interior_meshes, interior_plan = generate_interiors(manifest)
    (output / "interiors.glb").write_bytes(export_glb(interior_meshes, name=f"{spec.name} Interiors"))
    (output / "interiors.json").write_text(
        json.dumps(interior_plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    park_meshes,park_manifest=generate_parks(manifest)
    (output / "parks.glb").write_bytes(export_glb(park_meshes,name=f"{spec.name} Parks",
                                          materials=ENVIRONMENT_MATERIALS))
    (output / "parks.json").write_text(
        json.dumps(park_manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lod1_payload = export_glb(simple_building_lod(manifest), name=f"{spec.name} LOD1")
    (output / "world_lod1.glb").write_bytes(lod1_payload)
    manifest["quality"] = qc
    manifest["glb_quality"] = glb_qc
    manifest["artifact"] = {"path": "world.glb", "sha256": hashlib.sha256(payload).hexdigest(),
                            "bytes": len(payload)}
    manifest["additional_artifacts"] = {
        "obj": "world.obj", "mtl": "world.mtl", "road_graph": "navigation.json",
        "preview": "preview.svg", "chunks": "chunks.json", "lod1": "world_lod1.glb",
        "camera_tour": "camera_tour.json", "lighting": "lighting.json", "spatial_overview": "spatial_overview.json",
        "scene_facts": "scene_facts.json",
        "interiors": "interiors.glb", "interior_plan": "interiors.json",
        "parks":"parks.glb", "parks_manifest":"parks.json"}
    manifest["lod1_quality"] = inspect_glb(lod1_payload)
    manifest["execution"] = {"compute": "CPU", "external_api_calls": 0,
                             "model_inference": False, "blender_verified": False,
                             "independent_engine_import_verified": False}
    manifest["artifact_inventory"]={
        name:file_receipt(output/name)
        for name in sorted({"world.glb",*manifest["additional_artifacts"].values()})}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description="MGR Forge: deterministic, GPU-free 3D neighborhood")
    sub = parser.add_subparsers(dest="action", required=True)
    create = sub.add_parser("build", help="generate real GLB geometry + manifest")
    create.add_argument("--spec", type=Path, help="optional WorldSpec JSON")
    create.add_argument("--out", type=Path, required=True, help="output directory")
    create.add_argument("--seed", type=int, help="override seed")
    create.add_argument("--buildings", type=int, help="override building count")
    create.add_argument("--columns", type=int, help="override columns")
    create.add_argument("--rows", type=int, help="override rows")
    create.add_argument("--prompt", type=str, help="limited offline prompt, e.g. 'build 10 houses'")
    inspect = sub.add_parser("inspect", help="check a GLB for structural validity")
    inspect.add_argument("path", type=Path)
    character = sub.add_parser("character",help="export generic detachable mannequin T/A pose")
    character.add_argument("--pose",choices=("T","A"),default="T")
    character.add_argument("--out",type=Path,required=True)
    blender = sub.add_parser("blender-verify",help="run actual Blender GLB import verification if installed")
    blender.add_argument("path",type=Path)
    blender.add_argument("--report",type=Path,required=True)
    blender.add_argument("--binary",default="blender")
    render=sub.add_parser("blender-render",help="render real Blender workbench QA PNG")
    render.add_argument("path",type=Path)
    render.add_argument("--image",type=Path,required=True)
    render.add_argument("--report",type=Path,required=True)
    render.add_argument("--binary",default="blender")
    facts=sub.add_parser("blender-facts",help="inspect real Blender GLB object facts")
    facts.add_argument("path",type=Path)
    facts.add_argument("--report",type=Path,required=True)
    facts.add_argument("--binary",default="blender")
    rig=sub.add_parser("blender-rig",help="assemble modular T mannequin as Blender armature project")
    rig.add_argument("character_folder",type=Path)
    rig.add_argument("--blend",type=Path,required=True)
    rig.add_argument("--report",type=Path,required=True)
    rig.add_argument("--binary",default="blender")
    rig.add_argument("--skin",action="store_true",help="add armature modifier/weights and 2-frame motion proof")
    poses=sub.add_parser("blender-pose-render",help="render two animated Blender keyframes with transparent background")
    poses.add_argument("blend",type=Path)
    poses.add_argument("--first",type=Path,required=True)
    poses.add_argument("--second",type=Path,required=True)
    poses.add_argument("--report",type=Path,required=True)
    poses.add_argument("--binary",default="blender")
    guardian=sub.add_parser("blender-pose-audit", help="measure animated rig bones, joints and skin coverage inside Blender")
    guardian.add_argument("blend",type=Path)
    guardian.add_argument("--report",type=Path,required=True)
    guardian.add_argument("--binary",default="blender")
    cinema=sub.add_parser("blender-cinematic",help="materialize a 3D camera reel, lights, editable .blend and real CPU render")
    cinema.add_argument("glb",type=Path)
    cinema.add_argument("--tour",type=Path,required=True)
    cinema.add_argument("--mood",choices=("daylight","golden-hour","moonlit"),default="daylight")
    cinema.add_argument("--blend",type=Path,required=True)
    cinema.add_argument("--image",type=Path,required=True)
    cinema.add_argument("--report",type=Path,required=True)
    cinema.add_argument("--binary",default="blender")
    material_audit=sub.add_parser("blender-material-audit",help="check actual imported Blender PBR material sockets")
    material_audit.add_argument("glb",type=Path)
    material_audit.add_argument("--report",type=Path,required=True)
    material_audit.add_argument("--binary",default="blender")
    director_audit=sub.add_parser("blender-director-audit",help="audit actual saved Blender timeline cameras/cuts")
    director_audit.add_argument("blend",type=Path)
    director_audit.add_argument("--report",type=Path,required=True)
    director_audit.add_argument("--binary",default="blender")
    director_frames=sub.add_parser("blender-director-frames",help="render four actual timeline frames and compare dolly output")
    director_frames.add_argument("blend",type=Path)
    director_frames.add_argument("--out",type=Path,required=True)
    director_frames.add_argument("--report",type=Path,required=True)
    director_frames.add_argument("--binary",default="blender")
    bundle=sub.add_parser("verify-bundle",help="verify artifact hashes in world build folder")
    bundle.add_argument("directory",type=Path)
    visual=sub.add_parser("compare-renders",help="compare fixed-camera RGB PNG frames")
    visual.add_argument("reference",type=Path)
    visual.add_argument("candidate",type=Path)
    visual.add_argument("--threshold",type=float,default=0)
    views=sub.add_parser("compare-views",help="translation/quarter-turn aware appearance check; not identity proof")
    views.add_argument("reference",type=Path)
    views.add_argument("candidate",type=Path)
    views.add_argument("--acceptance-iou",type=float,default=0.92)
    identity=sub.add_parser("compare-asset-identity",help="compare trusted asset and neutral-mesh SHA receipts")
    identity.add_argument("reference",type=Path,help="AssetView JSON")
    identity.add_argument("candidate",type=Path,help="AssetView JSON")
    flow=sub.add_parser("pipeline",help="build world and optionally verify/render in real Blender")
    flow.add_argument("--out",type=Path,required=True)
    flow.add_argument("--blender-binary",default=None)
    flow.add_argument("--baseline",type=Path)
    flow.add_argument("--visual-threshold",type=float,default=0.0)
    flow.add_argument("--buildings",type=int,default=10)
    walk=sub.add_parser("rehearse-walk",help="simulate collision-checked road-centerline traversal")
    walk.add_argument("manifest",type=Path)
    walk.add_argument("--from-building",required=True)
    walk.add_argument("--to-building",required=True)
    walk.add_argument("--out",type=Path,required=True)
    args = parser.parse_args(argv)
    if args.action == "inspect":
        print(json.dumps(inspect_glb(args.path.read_bytes()), indent=2))
        return 0
    if args.action == "character":
        result = build_mannequin(args.out,args.pose)
        print(json.dumps({"output":str(args.out.resolve()), "pose":result["pose"],
                          "parts":len(result["editable_parts"]),
                          "anatomy":"PASS" if result["quality"]["passed"] else "FAIL"},indent=2))
        return 0
    if args.action == "blender-verify":
        print(json.dumps(verify_blender(args.path,args.report,blender_binary=args.binary),indent=2))
        return 0
    if args.action == "blender-render":
        import subprocess
        command=blender_render_command(args.binary,args.path,args.image,args.report)
        result=subprocess.run(command,timeout=180,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender render failed with exit code {result.returncode}")
        print(json.dumps({"status":"PASS","image":str(args.image.resolve())},indent=2))
        return 0
    if args.action == "blender-facts":
        import subprocess
        command=blender_facts_command(args.binary,args.path,args.report)
        result=subprocess.run(command,timeout=180,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender scene inspection failed with exit code {result.returncode}")
        report=json.loads(args.report.read_text(encoding="utf-8"))
        if report.get("status")!="PASS":
            raise RuntimeError("Blender scene facts receipt invalid")
        print(json.dumps({"status":"PASS","objects":len(report["objects"])},indent=2))
        return 0
    if args.action == "blender-rig":
        import subprocess
        command=blender_rig_command(args.binary,args.character_folder,args.blend,args.report,
                                    skin=args.skin)
        result=subprocess.run(command,timeout=180,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender modular rig assembly failed with exit code {result.returncode}")
        report=json.loads(args.report.read_text(encoding="utf-8"))
        if report.get("status")!="PASS" or report.get("mesh_parts",0)<1:
            raise RuntimeError("Blender modular rig receipt invalid")
        if args.skin and (report.get("rig_mode")!="skin" or
                          report.get("animation_motion_m") is None or
                          report["animation_motion_m"]<0.01):
            raise RuntimeError("actual evaluated mesh animation motion not verified")
        print(json.dumps({"status":"PASS","parts":report["mesh_parts"],
                          "bones":len(report["bones"])},indent=2))
        return 0
    if args.action == "blender-pose-render":
        import subprocess
        command=blender_pose_render_command(args.binary,args.blend,args.first,args.second,args.report)
        result=subprocess.run(command,timeout=180,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender pose rendering failed with exit code {result.returncode}")
        report=json.loads(args.report.read_text(encoding="utf-8"))
        if report.get("status")!="PASS" or len(report.get("frames",[]))!=2:
            raise RuntimeError("Blender pose render receipt invalid")
        from .visualqa import compare_pngs
        diff=compare_pngs(args.first,args.second)
        print(json.dumps({"status":"PASS", "frames":report["frames"],
                          "rgb_difference_mae":diff["rgb_mae"],
                          "pose_images_visibly_different":diff["rgb_mae"]>0},indent=2))
        if diff["rgb_mae"]<=0:
            raise RuntimeError("animated pose render did not change pixel output")
        return 0
    if args.action == "blender-pose-audit":
        import subprocess
        from .pose_guardian import validate_pose_frames
        observations=args.report.with_name(args.report.stem+"-observations.json")
        if args.report.exists() or observations.exists():
            raise FileExistsError("pose receipt already exists; use a fresh output path")
        command=blender_pose_inspect_command(args.binary,args.blend,observations)
        result=subprocess.run(command,timeout=180,capture_output=True,text=True,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender pose inspection failed ({result.returncode}): {result.stderr[-500:]}")
        data=json.loads(observations.read_text(encoding="utf-8"))
        report=validate_pose_frames(data["observations"])
        report["blender_version"]=data["blender_version"]
        args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2))
        return 0 if report["status"]=="PASS" else 2
    if args.action == "blender-cinematic":
        import subprocess
        if any(path.exists() for path in (args.blend,args.image,args.report)):
            raise FileExistsError("cinematic output already exists; choose a fresh folder")
        command=blender_cinematic_command(args.binary,args.glb,args.tour,args.mood,
                                          args.blend,args.image,args.report)
        result=subprocess.run(command,timeout=600,capture_output=True,text=True,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender cinematic failed ({result.returncode}): {result.stderr[-600:] or result.stdout[-600:]}")
        report=json.loads(args.report.read_text(encoding="utf-8"))
        if report.get("status")!="PASS" or not all(path.stat().st_size>0
                                                    for path in (args.blend,args.image)):
            raise RuntimeError("Blender cinematic receipt invalid")
        print(json.dumps(report,indent=2))
        return 0
    if args.action == "blender-material-audit":
        import subprocess
        from .material_guardian import validate_imported_materials
        observation=args.report.with_name(args.report.stem+"-observation.json")
        if args.report.exists() or observation.exists():
            raise FileExistsError("material receipt already exists")
        command=blender_material_inspect_command(args.binary,args.glb,observation)
        result=subprocess.run(command,timeout=180,capture_output=True,text=True,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender material inspection failed ({result.returncode}): {result.stderr[-600:] or result.stdout[-600:]}")
        raw=json.loads(observation.read_text(encoding="utf-8"))
        receipt=validate_imported_materials(raw)
        receipt["blender_version"]=raw["blender_version"]
        receipt["materials"]=raw["materials"]
        args.report.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(receipt,indent=2))
        return 0 if receipt["status"]=="PASS" else 2
    if args.action == "blender-director-audit":
        import subprocess
        if args.report.exists():
            raise FileExistsError("director receipt already exists")
        command=blender_director_inspect_command(args.binary,args.blend,args.report)
        result=subprocess.run(command,timeout=180,capture_output=True,text=True,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender director inspection failed ({result.returncode}): {result.stderr[-600:] or result.stdout[-600:]}")
        report=json.loads(args.report.read_text(encoding="utf-8"))
        if report.get("status")!="PASS" or report.get("camera_count",0)<2:
            raise RuntimeError("Blender director receipt invalid")
        print(json.dumps(report,indent=2))
        return 0
    if args.action == "blender-director-frames":
        import subprocess
        if args.report.exists():
            raise FileExistsError("director frame receipt already exists")
        command=blender_director_frames_command(args.binary,args.blend,args.out,args.report)
        result=subprocess.run(command,timeout=600,capture_output=True,text=True,check=False)
        if result.returncode:
            raise RuntimeError(f"Blender director frames failed ({result.returncode}): {result.stderr[-600:] or result.stdout[-600:]}")
        report=json.loads(args.report.read_text(encoding="utf-8"))
        frames=report.get("frames",[])
        if report.get("status")!="PASS" or len(frames)<4:
            raise RuntimeError("missing actual rendered director frames")
        from .visualqa import compare_pngs
        before=args.out/frames[1]["filename"]
        after=args.out/frames[2]["filename"]
        difference=compare_pngs(before,after)["rgb_mae"]
        if difference<=0:
            raise RuntimeError("moving camera produced unchanged rendered pixels")
        report["moving_shot_rgb_mae"]=difference
        args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2))
        return 0
    if args.action == "verify-bundle":
        print(json.dumps(verify_bundle(args.directory),indent=2))
        return 0
    if args.action == "compare-renders":
        report=compare_pngs(args.reference,args.candidate,
                            max_mean_absolute_error=args.threshold)
        print(json.dumps(report,indent=2))
        return 0 if report["pass"] else 2
    if args.action == "compare-views":
        report=compare_view_silhouettes(args.reference,args.candidate,
                     acceptance_iou=args.acceptance_iou)
        print(json.dumps(report,indent=2))
        return 0 if report["verdict"]=="APPEARANCE_CONSISTENT" else 2
    if args.action == "compare-asset-identity":
        first=AssetView(**json.loads(args.reference.read_text(encoding="utf-8")))
        second=AssetView(**json.loads(args.candidate.read_text(encoding="utf-8")))
        report=compare_asset_views(first,second)
        print(json.dumps(report,indent=2))
        return 0 if report["verdict"]=="SAME_VERIFIED_SOURCE_ASSET" else 2
    if args.action == "pipeline":
        from .pipeline import run_pipeline
        result=run_pipeline(WorldSpec(buildings=args.buildings),args.out,
                  blender_binary=args.blender_binary,visual_baseline=args.baseline,
                  visual_mae_threshold=args.visual_threshold)
        print(json.dumps(result,indent=2))
        return 0 if result["overall"].startswith("PASS") or result["overall"]=="PARTIAL_CPU_ONLY" else 2
    if args.action == "rehearse-walk":
        if args.out.exists():
            raise FileExistsError("walk report already exists; choose a new output")
        world=json.loads(args.manifest.read_text(encoding="utf-8"))
        result=rehearse_road_walk(world,args.from_building,args.to_building)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({"status":result["status"],"frames":len(result["frames"]),
                          "distance_m":result["distance_m"]},indent=2))
        return 0
    if args.spec and args.prompt:
        parser.error("choose either --spec or --prompt")
    base = (WorldSpec.from_json(args.spec).as_dict() if args.spec else
            plan_neighborhood(args.prompt).spec.as_dict() if args.prompt else
            WorldSpec().as_dict())
    for key in ("seed", "buildings", "columns", "rows"):
        value = getattr(args, key)
        if value is not None:
            base[key] = value
    result = build(WorldSpec(**base), args.out)
    print(json.dumps({"output": str(args.out.resolve()), "buildings": len(result["buildings"]),
                      "triangles": result["triangle_count"], "sha256": result["artifact"]["sha256"],
                      "quality": "PASS" if result["quality"]["passed"] else "FAIL"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
