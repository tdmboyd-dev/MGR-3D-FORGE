/** End-to-end browser editing smoke proof. Node 22+; Chrome with CDP; no npm packages. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp, rm, readdir, readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const chrome=process.argv[2];
const html=process.argv[3] || 'demos/mgr-world-editor.html';
if(!chrome)throw Error('Usage: node tests/browser_editor_smoke.mjs CHROME_BINARY [EDITOR_HTML]');
const profile=await mkdtemp(join(tmpdir(),'mgr-editor-cdp-'));
const port=19000+Math.floor(Math.random()*1000);
const child=spawn(chrome,['--headless=new','--no-first-run','--disable-extensions',
  '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader',
  '--disable-background-timer-throttling','--disable-renderer-backgrounding',
  '--remote-allow-origins=*',`--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`,pathToFileURL(resolve(html)).href],{stdio:'ignore'});
const pause=(ms)=>new Promise(r=>setTimeout(r,ms));
let socket,seq=0;const pending=new Map();
const call=async(method,params={})=>{
  const id=++seq;
  const result=new Promise((resolve,reject)=>pending.set(id,{resolve,reject}));
  socket.send(JSON.stringify({id,method,params}));
  const response=await Promise.race([result,pause(10000).then(()=>{throw Error('CDP timed out');})]);
  if(response.error||response.result?.exceptionDetails)throw Error(JSON.stringify(response));
  return response.result;
};
const evaluate=async expression=>(await call('Runtime.evaluate',{expression,
  returnByValue:true,awaitPromise:true})).result.value;
try{
  let endpoint;
  for(let i=0;i<60;i++){
    try{const tabs=await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      endpoint=tabs.find(t=>t.type==='page')?.webSocketDebuggerUrl;if(endpoint)break;}
    catch{}await pause(200);
  }
  if(!endpoint)throw Error('Chrome CDP endpoint never opened');
  socket=new WebSocket(endpoint);
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});
    socket.addEventListener('error',reject,{once:true});});
  socket.addEventListener('message',event=>{
    const message=JSON.parse(event.data);
    if(!message.id)return;
    const waiter=pending.get(message.id);if(waiter){pending.delete(message.id);waiter.resolve(message);}
  });
  for(let i=0;i<70;i++){
    if(await evaluate('Boolean(window.MGR_FORGE_RUNTIME?.getEdits)'))break;
    await pause(150);
  }
  const base=await evaluate('window.MGR_FORGE_RUNTIME.getEdits()');
  assert.equal(base.schema,'mgr.forge.world-edit.v1');
  assert.equal(base.buildings.length,10);
  const first=base.buildings[0];
  const modified=await evaluate(`(()=>{
    document.getElementById('edit-height').value='42';
    document.getElementById('edit-height').dispatchEvent(new Event('change',{bubbles:true}));
    return window.MGR_FORGE_RUNTIME.getEdits();})()`);
  assert.equal(modified.buildings[0].size[1],42);
  assert.equal(await evaluate("window.MGR_FORGE_RUNTIME.getHistory().undo"),1);
  await evaluate("document.getElementById('undo-world').click()");
  assert.equal(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings[0].size[1]'),first.size[1]);
  await evaluate("document.getElementById('redo-world').click()");
  assert.equal(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings[0].size[1]'),42);
  assert.equal(await evaluate(`JSON.parse(localStorage.getItem('mgr.forge.world-edits.v1.'+window.MGR_WORLD_SHA)??'null')?.buildings?.[0]?.size?.[1]`),42);
  await call('Page.setDownloadBehavior',{behavior:'allow',downloadPath:profile});
  await evaluate("document.getElementById('save-world').click()");
  let downloaded;
  for(let i=0;i<30;i++){
    if((await readdir(profile)).includes('mgr-world-edits.json')){
      downloaded=JSON.parse(await readFile(join(profile,'mgr-world-edits.json'),'utf8'));break;}
    await pause(150);
  }
  assert.equal(downloaded?.buildings?.[0]?.size?.[1],42);
  const restored=await evaluate(`(async()=>{
    const input=document.getElementById('import-world');
    const transfer=new DataTransfer();
    transfer.items.add(new File([JSON.stringify(${JSON.stringify(base)})], 'world.json',{type:'application/json'}));
    input.files=transfer.files; input.dispatchEvent(new Event('change',{bubbles:true}));
    await new Promise(resolve=>setTimeout(resolve,180));
    return window.MGR_FORGE_RUNTIME.getEdits();
  })()`);
  assert.equal(restored.buildings[0].size[1],first.size[1]);
  const reset=await evaluate(`(()=>{
    document.getElementById('edit-height').value='36';
    document.getElementById('edit-height').dispatchEvent(new Event('change'));
    document.getElementById('reset-world').click();
    return window.MGR_FORGE_RUNTIME.getEdits().buildings[0].size[1];
  })()`);
  assert.equal(reset,first.size[1]);
  const picked=await evaluate(`(()=>{
    const canvas=document.getElementById('world');const bounds=canvas.getBoundingClientRect();
    for(let y=120;y<bounds.height-80;y+=35)for(let x=40;x<bounds.width-340;x+=35){
      const hit=window.MGR_FORGE_RUNTIME.pickAt(x,y);if(hit)return {hit,x,y};
    }
    return null;
  })()`);
  assert.ok(picked?.hit?.startsWith('building-'),'3D ray selection must intersect a real building');
  assert.equal(await evaluate('document.getElementById("building").value'),picked.hit);
  const another=base.buildings.find(b=>b.id!==picked.hit)?.id;
  assert.ok(another);
  await evaluate(`(()=>{const s=document.getElementById('building');s.value=${JSON.stringify(another)};s.dispatchEvent(new Event('change'));})()`);
  await call('Input.dispatchMouseEvent',{type:'mousePressed',x:picked.x,y:picked.y,button:'left',clickCount:1});
  await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:picked.x,y:picked.y,button:'left',clickCount:1});
  assert.equal(await evaluate('document.getElementById("building").value'),picked.hit,'real canvas mouse click must select ray hit');
  await evaluate("document.activeElement?.blur()");
  const beforeMotion=await evaluate('window.MGR_FORGE_RUNTIME.getStatus().position');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'w',code:'KeyW',windowsVirtualKeyCode:87});
  await pause(650);
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:'w',code:'KeyW',windowsVirtualKeyCode:87});
  const afterMotion=await evaluate('window.MGR_FORGE_RUNTIME.getStatus().position');
  assert.ok(Math.hypot(...afterMotion.map((v,i)=>v-beforeMotion[i]))>0.1,
    'actual browser keyboard input must move world camera');
  await evaluate("document.getElementById('director-toggle').click()");
  assert.equal(await evaluate("document.getElementById('director').hidden"),false);
  const added=await evaluate(`(()=>{
    document.getElementById('director-prompt').value='create a gold building height 16 width 8 depth 8 at x 0 z 0';
    document.getElementById('director-run').click();
    return window.MGR_FORGE_RUNTIME.getEdits().buildings.at(-1);
  })()`);
  assert.equal(added.material,'building-gold');
  assert.deepEqual(added.center,[0,0,0]);
  assert.deepEqual(added.size,[8,16,8]);
  assert.ok(added.id.startsWith('mgr-created-'));
  assert.equal(await evaluate("window.MGR_FORGE_RUNTIME.executeCommand('set height to 27')"),true);
  assert.equal(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings.at(-1).size[1]'),27);
  assert.equal(await evaluate("window.MGR_FORGE_RUNTIME.executeCommand('make it blue')"),true);
  assert.equal(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings.at(-1).material'),'building-blue');
  assert.equal(await evaluate("window.MGR_FORGE_RUNTIME.executeCommand('move to x 10 z -10')"),true);
  assert.deepEqual(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings.at(-1).center'),[10,0,-10]);
  assert.equal(await evaluate("window.MGR_FORGE_RUNTIME.executeCommand('run arbitrary python code')"),false);
  assert.equal(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings.length'),11);
  await evaluate("document.getElementById('duplicate-building').click()");
  assert.equal(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings.length'),12);
  await evaluate("document.getElementById('delete-building').click()");
  assert.equal(await evaluate('window.MGR_FORGE_RUNTIME.getEdits().buildings.length'),11);
  const reference=await evaluate(`(async()=>{
    const canvas=document.createElement('canvas');canvas.width=16;canvas.height=16;
    const ctx=canvas.getContext('2d');ctx.fillStyle='#854030';ctx.fillRect(0,0,16,16);
    const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
    const input=document.getElementById('director-image'),transfer=new DataTransfer();
    transfer.items.add(new File([blob],'reference.png',{type:'image/png'}));input.files=transfer.files;
    const loaded=new Promise(resolve=>document.getElementById('director-preview').addEventListener('load',resolve,{once:true}));
    input.dispatchEvent(new Event('change',{bubbles:true}));await loaded;
    await new Promise(resolve=>setTimeout(resolve,25));
    document.getElementById('director-sample-color').click();
    return {hidden:document.getElementById('director-preview').hidden,
      message:document.getElementById('director-msg').textContent,
      material:window.MGR_FORGE_RUNTIME.getEdits().buildings.find(b=>b.id===document.getElementById('building').value).material};
  })()`);
  assert.equal(reference.hidden,false);
  assert.equal(reference.material,'building-brick');
  assert.ok(reference.message.includes('did not create 3D geometry'));
  await evaluate("document.getElementById('director-toggle').click()");
  assert.equal(await evaluate("document.getElementById('director').hidden"),true);
  console.log(JSON.stringify({schema:'mgr.forge.browser-editor-smoke.v1',status:'PASS',
    browser:'Chrome headless WebGL2',buildings:base.buildings.length,
    checks:['runtime boot','building changed','undo/redo','local persistence','downloaded edit JSON',
      'JSON import restored','reset restored','ray-picked actual building','canvas mouse clicked actual building',
      'keyboard navigated real 3D camera','expand/collapse creation chat','text generated new building',
      'text changed dimensions/material/position','arbitrary-code request rejected',
      'duplicated and deleted building','local image sampled into actual 3D material']}));
}finally{
  for(const waiter of pending.values())waiter.reject?.(new Error('browser ending'));
  socket?.close();child.kill();await rm(profile,{recursive:true,force:true,maxRetries:3,retryDelay:150});
}
