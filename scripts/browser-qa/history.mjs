import {chromium} from 'playwright-core';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import fs from 'node:fs/promises';

const [url,out,phase]=process.argv.slice(2);
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url)||!out||!['empty','restarted'].includes(phase))throw Error('Local Studio and explicit history phase required');
const token=process.env.MGR_FORGE_QA_TOKEN;
if(!token||!/^[A-Za-z0-9_-]{24,128}$/.test(token))throw Error('Scoped test token required');
const expected=JSON.parse(process.env.MGR_FORGE_QA_EXPECTED||'[]');
const owner=new URL(url);owner.hash='mgr-token='+token;
const browser=await chromium.launch({executablePath:'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',headless:true,
  args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage','--no-first-run']});
const errors=[], downloads=[];
let context;
async function checkpoint(stage){await fs.writeFile(`${out}/history-${phase}-checkpoint.json`,JSON.stringify({phase,stage})+'\n');}
try{
  await checkpoint('browser-launched');
  context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:900}});
  const anonymous=await context.request.post(new URL('/api/saved-jobs',url).href,{data:{}});
  assert.equal(anonymous.status(),403);
  const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(owner.href);await page.locator('#director-toggle').click();
  await checkpoint('unlocked');
  assert.equal(new URL(page.url()).hash,'');
  const status=page.locator('#director-history-status');
  await page.locator('#director-history-refresh').click();
  await status.filter({hasText:`${expected.length} saved creations.`}).waitFor();
  assert.equal(await page.locator('#director-history-results button').count(),expected.length);
  await checkpoint('listed');
  if(phase==='restarted'){
    const worldResponses=[];
    page.on('response',response=>{if(new URL(response.url()).pathname==='/api/world-job')worldResponses.push(response);});
    for(let trial=0;trial<2;trial++){
      await page.locator('#director-build-world').click();
      await page.locator('#director-msg').filter({hasText:'Saved actual'}).waitFor();
      await page.waitForFunction(()=>!document.getElementById('director-build-world').disabled);
    }
    assert.equal(worldResponses.length,2);
    const worldA=await worldResponses[0].json(),worldB=await worldResponses[1].json();
    assert.equal(worldA.job_id,worldB.job_id);assert.equal(worldA.request_id,worldB.request_id);
    assert.equal(worldB.replayed,true);
    expected.push({kind:'world',label:'Edited world',request_id:worldA.request_id,sha256:worldA.world_sha256});
    await page.locator('#director-history-refresh').click();
    await status.filter({hasText:`${expected.length} saved creations.`}).waitFor();
    await checkpoint('durable-world-replayed');
    // Pagination runs against real original journals, not a supplied list fixture.
    const headers={'X-MGR-Forge-Token':token};
    const first=await context.request.post(new URL('/api/saved-jobs',url).href,{headers,data:{limit:1}});
    const firstPage=await first.json();assert.equal(firstPage.items.length,1);assert.ok(firstPage.next_cursor);
    const second=await context.request.post(new URL('/api/saved-jobs',url).href,{headers,data:{limit:1,cursor:firstPage.next_cursor}});
    const secondPage=await second.json();assert.equal(secondPage.items.length,1);
    assert.notEqual(firstPage.items[0].request_id,secondPage.items[0].request_id);
    for(const item of expected){
      await checkpoint('reopening-'+item.kind);
      const row=page.locator('#director-history-results > div').filter({hasText:item.request_id});
      await row.getByRole('button',{name:'Reopen',exact:true}).click();
      await status.filter({hasText:`Reopened ${item.label} · ${item.request_id}.`}).waitFor();
      const link=page.locator('#director-downloads a').filter({hasText:`Download reopened ${item.label} · ${item.request_id}`}).first();
      const pending=page.waitForEvent('download');await link.click();const download=await pending;
      const bytes=await fs.readFile(await download.path());
      const sha=createHash('sha256').update(bytes).digest('hex');assert.equal(sha,item.sha256);
      assert.equal(bytes.toString('ascii',0,4),'glTF');downloads.push({kind:item.kind,sha256:sha,bytes:bytes.length});
      await checkpoint('downloaded-'+item.kind);
    }
    await page.locator('#director-history-kind').selectOption('creature');
    await status.filter({hasText:'1 saved creations.'}).waitFor();
    assert.equal(await page.locator('#director-history-results button').count(),1);
    await page.locator('#director-history-kind').selectOption('all');
    await status.filter({hasText:`${expected.length} saved creations.`}).waitFor();
    await checkpoint('filter-checked');
    // Deliberately supplied HTTP failure tests the visible recovery path only.
    await page.route('**/api/saved-jobs',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:'Synthetic history outage'})}));
    await page.locator('#director-history-refresh').click();
    await status.filter({hasText:'Synthetic history outage'}).waitFor();
    await page.unrouteAll({behavior:'wait'});
    await checkpoint('outage-checked');
    await page.route('**/api/saved-jobs',async route=>{await new Promise(resolve=>setTimeout(resolve,350));try{await route.abort();}catch(error){if(!String(error).includes('already handled'))throw error;}});
    await page.locator('#director-history-refresh').click();
    await page.locator('#director-history-cancel').click();
    await status.filter({hasText:'Lookup interrupted.'}).waitFor();
    await page.unrouteAll({behavior:'wait'});
    await checkpoint('cancel-checked');
    await page.locator('#director-history-refresh').click();
    await status.filter({hasText:`${expected.length} saved creations.`}).waitFor();
    // Serve altered download bytes while preserving the original status receipt.
    const chosen=expected.find(item=>item.kind==='creature');
    const link=page.locator('#director-downloads a').filter({hasText:`Download reopened Creature · ${chosen.request_id}`}).first();
    let unexpectedDownloads=0;const onDownload=()=>unexpectedDownloads++;page.on('download',onDownload);
    await page.route('**/files/*/creature/creature.glb',async route=>{
      const response=await route.fetch();const bytes=Buffer.from(await response.body());bytes[bytes.length-1]^=1;
      await route.fulfill({response,body:bytes});
    });
    await link.click();await page.locator('#director-msg').filter({hasText:'Download failed: Saved GLB changed'}).waitFor();
    assert.equal(unexpectedDownloads,0);page.off('download',onDownload);await page.unrouteAll({behavior:'wait'});
    await checkpoint('tamper-checked');
  }
  await page.locator('#director-history-status').scrollIntoViewIfNeeded();
  await checkpoint('before-desktop-screenshot');
  await page.screenshot({path:`${out}/forge-history-${phase}-desktop.png`});
  await checkpoint('after-desktop-screenshot');
  await page.setViewportSize({width:390,height:844});
  await page.locator('#director-history-status').scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/forge-history-${phase}-mobile.png`});
  await checkpoint('after-mobile-screenshot');
  const panel=await page.locator('#director').boundingBox();assert.ok(panel.x>=0&&panel.x+panel.width<=390);
  await checkpoint('mobile-bounds-checked');
  assert.deepEqual(errors,[]);
  console.log('MGR_HISTORY_CHROME_PROOF='+JSON.stringify({status:'PASS',phase,anonymous_denied:true,
    listed:expected.length,downloads,page_errors:errors,desktop_and_mobile_captured:true,
    durable_world_repeat_same_job:phase==='restarted',
    synthetic_failure_and_cancellation:phase==='restarted',synthetic_download_tamper_rejected:phase==='restarted'}));
}catch(error){
  await fs.writeFile(`${out}/history-${phase}-failure.json`,JSON.stringify({phase,error:String(error).replaceAll(token,'[redacted]')})+'\n');
  throw error;
}finally{
  await checkpoint('before-context-close');
  if(context)await context.close();
  await checkpoint('before-browser-close');
  await browser.close();
  await checkpoint('closed');
}
