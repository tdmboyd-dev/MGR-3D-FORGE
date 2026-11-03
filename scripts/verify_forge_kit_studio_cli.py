"""Verify offline synthetic kit transport and actual local Studio CLI lifecycle.

The kit mode produces owned ZIP/receipt inputs for a separate real REA inspection.
No network archive fetch or license promotion occurs. Studio prints no token.
"""
import argparse
import contextlib,hashlib,io,json,queue,re,subprocess,sys,tempfile,threading,urllib.error,urllib.request
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile,ZipInfo
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from forge.cli import main
from forge.geometry import Mesh
from forge.glb import export_glb
from forge.pack_mirror import mirror_kaykit_pack
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('mode',choices=('kit','asset','serve'))
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--fixture-dir',type=Path,help='new ignored local directory for the synthetic ZIP and pack receipt')
args=parser.parse_args()
base,out=args.fixture_dir,args.out
if args.mode=='kit' and base is None:parser.error('kit mode requires --fixture-dir')
out.mkdir(parents=True,exist_ok=False)
def save(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf8')

def kit():
 base.mkdir(parents=True,exist_ok=False)
 mesh=Mesh();mesh.box(0,0,0,1,1,1)
 glb=export_glb([mesh],materials=(("synthetic-owned",[.3,.5,.7,1]),))
 path=base/'owned-fixture.zip'
 with ZipFile(path,'x') as z:
  for name,data in [('fixture/Assets/LICENSE.txt',b'Own synthetic verification fixture: Creative Commons Zero CC0.'),('fixture/Assets/owned.glb',glb),('fixture/metadata.txt',b'Synthetic out-of-scope test receipt bytes.')]:z.writestr(ZipInfo(name),data)
 blob=path.read_bytes(); digest=hashlib.sha256(blob).hexdigest()
 class FixtureResponse:
  headers={'Content-Length':str(len(blob))}
  def __enter__(self):return self
  def __exit__(self,*_):return False
  def geturl(self):return 'https://codeload.github.com/KayKit-Game-Assets/KayKit-Prototype-Bits-1.0/zip/'+'a'*40
  def read(self,limit):return blob[:limit]
 args=['kit-mirror','--repo','KayKit-Prototype-Bits-1.0','--commit','a'*40,'--store',str(base/'vault'),'--sha256',digest]
 captured=io.StringIO()
 with patch('forge.pack_mirror.mirror_kaykit_pack',side_effect=lambda *a,**k:mirror_kaykit_pack(*a,**k,opener=lambda *_a,**_k:FixtureResponse())),contextlib.redirect_stdout(captured):
  rc=main(args)
 result=json.loads(captured.getvalue())
 receipt=json.loads(Path(result['receipt']).read_text(encoding='utf8'))
 assert rc==0 and result['files']==3 and receipt['outside_license_scope_count']==1 and receipt['rights_reviewed'] is False
 assert (base/'vault'/receipt['content_object']).read_bytes()==blob
 save(base/'pack-receipt.json',receipt)
 save(out/'kit-mirror-fixture.json',{'status':'PASS_SYNTHETIC_TRANSPORT','cli_args':args,'exit_code':rc,'archive_sha256':digest,'archive_bytes':len(blob),'files':3,'license_scope_file_count':2,'outside_license_scope_count':1,'publisher_network_request':False,'original_bytes_preserved':True,'rights_reviewed':False,'production_accepted':False})
 print(json.dumps({'archive':str(path),'archive_sha256':digest,'files':3},indent=2))

def serve():
 with tempfile.TemporaryDirectory(prefix='mgr-forge-cli-studio-') as t:
  p=Path(t)
  with contextlib.redirect_stdout(io.StringIO()):assert main(['build','--buildings','3','--out',str(p/'world')])==0
  shim='import _thread,runpy,sys,threading; threading.Thread(target=lambda: (_thread.interrupt_main() if sys.stdin.readline().strip()=="STOP" else None), daemon=True).start(); runpy.run_module("forge.cli",run_name="__main__")'
  args=[sys.executable,'-c',shim,'serve-studio','--world',str(p/'world'),'--workspace',str(p/'workspace'),'--port','0']
  process=subprocess.Popen(args,cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf8')
  lines=queue.Queue();threading.Thread(target=lambda:lines.put(process.stdout.readline()),daemon=True).start()
  result={'schema':'mgr.forge.serve-studio-cli-fixture.v1','token_logged':False,'token_written_to_receipt':False,'startup_entrypoint':'forge.cli __main__ in owned subprocess, test-only stdin graceful stop shim'}
  try:
   startup=lines.get(timeout=45)
   match=re.search(r'(http://127\.0\.0\.1:\d+)/#mgr-token=([A-Za-z0-9_-]+)',startup)
   if not match:raise RuntimeError('CLI did not return private loopback startup link')
   origin,token=match.groups()
   def fetch(path,payload=None,authorized=True):
    headers={'Content-Type':'application/json'}
    if authorized:headers['X-MGR-Forge-Token']=token
    req=urllib.request.Request(origin+path,headers=headers,data=None if payload is None else json.dumps(payload).encode())
    try:
     with urllib.request.urlopen(req,timeout=30) as r:return r.status,r.read()
    except urllib.error.HTTPError as e:return e.code,e.read()
   denied,_=fetch('/api/saved-jobs',{},False)
   page,html=fetch('/studio')
   payload={'request_id':'cli-owned-fixture-creature-0001','prompt':'Original winged blue creature','seed':7,'variants':1,'morph':{}}
   created,_=fetch('/api/creature-create',payload)
   saved,saved_bytes=fetch('/api/saved-jobs',{})
   verified,verified_bytes=fetch('/api/request-verify',{'kind':'creature','request':payload})
   assert denied==403 and page==200 and b'<html' in html.lower()
   assert created==saved==verified==200 and payload['request_id'].encode() in saved_bytes
   assert json.loads(verified_bytes)['input_verified'] is True
   result.update({'status':'PASS','unauthenticated_saved_status':denied,'authenticated_studio_status':page,'authenticated_create_status':created,'saved_job_read_status':saved,'native_exact_request_verified':True,'native_jobs':len(list((p/'workspace'/'jobs').iterdir()))})
  finally:
   if process.poll() is None:
    try:
     process.stdin.write('STOP\n');process.stdin.flush()
     process.wait(timeout=15)
    except (BrokenPipeError,subprocess.TimeoutExpired):process.terminate();process.wait(timeout=10)
   result['process_exit_code']=process.returncode
   result['graceful_owned_stop']=process.returncode==0
   save(out/'serve-studio-cli.json',result)
 assert result['status']=='PASS' and result['native_jobs']==1 and result['graceful_owned_stop']
 print(json.dumps(result,indent=2))

def asset():
 from forge.asset_atlas import MGRAssetCatalog
 from forge.assets import AssetRegistry
 with tempfile.TemporaryDirectory(prefix='mgr-forge-asset-cli-') as temporary:
  p=Path(temporary)
  mesh=Mesh();mesh.box(0,0,0,1,1,1)
  blob=export_glb([mesh],materials=(("synthetic-owned",[.3,.5,.7,1]),))
  url='https://cdn.3dassets.dev/assets/synthetic-fixture/model.glb'
  MGRAssetCatalog(p/'catalog').remember([{'id':'3dassets:synthetic-fixture','provider_id':'3dassets','license':'CC0-1.0','cdn_url':url,
   'bytes_claimed':len(blob),'owner':'MGR synthetic fixture','source_url':'https://3dassets.dev/fixture/synthetic-fixture',
   'title':'Owned synthetic fixture','category':'fixture','triangles_claimed':12,'ai_generated_claimed':False}])
  class FixtureResponse:
   headers={'Content-Length':str(len(blob))}
   def __enter__(self):return self
   def __exit__(self,*_):return False
   def geturl(self):return url
   def read(self,limit):return blob[:limit]
  acquire=MGRAssetCatalog.acquire_3dassets
  args=['asset-acquire','--catalog',str(p/'catalog'),'--slug','synthetic-fixture','--store',str(p/'vault')]
  captured=io.StringIO()
  with patch.object(MGRAssetCatalog,'acquire_3dassets',lambda self,*a,**k:acquire(self,*a,**k,opener=lambda *_a,**_k:FixtureResponse())),contextlib.redirect_stdout(captured):
   rc=main(args)
  result=json.loads(captured.getvalue())
  digest=result['asset']['sha256']
  stored,meta=AssetRegistry(p/'vault').get(digest)
  assert rc==0 and stored==blob and meta['rights_reviewed'] is False and result['status']=='QUARANTINED_RIGHTS_AND_QUALITY'
  proof={'status':'PASS_SYNTHETIC_TRANSPORT','exit_code':rc,'cli_args':args,'sha256':digest,'bytes':len(stored),
   'geometry_status':result['container_inspection']['status'],'provider_network_request':False,'rights_reviewed':False,'production_accepted':False}
  save(out/'asset-acquire-fixture.json',proof)
  print(json.dumps(proof,indent=2))

if args.mode=='kit':kit()
if args.mode=='asset':asset()
if args.mode=='serve':serve()
