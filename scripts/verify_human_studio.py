"""Real Studio Human Forge -> Blender -> authenticated GLB, blend + screenshot receipts.

Runs on authorized workstation with Blender 5.x; no network provider.
"""
import hashlib,json,sys,threading,time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request,urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import start_server

TIMINGS={"schema":"mgr.forge.phoneme-timeline.v1","actor_id":"mgr-real-human-proof",
  "language":"en-US","duration_ms":1100,
  "phonemes":[{"phoneme":"M","start_ms":0,"end_ms":170},
              {"phoneme":"AE","start_ms":170,"end_ms":450},
              {"phoneme":"TH","start_ms":450,"end_ms":720},
              {"phoneme":"OW","start_ms":720,"end_ms":1100}]}
binary=r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
if not Path(binary).is_file():raise RuntimeError("Real Blender binary not found")
with TemporaryDirectory(prefix="mgr-human-studio-") as t:
 root=Path(t)
 build(WorldSpec(seed=41,columns=2,rows=2,buildings=2),root/"world")
 service,studio=start_server(root/"world",root/"workspace",blender=binary)
 thread=threading.Thread(target=service.serve_forever,daemon=True)
 thread.start()
 def post(route,data):
  req=Request("http://127.0.0.1:"+str(service.server_port)+route,
    data=json.dumps(data).encode("utf8"),
    headers={"Content-Type":"application/json","X-MGR-Forge-Token":studio.token})
  with urlopen(req,timeout=9) as response:
   return json.loads(response.read())
 def get(route,auth=True):
  headers={"X-MGR-Forge-Token":studio.token} if auth else {}
  req=Request("http://127.0.0.1:"+str(service.server_port)+route,headers=headers)
  with urlopen(req,timeout=15) as response:
   return response.read()
 try:
  payload={"request_id":"human-studio-realproof-0001","timings":TIMINGS,"fps":24}
  a=post("/api/human-lipsync-start",payload)
  if a["status"]!="RUNNING":raise RuntimeError("Human worker did not start asynchronously")
  first=post("/api/human-lipsync-start",payload)
  assert first["replayed"] is True and first["job_id"]==a["job_id"]
  completed=None
  for _ in range(105):
   job=post("/api/human-lipsync-status",{"request_id":payload["request_id"]})
   if job["status"]=="MATERIALIZED":
    completed=job;break
   if job["status"]!="RUNNING":
    raise RuntimeError("Human Studio worker did not complete: "+str(job))
   time.sleep(1)
  if completed is None:raise RuntimeError("Human Blender job timed out")
  for field in ("glb_url","blend_url","preview_url","receipt_url"):
   try:get(completed[field],auth=False)
   except HTTPError as e:
    assert e.code==403,field
   else:raise RuntimeError("private Human Forge artifact exposed without session token")
  model=get(completed["glb_url"],auth=True)
  preview=get(completed["preview_url"],auth=True)
  blend=get(completed["blend_url"],auth=True)
  if (hashlib.sha256(model).hexdigest()!=completed["human_sha256"] or
      model[:4]!=b"glTF" or len(preview)<1000 or len(blend)<1000):
   raise RuntimeError("Human Studio returned unverified artifact bytes")
  receipt=json.loads(get(completed["receipt_url"],auth=True))
  if receipt["glb_sha256"]!=completed["human_sha256"]:
   raise RuntimeError("Human Studio receipt GLB SHA does not match actual file")
  assert receipt["status"]=="GENERATED_AND_INDEPENDENTLY_REIMPORTED"
  proof={
    "schema":"mgr.forge.studio-human-lipsync-real-blender.v1","date":"2026-10-31",
    "status":"REAL_HUMAN_STUDIO_BLENDER_GLTF_AUTH_VERIFIED",
    "source":"current ForgeWorkstation human-lipsync asynchronous job using existing human generator",
    "blender":"5.2.2 LTS",
    "human_sha256":completed["human_sha256"],"human_bytes":len(model),
    "blend_bytes":len(blend),"blend_sha256":hashlib.sha256(blend).hexdigest(),
    "preview_sha256":hashlib.sha256(preview).hexdigest(),
    "morph_targets":completed["morph_targets"],
    "animation_actions":completed["animation_actions"],
    "replay_same_single_job":True,"all_artifacts_tokenless_denied":True,
    "actual_original_human_manifold_quality_approved":False,
    "audio_alignment_performed":False,"external_gpu_or_paid_api":False,
    "hosted_chatgpt_tevin":False,
    "browser_click_accepted":False
  }
  target=Path(__file__).resolve().parents[1]/"evidence"/"human"/"2026-10-31-human-studio-authenticated.json"
  target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():raise FileExistsError("Human proof receipt exists")
  target.write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n",encoding="utf8")
  print("HUMAN_STUDIO_REAL_PROOF="+json.dumps({
     "sha256":completed["human_sha256"],
     "bytes":len(model),"morph_targets":completed["morph_targets"],
     "token_gate":True}))
 finally:
  service.shutdown();service.server_close();thread.join(timeout=2)
