"""Source-bound Blender retarget revision for explicitly mapped original rigs."""
import hashlib
import json
import math
import re
from pathlib import Path
import shutil
import subprocess
import struct

from .character_glb import parse_character_glb
from .imported_morph import _accessor

SCHEMA='mgr.forge.motion-retarget-map.v1'
MAX_BYTES=24_000_000
MAX_FRAMES=240
MAX_BONES=128
MAX_VERTICES=120_000
MAX_TRIANGLES=180_000
_NAME=re.compile(r'[A-Za-z0-9_. -]{1,100}\Z')


def validate_retarget_map(recipe):
    fields={'schema','bone_map','start_frame','end_frame','fps','root_motion'}
    if not isinstance(recipe,dict) or set(recipe)!=fields or recipe.get('schema')!=SCHEMA:
        raise ValueError('exact native motion-retarget mapping document required')
    mapping=recipe['bone_map']
    if (not isinstance(mapping,dict) or not 1<=len(mapping)<=MAX_BONES or
        any(type(n) is not str or not n.strip() or not _NAME.fullmatch(n) for pair in mapping.items() for n in pair) or
        len(set(mapping.values()))!=len(mapping)):
        raise ValueError('motion retarget requires a bounded one-to-one named bone map')
    first,last,fps=recipe['start_frame'],recipe['end_frame'],recipe['fps']
    if (type(first) is not int or type(last) is not int or not 0<=first<last<=100_000 or
        last-first+1>MAX_FRAMES or type(fps) is not int or not 12<=fps<=60):
        raise ValueError('motion retarget requires 2..240 explicit frames at 12..60 FPS')
    if recipe['root_motion']!='in_place':
        raise ValueError('only explicit in_place rotation transfer is supported')
    return {**recipe,'bone_map':dict(sorted(mapping.items()))}


