"""Private stdio-launched native service, retaining existing Forge journals.

No model, grants, arbitrary command channel or provider configuration. Windows
Job ownership covers this trusted worker and its Blender descendants. EOF closes
HTTP admission, lets accepted native work finish, then exits. A worker crash
closes its sole Job handle and stops descendants. Workspace data is never erased.
"""
import ctypes
from ctypes import wintypes as w
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import threading
import time


def direct(path):
    p=Path(path)
    if not p.is_absolute() or str(p).startswith('\\\\'):
        raise ValueError('local-absolute-worker-path-required')
    for item in [p,*p.parents]:
        if item.exists() and (item.is_symlink() or getattr(item.lstat(),'st_file_attributes',0)&0x400):
            raise ValueError('worker-path-link-denied')
    return p


class NativeJob:
    """Existing Windows Job primitives, specialized to this native service."""
    class Basic(ctypes.Structure):
        _fields_=[('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),('flags',w.DWORD),('min_work',ctypes.c_size_t),('max_work',ctypes.c_size_t),('active',w.DWORD),('affinity',ctypes.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
    class Io(ctypes.Structure):
        _fields_=[(name,ctypes.c_uint64) for name in ['read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes']]
    class Accounting(ctypes.Structure):
        _fields_=[(name,ctypes.c_int64) for name in ['user','kernel','period_user','period_kernel']]+[(name,w.DWORD) for name in ['faults','total','active','terminated']]
    def __init__(self,name):
        if os.name!='nt':raise ValueError('windows-native-owner-worker-required')
        self.k=ctypes.WinDLL('kernel32',use_last_error=True);k=self.k
        k.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR];k.CreateJobObjectW.restype=w.HANDLE
        k.OpenJobObjectW.argtypes=[w.DWORD,w.BOOL,w.LPCWSTR];k.OpenJobObjectW.restype=w.HANDLE
        k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle.restype=w.BOOL
        k.GetCurrentProcess.restype=w.HANDLE
        k.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE];k.AssignProcessToJobObject.restype=w.BOOL
        k.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD];k.SetInformationJobObject.restype=w.BOOL
        k.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p];k.QueryInformationJobObject.restype=w.BOOL
        self.handle=k.CreateJobObjectW(None,name)
        if not self.handle or ctypes.get_last_error()==183:raise RuntimeError('fresh-worker-job-required')
        class Limits(ctypes.Structure):
            _fields_=[('basic',NativeJob.Basic),('io',NativeJob.Io),('process_memory',ctypes.c_size_t),('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
        limits=Limits();limits.basic.flags=0x2000 # KILL_ON_JOB_CLOSE, no breakaway.
        if not k.SetInformationJobObject(self.handle,9,ctypes.byref(limits),ctypes.sizeof(limits)) or not k.AssignProcessToJobObject(self.handle,k.GetCurrentProcess()):
            k.CloseHandle(self.handle);raise RuntimeError('worker-job-assignment-denied')
        # Do not explicitly close a Job containing this live process. Kernel
        # process exit closes the sole, non-inherited handle and any descendants.
    def active(self,handle=None):
        value=self.Accounting()
        if not self.k.QueryInformationJobObject(handle or self.handle,1,ctypes.byref(value),ctypes.sizeof(value),None):raise RuntimeError('worker-job-query-unconfirmed')
        return value.active
    def previous_stopped(self,name):
        return self.named_active(name) in (None,0)
    @classmethod
    def named_active(cls,name):
        """Independent read-only kernel observation; never a PID-only stop."""
        if os.name!='nt' or not isinstance(name,str) or not re.fullmatch(r'Local\\MGR\.Forge\.Owner\.[a-f0-9]{64}\.[a-f0-9]{64}',name):raise ValueError('invalid-native-job-query')
        k=ctypes.WinDLL('kernel32',use_last_error=True)
        k.OpenJobObjectW.argtypes=[w.DWORD,w.BOOL,w.LPCWSTR];k.OpenJobObjectW.restype=w.HANDLE
        k.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p];k.QueryInformationJobObject.restype=w.BOOL
        k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle.restype=w.BOOL
        handle=k.OpenJobObjectW(4,False,name)
        if not handle:
            if ctypes.get_last_error()==2:return None
            raise RuntimeError('prior-worker-job-query-unconfirmed')
        try:
            value=cls.Accounting()
            if not k.QueryInformationJobObject(handle,1,ctypes.byref(value),ctypes.sizeof(value),None):raise RuntimeError('prior-worker-job-query-unconfirmed')
            return value.active
        finally:k.CloseHandle(handle)


def run(config):
    if os.name!='nt':raise ValueError('windows-native-owner-worker-required')
    if not isinstance(config,dict) or set(config)!={'schema','nonce','root','blender'} or config['schema']!='mgr.forge.owner-worker.v1' or not isinstance(config['nonce'],str) or not re.fullmatch('[a-f0-9]{64}',config['nonce']):raise ValueError('invalid-owner-worker-contract')
    root=direct(config['root']);blender=direct(config['blender'])
    if not blender.is_file():raise ValueError('native-blender-unavailable')
    root.mkdir(parents=True,exist_ok=True);root=direct(root.resolve())
    import msvcrt
    lock=open(root/'worker.lock','a+b');lock.seek(0)
    if lock.read(1)==b'':lock.write(b'0');lock.flush()
    lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:raise RuntimeError('native-workspace-already-owned')
    context=hashlib.sha256(str(root).casefold().encode()).hexdigest();prefix='Local\\MGR.Forge.Owner.'+context+'.';nonce=config['nonce'];job=NativeJob(prefix+nonce)
    marker=direct(root/'worker.json')
    if marker.exists():
        if marker.stat().st_size>4096:raise ValueError('prior-worker-custody-invalid')
        prior=json.loads(marker.read_text(encoding='utf-8'))
        if not isinstance(prior,dict) or not isinstance(prior.get('jobName'),str) or not re.fullmatch(re.escape(prefix)+'[a-f0-9]{64}',prior['jobName']):raise ValueError('prior-worker-custody-invalid')
        if not job.previous_stopped(prior['jobName']):raise RuntimeError('prior-native-family-still-active')
    temporary=root/('worker-'+nonce+'.tmp');temporary.write_text(json.dumps({'jobName':prefix+nonce,'pid':os.getpid(),'nonce':nonce})+'\n',encoding='utf-8');os.replace(temporary,marker)
    stopping=threading.Event()
    def control():
        # STOP or EOF only. No configurable operations/commands on this pipe.
        try:sys.stdin.buffer.readline(4097)
        finally:stopping.set()
    monitor=threading.Thread(target=control,name='forge-owner-control',daemon=True);monitor.start()
    from .cli import build
    from .spec import WorldSpec
    from .studio_server import start_server
    world=direct(root/'world')
    if stopping.is_set():return
    if not world.exists():
        staging=direct(root/('world-initializing-'+nonce));build(WorldSpec(seed=42,columns=2,rows=2,buildings=2,name='Owner Forge workspace'),staging);os.rename(staging,world)
    baseline=set(threading.enumerate())
    server,studio=start_server(world,direct(root/'workspace'),blender=str(blender));server.daemon_threads=False
    service=threading.Thread(target=server.serve_forever,name='forge-owner-http',daemon=True);service.start()
    print(json.dumps({'kind':'forge-owner-ready','nonce':nonce,'pid':os.getpid(),'jobName':prefix+nonce,'baseUrl':'http://127.0.0.1:'+str(server.server_port),'token':studio.token,'killOnWorkerExit':True}),flush=True)
    stopping.wait();server.shutdown();server.server_close();service.join()
    # The original HTTP handlers are closed first, so no new native work can
    # enter while already accepted jobs finish and write their original journals.
    while True:
        workers=[t for t in threading.enumerate() if t not in baseline and t is not threading.current_thread() and t.is_alive()]
        if not workers:break
        for thread in workers:thread.join(timeout=1)
    if job.active()!=1:raise RuntimeError('native-descendant-close-unconfirmed')
    print(json.dumps({'kind':'forge-owner-stopped','nonce':nonce,'pid':os.getpid(),'jobName':prefix+nonce,'httpAdmissionClosed':True,'nativeWorkers':0,'jobActiveBeforeSelfExit':1,'descendantsBeforeSelfExit':0}),flush=True)
    # Lock and Job handles intentionally remain owned until kernel process exit.


def main():
    try:
        raw=sys.stdin.buffer.readline(16385)
        if len(raw)>16384:raise ValueError('owner-worker-contract-too-large')
        run(json.loads(raw.decode('utf-8')));os._exit(0)
    except BaseException as error:
        message=str(error)
        print(json.dumps({'kind':'forge-owner-error','error':message if re.fullmatch('[a-z][a-z-]{1,100}',message) else 'native-owner-worker-unconfirmed'}),flush=True);os._exit(1)
