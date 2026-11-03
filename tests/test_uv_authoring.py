"""Original topology correspondence, source preservation and real atlas islands."""
import hashlib
import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from forge.geometry import Mesh
from forge.glb import export_glb
from forge.character_glb import parse_character_glb
from forge.uv_authoring import atlas_glb_bytes,author_uv_atlas,validate_uv_glb
from tests.test_imported_morph import unpack,pack,values,fixture as textured_fixture


def fixture(*,attributes=False):
    parts=[Mesh(),Mesh()]
    for mesh in parts:mesh.box(0,0,0,1,2,1)
    doc,binary=unpack(export_glb(parts,materials=[('shell',[.3,.4,.5,1]),('accessory',[.6,.2,.1,1])]))
    primitives=doc['meshes'][0]['primitives']
    doc['meshes']=[{'name':name,'primitives':[primitive]} for name,primitive in zip(('shell','accessory'),primitives)]
    doc['nodes']=[{'name':'original root','translation':[10,0,0],'children':[1,2]},
                  {'name':'original shell','mesh':0,'translation':[-2,0,0]},
                  {'name':'original accessory','mesh':1,'translation':[2,0,0]}]
    if attributes:
        for primitive in primitives:
            count=doc['accessors'][primitive['attributes']['POSITION']]['count']
            normals=values(doc,binary,primitive['attributes']['NORMAL'])
            for name,raw,kind,component,normalized in [
                ('COLOR_0',bytes([20,80,140,255])*count,'VEC4',5121,True),
                ('TANGENT',b''.join(struct.pack('<4f',*( (0,1,0,-1) if abs(n[1])<.5 else (1,0,0,-1))) for n in normals),'VEC4',5126,False)]:
                doc['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(raw)})
                binary+=raw
                doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'type':kind,
                    'componentType':component,'normalized':normalized,'count':count})
                primitive['attributes'][name]=len(doc['accessors'])-1
        doc['buffers'][0]['byteLength']=len(binary)
    return pack(doc,binary)