def _read_original(path,expected_sha256,*,animated):
    path=Path(path)
    if (not path.is_file() or path.is_symlink() or path.suffix.lower()!='.glb' or
        not 28<=path.stat().st_size<=MAX_BYTES):
        raise ValueError('bounded ordinary original skinned GLB required')
    with path.open('rb') as stream:raw=stream.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('original rig source exceeded byte budget during read')
    if type(expected_sha256) is not str or not re.fullmatch('[a-f0-9]{64}',expected_sha256) or hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('original retarget input does not match required SHA-256')
    doc,geometry=parse_character_glb(raw)
    if (geometry['vertices']>MAX_VERTICES or geometry['triangles']>MAX_TRIANGLES or
        geometry['primitives']>256 or len(doc.get('nodes',[]))>2048):
        raise ValueError('motion retarget geometry exceeds local bounds')
    if ('uri' in doc['buffers'][0] or doc.get('extensions') or doc.get('extensionsUsed') or doc.get('extensionsRequired') or
        any('uri' in image for image in doc.get('images',[])) or
        any(view.get('extensions') or view.get('buffer',0)!=0 for view in doc['bufferViews'])):
        raise ValueError('motion retarget requires self-contained uncompressed standard GLBs')
    json_size=struct.unpack_from('<I',raw,12)[0]
    binary=memoryview(raw)[28+json_size:]
    views=doc['bufferViews'];accessors=doc['accessors'];pixels=0
    length=doc['buffers'][0]['byteLength']
    if type(length) is not int or not 0<length<=len(binary) or any(
            view.get('byteOffset',0)+view['byteLength']>length for view in views):
        raise ValueError('retarget buffer view escapes declared embedded data')
    if len(doc.get('images',[]))>16:raise ValueError('retarget embedded texture count exceeded')
    for image in doc.get('images',[]):
        index=image.get('bufferView')
        if image.get('mimeType')!='image/png' or type(index) is not int or not 0<=index<len(views):
            raise ValueError('retarget currently admits bounded embedded PNG images only')
        view=views[index];start=view.get('byteOffset',0)
        if view['byteLength']<33 or bytes(binary[start:start+16])!=b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR':
            raise ValueError('embedded retarget PNG header invalid')
        width,height=struct.unpack_from('>II',binary,start+16);pixels+=width*height
        if not 1<=width<=2048 or not 1<=height<=2048 or pixels>8_388_608:
            raise ValueError('retarget texture expanded pixel budget exceeded')
    skins=doc.get('skins',[])
    if not isinstance(skins,list) or len(skins)!=1 or not isinstance(skins[0],dict):
        raise ValueError('one original skin per retarget GLB required')
    nodes=doc['nodes'];joints=skins[0].get('joints',[])
    scenes=doc.get('scenes')
    if not isinstance(scenes,list) or len(scenes)!=1 or doc.get('scene',0)!=0:
        raise ValueError('retarget requires one explicit original scene')
    stack=[(index,None,0) for index in scenes[0]['nodes']];seen=set();parent_index={}
    while stack:
        index,parent,depth=stack.pop()
        if type(index) is not int or not 0<=index<len(nodes) or index in seen or depth>128:
            raise ValueError('retarget refuses invalid, cyclic, shared or too deep node hierarchy')
        seen.add(index)
        parent_index[index]=parent
        children=nodes[index].get('children',[])
        if not isinstance(children,list):raise ValueError('retarget node children must be an array')
        stack.extend((child,index,depth+1) for child in children)
    if len(seen)!=len(nodes):raise ValueError('all original retarget nodes must belong to the selected scene')
    if (not isinstance(joints,list) or not 1<=len(joints)<=MAX_BONES or
        any(type(i) is not int or not 0<=i<len(nodes) for i in joints) or len(set(joints))!=len(joints)):
        raise ValueError('bounded original skin joint indices required')
    names=[nodes[i].get('name') for i in joints]
    if any(type(n) is not str or not n.strip() or not _NAME.fullmatch(n) for n in names) or len(set(names))!=len(names):
        raise ValueError('original skin joints must have unique supported names')
    joint_set=set(joints);bone_parents={}
    for index,name in zip(joints,names):
        parent=parent_index[index]
        while parent is not None and parent not in joint_set:parent=parent_index[parent]
        bone_parents[name]=nodes[parent]['name'] if parent is not None else None
    bound={node.get('mesh') for node in nodes if node.get('skin')==0}
    if bound!=set(range(len(doc['meshes']))):
        raise ValueError('all retarget meshes must belong to the original skin')
    for mesh in doc['meshes']:
        if mesh.get('weights') or mesh.get('extensions'):
            raise ValueError('retarget does not alter weighted morph targets/extensions')
        for primitive in mesh['primitives']:
            attrs=primitive['attributes']
            if ('targets' in primitive or primitive.get('extensions') or
                'JOINTS_0' not in attrs or 'WEIGHTS_0' not in attrs):
                raise ValueError('original skin weights required; morph targets and geometry extensions refuse')
            count=accessors[attrs['POSITION']]['count']
            _accessor(doc,binary,attrs['POSITION'])
            if 'NORMAL' in attrs:_accessor(doc,binary,attrs['NORMAL'])
            if any(name.startswith(('JOINTS_','WEIGHTS_')) and name not in ('JOINTS_0','JOINTS_1','WEIGHTS_0','WEIGHTS_1') for name in attrs):
                raise ValueError('retarget admits at most eight original bone influences')
            layers=[]
            for layer in (0,1):
                jkey,wkey=f'JOINTS_{layer}',f'WEIGHTS_{layer}'
                if (jkey in attrs)!=(wkey in attrs):raise ValueError('retarget source JOINTS and WEIGHTS must be paired')
                if jkey not in attrs:continue
                ja,wa=accessors[attrs[jkey]],accessors[attrs[wkey]]
                if (ja['type']!='VEC4' or wa['type']!='VEC4' or ja['count']!=count or wa['count']!=count or
                    ja['componentType'] not in (5121,5123) or ja.get('normalized',False) or
                    wa['componentType'] not in (5121,5123,5126) or
                    bool(wa.get('normalized',False))!=(wa['componentType']!=5126)):
                    raise ValueError('retarget source skin accessor format invalid')
                def layout(accessor):
                    view=views[accessor['bufferView']]
                    char,width={5121:('B',4),5123:('H',8),5126:('f',16)}[accessor['componentType']]
                    return ('<'+char*4,view.get('byteOffset',0)+accessor.get('byteOffset',0),view.get('byteStride',width))
                layers.append((layout(ja),layout(wa),{5121:255,5123:65535,5126:1}[wa['componentType']]))
            for vertex in range(count):
                total=0.
                for (jf,jo,js),(wf,wo,ws),denom in layers:
                    if any(j>=len(joints) for j in struct.unpack_from(jf,binary,jo+vertex*js)):
                        raise ValueError('retarget source skin joint index exceeds original joint table')
                    weights=[w/denom for w in struct.unpack_from(wf,binary,wo+vertex*ws)]
                    if any(not math.isfinite(w) or not 0<=w<=1 for w in weights):
                        raise ValueError('retarget source skin weight outside [0,1]')
                    total+=sum(weights)
                if abs(total-1)>.001:raise ValueError('retarget original skin weights must be normalized')
    clips=doc.get('animations',[])
    if not isinstance(clips,list) or len(clips)!=(1 if animated else 0):
        raise ValueError('source requires exactly one clip; target must have no earlier animations to replace')
    if animated:
        clip=clips[0];channels=clip.get('channels',[]);samplers=clip.get('samplers',[])
        if (not isinstance(channels,list) or not 1<=len(channels)<=MAX_BONES*3 or
            not isinstance(samplers,list) or not 1<=len(samplers)<=MAX_BONES*3):
            raise ValueError('source clip exceeds supported skeletal channel budget')
        for channel in channels:
            target=channel['target'];sampler=channel['sampler']
            if (type(sampler) is not int or not 0<=sampler<len(samplers) or target.get('node') not in joints or
                target.get('path') not in ('rotation','translation','scale')):
                raise ValueError('source clip must animate only original skeletal TRS channels')
            item=samplers[sampler]
            if item.get('interpolation','LINEAR') not in ('LINEAR','STEP'):
                raise ValueError('retarget source clips currently require linear/step skeletal tracks')
            timing=accessors[item['input']];values=accessors[item['output']]
            kind='VEC4' if target['path']=='rotation' else 'VEC3'
            if (timing['type']!='SCALAR' or values['type']!=kind or
                timing['componentType']!=5126 or values['componentType']!=5126 or
                timing['count']!=values['count'] or not 1<=timing['count']<=7201):
                raise ValueError('bounded float skeletal animation accessors required')
            for accessor,width in [(timing,1),(values,4 if kind=='VEC4' else 3)]:
                view=views[accessor['bufferView']];stride=view.get('byteStride',width*4)
                start=view.get('byteOffset',0)+accessor.get('byteOffset',0)
                previous=-1.
                for i in range(accessor['count']):
                    row=struct.unpack_from('<'+'f'*width,binary,start+i*stride)
                    if any(not math.isfinite(value) for value in row):
                        raise ValueError('nonfinite skeletal animation source values')
                    if width==1:
                        if not 0<=row[0]<=3600 or row[0]<=previous:
                            raise ValueError('source key times must be increasing and bounded')
                        previous=row[0]
                    elif width==4 and abs(sum(v*v for v in row)-1)>2e-3:
                        raise ValueError('source skeletal rotation quaternion must be unit length')
    return raw,bone_parents


