"""Real private worker/kernel family custody; no account/model fixtures."""
import json,os,secrets,subprocess,sys,time,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request,urlopen
from forge.owner_worker import NativeJob

@unittest.skipUnless(os.name=='nt','Windows-owned service bridge')
class OwnerWorkerTests(unittest.TestCase):
    def open(self,root):
        process=subprocess.Popen([sys.executable,'-I','-u',str(Path(__file__).resolve().parents[1]/'scripts/owner-worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        process.stdin.write(json.dumps({'schema':'mgr.forge.owner-worker.v1','nonce':secrets.token_hex(32),'root':str(root/'service'),'blender':r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'})+'\n');process.stdin.flush()
        ready=json.loads(process.stdout.readline());self.assertEqual(ready['kind'],'forge-owner-ready',ready.get('error'));self.assertEqual(ready['pid'],process.pid);return process,ready
    def call(self,ready,path,body):
        request=Request(ready['baseUrl']+path,data=json.dumps(body).encode(),headers={'X-MGR-Forge-Token':ready['token'],'Content-Type':'application/json'})
        with urlopen(request,timeout=15) as response:return json.load(response)
    def close(self,process):
        process.stdin.close();process.wait(timeout=30);result=[json.loads(line) for line in process.stdout.read().splitlines()];self.assertEqual(process.returncode,0);self.assertEqual(result[-1]['kind'],'forge-owner-stopped');self.assertEqual(result[-1]['descendantsBeforeSelfExit'],0);process.stdout.close();process.stderr.close()
    def test_control_pipe_eof_closes_original_service_and_reopens_same_workspace(self):
        with TemporaryDirectory(prefix='forge-owner-worker-') as name:
            root=Path(name);process,ready=self.open(root)
            try:self.assertEqual(NativeJob.named_active(ready['jobName']),1);self.close(process);self.assertIn(NativeJob.named_active(ready['jobName']),(None,0));process,second=self.open(root);self.assertNotEqual(second['jobName'],ready['jobName']);self.close(process)
            finally:
                if process.poll() is None:process.kill();process.wait(timeout=15)
    def test_crashed_original_worker_stops_actual_blender_descendant_and_preserves_unknown_job(self):
        with TemporaryDirectory(prefix='forge-owner-crash-') as name:
            root=Path(name);process,ready=self.open(root);request={'request_id':'owned-worker-crash-001','fps':60,'timings':{'schema':'mgr.forge.phoneme-timeline.v1','actor_id':'owned-worker','language':'en-US','duration_ms':120000,'phonemes':[{'phoneme':'AA','start_ms':0,'end_ms':120000}]}}
            try:
                created=self.call(ready,'/api/human-lipsync-start',request);self.assertEqual(created['status'],'RUNNING');deadline=time.monotonic()+20
                while NativeJob.named_active(ready['jobName'])<2 and time.monotonic()<deadline:time.sleep(.02)
                self.assertGreaterEqual(NativeJob.named_active(ready['jobName']),2,'Real Blender child never entered the owned Job')
                process.kill();process.wait(timeout=15);deadline=time.monotonic()+15
                while NativeJob.named_active(ready['jobName']) not in (None,0) and time.monotonic()<deadline:time.sleep(.02)
                self.assertIn(NativeJob.named_active(ready['jobName']),(None,0));process.stdin.close();process.stdout.close();process.stderr.close();process,reopened=self.open(root)
                receipt=self.call(reopened,'/api/request-verify',{'kind':'human','request':request});self.assertEqual(receipt['status'],'NEEDS_RECONCILIATION');self.assertTrue(receipt['input_verified']);self.assertEqual(receipt['job_id'],created['job_id']);self.assertEqual(len(list((root/'service/workspace/jobs').iterdir())),1);self.close(process)
            finally:
                if process.poll() is None:process.kill();process.wait(timeout=15)