class UVAuthoringTests(unittest.TestCase):
    def test_shared_indices_and_aliased_colors_cannot_amplify_past_output_budget(self):
        doc,binary=unpack(fixture(attributes=True))
        primitive=doc['meshes'][0]['primitives'][0]
        color=primitive['attributes']['COLOR_0']
        for i in range(1,1001):primitive['attributes'][f'COLOR_{i}']=color
        raw=struct.pack('<'+'I'*30_000,*([0,1,2]*10_000))
        doc['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(raw)})
        binary+=raw
        doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':5125,
                                 'type':'SCALAR','count':30_000})
        primitive['indices']=len(doc['accessors'])-1
        doc['buffers'][0]['byteLength']=len(binary)
        original=pack(doc,binary)
        self.assertLess(len(original),900_000)
        # The malformed amplification must refuse before creating the working
        # bytearray, not after appending >120MB of duplicated attribute bytes.
        with patch('forge.uv_authoring.bytearray',side_effect=AssertionError('allocated output payload'),create=True):
            with self.assertRaisesRegex(ValueError,'expanded UV.*before allocation'):
                atlas_glb_bytes(original)

    def test_actual_atlas_preserves_source_parts_materials_and_triangle_positions(self):
        original=fixture()
        output,receipt=atlas_glb_bytes(original,expected_sha256=hashlib.sha256(original).hexdigest(),atlas_size=256,padding=3)
        before,source=unpack(original)
        after,binary=unpack(output)
        self.assertEqual(binary[:len(source)],source)
        for key in ('nodes','scenes','scene','materials'):
            self.assertEqual(before[key],after[key])
        self.assertEqual(receipt['chart_count'],24)
        self.assertEqual(receipt['geometry_after']['triangles'],24)
        self.assertEqual(receipt['geometry_before']['vertices'],48)
        self.assertEqual(receipt['geometry_after']['vertices'],72)
        self.assertTrue(receipt['preservation']['active_indices_remapped'])
        self.assertFalse(receipt['texture_art_generated'])
        for mi,(first,last) in enumerate(zip(before['meshes'],after['meshes'])):
            self.assertEqual(first['name'],last['name'])
            p,q=first['primitives'][0],last['primitives'][0]
            old=values(before,source,p['attributes']['POSITION'])
            moved=values(after,binary,q['attributes']['POSITION'])
            self.assertEqual(p['material'],q['material'])
            source_acc=before['accessors'][p['indices']]
            view=before['bufferViews'][source_acc['bufferView']]
            source_indices=struct.unpack_from('<'+'I'*source_acc['count'],source,view['byteOffset'])
            self.assertEqual(moved,[old[index] for index in source_indices])
            self.assertEqual(after['accessors'][q['indices']]['count'],source_acc['count'])
        self.assertEqual(receipt['artifact_sha256'],hashlib.sha256(output).hexdigest())

    def test_every_float32_uv_triangle_is_nonzero_inside_unique_padded_cells(self):
        output,receipt=atlas_glb_bytes(fixture(),atlas_size=256,padding=3)
        doc,binary=unpack(output)
        uvs=[uv for mesh in doc['meshes'] for primitive in mesh['primitives']
             for uv in values(doc,binary,primitive['attributes']['TEXCOORD_0'])]
        cells=set()
        total_uv_area = 0.0
        for i,chart in enumerate(receipt['charts']):
            cell=tuple(chart['cell'])
            self.assertNotIn(cell,cells);cells.add(cell)
            points=uvs[i*3:i*3+3]
            a,b,c=points
            area=abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2
            self.assertGreater(area,1e-12)
            total_uv_area += area
            for uv in points:
                for axis in range(2):
                    pixel=uv[axis]*256
                    self.assertGreaterEqual(pixel+1e-5,cell[axis]*receipt['cell_pixels']+3)
                    self.assertLessEqual(pixel-1e-5,(cell[axis]+1)*receipt['cell_pixels']-3)
                    self.assertTrue(0<uv[axis]<1)
        self.assertAlmostEqual(receipt['atlas_coverage_fraction'], total_uv_area, places=12)
        self.assertLess(receipt['atlas_coverage_fraction'], 1)
        for i,first in enumerate(receipt['charts']):
            for last in receipt['charts'][i+1:]:
                self.assertTrue(any(first['uv_max'][axis]<last['uv_min'][axis] or
                                    last['uv_max'][axis]<first['uv_min'][axis] for axis in range(2)))

    def test_all_supported_attributes_are_duplicated_and_tangents_follow_new_uvs(self):
        output,receipt=atlas_glb_bytes(fixture(attributes=True))
        doc,binary=unpack(output)
        self.assertTrue(receipt['preservation']['existing_tangents_recomputed_for_new_uvs'])
        for mesh in doc['meshes']:
            attrs=mesh['primitives'][0]['attributes']
            counts={doc['accessors'][index]['count'] for index in attrs.values()}
            self.assertEqual(counts,{36})
            color=doc['accessors'][attrs['COLOR_0']]
            view=doc['bufferViews'][color['bufferView']]
            self.assertEqual(binary[view['byteOffset']:view['byteOffset']+view['byteLength']],bytes([20,80,140,255])*36)
            self.assertTrue(color['normalized'])
            normals=values(doc,binary,attrs['NORMAL'])
            for normal,tangent in zip(normals,values(doc,binary,attrs['TANGENT'])):
                self.assertAlmostEqual(sum(a*b for a,b in zip(normal,tangent)),0,places=6)
                self.assertAlmostEqual(sum(v*v for v in tangent[:3]),1,places=6)
                self.assertIn(tangent[3],(-1,1))

    def test_existing_uv_or_texture_and_dynamic_sources_refuse_before_output_allocation(self):
        original=fixture()
        doc,binary=unpack(original)
        inputs=[textured_fixture()]
        for key,value in [('animations',[{}]),('skins',[{'joints':[0]}]),('textures',[{'source':0}])]:
            changed=json.loads(json.dumps(doc));changed[key]=value;inputs.append(pack(changed,binary))
        changed=json.loads(json.dumps(doc));changed['meshes'][0]['primitives'][0]['targets']=[]
        inputs.append(pack(changed,binary))
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            for i,raw in enumerate(inputs):
                source=root/f'source-{i}.glb';source.write_bytes(raw)
                target=root/f'output-{i}'
                with self.subTest(i=i),self.assertRaises(ValueError):author_uv_atlas(source,target)
                self.assertFalse(target.exists())

    def test_exact_source_binding_determinism_and_new_revision_preservation(self):
        original=fixture();sha=hashlib.sha256(original).hexdigest()
        raw,receipt=atlas_glb_bytes(original,expected_sha256=sha)
        self.assertEqual(receipt,validate_uv_glb(original,expected_sha256=sha))
        with TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source.glb';source.write_bytes(original)
            with self.assertRaises(ValueError):author_uv_atlas(source,root/'bad',expected_sha256='0'*64)
            self.assertFalse((root/'bad').exists())
            found=author_uv_atlas(source,root/'atlas',expected_sha256=sha)
            self.assertEqual((root/'atlas/original.glb').read_bytes(),original)
            self.assertEqual((root/'atlas/uv-mapped.glb').read_bytes(),raw)
            self.assertEqual((root/'atlas/diagnostic-checker.png').read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual(found['checker']['sha256'],hashlib.sha256((root/'atlas/diagnostic-checker.png').read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):author_uv_atlas(source,root/'atlas',expected_sha256=sha)
            self.assertEqual(source.read_bytes(),original)

    def test_budgets_and_malformed_inputs_refuse_as_validation_errors(self):
        for settings in [{'atlas_size':1},{'atlas_size':True},{'padding':0},{'padding':True},{'padding':17}]:
            with self.subTest(settings=settings),self.assertRaises(ValueError):atlas_glb_bytes(fixture(),**settings)
        with patch('forge.uv_authoring.MAX_TRIANGLES',1),self.assertRaisesRegex(ValueError,'triangle budget'):
            atlas_glb_bytes(fixture())
        with self.assertRaises(ValueError):atlas_glb_bytes(b'invalid')
        doc,binary=unpack(fixture(attributes=True))
        color=doc['meshes'][0]['primitives'][0]['attributes']['COLOR_0']
        doc['accessors'][color]['normalized']=False
        with self.assertRaisesRegex(ValueError,'vertex colors'):atlas_glb_bytes(pack(doc,binary))


if __name__=='__main__':unittest.main()