def prepare_retarget(source,target,recipe,*,source_sha256,target_sha256):
    """Read/validate exact original bytes and explicit names without output writes."""
    spec=validate_retarget_map(recipe)
    try:
        original_source,source_parents=_read_original(source,source_sha256,animated=True)
        original_target,target_parents=_read_original(target,target_sha256,animated=False)
    except (KeyError,IndexError,TypeError,AttributeError,OverflowError,struct.error) as error:
        raise ValueError('malformed original rig or animation GLB') from error
    mapping=spec['bone_map'];reverse={target:source for source,target in mapping.items()}
    if set(mapping)-set(source_parents) or set(reverse)-set(target_parents):
        raise ValueError('retarget map references a bone absent from an original skin')
    for src,dst in mapping.items():
        sp,tp=source_parents[src],target_parents[dst]
        if ((sp is None)!=(tp is None) or (sp in mapping and mapping[sp]!=tp) or
            (tp in reverse and reverse[tp]!=sp)):
            raise ValueError('explicit mapped parent relations disagree between original skins')
    return original_source,original_target,spec


def _run(binary,script,out,timeout):
    bridge=Path(__file__).resolve().parents[1]/'bridge'/script
    command=[binary,'--background','--factory-startup','--python-exit-code','1','--python',str(bridge),'--',str(out.resolve())]
    log=out/(bridge.stem+'.log')
    try:
        result=subprocess.run(command,capture_output=True,text=True,stdin=subprocess.DEVNULL,timeout=timeout)
    except subprocess.TimeoutExpired as error:
        def decode(raw):return raw.decode('utf8',errors='replace') if isinstance(raw,bytes) else raw or ''
        log.write_text(decode(error.stdout)+decode(error.stderr),encoding='utf8')
        raise RuntimeError('local Blender motion retarget timed out; inspect preserved log') from error
    log.write_text(result.stdout+result.stderr,encoding='utf8')
    if result.returncode or 'Traceback (most recent call last)' in result.stdout+result.stderr:
        raise RuntimeError('local Blender motion retarget refused; inspect preserved log')


