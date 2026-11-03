"""Real facial receiver: timed cues, PCM loudness, silence and inert-shape refusal."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forge.human_lipsync import build_human_lipsync
from tests.test_human_lipsync import SPEC
from tests.test_audio_motion import synthetic_audio


def verify(output,blender):
    out=Path(output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    results={}
    results['timed_30fps']=build_human_lipsync(SPEC,out/'timed',blender=blender,fps=30)
    for name,amplitude,fps in [('audio_60fps',.7,60),('silent_12fps',0.,12)]:
        wav=out/(name+'.wav')
        wav.write_bytes(synthetic_audio(amplitude=amplitude))
        results[name]=build_human_lipsync({'actor_id':'mgr-original-fixture'},out/name,
                                         audio_wav=wav,blender=blender,fps=fps)
    if results['audio_60fps']['receiver_max_vertex_motion_m']<=1e-6:
        raise RuntimeError('real audio did not deform imported face')
    if results['silent_12fps']['receiver_max_vertex_motion_m']>1e-6:
        raise RuntimeError('silence unexpectedly animated imported face')
    face=out/'timed/facial-animation'
    raw=(face/'human-lipsync.glb').read_bytes()
    size=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+size])
    binary=bytearray(raw[28+size:])
    changed=set()
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            for target in primitive.get('targets',[]):
                for index in target.values():
                    if index in changed:continue
                    changed.add(index)
                    accessor=doc['accessors'][index]
                    view=doc['bufferViews'][accessor['bufferView']]
                    if accessor['componentType']!=5126 or accessor['type']!='VEC3':
                        raise ValueError('float VEC3 authored shape displacement required')
                    start=view.get('byteOffset',0)+accessor.get('byteOffset',0)
                    stride=view.get('byteStride',12)
                    for n in range(accessor['count']):binary[start+n*stride:start+n*stride+12]=bytes(12)
    inert=raw[:28+size]+bytes(binary)
    negative=out/'inert-shapes'
    negative.mkdir()
    (negative/'human-lipsync.glb').write_bytes(inert)
    proof=json.loads((face/'lipsync-blender-proof.json').read_text())
    proof['export_sha256']=hashlib.sha256(inert).hexdigest()
    (negative/'lipsync-blender-proof.json').write_text(json.dumps(proof),encoding='utf8')
    result=subprocess.run([str(blender),'--background','--factory-startup','--python',
        str(ROOT/'bridge/blender_face_reimport.py'),'--',str(negative)],capture_output=True,text=True,timeout=120)
    log=result.stdout+result.stderr
    (out/'inert-receiver.log').write_text(log,encoding='utf8')
    if 'receiving animated facial keys failed to deform imported vertices' not in log or 'MGR_FACE_REIMPORT=' in log:
        raise RuntimeError('inert facial shape geometry was not independently refused')
    receipt={'schema':'mgr.forge.human-receiver-regression.v1','status':'PASS','positive':results,
             'negative':{'animation_and_shape_inventory_retained':True,'zeroed_shape_accessors':len(changed),
                         'independently_refused_for_no_deformation':True,'sha256':hashlib.sha256(inert).hexdigest()},
             'owner_visual_accepted':False,'speech_alignment_performed':False}
    (out/'verification.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--blender',default=r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
    args=parser.parse_args()
    result=verify(args.out,args.blender)
    print(json.dumps({'status':result['status'],'cases':list(result['positive']),
                      'inert_shapes_refused':result['negative']['independently_refused_for_no_deformation']}))
