"""True owner-audio WAV data -> authenticated existing Forge Studio -> Blender face.

Uses synthetic test PCM only; any personal user voice must be explicitly approved.
"""
import base64,hashlib,io,json,math,struct,sys,threading,time,wave
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
if not BLENDER.is_file():raise RuntimeError("Real Windows Blender 5.2 required")
buffer=io.BytesIO()
rate=16000
with wave.open(buffer,"wb") as writer:
    writer.setnchannels(1);writer.setsampwidth(2);writer.setframerate(rate)
    n=rate*2
    samples=[]
    for i in range(n):
        t=i/rate
        value=math.sin(2*math.pi*200*t)*.55 if .25<t<1.70 else 0.
        samples.append(round(32000*value))
    writer.writeframes(struct.pack("<"+str(n)+"h",*samples))
pcm=buffer.getvalue()
with TemporaryDirectory(prefix="mgr-human-audio-studio-") as tmp:
    scratch=Path(tmp)
    build(WorldSpec(seed=26,columns=2,rows=2,buildings=2),scratch/"world")
    service,studio=start_server(scratch/"world",scratch/"workspace",blender=str(BLENDER))
    thread=threading.Thread(target=service.serve_forever,daemon=True)
    thread.start()
    origin="http://127.0.0.1:"+str(service.server_port)
    def post(route,doc):
        req=Request(origin+route,data=json.dumps(doc).encode("utf8"),headers={
            "X-MGR-Forge-Token":studio.token,"Content-Type":"application/json"})
        with urlopen(req,timeout=10) as response:return json.loads(response.read())
    def get(route,token=True):
        headers={"X-MGR-Forge-Token":studio.token} if token else {}
        with urlopen(Request(origin+route,headers=headers),timeout=10) as response:return response.read()
    try:
        payload={"request_id":"owner-human-real-audio-0001","actor_id":"mgr-generic-source",
                 "wav_base64":base64.b64encode(pcm).decode("ascii"),"fps":24}
        created=post("/api/human-lipsync-start",payload)
        assert created["status"]=="RUNNING"
        replay=post("/api/human-lipsync-start",payload)
        assert replay["job_id"]==created["job_id"] and replay["replayed"] is True
        end=None
        for _ in range(105):
            now=post("/api/human-lipsync-status",{"request_id":payload["request_id"]})
            if now["status"]=="MATERIALIZED":
                end=now;break
            if now["status"]!="RUNNING":
                raise RuntimeError("Real WAV Human Forge job failed: "+str(now))
            time.sleep(.8)
        if end is None:raise RuntimeError("WAV face generation timeout")
        assert end["source_wav_loudness_reactive"] is True
        for name in ("glb_url","blend_url","preview_url"):
            try:get(end[name],token=False)
            except HTTPError as error:assert error.code==403
            else:raise RuntimeError("Private Human WAV Studio output leaked")
        model=get(end["glb_url"])
        assert model[:4]==b"glTF" and hashlib.sha256(model).hexdigest()==end["human_sha256"]
        receipt=json.loads(get(end["receipt_url"]))
        if receipt["source_audio_sha256"]!=hashlib.sha256(pcm).hexdigest() or (
            receipt["raw_audio_alignment_performed"] is not False):
            raise RuntimeError("Original audio hash or honest lip-sync classification wrong")
        doc={
         "schema":"mgr.forge.real-human-wav-studio.v1","date":"2026-11-01",
         "status":"REAL_PCM_WAV_TO_MGR_HUMAN_BLENDER_ANIMATION_PASS",
         "synthetic_original_audio":True,"source_wav_sha256":hashlib.sha256(pcm).hexdigest(),
         "source_wav_bytes":len(pcm),
         "real_output_glb_sha256":end["human_sha256"],"real_output_glb_bytes":len(model),
         "real_morph_targets":end["morph_targets"],
         "real_animation_actions":end["animation_actions"],
         "studio_async_job_replay":True,
         "private_file_tokenless_denied":True,
         "source_audio_private_no_public_git":True,
         "real_blender_independent_reimport":True,
         "automatic_audio_envelope_reactive":True,
         "automatic_phoneme_alignment":False,
         "actual_user_original_audio_consent_not_tested":True,
         "owner_art_approved":False,
         "neural_model_used":False
        }
        output=ROOT/"evidence"/"human"/"2026-11-01-audio-reactive-studio-blender.json"
        if output.exists():raise FileExistsError("Do not overwrite previous audio Studio proof")
        output.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("MGR_ORIGINAL_AUDIO_STUDIO_BLENDER_PASS",json.dumps({"sha":end["human_sha256"],"bytes":len(model),"morphs":end["morph_targets"]}))
    finally:
        service.shutdown();service.server_close();thread.join(timeout=2)
