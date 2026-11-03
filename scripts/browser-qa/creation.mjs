import {chromium} from 'playwright-core';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
const [url,out,phase,hold]=process.argv.slice(2),token=process.env.MGR_FORGE_QA_TOKEN;
assert.match(url,/^http:\/\/127\.0\.0\.1:\d+\/$/);assert.ok(token);
const browser=await chromium.launch({executablePath:'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',headless:true,
  args:['--remote-debugging-port=0','--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-first-run']});
const errors=[],checks=[];
try{
 const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:1000}});
 assert.equal((await context.request.post(url+'api/morph-status',{data:{request_id:'unknown-asset-001'}})).status(),403);
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(url+'#mgr-token='+token);await page.locator('#director-toggle').click();assert.equal(new URL(page.url()).hash,'');
 if(phase==='create'){
  await page.locator('#director-model').setInputFiles(out+'/source.glb');
  await page.locator('#director-model-morph').evaluate(el=>el.closest('details').open=true);
  await page.locator('#director-model-length').fill('1.5');
  let before;
  for(let i=0;i<2;i++){
   const response=page.waitForResponse(r=>r.url().endsWith('/api/morph-create'));
   await page.locator('#director-model-morph').click();const state=await(await response).json();assert.equal(state.status,'MATERIALIZED');
   if(i){assert.equal(state.job_id,before.job_id);assert.equal(state.replayed,true);}else before=state;
   await page.locator('#director-model-morph-status').filter({hasText:'Saved'}).waitFor();
   await page.waitForFunction(()=>!document.getElementById('director-model-morph').disabled);
  }
  checks.push('static original uploaded, native morph saved and repeated without duplicate');
  // Stop waiting after a REAL replay reaches native Studio, before its reply is delivered.
  // This is a controlled lost-reply fixture; it does not pretend to cancel native execution.
  let received;const arrived=new Promise(resolve=>{received=resolve;});let release;
  const held=new Promise(resolve=>{release=resolve;});
  await page.route('**/api/morph-create',async route=>{const reply=await route.fetch();received();await held;try{await route.fulfill({response:reply});}catch{}});
  await page.locator('#director-model-morph').click();await arrived;
  await page.locator('#director-model-morph-cancel').click();
  await page.locator('#director-model-morph-status').filter({hasText:'Stopped waiting. Native work may have finished.'}).waitFor();
  release();await page.unroute('**/api/morph-create');checks.push('stop-waiting preserves unknown reply and durable original identity');
  await page.locator('#director-recon-create').evaluate(el=>el.closest('details').open=true);
  await page.locator('#director-recon-front').setInputFiles(out+'/mask.png');await page.locator('#director-recon-side').setInputFiles(out+'/mask.png');
  await page.locator('#director-recon-grid').fill('12');
  const response=page.waitForResponse(r=>r.url().endsWith('/api/reconstruction-create'));
  await page.locator('#director-recon-create').click();assert.equal((await(await response).json()).status,'MATERIALIZED');
  await page.locator('#asset-preview-status').filter({hasText:'saved SHA-256 checked'}).waitFor();
  assert.ok(Number(await page.locator('#asset-preview').getAttribute('data-triangles'))>0);
  await page.locator('#asset-preview').scrollIntoViewIfNeeded();await page.locator('#asset-preview').screenshot({path:out+'/saved-hull-preview.png'});
  const first=await page.locator('#asset-preview').evaluate(c=>c.toDataURL());
  const rect=await page.locator('#asset-preview').boundingBox();await page.mouse.move(rect.x+50,rect.y+60);await page.mouse.down();await page.mouse.move(rect.x+130,rect.y+90,{steps:5});await page.mouse.up();
  assert.notEqual(await page.locator('#asset-preview').evaluate(c=>c.toDataURL()),first);checks.push('actual saved geometry renders and orbits');
  await page.locator('#director-model').setInputFiles(out+'/source-untextured.glb');
  await page.locator('#director-uv-create').evaluate(el=>el.closest('details').open=true);
  for(let i=0,original;i<2;i++){
   const response=page.waitForResponse(r=>r.url().endsWith('/api/uv-create'));
   await page.locator('#director-uv-create').click();const state=await(await response).json();assert.equal(state.status,'MATERIALIZED');
   if(i){assert.equal(state.job_id,original);assert.equal(state.replayed,true);}else original=state.job_id;
   await page.locator('#director-uv-status').filter({hasText:'Saved'}).waitFor();
   await page.waitForFunction(()=>!document.getElementById('director-uv-create').disabled);
   await page.waitForFunction(sha=>document.getElementById('asset-preview').dataset.assetSha256===sha,state.asset_sha256);
  }
  await page.locator('#asset-preview').scrollIntoViewIfNeeded();await page.locator('#asset-preview').screenshot({path:out+'/saved-uv-geometry-preview.png'});
  checks.push('native UV coordinates authored from upload, hash-checked preview and duplicate-free replay');
 }
 await page.locator('#director-history-refresh').click();await page.locator('#director-history-status').filter({hasText:'3 saved creations.'}).waitFor();
 for(const [kind,label] of [['morph','Static model morph'],['reconstruction','Measured image hull'],['uv','UV atlas revision']]){
  await page.locator('#director-history-kind').selectOption(kind);
  await page.locator('#director-history-status').filter({hasText:'1 saved creations.'}).waitFor();
  const reopened=page.waitForResponse(r=>r.url().endsWith('/api/saved-job-reopen'));
  await page.locator('#director-history-results button').click();const state=await(await reopened).json();
  await page.locator('#director-history-status').filter({hasText:'Reopened '+label}).waitFor();
  await page.waitForFunction(sha=>document.getElementById('asset-preview').dataset.assetSha256===sha,state.asset_sha256);
  const link=page.locator('#director-downloads a').filter({hasText:'Download reopened '+label}).first();
  const pending=page.waitForEvent('download');await link.click();const file=await pending,raw=await fs.readFile(await file.path());
  assert.equal(createHash('sha256').update(raw).digest('hex'),state.asset_sha256);checks.push(kind+' reopen/download exact SHA-256');
  if(kind==='uv'){
   const checker=page.locator('#director-downloads a').filter({hasText:'UV diagnostic checker · '+state.request_id}).first();
   const pendingChecker=page.waitForEvent('download');await checker.click();const file=await pendingChecker;
   const pixels=await fs.readFile(await file.path());assert.equal(createHash('sha256').update(pixels).digest('hex'),state.diagnostic_sha256);
   assert.equal(pixels.toString('hex',0,8),'89504e470d0a1a0a');checks.push('UV diagnostic download exact PNG and SHA-256');
  }
 }
 // Real key input at the initial heading must strafe along +X independently of camera height.
 await page.locator('#director-toggle').click();await page.locator('#world').click({position:{x:700,y:700}});
 const before=await page.evaluate(()=>window.MGR_FORGE_RUNTIME.getStatus().position);
 await page.keyboard.down('KeyD');await page.waitForTimeout(400);await page.keyboard.up('KeyD');
 const after=await page.evaluate(()=>window.MGR_FORGE_RUNTIME.getStatus().position);
 assert.ok(after[0]>before[0]+.3);assert.ok(Math.abs(after[2]-before[2])<.05);checks.push('camera +X strafe at initial heading');
 await page.setViewportSize({width:390,height:844});await page.locator('#director-toggle').click();
 await page.locator('#director-history-refresh').click();await page.screenshot({path:out+'/studio-mobile-'+phase+'.png'});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);checks.push('390px mobile layout no horizontal overflow');
 assert.deepEqual(errors,[]);
 if(hold==='hold'){
  await page.setViewportSize({width:1440,height:1000});
  const cdp=await browser.newBrowserCDPSession();const {targetInfos}=await cdp.send('Target.getTargets');
  const target=targetInfos.find(t=>t.type==='page'&&t.url===url);
  // DevTools HTTP endpoint is read from Chrome's browser command-line argument.
  const {arguments:args}=await cdp.send('Browser.getBrowserCommandLine');const profile=args.find(a=>a.startsWith('--user-data-dir=')).split('=').slice(1).join('=');
  const port=(await fs.readFile(profile+'/DevToolsActivePort','utf8')).split('\n')[0];
  await fs.writeFile(out+'/rea-target.json',JSON.stringify({cdp_endpoint:'http://127.0.0.1:'+port,target_id:target.targetId,origin:url.slice(0,-1)})+'\n');
  for(let i=0;i<240;i++){try{await fs.access(out+'/rea-complete');break;}catch{}await page.waitForTimeout(1000);}
 }
 console.log('MGR_CREATION_BROWSER='+JSON.stringify({status:'PASS',phase,checks,errors}));
}finally{await browser.close();}
