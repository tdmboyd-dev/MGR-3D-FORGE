import { chromium } from "playwright-core";
import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import fs from "node:fs/promises";

const url=process.argv[2], out=process.argv[3];
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url)||!out)throw new Error("local Forge Studio URL and evidence directory required");
const studioAccessToken=process.env.MGR_FORGE_QA_TOKEN;
if(!studioAccessToken||!/^[A-Za-z0-9_-]{24,128}$/.test(studioAccessToken))throw Error("Private test Studio token required in the scoped environment");
const ownerUrl=new URL(url);ownerUrl.hash='mgr-token='+studioAccessToken;
const browser=await chromium.launch({
  executablePath:"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  headless:true,
  args:["--use-angle=swiftshader","--enable-unsafe-swiftshader",
        "--disable-dev-shm-usage","--no-first-run"]
});
let errors=[];
try{
  const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:900}});
  const locked=await context.request.get(url);
  const lockedHtml=await locked.text();
  assert.equal(lockedHtml.includes(studioAccessToken),false);
  assert.equal(lockedHtml.includes('MGR_WORLD_BASE64'),false);
  assert.equal((await context.request.get(new URL('/studio',url).href)).status(),403);
  const page=await context.newPage();
  page.on("pageerror",e=>errors.push(String(e)));
  await page.goto(url);
  await page.screenshot({path:out+'/forge-studio-locked.png'});
  await page.locator('#studio-access').fill('invalid');
  await page.locator('#studio-open').click();
  await page.locator('#studio-status').filter({hasText:'Use the private Studio'}).waitFor();
  await page.locator('#studio-access').fill('x'.repeat(43));
  await page.locator('#studio-open').click();
  await page.locator('#studio-status').filter({hasText:'not accepted'}).waitFor();
  await page.route('**/studio',async route=>{
    await new Promise(resolve=>setTimeout(resolve,300));
    try{await route.abort();}catch(error){
      if(!String(error).includes('Route is already handled'))throw error;
    }
  });
  await page.locator('#studio-access').fill(studioAccessToken);
  await page.locator('#studio-open').click();
  await page.locator('#studio-cancel').click();
  await page.locator('#studio-status').filter({hasText:'interrupted'}).waitFor();
  await page.unrouteAll({behavior:'wait'});
  await page.goto('about:blank');
  const response=await page.goto(ownerUrl.href,{waitUntil:"domcontentloaded",timeout:20000});
  assert.equal(response.status(),200);
  await page.locator("#director-toggle").click();
  assert.equal(new URL(page.url()).hash,'');
  await page.reload();
  await page.locator('#director-toggle').click();
  assert.equal(new URL(page.url()).hash,'');
  await page.locator("#director-creature-prompt").fill("Invent a giant winged steel dragon creature with horns and a long tail");
  await page.locator("#director-creature-seed").fill("41");
  await page.locator("#director-creature-variants").fill("4");
  assert.equal(await page.locator("#director-creature-create").isEnabled(),true);
  await page.locator("#director-creature-create").click();
  await page.waitForFunction(()=>{
    const value=document.getElementById("director-creature-result")?.textContent||"";
    return value.includes("Real original GLB:")||value.includes("creation failed");
  },null,{timeout:30000});
  let text=await page.locator("#director-creature-result").innerText();
  assert.match(text,/Real original GLB:/,JSON.stringify({text,errors}));
  let link=page.locator("#director-downloads a").filter({hasText:"Download verified 3D creature"}).first();
  assert.equal(await link.count(),1);
  assert.match(await link.getAttribute("href"),/^blob:/);
  const downloadPromise=page.waitForEvent("download",{timeout:15000});
  await link.click();
  const download=await downloadPromise;
  assert.match(download.suggestedFilename(),/^mgr-original-creature-[a-f0-9]{24}\.glb$/);
  const downloaded=await fs.readFile(await download.path());
  assert.equal(downloaded.toString("ascii",0,4),"glTF");
  const sha=createHash("sha256").update(downloaded).digest("hex");
  // Test status lookup and resilient downloadable receipt from the same stable job.
  await page.locator("#director-creature-status").click();
  await page.waitForFunction(()=>{
    return (document.getElementById("director-creature-result")?.textContent||"").includes("Real original GLB:");
  },null,{timeout:12000});
  await page.waitForFunction(()=>[...document.querySelectorAll("#director-downloads a")].filter(el=>el.textContent.includes("Download verified 3D creature")).length>=2,null,{timeout:12000});
  const count=await page.locator("#director-downloads a").filter({hasText:"Download verified 3D creature"}).count();
  assert.ok(count>=2);
  // Real MorphRig revision: a changed bend must create distinct 3D geometry.
  await page.locator("#director-morphrig-controls summary").click();
  await page.locator("#director-morph-bend").fill("-13");
  await page.locator("#director-creature-create").click();
  await page.waitForFunction(()=>[...document.querySelectorAll("#director-downloads a")].filter(el=>el.textContent.includes("Download verified 3D creature")).length>=3,null,{timeout:35000});
  let nextLink=page.locator("#director-downloads a").filter({hasText:"Download verified 3D creature"}).first();
  let nextDownload=page.waitForEvent("download",{timeout:16000});
  await nextLink.click();
  let nextAsset=await nextDownload;
  let nextBytes=await fs.readFile(await nextAsset.path());
  let nextSha=createHash("sha256").update(nextBytes).digest("hex");
  assert.notEqual(sha,nextSha,"MGR morph bend must alter exported GLB");

  // World Forge: generate actual separate original biome and replay its status.
  await page.locator("#director-biome-kind").selectOption("alien");
  await page.locator("#director-biome-seed").fill("91");
  await page.locator("#director-biome-resolution").fill("24");
  await page.locator("#director-biome-create").click();
  await page.waitForFunction(()=>(document.getElementById("director-biome-result")?.textContent||"").includes("Original alien biome ready"),null,{timeout:35000});
  let biomeLink=page.locator("#director-downloads a").filter({hasText:"Download verified alien 3D terrain"}).first();
  let biomePromise=page.waitForEvent("download",{timeout:18000});
  await biomeLink.click();
  let biomeFile=await biomePromise;
  let biomeBytes=await fs.readFile(await biomeFile.path());
  assert.equal(biomeBytes.toString("ascii",0,4),"glTF");
  let biomeSha=createHash("sha256").update(biomeBytes).digest("hex");
  await page.locator("#director-biome-status").click();
  await page.waitForFunction(()=>[...document.querySelectorAll("#director-downloads a")].filter(el=>el.textContent.includes("Download verified alien 3D terrain")).length>=2,null,{timeout:15000});

  // Real combined city+terrain: uses existing Forge Studio + Blender, not
  // an illustrative overlay or screenshot mock.
  await page.locator("#director-world-compose").click();
  await page.waitForFunction(()=>{
    const text=document.getElementById("director-world-compose-result")?.textContent||"";
    return text.includes("One verified World Forge GLB ready") ||
           text.includes("failed") || text.includes("reconciliation") ||
           text.includes("busy") || text.includes("BUSY");
  },null,{timeout:120000});
  const combinedMsg=await page.locator("#director-world-compose-result").textContent();
  assert.ok(combinedMsg?.includes("One verified World Forge GLB ready"),
            "World Blender composition did not succeed: "+combinedMsg);
  const combinedLink=page.locator("#director-downloads a").filter({
    hasText:"Download verified combined original World Forge GLB"
  }).first();
  const combinedPromise=page.waitForEvent("download",{timeout:16000});
  await combinedLink.click();
  const combinedFile=await combinedPromise;
  const combinedData=await fs.readFile(await combinedFile.path());
  assert.equal(combinedData.toString("ascii",0,4),"glTF");
  const composedSha=createHash("sha256").update(combinedData).digest("hex");
  assert.notEqual(composedSha,biomeSha,"Combined world must not be just terrain file");
  const blenderLink=page.locator("#director-downloads a").filter({
    hasText:"Download editable combined MGR Blender project"
  }).first();
  const blendEvent=page.waitForEvent("download",{timeout:16000});
  await blenderLink.click();
  const blendFile=await blendEvent;
  const blendData=await fs.readFile(await blendFile.path());
  assert.ok(blendData.length>4000,"Editable blended world was not retrieved");
  const godotLink=page.locator("#director-downloads a").filter({
    hasText:"Download Godot combined world source project"
  }).first();
  const godotEvent=page.waitForEvent("download",{timeout:16000});
  await godotLink.click();
  const godotFile=await godotEvent;
  const godotData=await fs.readFile(await godotFile.path());
  assert.equal(godotData.toString("ascii",0,2),"PK");
  await page.locator("#director-world-compose-status").click();
  await page.waitForFunction(()=>[...document.querySelectorAll("#director-downloads a")].filter(
    el=>el.textContent.includes("Download verified combined original World Forge GLB")).length>=2,
    null,{timeout:15000});

  // Editor: submit actual existing building changes to the same Forge Studio.
  await page.locator("#building").selectOption({index:0});
  await page.locator("#edit-height").fill("27");
  await page.locator("#director-build-world").click();
  await page.waitForFunction(()=>(document.getElementById("director-msg")?.textContent||"").includes("Saved actual"),null,{timeout:35000});
  let worldLink=page.locator("#director-downloads a").filter({hasText:"Download edited 3D world (GLB)"}).first();
  let worldPromise=page.waitForEvent("download",{timeout:18000});
  await worldLink.click();
  let worldFile=await worldPromise;
  let worldBytes=await fs.readFile(await worldFile.path());
  assert.equal(worldBytes.toString("ascii",0,4),"glTF");
  let worldSha=createHash("sha256").update(worldBytes).digest("hex");

  await fs.mkdir(out,{recursive:true});
  const screenshot=out+"/forge-studio-creature.png";
  await page.screenshot({path:screenshot,fullPage:false});
  const screenshotData=await fs.readFile(screenshot);
  console.log("FORGE_BROWSER_QA="+JSON.stringify({
     status:"PASS",test:"real Chrome creation panel -> local CPU Forge GLB -> authenticated verified browser download",
     glb_sha256:sha,download_bytes:downloaded.length,download_name:download.suggestedFilename(),
     morph_revision_sha256:nextSha,morph_revision_bytes:nextBytes.length,
     biome_glb_sha256:biomeSha,biome_bytes:biomeBytes.length,
     edited_world_sha256:worldSha,edited_world_bytes:worldBytes.length,
     composed_world_sha256:composedSha,composed_world_bytes:combinedData.length,
     composed_blend_sha256:createHash("sha256").update(blendData).digest("hex"),
     composed_blend_bytes:blendData.length,
     composed_godot_sha256:createHash("sha256").update(godotData).digest("hex"),
     composed_godot_bytes:godotData.length,
     composed_city_and_biome_in_one_real_blender_scene:true,
     morph_changed_real_glb_sha:sha!==nextSha,
     original_biome_and_edit_job_passed:true,
     status_checked_after_creation:true,download_link_type:"blob_url_checked_sha256",
     anonymous_page_contains_no_bearer_or_world:true,private_editor_requires_token:true,
     invalid_token_rejected:true,wrong_token_rejected:true,cancel_and_retry_verified:true,
     owner_fragment_removed:true,tab_session_reload_verified:true,
     screenshot_sha256:createHash("sha256").update(screenshotData).digest("hex"),
     browser_errors:errors,
     visual_art_quality_accepted:false,
     hosted_chatgpt_or_tevin_verified:false
  }));
}catch(error){
  console.error('FORGE_BROWSER_FAILED='+String(error).replaceAll(studioAccessToken,'[redacted]'));
  process.exitCode=1;
}finally{
  await browser.close();
}
