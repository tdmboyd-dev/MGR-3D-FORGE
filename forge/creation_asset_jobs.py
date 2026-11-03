"""Image reconstruction and static imported-mesh revisions on original Studio jobs.

Original native implementations own geometry. This adapter binds bounded uploaded
bytes to existing workspace journals, immutable request IDs and exact artifacts.
"""
import base64
import binascii
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from .glb import inspect_glb
from .image_relief import decode_png
from .morph_engine import normalize_morph
from .world_jobs import _atomic_json, _index, _ID

KINDS = {
    'reconstruction': ('reconstruction-requests.json', 'reconstructed', 'hull.glb', 'reconstruction.json'),
    'morph': ('morph-requests.json', 'morphed', 'morphed.glb', 'morph-receipt.json'),
    'uv': ('uv-requests.json', 'uv', 'uv-mapped.glb', 'uv-receipt.json'),
}
MAX_UPLOAD = 900_000
MAX_SAVED_REQUEST = 1_800_000
MAX_UV_RECEIPT = 8_000_000


def _binary(value):
    if not isinstance(value, str) or not 4 <= len(value) <= 1_200_000:
        raise ValueError('uploaded asset outside bounded base64 size')
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError('invalid uploaded asset base64') from error
    if not raw or len(raw) > MAX_UPLOAD:
        raise ValueError('uploaded asset outside byte budget')
    return raw


