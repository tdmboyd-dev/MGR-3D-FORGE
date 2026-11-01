"""Native original-creature durable request adapter for the existing Forge Studio.

Reuses ForgeWorkstation, job directories, owner lock and WorldJob journal
primitives; no second server, remote renderer, model weights or asset store.
"""
import hashlib, json, math, re
from pathlib import Path
from .imagination import create_original_creature
from .morph_engine import normalize_morph
from .glb import inspect_glb
from .world_jobs import _atomic_json, _index, _ID

LEDGER="creature-requests.json"
MAX_REQUEST_BYTES=2000

def _validate(request):
    if not isinstance(request,dict) or set(request)!={"request_id","prompt","seed","variants","morph"}:
        raise ValueError("creature creation requires exact bounded request fields")
    rid,prompt,seed,variants=request["request_id"],request["prompt"],request["seed"],request["variants"]
    if not isinstance(rid,str) or not _ID.fullmatch(rid):
        raise ValueError("stable creature request ID invalid")
    if not isinstance(prompt,str) or not 8<=len(prompt.strip())<=500 or (
          any(ord(c)<32 and c not in "\n\t" for c in prompt)):
        raise ValueError("creature prompt outside supported bounds")
    if type(seed) is not int or not 0<=seed<2**32:
        raise ValueError("seed invalid")
    if type(variants) is not int or not 1<=variants<=12:
        raise ValueError("variants outside 1..12")
    morph=normalize_morph(request["morph"])
    data={"request_id":rid,"prompt":prompt.strip(),"seed":seed,"variants":variants,"morph":morph}
    canonical=json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf8")
    if len(canonical)>MAX_REQUEST_BYTES:
        raise ValueError("request too large")
    return data,canonical

def _receipt(studio,rid,row,*,replayed):
    if row.get("status")!="MATERIALIZED":
        return {"status":"NEEDS_RECONCILIATION","request_id":rid,
                "job_id":row.get("job_id"),"replayed":replayed}
    job=studio.valid_job(row.get("job_id"))
    mesh=job/"creature"/"creature.glb"
    if mesh.is_symlink() or not mesh.is_file() or mesh.stat().st_size>50_000_000:
        raise RuntimeError("stored Forge creature artifact missing or corrupted")
    raw=mesh.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=row.get("sha256"):
        raise RuntimeError("stored creature SHA-256 changed; reconciliation required")
    found=inspect_glb(raw)
    if not found["triangles"] or raw[:4]!=b"glTF":
        raise RuntimeError("stored creator asset is not real GLB")
    return {"status":"MATERIALIZED","request_id":rid,"job_id":row["job_id"],
            "creature_sha256":row["sha256"],"creature_bytes":len(raw),
            "triangles":found["triangles"],
            "glb_url":f"/files/{row['job_id']}/creature/creature.glb",
            "manifest_url":f"/files/{row['job_id']}/creature/creature.json",
            "model_inference_used":False,"external_spend_usd":0,
            "independently_blender_verified":False,
            "owner_art_accepted":False,"replayed":replayed}

def creature_job_status(studio,rid):
    if not isinstance(rid,str) or not _ID.fullmatch(rid):
        raise ValueError("invalid stable creature request ID")
    with studio.world_job_lock:
        rows,_=_index(studio,LEDGER)
        row=rows.get(rid)
        return {"status":"NOT_FOUND","request_id":rid} if row is None else _receipt(studio,rid,row,replayed=True)

def _binding(request):
    data,encoded=_validate(request)
    fingerprint=hashlib.sha256(encoded).hexdigest()
    return data,encoded,fingerprint


def create_creature_job(studio,request):
    data,encoded,fingerprint=_binding(request)
    rid=data["request_id"]
    with studio.world_job_lock:
        rows,path=_index(studio,LEDGER)
        previous=rows.get(rid)
        if previous is not None:
            if previous.get("fingerprint")!=fingerprint:
                raise ValueError("creature request ID reused with different instructions")
            return _receipt(studio,rid,previous,replayed=True)
        if len(rows)>=1000:raise ValueError("creature request ledger full")
        jid,job=studio.create_job()
        rows[rid]={"status":"STARTED","fingerprint":fingerprint,"job_id":jid}
        _atomic_json(path,rows)
        try:
            (job/"creature-request.json").write_bytes(encoded)
            result=create_original_creature(
                data["prompt"],job/"creature",seed=data["seed"],variants=data["variants"],morph=data["morph"])
            artifact=job/"creature"/"creature.glb"
            blob=artifact.read_bytes()
            if hashlib.sha256(blob).hexdigest()!=result["artifact"]["sha256"]:
                raise RuntimeError("native generator produced inconsistent hash")
            rows[rid]["sha256"]=result["artifact"]["sha256"]
            rows[rid]["status"]="MATERIALIZED"
            _atomic_json(path,rows)
        except Exception:
            rows[rid]["status"]="NEEDS_RECONCILIATION"
            _atomic_json(path,rows)
            raise
        return _receipt(studio,rid,rows[rid],replayed=False)
