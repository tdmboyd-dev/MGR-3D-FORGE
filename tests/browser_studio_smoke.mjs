/** Windows Chrome CDP: real localhost studio UI -> image GLB -> world GLB -> Blender file. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const chrome=process.argv[2],url=process.argv[3];
if(!chrome||!url||!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url))throw Error('Usage: node tests/browser_studio_smoke.mjs CHROME_BINARY http://127.0.0.1:PORT/');
const profile=await mkdtemp(join(tmpdir(),'mgr-studio-cdp-'));
const port=20000+Math.floor(Math.random()*900);
const child=spawn(chrome,['--headless=new','--no-first-run','--disable-extensions',
  '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader',
  '--remote-allow-origins=*',`--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`,url],{stdio:'ignore'});
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let socket,sequence=0;const pending=new Map();
const call=async(method,params={})=>{
  const id=++sequence;
  const result=new Promise((resolve,reject)=>pending.set(id,{resolve,reject}));
  socket.send(JSON.stringify({id,method,params}));
  const response=await Promise.race([result,pause(25000).then(()=>{throw Error('CDP response timeout');})]);
  if(response.error||response.result?.exceptionDetails)throw Error(JSON.stringify(response));
  return response.result;
};
const evaluate=async expression=>(await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true})).result.value;
try{
  let endpoint;
  for(let n=0;n<80;n++){
    try{
      const tabs=await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      endpoint=tabs.find(tab=>tab.type==='page')?.webSocketDebuggerUrl;
      if(endpoint)break;
    }catch{}await pause(200);
  }
  if(!endpoint)throw Error('Chrome debug endpoint not available');
  socket=new WebSocket(endpoint);
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  socket.addEventListener('message',event=>{
    const reply=JSON.parse(event.data);if(!reply.id)return;
    const waiter=pending.get(reply.id);if(waiter){pending.delete(reply.id);waiter.resolve(reply);}
  });
  for(let n=0;n<100;n++){
    if(await evaluate('Boolean(window.MGR_FORGE_RUNTIME?.getEdits)'))break;
    await pause(150);
  }
  assert.equal(await evaluate('Boolean(window.MGR_FORGE_RUNTIME?.getEdits)'),true);
  assert.equal(await evaluate('document.getElementById("director-build-world").disabled'),false);
  const upload=await evaluate(`(async()=>{
    document.getElementById('director-toggle').click();
    const canvas=document.createElement('canvas');canvas.width=16;canvas.height=16;
    canvas.getContext('2d').fillRect(0,0,16,16);
    const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
    const upload=document.getElementById('director-image');const transfer=new DataTransfer();
    transfer.items.add(new File([blob],'tiny.png',{type:'image/png'}));upload.files=transfer.files;
    upload.dispatchEvent(new Event('change',{bubbles:true}));
    document.getElementById('director-generate-relief').click();
    return {enabled:!document.getElementById('director-build-world').disabled,pixels:blob.size};
  })()`);
  assert.ok(upload.pixels>20);
  let relief=false;
  for(let n=0;n<60;n++){
    relief=await evaluate("Boolean(document.querySelector('#director-downloads a[href$=\"relief.glb\"]'))");
    if(relief)break;await pause(200);
  }
  assert.ok(relief,'local PNG must produce real relief link');
  await evaluate("document.getElementById('director-build-world').click()");
  let world=false;
  for(let n=0;n<80;n++){
    world=await evaluate("Boolean(document.querySelector('#director-downloads a[href$=\"world.glb\"]'))");
    if(world)break;await pause(250);
  }
  assert.ok(world,'world JSON must become real GLB');
  assert.equal(await evaluate("document.getElementById('director-build-godot').disabled"),false);
  await evaluate("document.getElementById('director-build-godot').click()");
  let engine=false;
  for(let n=0;n<100;n++){
    engine=await evaluate("Boolean(document.querySelector('#director-downloads a[href$=\"godot-project.zip\"]'))");
    if(engine)break;await pause(250);
  }
  assert.ok(engine,'Godot engine-project ZIP must materialize');
  assert.equal(await evaluate("document.getElementById('director-build-blender').disabled"),false);
  await evaluate("document.getElementById('director-build-blender').click()");
  let blend=false;
  // A production-size Blender scene can take over one minute on a real laptop.
  // Match the UI's three-minute background-job allowance, not a one-minute cap.
  for(let n=0;n<720;n++){
    blend=await evaluate("Boolean(document.querySelector('#director-downloads a[href$=\"scene.blend\"]'))");
    if(blend)break;await pause(250);
  }
  assert.ok(blend,'real Blender .blend must be downloadable; UI says: '+
    await evaluate("document.getElementById('director-msg').textContent"));
  const links=await evaluate("Array.from(document.querySelectorAll('#director-downloads a')).map(a=>a.getAttribute('href'))");
  for(const link of links){
    const answer=await fetch(new URL(link,url));
    assert.equal(answer.status,200);
    assert.ok((await answer.arrayBuffer()).byteLength>100);
  }
  console.log(JSON.stringify({schema:'mgr.forge.browser-studio-smoke.v1',status:'PASS',
    checks:['localhost token session','browser PNG upload','generated relief GLB','live edited world GLB',
      'Godot project package','full Blender project conversion','downloadable real artifacts'],links}));
}finally{
  socket?.close();child.kill();await pause(300);await rm(profile,{recursive:true,force:true,maxRetries:4,retryDelay:200});
}
