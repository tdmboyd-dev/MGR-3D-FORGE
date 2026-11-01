"""World Forge optional biome creation via existing Studio job/ledger controller.

Does not modify already-authored city roads/buildings or regenerate their GLB.
"""
import hashlib,json
from pathlib import Path
from .environment import write_biome_shell,BIOME_TYPES
from .world_jobs import _index,_atomic_json,_ID
from .glb import inspect_glb

LEDGER="biome-requests.json"

def _validate(payload):
    if not isinstance(payload,dict) or set(payload)!={"request_id","biome","seed","resolution"}:
        raise ValueError("biome job requires request_id, biome, seed and resolution")
    rid=payload["request_id"]
    if not isinstance(rid,str) or not _ID.fullmatch(rid):
        raise ValueError("invalid stable biome request ID")
    if payload["biome"] not in BIOME_TYPES or type(payload["seed"]) is not int or not 0<=payload["seed"]<2**32:
        raise ValueError("invalid biome/seed")
    if type(payload["resolution"]) is not int or not 10<=payload["resolution"]<=64:
        raise ValueError("invalid terrain resolution")
    return json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf8")

def _readback(studio,rid,row,*,replayed):
    if row["status"]!="MATERIALIZED":
        return {"status":"NEEDS_RECONCILIATION","request_id":rid,
                "job_id":row.get("job_id"),"replayed":replayed}
    job=studio.valid_job(row["job_id"])
    target=job/"biome"/"biome.glb"
    if target.is_symlink() or not target.is_file() or target.stat().st_size>30_000_000:
        raise RuntimeError("biome artifact missing or outside safe size")
    raw=target.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=row.get("sha256") or not inspect_glb(raw)["triangles"]:
        raise RuntimeError("biome output corrupted; no false success")
    return {"status":"MATERIALIZED","request_id":rid,"job_id":row["job_id"],
            "biome_sha256":sha,"biome_bytes":len(raw),"biome":row["biome"],
            "triangles":inspect_glb(raw)["triangles"],
            "glb_url":f"/files/{row['job_id']}/biome/biome.glb",
            "manifest_url":f"/files/{row['job_id']}/biome/biome.json",
            "source_world_sha256":row["world_sha256"],"replayed":replayed,
            "external_model_used":False,"added_as_layer":True,
            "editor_world_unchanged":True,"engine_visual_accepted":False}

def _binding(studio,payload):
    encoded=_validate(payload)
    world_hash=hashlib.sha256((studio.world/"world.glb").read_bytes()).hexdigest()
    fingerprint=hashlib.sha256(world_hash.encode()+b":"+encoded).hexdigest()
    return encoded,world_hash,fingerprint


def create_biome_job(studio,payload):
    encoded,world_hash,fingerprint=_binding(studio,payload)
    rid=payload["request_id"]
    with studio.world_job_lock:
        rows,path=_index(studio,LEDGER)
        previous=rows.get(rid)
        if previous:
            if previous.get("fingerprint")!=fingerprint:
                raise ValueError("biome request ID changed source or settings")
            return _readback(studio,rid,previous,replayed=True)
        if len(rows)>=1000:raise ValueError("biome journal full")
        job_id,job=studio.create_job()
        rows[rid]={"status":"STARTED","fingerprint":fingerprint,
                   "world_sha256":world_hash,"job_id":job_id,
                   "biome":payload["biome"]}
        _atomic_json(path,rows)
        try:
            (job/"biome-request.json").write_bytes(encoded)
            doc=write_biome_shell(studio.world,job/"biome",biome=payload["biome"],
                                  seed=payload["seed"],resolution=payload["resolution"])
            rows[rid]["sha256"]=doc["artifact"]["sha256"]
            rows[rid]["status"]="MATERIALIZED"
            _atomic_json(path,rows)
        except Exception:
            rows[rid]["status"]="NEEDS_RECONCILIATION"
            _atomic_json(path,rows)
            raise
        return _readback(studio,rid,rows[rid],replayed=False)

def biome_job_status(studio,rid):
    if not isinstance(rid,str) or not _ID.fullmatch(rid):
        raise ValueError("invalid stable biome request ID")
    with studio.world_job_lock:
        rows,_=_index(studio,LEDGER)
        current=rows.get(rid)
        return {"status":"NOT_FOUND","request_id":rid} if current is None else _readback(
            studio,rid,current,replayed=True)
