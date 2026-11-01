import { chromium } from "playwright-core";
import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import fs from "node:fs/promises";

const url=process.argv[2], out=process.argv[3];
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url)||!out)throw new Error("local Forge Studio URL and evidence directory required");
const browser=await chromium.launch({
  executablePath:"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  headless:true,
  args:["--use-angle=swiftshader","--enable-unsafe-swiftshader",
        "--disable-dev-shm-usage","--no-first-run"]
});
let errors=[];
try{
  const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:900}});
  const page=await context.newPage();
  page.on("pageerror",e=>errors.push(String(e)));
  const response=await page.goto(url,{waitUntil:"domcontentloaded",timeout:20000});
  assert.equal(response.status(),200);
  await page.locator("#director-toggle").click();
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
     morph_changed_real_glb_sha:sha!==nextSha,
     original_biome_and_edit_job_passed:true,
     status_checked_after_creation:true,download_link_type:"blob_url_checked_sha256",
     screenshot_sha256:createHash("sha256").update(screenshotData).digest("hex"),
     browser_errors:errors,
     visual_art_quality_accepted:false,
     hosted_chatgpt_or_tevin_verified:false
  }));
}finally{
  await browser.close();
}
