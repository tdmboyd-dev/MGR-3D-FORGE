"""Actual local Chrome saved-job recovery after restarting original Forge Studio.

Uses isolated temporary world/workspace; no owner accounts, providers or paid calls.
Outage/cancellation/altered-download probes are explicit browser route fixtures.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import start_server


def verify(out):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    destination = out / 'browser-history-receipt.json'
    if destination.exists():
        raise FileExistsError('Never overwrite a history acceptance receipt')
    script = ROOT / 'scripts' / 'browser-qa' / 'history.mjs'
    phases = []

    def browser(server, studio, phase, expected):
        environment = dict(os.environ)
        environment['MGR_FORGE_QA_TOKEN'] = studio.token
        environment['MGR_FORGE_QA_EXPECTED'] = json.dumps(expected)
        process = subprocess.run(['node', str(script), f'http://127.0.0.1:{server.server_port}/', str(out), phase],
                                 cwd=script.parent, env=environment, capture_output=True, text=True, timeout=240)
        if process.returncode:
            safe = process.stderr.replace(studio.token, '[redacted]')[-2000:]
            raise RuntimeError('Actual Chrome history trial failed: ' + safe)
        marker = 'MGR_HISTORY_CHROME_PROOF='
        rows = [json.loads(line[len(marker):]) for line in process.stdout.splitlines() if line.startswith(marker)]
        if len(rows) != 1 or rows[0].get('status') != 'PASS':
            raise RuntimeError('Missing actual browser history result')
        phases.append(rows[0])

    with tempfile.TemporaryDirectory(prefix='mgr-history-browser-') as temporary:
        root = Path(temporary)
        build(WorldSpec(seed=24, columns=2, rows=2, buildings=2), root / 'world')
        server, studio = start_server(root / 'world', root / 'workspace')
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            browser(server, studio, 'empty', [])
            creature = studio.command('/api/creature-create', {'request_id': 'history-browser-creature-001',
                'prompt': 'Invent an original winged forest creature', 'seed': 29, 'variants': 1, 'morph': {}})
            biome = studio.command('/api/biome-create', {'request_id': 'history-browser-biome-001',
                'biome': 'forest', 'seed': 31, 'resolution': 10})
            expected = [{'kind': 'creature', 'label': 'Creature', 'request_id': creature['request_id'], 'sha256': creature['creature_sha256']},
                        {'kind': 'biome', 'label': 'Terrain', 'request_id': biome['request_id'], 'sha256': biome['biome_sha256']}]
            before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in studio.workspace.glob('*-requests.json')}
            original_token = studio.token
        finally:
            server.shutdown(); server.server_close(); worker.join(timeout=2)
        # Fresh server/workstation, same saved journals and files, fresh credential.
        server, studio = start_server(root / 'world', root / 'workspace')
        worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
        try:
            if studio.token == original_token:
                raise RuntimeError('Restart did not rotate the Studio credential')
            browser(server, studio, 'restarted', expected)
            after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in studio.workspace.glob('*-requests.json')}
            original_preserved = all(after.get(name) == sha for name, sha in before.items())
            world_rows = json.loads((studio.workspace / 'world-requests.json').read_text(encoding='utf8'))
            if not original_preserved or len(world_rows) != 1 or len(list(studio.jobs.iterdir())) != 3:
                raise RuntimeError('History lookup changed journals or created duplicate jobs')
            receipt = {'schema': 'mgr.forge.history-browser-verification.v1', 'status': 'PASS',
                'actual_browser': 'installed Chrome, headless', 'phases': phases,
                'fresh_workstation_restart': True, 'fresh_token': True, 'original_journals_unchanged': True,
                'native_jobs_before': 2, 'native_jobs_after': 3, 'durable_world_clicks': 2,
                'durable_world_native_jobs': 1, 'model_provider_calls': 0,
                'hosted_mobile_or_owner_art_acceptance': False,
                'fixture_limits': 'HTTP outage, read cancellation and altered download are browser route fixtures; native artifacts and restart are real.'}
            destination.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n', encoding='utf8')
        finally:
            server.shutdown(); server.server_close(); worker.join(timeout=2)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    arguments = parser.parse_args()
    print('MGR_HISTORY_BROWSER_VERIFIED', verify(arguments.out))
