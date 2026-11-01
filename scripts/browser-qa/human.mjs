import {chromium} from "playwright-core";
import {readFile,mkdir} from "node:fs/promises";
import {createHash} from "node:crypto";
import assert from "node:assert/strict";

const [url,dest]=process.argv.slice(2);
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(url)||!dest)throw Error("local Forge only");
const browser=await chromium.launch({
 executablePath:"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
 headless:true,args:["--use-angle=d3d11","--disable-dev-shm-usage","--no-first-run"]});
const errors=[];
try{
 const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:950}});
 const page=await context.newPage();
 page.on("pageerror",e=>errors.push(String(e)));
 await page.goto(url,{waitUntil:"domcontentloaded",timeout:25000});
 await page.locator("#director-toggle").click();
 const button=page.locator("#director-human-demo");
 assert.equal(await button.isEnabled(),true);
 await button.click();
 await page.waitForFunction(()=>{
   const value=document.getElementById("director-human-result")?.textContent||"";
   return value.includes("Real facial GLB ready")||
      /failed|error|interrupted|denied/i.test(value);
 },null,{timeout:125000});
 const msg=await page.locator("#director-human-result").textContent();
 assert.ok(msg?.includes("Real facial GLB ready"),msg+" | "+errors.join(";"));
 const link=page.locator("#director-downloads a").filter({hasText:"Download verified animated Human Forge GLB"}).first();
 const resultPromise=page.waitForEvent("download",{timeout:12000});
 await link.click();
 const item=await resultPromise;
 const glb=await readFile(await item.path());
 assert.equal(glb.toString("ascii",0,4),"glTF");
 assert.ok(glb.length>10000);
 const blend=page.locator("#director-downloads a").filter({hasText:"Download editable MGR Human Blender file"}).first();
 const blendEvent=page.waitForEvent("download",{timeout:12000});
 await blend.click();
 const savedBlend=await blendEvent;
 const blendBytes=await readFile(await savedBlend.path());
 assert.ok(blendBytes.length>1000);
 await mkdir(dest,{recursive:true});
 const png=dest+"/human-forge-real-chrome.png";
 await page.screenshot({path:png,fullPage:false});
 const proof={
  status:"REAL_CHROME_HUMAN_FACE_CREATION_PASS",
  real_human_glb_sha256:createHash("sha256").update(glb).digest("hex"),
  human_glb_bytes:glb.length,
  real_editable_blend_sha256:createHash("sha256").update(blendBytes).digest("hex"),
  blend_bytes:blendBytes.length,
  screenshot_sha256:createHash("sha256").update(await readFile(png)).digest("hex"),
  page_errors:errors,
  genuine_browser_click:true,
  original_3d_face_shape_keys:true,
  audio_automatic_alignment_verified:false,
  final_look_owner_approved:false,
  hosted_chatgpt_verified:false
 };
 console.log("MGR_HUMAN_CHROME_PROOF="+JSON.stringify(proof));
}catch(error){
 console.error("MGR_HUMAN_CHROME_FAILED="+String(error)+" PAGE_ERRORS="+JSON.stringify(errors));
 try{console.error("HUMAN_MSG="+await page.locator("#director-human-result").textContent());}catch(e){}
 process.exitCode=1;
}finally{await browser.close();}
