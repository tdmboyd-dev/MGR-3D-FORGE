"""Read-only original-input verification using native creator identities.

No second ledger, creation retry, approval, normalization or cross-language hash.
Callers must still interpret RUNNING/FAILED/NEEDS_RECONCILIATION honestly.
"""
from . import world_jobs,creature_jobs,biome_jobs,human_jobs,world_composition_jobs


def verify_request(studio,payload):
    if not isinstance(payload,dict) or set(payload)!={'kind','request'}:
        raise ValueError('request verification requires exact kind and original request')
    kind=payload['kind'];request=payload['request']
    if not isinstance(request,dict):raise ValueError('original request must be an object')
    with studio.world_job_lock:
        if kind=='world':
            if set(request)!={'request_id','edits'}:raise ValueError('exact world request required')
            raw,world,fingerprint=world_jobs._binding(studio,request['request_id'],request['edits'])
            module=world_jobs;ledger='world-requests.json';file='edits.json';status=world_jobs.world_job_status;key='input_hash'
        elif kind=='creature':
            _,raw,fingerprint=creature_jobs._binding(request)
            module=creature_jobs;ledger=module.LEDGER;file='creature-request.json';status=module.creature_job_status;key='fingerprint'
        elif kind=='biome':
            raw,world,fingerprint=biome_jobs._binding(studio,request)
            module=biome_jobs;ledger=module.LEDGER;file='biome-request.json';status=module.biome_job_status;key='fingerprint'
        elif kind=='human':
            _,raw,_,fingerprint=human_jobs._binding(request)
            module=human_jobs;ledger=module.LEDGER;file='human-request.json';status=module.human_lipsync_job_status;key='fingerprint'
        elif kind=='composed':
            _,_,_,world,raw,fingerprint=world_composition_jobs._binding(studio,request)
            module=world_composition_jobs;ledger=module.LEDGER;file='world-compose-request.json';status=module.world_composition_status;key='fingerprint'
        else:raise ValueError('unsupported native request kind')
        rid=request['request_id'];rows,_=world_jobs._index(studio,ledger);row=rows.get(rid)
        if row is None:return {'status':'NOT_FOUND','request_id':rid,'request_kind':kind,'input_verified':False}
        if row.get(key)!=fingerprint:raise ValueError('stored job does not match original instructions or sources')
        saved=studio.valid_job(row.get('job_id'))/file
        if saved.is_symlink() or not saved.is_file() or saved.stat().st_size>1_100_000 or saved.read_bytes()!=raw:
            raise ValueError('original saved request changed; reconciliation required')
        result=status(studio,rid)
        if result.get('request_id')!=rid or result.get('job_id')!=row.get('job_id'):
            raise ValueError('native request identity changed during verification')
        return {**result,'request_kind':kind,'input_verified':True,'input_fingerprint':fingerprint}
