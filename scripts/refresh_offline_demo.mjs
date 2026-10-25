/** Refresh Forge-owned generated HTML without changing the embedded world or its SHA. */
import {readFile,writeFile,rename} from 'node:fs/promises';
import {resolve} from 'node:path';

const root=resolve(import.meta.dirname,'..');
const source=resolve(root,'demos/mgr-world-editor.html');
const old=await readFile(source,'utf8');
const manifest=old.match(/window\.MGR_WORLD_MANIFEST=([^;]+);window\.MGR_WORLD_BASE64=/)?.[1];
const binary=old.match(/window\.MGR_WORLD_BASE64="([A-Za-z0-9+/=]+)";window\.MGR_WORLD_SHA=/)?.[1];
const fingerprint=old.match(/window\.MGR_WORLD_SHA="([a-f0-9]{64})";/)?.[1];
if(!manifest||!binary||!fingerprint)throw Error('generated demo provenance missing');
const {createHash}=await import('node:crypto');
if(createHash('sha256').update(Buffer.from(binary,'base64')).digest('hex')!==fingerprint)
  throw Error('existing embedded GLB does not match its SHA-256');
let html=await readFile(resolve(root,'viewer/template.html'),'utf8');
const runtime=(await readFile(resolve(root,'viewer/runtime.js'),'utf8')).replaceAll('</script','<\\/script');
html=html.replace('__MGR_MANIFEST__',manifest).replace('__MGR_GLB_BASE64__',binary)
  .replace('__MGR_WORLD_SHA__',fingerprint).replace('__MGR_RUNTIME_JS__',runtime);
if(!html.includes('director-check-model')||!html.includes('director-build-godot'))
  throw Error('latest director controls missing from rendered output');
const temporary=source+'.refreshed';
await writeFile(temporary,html,'utf8');
await rename(temporary,source);
console.log(JSON.stringify({status:'PASS',source,sha256:fingerprint,bytes:Buffer.byteLength(html)}));
