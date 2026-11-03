"""Positive real rig deformation plus frozen-animation negative receiver witness."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forge.creature_rig import rig_creature
from forge.imagination import create_original_creature


def verify(output,blender):
    out=Path(output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    create_original_creature('invent a winged dragon with a flexible tail',out/'source',seed=11,variants=3)
    positive=rig_creature(out/'source',out/'rigged',blender=blender)
    raw=(out/'rigged/creature-rigged.glb').read_bytes()
    size=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+size])
    binary=bytearray(raw[28+size:])
    frozen_accessors=set()
    for animation in doc['animations']:
        for sampler in animation['samplers']:
            index=sampler['output']
            if index in frozen_accessors:continue
            frozen_accessors.add(index)
            accessor=doc['accessors'][index]
            if sampler.get('interpolation','LINEAR') not in ('LINEAR','STEP'):
                raise ValueError('negative witness only supports authored linear/step clips')
            view=doc['bufferViews'][accessor['bufferView']]
            if accessor['componentType']!=5126:raise ValueError('float animation output required')
            width={'VEC3':12,'VEC4':16}[accessor['type']]
            stride=view.get('byteStride',width)
            start=view.get('byteOffset',0)+accessor.get('byteOffset',0)
            first=bytes(binary[start:start+width])
            for n in range(accessor['count']):binary[start+n*stride:start+n*stride+width]=first
    negative=out/'frozen-animation'
    negative.mkdir()
    frozen=raw[:28+size]+bytes(binary)
    (negative/'creature-rigged.glb').write_bytes(frozen)
    initial={**positive,'rigged_glb_sha256':hashlib.sha256(frozen).hexdigest()}
    (negative/'skin-proof.json').write_text(json.dumps(initial),encoding='utf8')
    command=[str(blender),'--background','--factory-startup','--python',
             str(ROOT/'bridge/blender_creature_reimport.py'),'--',str(negative)]
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    log=result.stdout+result.stderr
    (out/'frozen-receiver.log').write_text(log,encoding='utf8')
    # Blender may return zero on Python exceptions: require the specific refusal
    # and absence of a new success marker, never rely solely on process code.
    if 'receiving skin/animation failed to deform imported vertices' not in log or 'MGR_CREATURE_REOPEN=' in log:
        raise RuntimeError('nondeforming clip was not explicitly refused by independent receiver')
    receipt={'schema':'mgr.forge.creature-receiver-regression.v1','status':'PASS',
             'positive':positive,'negative':{'frozen_clip_retains_skin_and_animation_inventory':True,
             'frozen_output_accessors':len(frozen_accessors),'sha256':hashlib.sha256(frozen).hexdigest(),
             'independently_refused_for_no_vertex_motion':True},
             'owner_art_accepted':False,'production_rig_accepted':False}
    (out/'verification.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--blender',default=r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
    args=parser.parse_args()
    result=verify(args.out,args.blender)
    print(json.dumps({'status':result['status'],'receiver_motion_m':result['positive']['receiver_max_vertex_motion_m'],
                      'frozen_animation_refused':result['negative']['independently_refused_for_no_vertex_motion']}))
