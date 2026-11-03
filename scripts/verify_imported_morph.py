"""Original textured static asset -> CPU morph -> independent real Blender proof."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.test_imported_morph import fixture
from forge.imported_morph import morph_imported_glb


def verify(out, blender):
    out = Path(out).resolve()
    if out.exists():raise FileExistsError('preserve prior imported morph verification')
    out.mkdir(parents=True)
    original = fixture()
    source = out/'original-owned-parts.glb'
    source.write_bytes(original)
    sha = hashlib.sha256(original).hexdigest()
    receipt = morph_imported_glb(source, out/'revision', {'length': 1.25, 'height': 1.6,
        'width': .8, 'twist_degrees': 20, 'bend_degrees': 18, 'taper': 1.2}, expected_sha256=sha)
    command = [str(blender), '--background', '--factory-startup', '--python',
               str(ROOT/'scripts/verify_imported_morph_blender.py'), '--',
               str(source), str(out/'revision/morphed.glb'), str(out/'revision/morph-receipt.json'), str(out/'blender')]
    result = subprocess.run(command, capture_output=True, text=True, timeout=240)
    (out/'blender.log').write_text(result.stdout+result.stderr, encoding='utf8')
    proof = out/'blender/blender-proof.json'
    if result.returncode or not proof.is_file():raise RuntimeError('independent Blender morph witness failed; preserved log')
    found = json.loads(proof.read_text(encoding='utf8'))
    if found.get('status') != 'INDEPENDENT_BLENDER_STATIC_MORPH_IMPORT_RENDER_PASS':
        raise RuntimeError('independent static morph proof refused')
    if hashlib.sha256(source.read_bytes()).hexdigest() != sha:
        raise RuntimeError('original source changed during the real workflow')
    return {'status': 'ACTUAL_STATIC_MORPH_ACCEPTANCE_PASS', 'native': receipt,
            'blender': found, 'fixture': 'original CPU-authored two-part GLB with embedded 2x2 image and UVs; not a paid or photoreal asset'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--blender', default=r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
    args = parser.parse_args()
    result = verify(args.out, args.blender)
    (args.out/'verification.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'status': result['status'], 'artifact_sha256': result['native']['artifact_sha256']}))
