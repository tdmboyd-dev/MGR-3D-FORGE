"""Asynchronous human facial Blender job on Forge's existing Studio owner worker.

This is a *job adapter* for the existing Human Forge build_human_lipsync
pipeline, not a second artist, geometry engine, model vault or MCP server.
"""
import hashlib,json,threading,base64,binascii
from pathlib import Path
from .lipsync import _validate
from .audio_motion import _validate_actor,_wav_features
from .world_jobs import _index,_atomic_json,_ID

LEDGER="human-lipsync-requests.json"

def _validated(payload):
    if not isinstance(payload,dict):
        raise ValueError("Human Forge expects an exact JSON object")
    fields=set(payload)
    if fields not in ({"request_id","timings","fps"},
                      {"request_id","actor_id","wav_base64","fps"}):
        raise ValueError("Human Forge expects exact phoneme timings OR bounded caller-owned WAV")
    rid=payload["request_id"]
    if not isinstance(rid,str) or not _ID.fullmatch(rid):
        raise ValueError("invalid human animation request ID")
    fps=payload["fps"]
    if type(fps) is not int or not 12<=fps<=60:
        raise ValueError("Human Forge fps must be 12..60")
    if "timings" in fields:
        _validate(payload["timings"])
        raw=json.dumps(payload,sort_keys=True,allow_nan=False,
                       separators=(",",":")).encode("utf8")
        if len(raw)>100_000:raise ValueError("Human phoneme timings oversized")
        return rid,raw,None
    actor=_validate_actor(payload["actor_id"])
    encoded=payload["wav_base64"]
    if not isinstance(encoded,str) or not 60<=len(encoded)<=1_500_000:
        raise ValueError("Human Forge WAV base64 exceeds local Studio limit")
    try:
        wave_bytes=base64.b64decode(encoded,validate=True)
    except (binascii.Error,ValueError) as exc:
        raise ValueError("invalid caller-provided WAV base64") from exc
    _wav_features(wave_bytes)
    # Do not store base64 original recording twice in a public/logged JSON.
    meta={"schema":"mgr.forge.human-original-audio-request.v1",
          "request_id":rid,"fps":fps,"actor_id":actor,
          "source_wav_sha256":hashlib.sha256(wave_bytes).hexdigest(),
          "source_wav_bytes":len(wave_bytes)}
    return rid,json.dumps(meta,sort_keys=True,separators=(",",":")).encode("utf8"),wave_bytes

def _readback(studio,rid,row,*,replayed):
    job=studio.valid_job(row["job_id"])
    state=row.get("status")
    if state=="RUNNING":
        active=getattr(studio,"human_active_jobs",set())
        return {"status":"RUNNING" if rid in active else "NEEDS_RECONCILIATION",
                "request_id":rid,"job_id":row["job_id"],"replayed":replayed,
                "message":"Blender Human Forge in progress" if rid in active else "Job interrupted; inspect on-disk outputs"}
    if state!="MATERIALIZED":
        return {"status":state or "NEEDS_RECONCILIATION","request_id":rid,
                "job_id":row["job_id"],"replayed":replayed,
                "message":"Failed or incomplete Human Forge worker; review saved files"}
    model=job/"human"/"facial-animation"/"human-lipsync.glb"
    report=job/"human"/"human-lipsync-receipt.json"
    preview=job/"human"/"facial-animation"/"human-lipsync-preview.png"
    blend=job/"human"/"facial-animation"/"human-lipsync.blend"
    for p in (model,report,preview,blend):
        if p.is_symlink() or not p.is_file() or p.stat().st_size>200_000_000:
            raise RuntimeError("Human lip sync output missing or excessive")
    blob=model.read_bytes()
    sha=hashlib.sha256(blob).hexdigest()
    data=json.loads(report.read_text(encoding="utf8"))
    if (sha!=row.get("sha256") or sha!=data.get("glb_sha256") or
        data.get("status")!="GENERATED_AND_INDEPENDENTLY_REIMPORTED" or
        blob[:4]!=b"glTF" or data.get("morph_target_count",0)<6):
        raise RuntimeError("Human Forge GLB mismatched real Blender proof")
    return {"status":"MATERIALIZED","request_id":rid,"job_id":row["job_id"],
            "human_sha256":sha,"human_bytes":len(blob),
            "morph_targets":data["morph_target_count"],
            "animation_actions":data["animation_actions"],
            "glb_url":f"/files/{row['job_id']}/human/facial-animation/human-lipsync.glb",
            "blend_url":f"/files/{row['job_id']}/human/facial-animation/human-lipsync.blend",
            "preview_url":f"/files/{row['job_id']}/human/facial-animation/human-lipsync-preview.png",
            "receipt_url":f"/files/{row['job_id']}/human/human-lipsync-receipt.json",
            "replayed":replayed,
            "source":"existing MGR Human Forge generic mannequin",
            "real_blender_verified":True,
            "audio_alignment_performed":False,
            "source_wav_loudness_reactive":bool(data.get("source_wav_loudness_reactive")),
            "owner_visual_approved":False,
            "neural_generation_used":False}

