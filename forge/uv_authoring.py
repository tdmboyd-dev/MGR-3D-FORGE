"""CPU-authored, fully seamed UV atlas revisions of original static GLBs.

Each original triangle receives a padded atlas island. Seams require duplicated
vertices and remapped active indices; original bytes remain an exact BIN prefix
and the source GLB is separately retained. No texture or generated art is claimed.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

from .character_glb import COMPONENT_BYTES, DIMENSIONS, parse_character_glb
from .imported_morph import (MAX_BYTES, _accessor, _indices, _unit,
                            validate_imported_glb)

MAX_TRIANGLES=16_384
SCHEMA='mgr.forge.uv-atlas-revision.v1'


def _cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def _dot(a,b):return sum(x*y for x,y in zip(a,b))


def _sub(a,b):return tuple(x-y for x,y in zip(a,b))


def _textured(value):
    if isinstance(value,dict):
        return any((key.endswith('Texture') and isinstance(item,dict)) or _textured(item)
                   for key,item in value.items())
    if isinstance(value,list):return any(_textured(item) for item in value)
    return False


def _checker(size):
    # Original diagnostic pixels; this is UV QA, not material/appearance art.
    def chunk(kind,raw):
        return struct.pack('>I',len(raw))+kind+raw+struct.pack('>I',zlib.crc32(kind+raw))
    rows=bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            line=x%32<2 or y%32<2
            color=(20,180,220) if line else ((235,235,235) if (x//16+y//16)%2 else (40,40,40))
            rows.extend(color)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress(bytes(rows)))+chunk(b'IEND',b''))


def _atlas_glb_bytes(blob,*,expected_sha256=None,atlas_size=2048,padding=2):
    if type(atlas_size) is not int or atlas_size not in (256,512,1024,2048,4096):
        raise ValueError('UV atlas size must be a power-of-two choice from 256 to 4096')
    if type(padding) is not int or not 1<=padding<=16:
        raise ValueError('UV atlas padding must be 1..16 pixels')
    source=validate_imported_glb(blob,expected_sha256=expected_sha256)
    doc,geometry=parse_character_glb(blob)
    if (doc.get('images') or doc.get('textures') or _textured(doc.get('materials',[])) or
        any(name.startswith('TEXCOORD_') for mesh in doc['meshes']
            for primitive in mesh['primitives'] for name in primitive['attributes'])):
        raise ValueError('preserve existing UVs/textures; atlas authoring requires an untextured source without UV attributes')
    triangles=geometry['triangles']
    if triangles>MAX_TRIANGLES:
        raise ValueError('fully seamed UV atlas triangle budget exceeded')
    columns=math.ceil(math.sqrt(triangles))
    cell=atlas_size//columns
    if cell<2*padding+4:
        raise ValueError('UV atlas resolution cannot fit padded triangle islands')
    size=struct.unpack_from('<I',blob,12)[0]
    binary=blob[28+size:]
    # A small source can alias many color attributes to one accessor while
    # reusing a short position buffer across thousands of indexed triangles.
    # Bound the expanded revision before allocating any duplicated payload.
    estimated=len(blob)
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            attrs=primitive['attributes']
            count=doc['accessors'][primitive.get('indices',attrs['POSITION'])]['count']
            widths=sum(COMPONENT_BYTES[doc['accessors'][index]['componentType']]*
                       DIMENSIONS[doc['accessors'][index]['type']] for index in attrs.values())
            estimated+=count*(widths+8+4)+(len(attrs)+2)*1024
            if estimated>MAX_BYTES:
                raise ValueError('expanded UV attribute/index/metadata byte budget exceeded before allocation')
    result=bytearray(binary)
    target=copy.deepcopy(doc)
    charts=[];vertex_count=0

    def append(raw,template,*,kind=None,component=None,count=None,bounds=None,target_type=34962):
        result.extend(bytes(-len(result)%4))
        offset=len(result)
        result.extend(raw)
        target['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':target_type})
        acc=copy.deepcopy(template)
        acc.update(bufferView=len(target['bufferViews'])-1,byteOffset=0)
        if kind is not None:acc['type']=kind
        if component is not None:acc['componentType']=component
        if count is not None:acc['count']=count
        if bounds is not None:acc['min'],acc['max']=bounds
        target['accessors'].append(acc)
        return len(target['accessors'])-1

    for mi,mesh in enumerate(doc['meshes']):
        for pi,primitive in enumerate(mesh['primitives']):
            attrs=primitive['attributes']
            for name,index in attrs.items():
                acc=doc['accessors'][index]
                if name.startswith('COLOR_') and (acc['type'] not in ('VEC3','VEC4') or
                    not ((acc['componentType']==5126 and not acc.get('normalized',False)) or
                         (acc['componentType'] in (5121,5123) and acc.get('normalized') is True))):
                    raise ValueError('UV revision supports float or normalized unsigned VEC3/VEC4 vertex colors')
                if name.startswith('COLOR_') and acc['componentType']==5126:
                    view=doc['bufferViews'][acc['bufferView']]
                    width=DIMENSIONS[acc['type']]
                    stride=view.get('byteStride',width*4)
                    offset=view.get('byteOffset',0)+acc.get('byteOffset',0)
                    if any(not math.isfinite(v) or not 0<=v<=1 for i in range(acc['count'])
                           for v in struct.unpack_from('<'+'f'*width,binary,offset+i*stride)):
                        raise ValueError('UV source float vertex colors must be finite in [0,1]')
            positions=_accessor(doc,binary,attrs['POSITION'])
            indices=list(_indices(doc,binary,primitive,len(positions)))
            normals=_accessor(doc,binary,attrs['NORMAL'])
            uvs=[];tangents=[]
            for start in range(0,len(indices),3):
                original_indices=indices[start:start+3]
                a,b,c=(positions[index] for index in original_indices)
                direction=_unit(_sub(b,a))
                face_normal=_unit(_cross(_sub(b,a),_sub(c,a)))
                vertical=_cross(face_normal,direction)
                projected=[(0.,0.),(_dot(_sub(b,a),direction),0.),
                           (_dot(_sub(c,a),direction),_dot(_sub(c,a),vertical))]
                low=[min(p[i] for p in projected) for i in range(2)]
                high=[max(p[i] for p in projected) for i in range(2)]
                scale=(cell-2*padding)/max(high[i]-low[i] for i in range(2))
                chart=len(charts)
                x,y=chart%columns,chart//columns
                mapped=[((x*cell+padding+(p[0]-low[0])*scale)/atlas_size,
                         (y*cell+padding+(p[1]-low[1])*scale)/atlas_size) for p in projected]
                mapped=[struct.unpack('<2f',struct.pack('<2f',*p)) for p in mapped]
                area=abs((mapped[1][0]-mapped[0][0])*(mapped[2][1]-mapped[0][1])-
                         (mapped[1][1]-mapped[0][1])*(mapped[2][0]-mapped[0][0]))/2
                if not math.isfinite(area) or area<=1e-12:
                    raise ValueError('triangle aspect ratio collapses a float32 UV island')
                uvs.extend(mapped)
                charts.append({'mesh':mi,'primitive':pi,'source_triangle':start//3,
                               'source_indices':original_indices,'cell':[x,y],
                               'uv_min':[min(p[i] for p in mapped) for i in range(2)],
                               'uv_max':[max(p[i] for p in mapped) for i in range(2)],'uv_area':area})
                if 'TANGENT' in attrs:
                    for index in original_indices:
                        n=_unit(normals[index])
                        tangent=_unit(tuple(direction[i]-n[i]*_dot(n,direction) for i in range(3)))
                        sign=1. if _dot(_cross(n,tangent),vertical)>=0 else -1.
                        tangents.append((*tangent,sign))
            new_attrs={}
            for name,index in attrs.items():
                acc=doc['accessors'][index]
                view=doc['bufferViews'][acc['bufferView']]
                width=COMPONENT_BYTES[acc['componentType']]*DIMENSIONS[acc['type']]
                stride=view.get('byteStride',width)
                offset=view.get('byteOffset',0)+acc.get('byteOffset',0)
                if name=='TANGENT':
                    raw=b''.join(struct.pack('<4f',*value) for value in tangents)
                else:raw=b''.join(binary[offset+i*stride:offset+i*stride+width] for i in indices)
                bounds=None
                if name=='POSITION':
                    bounds=([min(positions[j][i] for j in indices) for i in range(3)],
                            [max(positions[j][i] for j in indices) for i in range(3)])
                elif name=='TANGENT' and ('min' in acc or 'max' in acc):
                    bounds=([min(t[i] for t in tangents) for i in range(4)],
                            [max(t[i] for t in tangents) for i in range(4)])
                new_attrs[name]=append(raw,acc,count=len(indices),bounds=bounds)
            uv_raw=b''.join(struct.pack('<2f',*value) for value in uvs)
            new_attrs['TEXCOORD_0']=append(uv_raw,{},kind='VEC2',component=5126,count=len(indices),
                bounds=([min(p[i] for p in uvs) for i in range(2)],[max(p[i] for p in uvs) for i in range(2)]))
            new_primitive=target['meshes'][mi]['primitives'][pi]
            new_primitive['attributes']=new_attrs
            new_primitive['indices']=append(struct.pack('<'+'I'*len(indices),*range(len(indices))),{},
                kind='SCALAR',component=5125,count=len(indices),target_type=34963)
            vertex_count+=len(indices)
    target['buffers'][0]['byteLength']=len(result)
    encoded=json.dumps(target,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
    encoded+=b' '*(-len(encoded)%4)
    result.extend(bytes(-len(result)%4))
    total=28+len(encoded)+len(result)
    if total>MAX_BYTES:raise ValueError('derived UV atlas GLB exceeds static byte budget')
    artifact=(struct.pack('<4sII',b'glTF',2,total)+struct.pack('<I4s',len(encoded),b'JSON')+encoded+
              struct.pack('<I4s',len(result),b'BIN\0')+bytes(result))
    _,after=parse_character_glb(artifact)
    if after['triangles']!=triangles or after['materials']!=geometry['materials'] or after['meshes']!=geometry['meshes']:
        raise ValueError('UV revision changed original triangle/material/part inventory')
    receipt={'schema':SCHEMA,'status':'NATIVE_FULLY_SEAMED_UV_ATLAS',
        'source_sha256':source['source_sha256'],'source_bytes':len(blob),
        'artifact_sha256':hashlib.sha256(artifact).hexdigest(),'artifact_bytes':len(artifact),
        'artifact':{'file':'uv-mapped.glb','sha256':hashlib.sha256(artifact).hexdigest(),'bytes':len(artifact)},
        'atlas_size':atlas_size,'padding_pixels':padding,'columns':columns,'cell_pixels':cell,
        'chart_count':len(charts),'charts':charts,'geometry_before':geometry,'geometry_after':after,
        'preservation':{'original_bin_prefix_unchanged':bytes(result[:len(binary)])==binary,
                        'triangles_materials_parts_hierarchy_preserved':True,
                        'source_overwritten':False,'active_indices_remapped':True,
                        'vertex_count_before':geometry['vertices'],'vertex_count_after':vertex_count,
                        'all_supported_vertex_attributes_remapped':True,
                        'existing_tangents_recomputed_for_new_uvs':any('TANGENT' in p['attributes'] for m in doc['meshes'] for p in m['primitives'])},
        'checker_is_diagnostic_only':True,'texture_art_generated':False,'provider_spend_usd':0,
        'independently_blender_verified':False,'owner_art_accepted':False,
        'limitations':['fully seamed triangle islands; not distortion-optimized semantic chart unwrapping',
                       'duplicates vertices and remaps active indices while preserving triangle order and exact original bytes',
                       'existing UV/textured, skinned, animated, targeted and compressed assets refuse',
                       'tiny/aspect-degenerate islands refuse; no texture painting, baking or generated material art',
                       'diagnostic checker rendering does not establish artistic or target-engine acceptance']}
    return artifact,receipt


def atlas_glb_bytes(blob,*,expected_sha256=None,atlas_size=2048,padding=2):
    """Pure preflight plus deterministic UV revision; writes no files."""
    try:return _atlas_glb_bytes(blob,expected_sha256=expected_sha256,atlas_size=atlas_size,padding=padding)
    except (KeyError,IndexError,TypeError,AttributeError,OverflowError,struct.error) as error:
        raise ValueError('malformed or unsupported static UV atlas input') from error


def validate_uv_glb(blob,*,expected_sha256=None,atlas_size=2048,padding=2):
    return atlas_glb_bytes(blob,expected_sha256=expected_sha256,atlas_size=atlas_size,padding=padding)[1]


def author_uv_atlas(source,output,*,expected_sha256=None,atlas_size=2048,padding=2):
    path,out=Path(source),Path(output)
    if not path.is_file() or path.is_symlink() or path.suffix.lower()!='.glb' or not 28<=path.stat().st_size<=MAX_BYTES:
        raise ValueError('bounded ordinary original static GLB required')
    if out.exists():raise FileExistsError('preserve earlier UV atlas revision; choose a new output')
    original=path.read_bytes()
    artifact,receipt=atlas_glb_bytes(original,expected_sha256=expected_sha256,atlas_size=atlas_size,padding=padding)
    # Pixel generation is also preflight; allocation follows all native checks.
    checker=_checker(min(atlas_size,1024))
    receipt['checker']={'file':'diagnostic-checker.png','sha256':hashlib.sha256(checker).hexdigest(),
                        'bytes':len(checker),'diagnostic_only':True}
    out.mkdir(parents=True,exist_ok=False)
    (out/'original.glb').write_bytes(original)
    (out/'uv-mapped.glb').write_bytes(artifact)
    (out/'diagnostic-checker.png').write_bytes(checker)
    (out/'uv-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt
