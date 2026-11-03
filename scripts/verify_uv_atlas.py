"""Actual static GLB -> original CPU UV atlas -> independent Blender checker."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forge.uv_authoring import author_uv_atlas
from tests.test_uv_authoring import fixture


def verify(output,blender):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=out/'original.glb';source.write_bytes(fixture(attributes=True))
    native=author_uv_atlas(source,out/'revision',expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    result=subprocess.run([str(blender),'--background','--factory-startup','--python',
        str(ROOT/'scripts/verify_uv_atlas_blender.py'),'--',str(source),str(out/'revision'),str(out/'blender')],
        capture_output=True,text=True,timeout=180)
    (out/'blender.log').write_text(result.stdout+result.stderr,encoding='utf8')
    path=out/'blender/blender-proof.json'
    if result.returncode or not path.is_file():raise RuntimeError('UV receiving proof missing; inspect saved log')
    proof=json.loads(path.read_text())
    if proof.get('status')!='INDEPENDENT_UV_ATLAS_IMPORT_CHECKER_RENDER_PASS':raise RuntimeError('UV receiver refused')
    receipt={'status':'ACTUAL_NATIVE_UV_ATLAS_PASS','native':native,'blender':proof,
             'fixture':'owned two-part static boxes with original colors/normals/tangents; diagnostic checker only'}
    (out/'verification.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--blender',default=r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
    args=parser.parse_args();result=verify(args.out,args.blender)
    print(json.dumps({'status':result['status'],'artifact_sha256':result['native']['artifact_sha256']}))