def retarget_motion(source,target,output,recipe,*,source_sha256,target_sha256,blender='blender',timeout=180):
    """Create a NEW target motion revision and require independent Blender proof."""
    out=Path(output)
    if out.exists():raise FileExistsError('preserve earlier motion revision; choose a new output directory')
    if type(timeout) is not int or not 1<=timeout<=300:raise ValueError('Blender timeout must be 1..300 seconds')
    original_source,original_target,spec=prepare_retarget(source,target,recipe,
        source_sha256=source_sha256,target_sha256=target_sha256)
    binary=shutil.which(str(blender))
    if not binary:raise RuntimeError('real local Blender executable required for motion retarget')
    out.mkdir(parents=True,exist_ok=False)
    (out/'source-original.glb').write_bytes(original_source)
    (out/'target-original.glb').write_bytes(original_target)
    (out/'motion-map.json').write_text(json.dumps(spec,sort_keys=True,indent=2)+'\n',encoding='utf8')
    try:
        _run(binary,'blender_motion_retarget.py',out,timeout)
        _run(binary,'blender_motion_retarget_receive.py',out,timeout)
        proof=json.loads((out/'retarget-blender-proof.json').read_text(encoding='utf8'))
        model_path=out/'retargeted.glb'
        if not model_path.is_file() or not 28<=model_path.stat().st_size<=48_000_000:
            raise RuntimeError('actual retarget artifact missing or exceeds byte budget')
        model=model_path.read_bytes()
        parse_character_glb(model)
        sha=hashlib.sha256(model).hexdigest()
        if (proof.get('status')!='INDEPENDENT_RETARGET_GLTF_DEFORMATION_PASS' or
            proof.get('source_sha256')!=source_sha256 or proof.get('target_sha256')!=target_sha256 or
            proof.get('artifact_sha256')!=sha or proof.get('frames')!=spec['end_frame']-spec['start_frame']+1 or
            proof.get('mapped_bones')!=len(spec['bone_map']) or not proof.get('target_rest_skin_uv_materials_preserved') or
            proof.get('received_max_vertex_motion_m',0)<=1e-5):
            raise RuntimeError('independent receiving motion proof did not qualify original target revision')
        receipt={'schema':'mgr.forge.motion-retarget-revision.v1','status':'NATIVE_MAPPED_MOTION_RETARGET_VERIFIED',
                 'source_sha256':source_sha256,'target_sha256':target_sha256,
                 'artifact_sha256':sha,'artifact_bytes':len(model),'map':spec,'blender_witness':proof,
                 'artifact':{'file':'retargeted.glb','sha256':sha,'bytes':len(model)},
                 'originals_preserved':True,'owner_art_accepted':False,'provider_spend_usd':0,
                 'limitations':['explicit mapped bone rotation deltas only; no semantic recognition',
                                'in-place; no root translation, scaling, IK, foot contacts or animation merging',
                                'supported self-contained single-skin original GLBs, bounded embedded PNG textures only',
                                'verified target deformation does not establish artistic or game-engine acceptance']}
        (out/'retarget-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
        return receipt
    except Exception:
        (out/'needs-reconciliation.txt').write_text('Motion retarget incomplete; preserve originals and inspect saved output/logs.\n',encoding='utf8')
        raise
