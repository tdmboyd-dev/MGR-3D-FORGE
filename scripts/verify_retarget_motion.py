"""Actual cross-rest skeleton transfer and frozen-animation receiving refusal."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forge.retarget_motion import retarget_motion
from tests.test_retarget_motion import RECIPE


def run_blender(blender,script,out,log):
    result=subprocess.run([str(blender),'--background','--factory-startup','--python-exit-code','1','--python',
                           str(script),'--',str(out)],capture_output=True,text=True,timeout=180)
    raw=result.stdout+result.stderr;log.write_text(raw,encoding='utf8')
    return result.returncode,raw


def verify(out,blender):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    originals=out/'originals'
    code,_=run_blender(blender,ROOT/'scripts/verify_retarget_fixture_blender.py',originals,out/'fixture.log')
    if code:raise RuntimeError('real original source/target fixture creation failed; inspect fixture log')
    source,target=originals/'source-original.glb',originals/'target-original.glb'
    source_sha=hashlib.sha256(source.read_bytes()).hexdigest();target_sha=hashlib.sha256(target.read_bytes()).hexdigest()
    revision=out/'revision'
    positive=retarget_motion(source,target,revision,RECIPE,source_sha256=source_sha,target_sha256=target_sha,blender=blender)
    if (revision/'source-original.glb').read_bytes()!=source.read_bytes() or (revision/'target-original.glb').read_bytes()!=target.read_bytes():
        raise RuntimeError('native motion retarget failed to preserve original bytes')
    bad=out/'frozen-animation';bad.mkdir()
    for name in ('source-original.glb','target-original.glb','motion-map.json','retargeted.blend'):
        shutil.copyfile(revision/name,bad/name)
    raw=(revision/'retargeted.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+size]);binary=bytearray(raw[28+size:]);changed=set()
    for clip in doc['animations']:
        for channel in clip['channels']:
            if channel['target']['path']!='rotation':continue
            index=clip['samplers'][channel['sampler']]['output']
            if index in changed:continue
            changed.add(index);acc=doc['accessors'][index];view=doc['bufferViews'][acc['bufferView']]
            if acc['type']!='VEC4' or acc['componentType']!=5126:raise RuntimeError('unexpected fixture rotation encoding')
            start=view.get('byteOffset',0)+acc.get('byteOffset',0);stride=view.get('byteStride',16)
            initial=bytes(binary[start:start+16])
            for i in range(acc['count']):binary[start+i*stride:start+i*stride+16]=initial
    if not changed:raise RuntimeError('actual exported rotation channels absent')
    frozen=raw[:28+size]+bytes(binary)
    (bad/'retargeted.glb').write_bytes(frozen)
    creator=json.loads((revision/'retarget-creator.json').read_text());creator['artifact_sha256']=hashlib.sha256(frozen).hexdigest()
    (bad/'retarget-creator.json').write_text(json.dumps(creator),encoding='utf8')
    code,log=run_blender(blender,ROOT/'bridge/blender_motion_retarget_receive.py',bad,out/'frozen-receiver.log')
    if not code or 'received target rotations do not follow original mapped source clip' not in log or (bad/'retarget-blender-proof.json').exists():
        raise RuntimeError('independent receiving witness did not explicitly refuse frozen clip')
    report={'schema':'mgr.forge.retarget-regression.v1','status':'ACTUAL_MAPPED_CROSS_SKELETON_RETARGET_PASS',
            'native':positive,'negative':{'frozen_rotation_accessors':len(changed),'sha256':creator['artifact_sha256'],
                                         'skeleton_skin_action_inventories_retained':True,
                                         'independently_refused_for_wrong_mapped_rotations':True},
            'fixture':'original two-bone animated source and differently named/angled/rolled/longer three-bone target with owned texture'}
    (out/'verification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--blender',default=r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
    args=parser.parse_args();result=verify(args.out,args.blender)
    print(json.dumps({'status':result['status'],'artifact_sha256':result['native']['artifact_sha256'],
                      'frozen_clip_refused':result['negative']['independently_refused_for_wrong_mapped_rotations']}))
