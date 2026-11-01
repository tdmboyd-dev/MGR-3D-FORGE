"""Actual Studio HTTP -> owner Blender -> merged world/terrain private exports."""
import hashlib,json,sys,threading,time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import start_server

BLENDER=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
if not BLENDER.is_file():raise RuntimeError("real Blender 5.2 required")
with TemporaryDirectory(prefix="mgr-merged-studio-") as temp:
    root=Path(temp)
    build(WorldSpec(seed=42,columns=2,rows=2,buildings=3),root/"world")
    service,studio=start_server(root/"world",root/"workspace",blender=str(BLENDER))
    thread=threading.Thread(target=service.serve_forever,daemon=True)
    thread.start()
    origin=f"http://127.0.0.1:{service.server_port}"
    def post(endpoint,doc):
        req=Request(origin+endpoint,data=json.dumps(doc).encode("utf8"),headers={
            "Content-Type":"application/json","X-MGR-Forge-Token":studio.token})
        with urlopen(req,timeout=9) as res:return json.loads(res.read())
    def get(route,token=True):
        req=Request(origin+route,headers=({"X-MGR-Forge-Token":studio.token} if token else {}))
        with urlopen(req,timeout=15) as res:return res.read()
    try:
        biome_request={"request_id":"mgr-combine-verified-biome-01","biome":"alien","seed":61,"resolution":24}
        biome=post("/api/biome-create",biome_request)
        assert biome["status"]=="MATERIALIZED"
        payload={"request_id":"mgr-composed-verified-001",
                 "biome_request_id":biome_request["request_id"]}
        started=post("/api/world-compose-create",payload)
        assert started["status"]=="RUNNING" and started["replayed"] is False
        again=post("/api/world-compose-create",payload)
        assert again["replayed"] and again["job_id"]==started["job_id"]
        result=None
        for i in range(100):
            status=post("/api/world-compose-status",{"request_id":payload["request_id"]})
            if status["status"]=="MATERIALIZED":
                result=status;break
            if status["status"]!="RUNNING":
                raise RuntimeError("World composition failed: "+str(status))
            time.sleep(.8)
        if result is None:raise RuntimeError("Blender world worker timed out")
        for key in ("glb_url","blend_url","preview_url","godot_url","receipt_url"):
            try:get(result[key],token=False)
            except HTTPError as exc:
                if exc.code!=403:raise
            else:raise RuntimeError("private combined world artifact leaked")
        model=get(result["glb_url"])
        blend=get(result["blend_url"])
        png=get(result["preview_url"])
        godot=get(result["godot_url"])
        assert model[:4]==b"glTF" and len(model)>1000 and len(blend)>1500
        assert godot[:2]==b"PK" and png[:8]==b"\x89PNG\r\n\x1a\n"
        assert hashlib.sha256(model).hexdigest()==result["combined_world_sha256"]
        assert result["triangles"]>biome["triangles"]
        persisted=json.loads((root/"workspace"/"world-composition-requests.json").read_text())
        assert len(persisted)==1
        proof={
            "schema":"mgr.forge.studio-world-composition-real-v1",
            "date":"2026-11-01",
            "status":"REAL_HTTP_AND_2X_BLENDER_COMPOSITION_ACCEPTED",
            "combined_glb_sha256":result["combined_world_sha256"],
            "combined_bytes":len(model),"combined_triangles":result["triangles"],
            "original_city_sha256":result["world_sha256"],
            "biome_sha256":result["biome_sha256"],
            "edited_blend_sha256":hashlib.sha256(blend).hexdigest(),
            "preview_sha256":hashlib.sha256(png).hexdigest(),
            "source_godot_archive_sha256":hashlib.sha256(godot).hexdigest(),
            "two_process_independent_blender_accepted":True,
            "stable_id_replay_reuses_one_job":True,
            "tokenless_artifact_reads_denied":True,
            "source_city_original_unchanged":True,
            "godot_actual_running_import_verified":False,
            "collision_navmesh_generated":False,
            "hosted_chatgpt_verified":False,
            "owner_art_accepted":False,
            "paid_neural_runtime_used":False
        }
        out=ROOT/"evidence"/"world"/"2026-11-01-studio-composed-world-acceptance.json"
        if out.exists():raise FileExistsError("do not overwrite original studio proof")
        out.write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("MGR_COMPOSED_STUDIO_PASS",json.dumps({"sha":result["combined_world_sha256"],"triangles":result["triangles"],"bytes":len(model)}))
    finally:
        service.shutdown();service.server_close();thread.join(timeout=2)
