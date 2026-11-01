"""Asynchronous human facial Blender job on Forge's existing Studio owner worker.

This is a *job adapter* for the existing Human Forge build_human_lipsync
pipeline, not a second artist, geometry engine, model vault or MCP server.
"""
import hashlib,json,threading
from pathlib import Path
from .lipsync import _validate
from .world_jobs import _index,_atomic_json,_ID

LEDGER="human-lipsync-requests.json"

def _validated(payload):
    if not isinstance(payload,dict) or set(payload)!={"request_id","timings","fps"}:
        raise ValueError("human lip sync expects request_id, timings, fps")
    rid=payload["request_id"]
    if not isinstance(rid,str) or not _ID.fullmatch(rid):
        raise ValueError("invalid human animation request ID")
    events,duration=_validate(payload["timings"])
    fps=payload["fps"]
    if type(fps) is not int or not 12<=fps<=60:
        raise ValueError("human lip sync fps must be 12..60")
    raw=json.dumps(payload,sort_keys=True,allow_nan=False,separators=(",",":")).encode("utf8")
    if len(raw)>100_000:
        raise ValueError("human lip sync timings too large")
    return rid,raw

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
            "owner_visual_approved":False,
            "neural_generation_used":False}

def _worker(studio,rid,job,timings,fps):
    try:
        from .human_lipsync import build_human_lipsync
        result=build_human_lipsync(timings,job/"human",blender=studio.blender,fps=fps)
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

def start_human_lipsync_job(studio,payload):
    rid,raw=_validated(payload)
    fingerprint=hashlib.sha256(raw).hexdigest()
    with studio.world_job_lock:
        rows,path=_index(studio,LEDGER)
        previous=rows.get(rid)
        if previous is not None:
            if previous["fingerprint"]!=fingerprint:
                raise ValueError("same human request ID reused with altered timings")
            return _readback(studio,rid,previous,replayed=True)
        if len(rows)>=1000:raise ValueError("Human Forge journal full")
        job_id,job=studio.create_job()
        (job/"human-request.json").write_bytes(raw)
        rows[rid]={"status":"RUNNING","job_id":job_id,
                   "fingerprint":fingerprint}
        _atomic_json(path,rows)
        studio.human_active_jobs.add(rid)
        try:
            thread=threading.Thread(target=_worker,args=(studio,rid,job,payload["timings"],payload["fps"]),
                                    daemon=True,name="mgr-human-lipsync-"+job_id)
            thread.start()
        except Exception:
            studio.human_active_jobs.discard(rid)
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
