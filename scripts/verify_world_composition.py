"""Actual native city+biome -> one editable Blender scene -> Godot source project."""
import hashlib,json,sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forge.cli import build
from forge.spec import WorldSpec
from forge.environment import write_biome_shell
from forge.world_composition import compose_world
from forge.glb import inspect_glb

BLENDER=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
if not BLENDER.is_file():raise RuntimeError("Real Blender required for World Forge composition acceptance")
with TemporaryDirectory(prefix="mgr-native-world-compose-") as scratch:
    folder=Path(scratch)
    city=folder/"city"
    biome=folder/"biome"
    assembled=folder/"combined"
    build(WorldSpec(seed=38,columns=2,rows=2,buildings=2),city)
    write_biome_shell(city,biome,biome="alien",seed=11,resolution=26)
    city_sha=hashlib.sha256((city/"world.glb").read_bytes()).hexdigest()
    biome_sha=hashlib.sha256((biome/"biome.glb").read_bytes()).hexdigest()
    report=compose_world(city,biome,assembled,blender=BLENDER)
    assert report["status"]=="BLENDER_COMPOSED_INDEPENDENT_REOPEN"
    assert report["combined_world_sha256"]==hashlib.sha256((assembled/"world.glb").read_bytes()).hexdigest()
    assert report["combined_triangles"]>report["city_faces"]
    assert hashlib.sha256((city/"world.glb").read_bytes()).hexdigest()==city_sha
    assert hashlib.sha256((biome/"biome.glb").read_bytes()).hexdigest()==biome_sha
    assert (assembled/"godot-project"/"assets"/"world.glb").read_bytes()==(assembled/"world.glb").read_bytes()
    info=inspect_glb((assembled/"world.glb").read_bytes())
    safe={"schema":"mgr.forge.world-composition-real-blender.v1","date":"2026-11-01",
          "world_blender_proof":report,
          "source_city_sha256":city_sha,"source_biome_sha256":biome_sha,
          "combined_glb_bytes":(assembled/"world.glb").stat().st_size,
          "combined_blend_sha256":hashlib.sha256((assembled/"world-composed.blend").read_bytes()).hexdigest(),
          "combined_preview_sha256":hashlib.sha256((assembled/"world-composed-preview.png").read_bytes()).hexdigest(),
          "godot_source_project_verified":True,
          "godot_runtime_import_verified":False,
          "original_city_glb_unchanged":True,"original_biome_glb_unchanged":True,
          "two_independent_blender_processes":True,
          "licensed_upstream_assets_included":False,
          "physically_seamless_terrain_navmesh_verified":False,
          "user_art_accepted":False,"model_inference_used":False,
          "triangles":info["triangles"],"private_originals":"Windows disposable temp, not shipped in Git"}
    dest=ROOT/"evidence"/"world"/"2026-11-01-combined-world-blender-godot.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise FileExistsError("World proof already exists; don't overwrite")
    dest.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("MGR_WORLD_COMPOSITION_ACCEPTED",json.dumps({"sha":report["combined_world_sha256"],"city":report["city_faces"],"biome":report["biome_faces"],"bytes":safe["combined_glb_bytes"]}))