def _binding(kind, request):
    if not isinstance(kind, str) or kind not in KINDS or not isinstance(request, dict):
        raise ValueError('supported exact asset request required')
    fields = ({'request_id', 'glb_base64', 'expected_sha256', 'morph'} if kind == 'morph' else
              {'request_id', 'glb_base64', 'expected_sha256', 'atlas_size', 'padding'} if kind == 'uv' else
              {'request_id', 'front_png_base64', 'side_png_base64', 'bounds', 'grid', 'surface'})
    if set(request) != fields or not isinstance(request.get('request_id'), str) or not _ID.fullmatch(request['request_id']):
        raise ValueError('asset request fields or stable request identity invalid')
    if kind in ('morph', 'uv'):
        source = _binary(request['glb_base64'])
        expected = request['expected_sha256']
        if not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected) or hashlib.sha256(source).hexdigest() != expected:
            raise ValueError('uploaded original model does not match expected SHA-256')
        if kind == 'morph':
            normalize_morph(request['morph'])
        elif (type(request['atlas_size']) is not int or request['atlas_size'] not in (256, 512, 1024, 2048, 4096)
              or type(request['padding']) is not int or not 1 <= request['padding'] <= 16):
            raise ValueError('UV atlas size or padding outside native supported choices')
        sources = {'original-upload.glb': source}
    else:
        from .multiview import _validate_bounds
        if not isinstance(request['bounds'], dict) or set(request['bounds']) != {'width', 'height', 'depth'}:
            raise ValueError('exact physical width, height and depth required')
        _validate_bounds(request['bounds'])
        if type(request['grid']) is not int or not 8 <= request['grid'] <= 64 or request['surface'] not in ('voxel', 'smooth'):
            raise ValueError('interactive reconstruction grid must be 8..64 with voxel or smooth surface')
        sources = {'front.png': _binary(request['front_png_base64']), 'side.png': _binary(request['side_png_base64'])}
        for raw in sources.values():
            decode_png(raw)
    encoded = json.dumps(request, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf8')
    if len(encoded) > MAX_SAVED_REQUEST:
        raise ValueError('combined asset request exceeds byte budget')
    fingerprint = hashlib.sha256(kind.encode() + b':' + encoded).hexdigest()
    return encoded, fingerprint, sources


def _prepared(kind, request, sources, scratch):
    if kind == 'uv':
        from .uv_authoring import validate_uv_glb
        receipt = validate_uv_glb(sources['original-upload.glb'], expected_sha256=request['expected_sha256'],
                                  atlas_size=request['atlas_size'], padding=request['padding'])
        # Atlas charts are per-triangle; their receipt can legitimately exceed
        # other jobs' 1 MB cap. Reserve the bounded writer's checker metadata.
        if len(json.dumps(receipt, sort_keys=True, indent=2).encode('utf8')) > MAX_UV_RECEIPT - 1024:
            raise ValueError('UV atlas receipt exceeds native saved budget')
        return receipt
    if kind == 'morph':
        from .imported_morph import validate_imported_glb
        return validate_imported_glb(sources['original-upload.glb'], request['morph'],
                                     expected_sha256=request['expected_sha256'])
    from .multiview import prepare_reconstruction
    for name, raw in sources.items():
        (scratch / name).write_bytes(raw)
    spec = {'bounds': request['bounds'], 'grid': request['grid'], 'base_dir': str(scratch),
            'views': [{'axis': 'front', 'mask': 'front.png'}, {'axis': 'left', 'mask': 'side.png'}]}
    return prepare_reconstruction(spec, marching=request['surface'] == 'smooth')


def asset_job_status(studio, kind, request_id):
    if not isinstance(kind, str) or kind not in KINDS or not isinstance(request_id, str) or not _ID.fullmatch(request_id):
        raise ValueError('invalid native asset job identity')
    with studio.world_job_lock:
        ledger, directory, model, manifest = KINDS[kind]
        rows, _ = _index(studio, ledger)
        row = rows.get(request_id)
        if row is None:
            return {'status': 'NOT_FOUND', 'request_id': request_id}
        if not isinstance(row, dict):
            raise ValueError('invalid stored asset journal')
        if row.get('status') != 'MATERIALIZED':
            return {'status': 'NEEDS_RECONCILIATION', 'request_id': request_id,
                    'job_id': row.get('job_id'), 'replayed': True}
        job = studio.valid_job(row.get('job_id'))
        original = job / 'asset-request.json'
        if original.is_symlink() or not original.is_file() or original.stat().st_size > MAX_SAVED_REQUEST:
            raise RuntimeError('saved original asset request missing or excessive')
        raw_request = original.read_bytes()
        if hashlib.sha256(kind.encode() + b':' + raw_request).hexdigest() != row.get('fingerprint'):
            raise RuntimeError('saved original asset request changed; reconciliation required')
        expected_names = {'original-upload.glb'} if kind in ('morph', 'uv') else {'front.png', 'side.png'}
        if not isinstance(row.get('source_sha256'), dict) or set(row['source_sha256']) != expected_names:
            raise RuntimeError('saved original source identities missing')
        for name, sha in row['source_sha256'].items():
            if name not in ('original-upload.glb', 'front.png', 'side.png'):
                raise RuntimeError('stored source identity invalid')
            path = job / name
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_UPLOAD or hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                raise RuntimeError('original uploaded source changed; reconciliation required')
        target = job / directory / model
        receipt = job / directory / manifest
        if (target.parent.is_symlink() or target.is_symlink() or not target.is_file() or
                target.stat().st_size > 64_000_000 or receipt.is_symlink() or not receipt.is_file() or
                receipt.stat().st_size > (MAX_UV_RECEIPT if kind == 'uv' else 1_000_000)):
            raise RuntimeError('saved asset output missing or excessive')
        raw = target.read_bytes()
        if hashlib.sha256(receipt.read_bytes()).hexdigest() != row.get('receipt_sha256'):
            raise RuntimeError('saved asset receipt changed; reconciliation required')
        if hashlib.sha256(raw).hexdigest() != row.get('sha256') or len(raw) != row.get('bytes'):
            raise RuntimeError('saved asset SHA-256 changed; reconciliation required')
        diagnostic = {}
        if kind == 'uv':
            checker = json.loads(receipt.read_text(encoding='utf8')).get('checker', {})
            path = target.parent / 'diagnostic-checker.png'
            if (not isinstance(checker, dict) or checker.get('file') != path.name or path.is_symlink() or
                    not path.is_file() or path.stat().st_size > 5_000_000 or
                    path.stat().st_size != checker.get('bytes') or hashlib.sha256(path.read_bytes()).hexdigest() != checker.get('sha256')):
                raise RuntimeError('saved UV diagnostic changed; reconciliation required')
            diagnostic = {'diagnostic_url': f'/files/{row["job_id"]}/uv/{path.name}',
                          'diagnostic_sha256': checker['sha256'], 'diagnostic_bytes': checker['bytes']}
        inspect_glb(raw)
        return {'status': 'MATERIALIZED', 'request_id': request_id, 'job_id': row['job_id'],
                'asset_sha256': row['sha256'], 'asset_bytes': len(raw),
                'glb_url': f'/files/{row["job_id"]}/{directory}/{model}',
                'manifest_url': f'/files/{row["job_id"]}/{directory}/{manifest}',
                'source_sha256': row['source_sha256'], 'replayed': True,
                'kind': kind, 'model_inference_used': False, 'owner_art_accepted': False,
                **diagnostic, 'method': {'reconstruction': 'measured-silhouette-hull', 'morph': 'static-original-mesh-morph',
                           'uv': 'fully-seamed-padded-triangle-uv-atlas'}[kind]}


def create_asset_job(studio, kind, request):
    encoded, fingerprint, sources = _binding(kind, request)
    rid = request['request_id']
    with studio.world_job_lock:
        ledger, directory, model, manifest = KINDS[kind]
        rows, journal = _index(studio, ledger)
        if rid in rows:
            if rows[rid].get('fingerprint') != fingerprint:
                raise ValueError('asset request ID reused with changed original input')
            return asset_job_status(studio, kind, rid)
        if len(rows) >= 1000:
            raise ValueError('asset request journal full; preserve existing work')
        # Full native preflight precedes persistent request/job allocation.
        with TemporaryDirectory(prefix='mgr-asset-prepare-', dir=studio.workspace) as temporary:
            prepared = _prepared(kind, request, sources, Path(temporary))
        jid, job = studio.create_job()
        rows[rid] = {'status': 'STARTED', 'job_id': jid, 'fingerprint': fingerprint,
                     'source_sha256': {name: hashlib.sha256(raw).hexdigest() for name, raw in sources.items()}}
        try:
            _atomic_json(journal, rows)
        except Exception:
            # A failed admission write may have committed before reporting an
            # error. Preserve that original identity, or any ambiguous journal.
            # Only discard our still-empty allocation when the original journal
            # can positively establish that neither this request nor job owns it.
            try:
                try:
                    journal.lstat()
                except FileNotFoundError:
                    admitted = {}
                else:
                    if journal.is_symlink():
                        raise ValueError('ambiguous admission journal')
                    admitted, _ = _index(studio, ledger)
                    if any(not isinstance(row, dict) or not isinstance(row.get('job_id'), str)
                           or not re.fullmatch('[a-f0-9]{24}', row['job_id']) for row in admitted.values()):
                        raise ValueError('ambiguous admission journal rows')
                if rid not in admitted and not any(row.get('job_id') == jid for row in admitted.values()):
                    if not job.is_symlink():
                        job.rmdir()  # no recursive deletion, never remove populated work
            except (OSError, ValueError, UnicodeError):
                pass  # retain uncertainty; never replace the original admission error
            raise
        try:
            (job / 'asset-request.json').write_bytes(encoded)
            for name, raw in sources.items():
                (job / name).write_bytes(raw)
            if kind == 'uv':
                from .uv_authoring import author_uv_atlas
                author_uv_atlas(job / 'original-upload.glb', job / directory,
                                expected_sha256=request['expected_sha256'], atlas_size=request['atlas_size'], padding=request['padding'])
            elif kind == 'morph':
                from .imported_morph import morph_imported_glb
                morph_imported_glb(job / 'original-upload.glb', job / directory, request['morph'],
                                   expected_sha256=request['expected_sha256'])
            else:
                from .multiview import export_prepared_reconstruction
                export_prepared_reconstruction(*prepared, job / directory)
                (job / 'reconstruction-spec.json').write_text(json.dumps({
                    'bounds': request['bounds'], 'grid': request['grid'],
                    'views': [{'axis': 'front', 'mask': 'front.png'}, {'axis': 'left', 'mask': 'side.png'}]}, indent=2), encoding='utf8')
            raw = (job / directory / model).read_bytes()
            inspect_glb(raw)
            rows[rid].update(status='MATERIALIZED', sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                             receipt_sha256=hashlib.sha256((job / directory / manifest).read_bytes()).hexdigest())
            _atomic_json(journal, rows)
        except Exception:
            rows[rid]['status'] = 'NEEDS_RECONCILIATION'
            _atomic_json(journal, rows)
            raise
        return {**asset_job_status(studio, kind, rid), 'replayed': False}


def verify_asset_request(studio, kind, request):
    encoded, fingerprint, _ = _binding(kind, request)
    rid = request['request_id']
    with studio.world_job_lock:
        rows, _ = _index(studio, KINDS[kind][0])
        if rid not in rows:
            return {'status': 'NOT_FOUND', 'request_id': rid, 'input_verified': False, 'request_kind': kind}
        row = rows[rid]
        if row.get('fingerprint') != fingerprint:
            raise ValueError('stored asset job does not match original input')
        path = studio.valid_job(row.get('job_id')) / 'asset-request.json'
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SAVED_REQUEST or path.read_bytes() != encoded:
            raise ValueError('original asset request changed; reconciliation required')
        result = asset_job_status(studio, kind, rid)
        return {**result, 'request_kind': kind, 'input_verified': True, 'input_fingerprint': fingerprint}
