"""Existing World Forge: independently verified single GLB city + native biome.

Uses Blender as the scene compositing receiver. Retains original city/biome
bytes unchanged; emits one new editable scene and Godot source project with
explicitly measured state. Not a trained neural terrain or automatic navmesh.
"""
import hashlib,json,shutil,subprocess
from pathlib import Path
from .glb import inspect_glb
from .engine_handoff import export_godot_project

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _require_blender(binary):
    found=shutil.which(str(binary))
    if not found:raise RuntimeError("Real Blender required for native World composition")
    return found

def _run(binary,filename,arguments,timeout=110):
    script=Path(__file__).resolve().parents[1]/"bridge"/filename
    result=subprocess.run([binary,"--background","--factory-startup",
        "--python",str(script),"--",*(str(x) for x in arguments)],
        capture_output=True,text=True,timeout=timeout,stdin=subprocess.DEVNULL)
    if result.returncode or "Traceback (most recent call last)" in (result.stdout+result.stderr):
        raise RuntimeError("Real Blender world composition failed: "+(result.stderr or result.stdout)[-700:])
    return result.stdout

def compose_world(world_dir,biome_dir,out,*,blender="blender",export_godot=True):
    world,biome,dest=Path(world_dir),Path(biome_dir),Path(out)
    if dest.exists():raise FileExistsError("Do not overwrite another MGR world")
    binary=_require_blender(blender)
    for parent,name,limit in ((world,"world.glb",90_000_000),(biome,"biome.glb",30_000_000)):
        src=parent/name
        if src.is_symlink() or not src.is_file() or src.stat().st_size>limit:
            raise ValueError("verified MGR source not found or oversized")
        inspect_glb(src.read_bytes())
    city=json.loads((world/"manifest.json").read_text(encoding="utf8"))
    overlay=json.loads((biome/"biome.json").read_text(encoding="utf8"))
    world_sha=_sha(world/"world.glb")
    biome_sha=_sha(biome/"biome.glb")
    if world_sha!=city.get("artifact",{}).get("sha256") or (
            world_sha!=overlay.get("source_world_glb_sha256") or
            biome_sha!=overlay.get("artifact",{}).get("sha256")):
        raise ValueError("biome and city source SHA identities do not agree")
    # Keep copies outside the public repo, independent from private user inputs.
    try:
        step=_run(binary,"blender_world_compose.py",[world,biome,dest])
        if "MGR_WORLD_COMPOSE=" not in step:
            raise RuntimeError("Blender did not return composed geometry witness")
        receiver=_run(binary,"blender_world_compose_reimport.py",[dest])
        if "MGR_WORLD_COMPOSE_REIMPORT=" not in receiver:
            raise RuntimeError("Independent Blender world reimport did not report proof")
        proof=json.loads((dest/"world-composed-proof.json").read_text(encoding="utf8"))
        if proof.get("status")!="WORLD_COMPOSITION_INDEPENDENT_IMPORT_RENDER_PASS" or (
             proof.get("source_world_sha256")!=world_sha or
             proof.get("source_biome_sha256")!=biome_sha or
             proof.get("combined_glb_sha256")!=_sha(dest/"world-composed.glb")):
            raise RuntimeError("Composed world source lineage/independent Blender proof failed")
        raw=(dest/"world-composed.glb").read_bytes()
        counts=inspect_glb(raw)
        if counts["triangles"]<proof["combined_faces"]:
            raise RuntimeError("Merged GLB has fewer triangles than independent Blender mesh")
        # Make the output compatible with the EXISTING Godot handoff and
        # scene-management contracts, not a second world manifest format.
        shutil.copyfile(dest/"world-composed.glb",dest/"world.glb")
        manifest=json.loads(json.dumps(city))
        manifest["artifact"]={"path":"world.glb","sha256":_sha(dest/"world.glb"),
                              "bytes":(dest/"world.glb").stat().st_size}
        manifest["world_composition"]={
            "schema":"mgr.forge.world-composition.v1",
            "source_city_sha256":world_sha,"source_biome_sha256":biome_sha,
            "biome_kind":overlay["biome"],
            "reversible_originals_remain_in_source_paths":True,
            "blender_second_process_verified":True,
            "collision_navmesh_auto_generated":False,
            "art_accepted_by_owner":False}
        (dest/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf8")
        godot_result=None
        if export_godot:
            godot_result=export_godot_project(dest,dest/"godot-project")
        if _sha(world/"world.glb")!=world_sha or _sha(biome/"biome.glb")!=biome_sha:
            raise RuntimeError("MGR source world or biome was changed")
        result={
            "schema":"mgr.forge.world-composition.v1",
            "status":"BLENDER_COMPOSED_INDEPENDENT_REOPEN",
            "city_input_sha256":world_sha,"biome_input_sha256":biome_sha,
            "combined_world_sha256":_sha(dest/"world.glb"),
            "combined_triangles":counts["triangles"],
            "city_faces":proof["original_city_faces"],
            "biome_faces":proof["original_biome_faces"],
            "blender_version":proof["blender_version"],
            "preview_sha256":proof["preview_sha256"],
            "source_meshes_preserved":True,
            "source_files_unchanged":True,
            "godot_project_packaged":godot_result is not None,
            "godot_engine_runtime_tested":False,
            "world_collision_navmesh_generated":False,
            "external_paid_model_used":False,
            "owner_art_accepted":False,
            "paths":["world.glb","world-composed.blend","world-composed-preview.png",
                     "world-composed-proof.json","manifest.json"]+
                    (["godot-project/project.godot","godot-project/world.tscn",
                      "godot-project/assets/world.glb"] if godot_result else [])
        }
        (dest/"composition-receipt.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
        return result
    except Exception:
        if dest.exists():
            (dest/"needs-reconciliation.txt").write_text(
                "MGR World composition incomplete; preserve source and inspect Blender process evidence.\n",
                encoding="utf8")
        raise
