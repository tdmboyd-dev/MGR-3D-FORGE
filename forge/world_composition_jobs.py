"""Existing Forge Studio: durable original city+biome composition in real Blender.

Same ForgeWorkstation, job ID, SHA journal, shared heavy-worker cap and token
file delivery; NO duplicate project, approval router, backup or backend.
"""
import hashlib,json,threading,zipfile
from pathlib import Path
from .world_jobs import _index,_atomic_json,_ID
from .glb import inspect_glb

LEDGER="world-composition-requests.json"

def _validate(input_data):
    if not isinstance(input_data,dict) or set(input_data)!={"request_id","biome_request_id"}:
        raise ValueError("world composition accepts only request_id and biome_request_id")
    a,b=input_data["request_id"],input_data["biome_request_id"]
    if not all(isinstance(x,str) and _ID.fullmatch(x) for x in (a,b)):
        raise ValueError("invalid world composition or biome request ID")
    return a,b

def _get_biome(studio,biome_request):
    from .biome_jobs import LEDGER as B_LEDGER
    entries,_=_index(studio,B_LEDGER)
    chosen=entries.get(biome_request)
    if not chosen or chosen.get("status")!="MATERIALIZED":
        raise ValueError("an already MATERIALIZED original MGR World biome required")
    directory=studio.valid_job(chosen["job_id"])/"biome"
    source=directory/"biome.glb"
    if source.is_symlink() or not source.is_file() or source.stat().st_size>30_000_000 or (
         hashlib.sha256(source.read_bytes()).hexdigest()!=chosen.get("sha256")):
        raise ValueError("saved biome GLB has changed; do not combine a corrupt source")
    return directory,chosen["sha256"]

def _readback(studio,rid,row,*,replayed):
    if row["status"]!="MATERIALIZED":
        return {"status":"RUNNING" if row["status"]=="RUNNING" and
                rid in getattr(studio,"composed_active_jobs",set()) else (
                    "NEEDS_RECONCILIATION" if row["status"]=="RUNNING" else row["status"]),
                "request_id":rid,"job_id":row["job_id"],"replayed":replayed}
    job=studio.valid_job(row["job_id"])/"composed"
    file=job/"world.glb"
    receipt=job/"composition-receipt.json"
    blend=job/"world-composed.blend"
    preview=job/"world-composed-preview.png"
    godot=job/"godot-project.zip"
    for one in (file,receipt,blend,preview,godot):
        if one.is_symlink() or not one.is_file() or one.stat().st_size>100_000_000:
            raise RuntimeError("original World Forge composed output missing or oversized")
    raw=file.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=row["sha256"] or raw[:4]!=b"glTF":
        raise RuntimeError("composed World GLB changed from durable job")
    report=json.loads(receipt.read_text(encoding="utf8"))
    if report["status"]!="BLENDER_COMPOSED_INDEPENDENT_REOPEN" or report["combined_world_sha256"]!=sha:
        raise RuntimeError("composed World receipt missing independent Blender proof")
    geometry=inspect_glb(raw)
    if geometry["triangles"]<=0:raise RuntimeError("no actual composed geometry")
    return {"status":"MATERIALIZED","request_id":rid,"job_id":row["job_id"],
            "replayed":replayed,"combined_world_sha256":sha,
            "world_sha256":row["original_world_sha256"],
            "biome_sha256":row["source_biome_sha256"],
            "combined_bytes":len(raw),"triangles":geometry["triangles"],
            "glb_url":f"/files/{row['job_id']}/composed/world.glb",
            "blend_url":f"/files/{row['job_id']}/composed/world-composed.blend",
            "preview_url":f"/files/{row['job_id']}/composed/world-composed-preview.png",
            "godot_url":f"/files/{row['job_id']}/composed/godot-project.zip",
            "receipt_url":f"/files/{row['job_id']}/composed/composition-receipt.json",
            "independently_blender_verified":True,
            "full_game_navigation_verified":False,
            "hosted_chatgpt_verified":False,"user_art_accepted":False}

