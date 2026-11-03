"""Source identity and rejection contracts for original mapped rig revisions."""
import hashlib
import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from forge.geometry import Mesh
from forge.glb import export_glb
from forge.retarget_motion import SCHEMA,prepare_retarget,retarget_motion,validate_retarget_map
from tests.test_imported_morph import pack,unpack


RECIPE={'schema':SCHEMA,'bone_map':{'source_root':'target_base','source_arm':'target_tip'},
        'start_frame':1,'end_frame':16,'fps':24,'root_motion':'in_place'}


def fixture(animated):
    mesh=Mesh();mesh.box(0,0,0,1,2,1)
    doc,binary=unpack(export_glb([mesh],materials=[('Owned skin fixture',[.2,.4,.6,1])]))
    names=('source_root','source_arm') if animated else ('target_base','target_tip')
    doc['nodes']=[{'name':'original rig','children':[1,2]}, {'name':'original skinned part','mesh':0,'skin':0},
                  {'name':names[0],'children':[3]}, {'name':names[1],'translation':[1,0,0]}]
    def append(raw,kind,component,count):
        nonlocal binary
        doc['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(raw)})
        binary+=raw;binary+=bytes(-len(binary)%4)
        doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'type':kind,'componentType':component,'count':count})
        return len(doc['accessors'])-1
    attrs=doc['meshes'][0]['primitives'][0]['attributes'];count=len(mesh.positions)//3
    attrs['JOINTS_0']=append(bytes((0,1,0,0))*count,'VEC4',5121,count)
    attrs['WEIGHTS_0']=append(struct.pack('<4f',.25,.75,0,0)*count,'VEC4',5126,count)
    first=(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1);last=(*first[:12],-1,0,0,1)
    inv=append(struct.pack('<32f',*first,*last),'MAT4',5126,2)
    doc['skins']=[{'joints':[2,3],'inverseBindMatrices':inv,'skeleton':2}]
    if animated:
        timing=append(struct.pack('<2f',1/24,16/24),'SCALAR',5126,2)
        rotations=append(struct.pack('<8f',0,0,0,1,0,0,.38268343,.92387953),'VEC4',5126,2)
        doc['animations']=[{'name':'original motion','samplers':[{'input':timing,'output':rotations}],
                           'channels':[{'sampler':0,'target':{'node':3,'path':'rotation'}}]}]
    doc['buffers'][0]['byteLength']=len(binary)
    return pack(doc,binary)


class RetargetMotionTests(unittest.TestCase):
    def setUp(self):
        temp=TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        self.source,self.target,self.out=[self.root/name for name in ('source.glb','target.glb','revision')]
        self.source.write_bytes(fixture(True));self.target.write_bytes(fixture(False))

    def binding(self):
        return {'source_sha256':hashlib.sha256(self.source.read_bytes()).hexdigest(),
                'target_sha256':hashlib.sha256(self.target.read_bytes()).hexdigest()}

    def test_native_preflight_binds_exact_owned_rig_bytes_and_bone_names_without_allocating(self):
        source,target,recipe=prepare_retarget(self.source,self.target,RECIPE,**self.binding())
        self.assertEqual(source,self.source.read_bytes());self.assertEqual(target,self.target.read_bytes())
        self.assertEqual(recipe,RECIPE);self.assertFalse(self.out.exists())
        with self.assertRaisesRegex(ValueError,'absent'):
            prepare_retarget(self.source,self.target,{**RECIPE,'bone_map':{'source_arm':'missing'}},**self.binding())
        with self.assertRaisesRegex(ValueError,'parent relations'):
            prepare_retarget(self.source,self.target,{**RECIPE,'bone_map':{'source_root':'target_tip','source_arm':'target_base'}},**self.binding())

    def test_exact_map_rejects_ambiguous_or_unsupported_rotation_transfer(self):
        for changes in [{'bone_map':{'source_arm':'target_tip','source_root':'target_tip'}},
                        {'bone_map':{'/unsafe':'target_tip'}},{'bone_map':{}},{'start_frame':True},
                        {'end_frame':241},{'fps':1},{'root_motion':'inferred_world_travel'},{'surplus':True}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):validate_retarget_map({**RECIPE,**changes})

    def test_source_hash_change_and_target_already_animated_refuse_before_output(self):
        binding=self.binding();self.target.write_bytes(fixture(True))
        with self.assertRaisesRegex(ValueError,'SHA-256'):retarget_motion(self.source,self.target,self.out,RECIPE,**binding)
        self.assertFalse(self.out.exists())
        with self.assertRaisesRegex(ValueError,'target must have no earlier animations'):
            retarget_motion(self.source,self.target,self.out,RECIPE,**self.binding())
        self.assertFalse(self.out.exists())

    def test_corrupt_skin_weights_nodes_or_animation_accessors_do_not_reach_blender(self):
        raw=self.source.read_bytes()
        for defect in ('weights','joints','cycle','nonfinite'):
            doc,binary=unpack(raw);binary=bytearray(binary)
            attrs=doc['meshes'][0]['primitives'][0]['attributes']
            if defect=='cycle':doc['nodes'][3]['children']=[2]
            elif defect=='weights':
                acc=doc['accessors'][attrs['WEIGHTS_0']];offset=doc['bufferViews'][acc['bufferView']]['byteOffset']
                struct.pack_into('<4f',binary,offset,.25,.25,0,0)
            elif defect=='joints':
                acc=doc['accessors'][attrs['JOINTS_0']];offset=doc['bufferViews'][acc['bufferView']]['byteOffset'];binary[offset]=99
            else:
                acc=doc['accessors'][doc['animations'][0]['samplers'][0]['output']]
                offset=doc['bufferViews'][acc['bufferView']]['byteOffset'];struct.pack_into('<f',binary,offset,float('nan'))
            self.source.write_bytes(pack(doc,bytes(binary)))
            with self.subTest(defect=defect),patch('forge.retarget_motion.shutil.which',side_effect=AssertionError('called Blender')):
                with self.assertRaises(ValueError):retarget_motion(self.source,self.target,self.out,RECIPE,**self.binding())
                self.assertFalse(self.out.exists())

    def test_missing_blender_and_existing_revision_cannot_overwrite_originals(self):
        with patch('forge.retarget_motion.shutil.which',return_value=None):
            with self.assertRaisesRegex(RuntimeError,'real local Blender'):retarget_motion(self.source,self.target,self.out,RECIPE,**self.binding())
        self.assertFalse(self.out.exists())
        self.out.mkdir();sentinel=self.out/'earlier-revision.json';sentinel.write_text(json.dumps({'original':True}))
        with self.assertRaises(FileExistsError):retarget_motion(self.source,self.target,self.out,RECIPE,**self.binding())
        self.assertEqual(json.loads(sentinel.read_text()),{'original':True})


if __name__=='__main__':unittest.main()
