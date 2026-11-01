"""Real native ledgers/output, with explicit held-worker fixtures for async states."""
import copy,hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation

class RequestBindingTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory();self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        build(WorldSpec(seed=7,columns=2,rows=2,buildings=2),self.root/'world')
        self.studio=ForgeWorkstation(self.root/'world',self.root/'workspace')
        manifest=json.loads((self.root/'world/manifest.json').read_text())
        self.requests={
          'world':{'request_id':'native-world-binding-001','edits':{'schema':'mgr.forge.world-edit.v1','asset_sha256':hashlib.sha256((self.root/'world/world.glb').read_bytes()).hexdigest(),'buildings':[{k:b[k] for k in ['id','center','size','material']} for b in manifest['buildings']]}},
          'creature':{'request_id':'native-creature-binding-001','prompt':'An original winged crystal dragon','seed':3,'variants':1,'morph':{}},
          'biome':{'request_id':'native-biome-binding-001','biome':'alien','seed':7,'resolution':10},
          'human':{'request_id':'native-human-binding-001','fps':24,'timings':{'schema':'mgr.forge.phoneme-timeline.v1','actor_id':'native-test','language':'en-US','duration_ms':500,'phonemes':[{'phoneme':'AA','start_ms':0,'end_ms':500}]}},
          'composed':{'request_id':'native-composition-binding-001','biome_request_id':'native-biome-binding-001'}}
        self.routes={'world':'world-job','creature':'creature-create','biome':'biome-create','human':'human-lipsync-start','composed':'world-compose-create'}
    def create(self,kind):
        if kind=='composed':self.create('biome')
        # Held workers deliberately do not execute Blender; their state must
        # stay RUNNING/NEEDS_RECONCILIATION, never fixture success.
        with patch('threading.Thread.start'):
            return self.studio.command('/api/'+self.routes[kind],self.requests[kind])
    def verify(self,kind,request=None):
        return self.studio.command('/api/request-verify',{'kind':kind,'request':request or self.requests[kind]})
    def test_all_five_original_inputs_verified_without_new_jobs_or_false_async_success(self):
        for kind in self.requests:
            if kind=='human':self.studio.heavy_worker_slot=__import__('threading').BoundedSemaphore(1)
            if kind=='composed':self.studio.heavy_worker_slot=__import__('threading').BoundedSemaphore(1)
            created=self.create(kind);before=len(list(self.studio.jobs.iterdir()))
            result=self.verify(kind)
            self.assertTrue(result['input_verified']);self.assertEqual(result['request_kind'],kind)
            self.assertEqual(result['job_id'],created['job_id']);self.assertEqual(len(result['input_fingerprint']),64)
            self.assertEqual(len(list(self.studio.jobs.iterdir())),before)
            self.assertEqual(result['status'],'RUNNING' if kind in ('human','composed') else 'MATERIALIZED')
    def test_changed_instruction_under_same_id_is_never_accepted_as_old_job(self):
        for kind in self.requests:
            with self.subTest(kind=kind):
                self.studio.heavy_worker_slot=__import__('threading').BoundedSemaphore(1)
                self.create(kind);other=copy.deepcopy(self.requests[kind])
                if kind=='world':other['edits']['buildings'][0]['size'][1]+=1
                elif kind in ('creature','biome'):other['seed']+=1
                elif kind=='human':other['fps']=30
                else:other['biome_request_id']='missing-biome-binding-001'
                before=len(list(self.studio.jobs.iterdir()))
                with self.assertRaises(ValueError):self.verify(kind,other)
                self.assertEqual(len(list(self.studio.jobs.iterdir())),before)
    def test_reopen_reads_exact_original_and_async_interruption_stays_unknown(self):
        for kind in self.requests:
            self.studio.heavy_worker_slot=__import__('threading').BoundedSemaphore(1);self.create(kind)
        self.studio=ForgeWorkstation(self.root/'world',self.root/'workspace')
        for kind in self.requests:
            r=self.verify(kind);self.assertTrue(r['input_verified'])
            self.assertEqual(r['status'],'NEEDS_RECONCILIATION' if kind in ('human','composed') else 'MATERIALIZED')
    def test_missing_request_is_read_only_not_a_creation(self):
        for kind in ('world','creature','biome','human'):
            r=self.verify(kind);self.assertEqual(r['status'],'NOT_FOUND');self.assertFalse(r['input_verified'])
        self.assertEqual(len(list(self.studio.jobs.iterdir())),0)
    def test_world_context_is_actual_validated_source_without_creating_a_job(self):
        result=self.studio.command('/api/world-context',{})
        self.assertTrue(result['sourceVerified']);self.assertFalse(result['sideEffects']);self.assertEqual(result['edits'],self.requests['world']['edits']);self.assertIn('building-gold',result['materials']);self.assertEqual(len(list(self.studio.jobs.iterdir())),0)
        with self.assertRaises(ValueError):self.studio.command('/api/world-context',{'world':'caller-selected'})
        path=self.root/'world/world.glb';path.write_bytes(path.read_bytes()+b'changed')
        with self.assertRaises(ValueError):self.studio.command('/api/world-context',{})
    def test_new_world_request_runs_editor_source_and_geometry_validation_without_allocation(self):
        invalid=[]
        for field,value in [('asset_sha256','0'*64),('schema','unknown')]:
            request=copy.deepcopy(self.requests['world']);request['edits'][field]=value;invalid.append(request)
        for field,value in [('id','unrecognized'),('material',{}),('center',[100000,0,0]),('size',[-1,20,10])]:
            request=copy.deepcopy(self.requests['world']);request['edits']['buildings'][0][field]=value;invalid.append(request)
        for request in invalid:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):self.verify('world',request)
                self.assertEqual(len(list(self.studio.jobs.iterdir())),0)
                self.assertFalse((self.studio.workspace/'world-requests.json').exists())
    def test_changed_world_refuses_previous_world_and_biome_acceptance(self):
        self.create('world');self.create('biome')
        file=self.root/'world/world.glb';file.write_bytes(file.read_bytes()+b'changed')
        for kind in ('world','biome'):
            with self.assertRaises(ValueError):self.verify(kind)
    def test_saved_original_request_tampering_cannot_be_hidden_by_unchanged_output(self):
        r=self.create('creature');file=self.studio.valid_job(r['job_id'])/'creature-request.json';file.write_text('{}')
        with self.assertRaises(ValueError):self.verify('creature')
    def test_native_normalization_remains_owned_by_original_creature_validator(self):
        self.create('creature');request=copy.deepcopy(self.requests['creature']);request['prompt']='  '+request['prompt']+'  '
        self.assertTrue(self.verify('creature',request)['input_verified'])