def _worker(studio,rid,job,timings,fps,audio_wav=None):
    try:
        from .human_lipsync import build_human_lipsync
        result=build_human_lipsync(timings,job/"human",blender=studio.blender,fps=fps,
                                    audio_wav=audio_wav)
        sha=result["glb_sha256"]
        with studio.world_job_lock:
            rows,path=_index(studio,LEDGER)
            current=rows.get(rid)
            if not current or current["job_id"]!=job.name or current["status"]!="RUNNING":
                raise RuntimeError("Human lip-sync job ledger changed while running")
            current["sha256"]=sha
            current["status"]="MATERIALIZED"
            _atomic_json(path,rows)
    except Exception as error:
        # Preserve a private forensic failure receipt; never claim a missing
        # animated GLB was produced, and never return raw exception paths
        # or credential material over the public API.
        import traceback
        safe_type=type(error).__name__
        detail={"schema":"mgr.forge.human-worker-error.v1",
                "job_id":job.name,"request_id":rid,
                "state":"FAILED",
                "error_type":safe_type,
                "error_detail_private":str(error)[:600],
                "stack_private":traceback.format_exc(limit=5)[-1500:]}
        (job/"human-error.json").write_text(json.dumps(detail,sort_keys=True,indent=2)+"\n",encoding="utf8")
        with studio.world_job_lock:
            rows,path=_index(studio,LEDGER)
            if rid in rows and rows[rid]["status"]=="RUNNING":
                rows[rid]["status"]="FAILED"
                rows[rid]["failure_type"]=safe_type
                _atomic_json(path,rows)
    finally:
        with studio.world_job_lock:
            studio.human_active_jobs.discard(rid)
            studio.heavy_worker_slot.release()

def start_human_lipsync_job(studio,payload):
    rid,raw,wav_bytes=_validated(payload)
    fingerprint=hashlib.sha256(raw).hexdigest()
    with studio.world_job_lock:
        rows,path=_index(studio,LEDGER)
        previous=rows.get(rid)
        if previous is not None:
            if previous["fingerprint"]!=fingerprint:
                raise ValueError("same human request ID reused with altered timings")
            return _readback(studio,rid,previous,replayed=True)
        if len(rows)>=1000:raise ValueError("Human Forge journal full")
        if not studio.heavy_worker_slot.acquire(blocking=False):
            return {"status":"BUSY","request_id":rid,
                    "reason":"another original Blender creation is active"}
        job_id,job=studio.create_job()
        (job/"human-request.json").write_bytes(raw)
        if wav_bytes is not None:
            (job/"human-original.wav").write_bytes(wav_bytes)
        rows[rid]={"status":"RUNNING","job_id":job_id,
                   "fingerprint":fingerprint}
        _atomic_json(path,rows)
        studio.human_active_jobs.add(rid)
        try:
            spec=payload["timings"] if wav_bytes is None else {"actor_id":payload["actor_id"]}
            audio_file=None if wav_bytes is None else job/"human-original.wav"
            thread=threading.Thread(target=_worker,args=(studio,rid,job,spec,payload["fps"],audio_file),
                                    daemon=True,name="mgr-human-lipsync-"+job_id)
            thread.start()
        except Exception:
            studio.human_active_jobs.discard(rid)
            studio.heavy_worker_slot.release()
            rows[rid]["status"]="FAILED"
            _atomic_json(path,rows)
            raise
        return _readback(studio,rid,rows[rid],replayed=False)

def human_lipsync_job_status(studio,rid):
    if not isinstance(rid,str) or not _ID.fullmatch(rid):
        raise ValueError("invalid human animation request ID")
    with studio.world_job_lock:
        rows,_=_index(studio,LEDGER)
        row=rows.get(rid)
        return {"status":"NOT_FOUND","request_id":rid} if row is None else _readback(studio,rid,row,replayed=True)