def _compose_worker(studio,rid,job,biome):
    try:
        from .world_composition import compose_world
        output=job/"composed"
        result=compose_world(studio.world,biome,output,blender=studio.blender)
        if result["status"]!="BLENDER_COMPOSED_INDEPENDENT_REOPEN":
            raise RuntimeError("Blender did not approve original combined geometry")
        archive=output/"godot-project.zip"
        if archive.exists():raise FileExistsError("cannot override existing Godot archive")
        with zipfile.ZipFile(archive,"x",compression=zipfile.ZIP_DEFLATED) as package:
            for item in ("project.godot","world.tscn","assets/world.glb","handoff.json"):
                package.write(output/"godot-project"/item,arcname=item)
        with studio.world_job_lock:
            entries,path=_index(studio,LEDGER)
            row=entries.get(rid)
            if not row or row.get("status")!="RUNNING":
                raise RuntimeError("world composition journal changed while creating")
            row["sha256"]=result["combined_world_sha256"]
            row["status"]="MATERIALIZED"
            _atomic_json(path,entries)
    except Exception as exc:
        import traceback
        detail={"schema":"mgr.forge.world-composer-worker-error.v1",
                "failure_type":type(exc).__name__,
                "error_private":str(exc)[:550],
                "stack_private":traceback.format_exc(limit=5)[-1600:]}
        (job/"compose-error.json").write_text(json.dumps(detail,indent=2,sort_keys=True)+"\n",encoding="utf8")
        with studio.world_job_lock:
            entries,path=_index(studio,LEDGER)
            if rid in entries and entries[rid]["status"]=="RUNNING":
                entries[rid]["status"]="FAILED"
                entries[rid]["failure_type"]=type(exc).__name__
                _atomic_json(path,entries)
    finally:
        with studio.world_job_lock:
            studio.composed_active_jobs.discard(rid)
            studio.heavy_worker_slot.release()

def _binding(studio,payload):
    rid,biome_request=_validate(payload)
    directory,biome_sha=_get_biome(studio,biome_request)
    world_sha=hashlib.sha256((studio.world/"world.glb").read_bytes()).hexdigest()
    encoded=json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf8")
    fingerprint=hashlib.sha256(world_sha.encode()+b":"+biome_sha.encode()+b":"+encoded).hexdigest()
    return rid,directory,biome_sha,world_sha,encoded,fingerprint


def start_world_composition(studio,payload):
    with studio.world_job_lock:
        rid,directory,biome_sha,world_sha,encoded,fingerprint=_binding(studio,payload)
        entries,path=_index(studio,LEDGER)
        previous=entries.get(rid)
        if previous:
            if previous.get("fingerprint")!=fingerprint:
                raise ValueError("world composition ID reused with different source or settings")
            return _readback(studio,rid,previous,replayed=True)
        if len(entries)>=300:raise ValueError("world composition journal full")
        if not studio.heavy_worker_slot.acquire(blocking=False):
            return {"status":"BUSY","request_id":rid,
                    "reason":"another real Blender creation is active; retry after it finishes"}
        try:
            job_id,job=studio.create_job()
            (job/"world-compose-request.json").write_bytes(encoded)
            entries[rid]={"status":"RUNNING","job_id":job_id,
                          "fingerprint":fingerprint,
                          "source_biome_sha256":biome_sha,
                          "original_world_sha256":world_sha}
            _atomic_json(path,entries)
            studio.composed_active_jobs.add(rid)
            worker=threading.Thread(target=_compose_worker,args=(studio,rid,job,directory),
                                    name="mgr-world-composition-"+job_id,daemon=True)
            worker.start()
        except Exception:
            studio.composed_active_jobs.discard(rid)
            studio.heavy_worker_slot.release()
            raise
        return _readback(studio,rid,entries[rid],replayed=False)

def world_composition_status(studio,request_id):
    if not isinstance(request_id,str) or not _ID.fullmatch(request_id):
        raise ValueError("invalid stable world composition ID")
    with studio.world_job_lock:
        entries,_=_index(studio,LEDGER)
        row=entries.get(request_id)
        return {"status":"NOT_FOUND","request_id":request_id} if row is None else _readback(
            studio,request_id,row,replayed=True)
