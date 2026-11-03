"""Actual browser acceptance of native upload/revision/recovery and navigation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import start_server


def verify(out, hold=False):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    # Existing owned synthetic fixtures preserve their independent source identities.
    from tests.test_imported_morph import fixture
    from tests.test_uv_authoring import fixture as uv_fixture
    from tests.test_multiview import mask_png, square_grid
    (out / 'source.glb').write_bytes(fixture())
    (out / 'source-untextured.glb').write_bytes(uv_fixture())
    (out / 'mask.png').write_bytes(mask_png(square_grid(8, 0, 8)))
    build(WorldSpec(seed=54, columns=2, rows=2, buildings=2), out / 'world')
    phases = []
    for phase in ['create', 'restart']:
        server, studio = start_server(out / 'world', out / 'workspace')
        worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
        try:
            env = dict(os.environ, MGR_FORGE_QA_TOKEN=studio.token)
            script = ROOT / 'scripts/browser-qa/creation.mjs'
            process = subprocess.run(['node', str(script), f'http://127.0.0.1:{server.server_port}/', str(out), phase,
                                      'hold' if hold and phase == 'restart' else 'close'],
                                     env=env, cwd=script.parent, capture_output=True, text=True, timeout=360)
            if process.returncode:
                raise RuntimeError(process.stderr.replace(studio.token, '[redacted]')[-3000:])
            marker = 'MGR_CREATION_BROWSER='
            result = [json.loads(line[len(marker):]) for line in process.stdout.splitlines() if line.startswith(marker)]
            if len(result) != 1 or result[0]['status'] != 'PASS': raise RuntimeError('Browser proof missing')
            phases.append(result[0])
        finally:
            server.shutdown(); server.server_close(); worker.join(timeout=2)
    if len(list((out / 'workspace/jobs').iterdir())) != 3: raise RuntimeError('Unexpected duplicate job')
    receipt = {'status': 'PASS', 'actual_browser': 'installed Chrome headless', 'phases': phases,
               'native_jobs': 3, 'fresh_server_restart': True, 'model_provider_calls': 0,
               'source_sha256': hashlib.sha256((out / 'source.glb').read_bytes()).hexdigest(),
               'limits': 'Original synthetic static GLB and calibrated masks; no arbitrary photo likeness or production claim.'}
    (out / 'browser-proof.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
    print('MGR_CREATION_BROWSER_VERIFIED', out / 'browser-proof.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True); parser.add_argument('--hold-rea', action='store_true')
    args = parser.parse_args(); verify(args.out, args.hold_rea)
