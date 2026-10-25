"use strict";
// MGR Forge World Flight — locally bundled, zero-network WebGL2 world runtime.
(() => {
  const status = document.getElementById("status");
  const canvas = document.getElementById("world");
  const gl = canvas.getContext("webgl2", { antialias: true, depth: true });
  if (!gl) { status.textContent = "WebGL2 unavailable on this browser/device"; return; }
  const fail = (message) => { status.textContent = "WORLD ERROR: " + message; throw new Error(message); };
  const manifest = window.MGR_WORLD_MANIFEST;
  const encoded = window.MGR_WORLD_BASE64;
  if (!manifest || !encoded || encoded.length > 80000000) fail("missing or oversized world");
  const raw = atob(encoded);
  const bytes = Uint8Array.from(raw, c => c.charCodeAt(0));
  const view = new DataView(bytes.buffer);
  if (bytes.length < 28 || view.getUint32(0, true) !== 0x46546c67 ||
      view.getUint32(4, true) !== 2 || view.getUint32(8, true) !== bytes.length) fail("invalid GLB header");
  const jsonSize = view.getUint32(12, true);
  if (view.getUint32(16, true) !== 0x4e4f534a || 20 + jsonSize + 8 > bytes.length) fail("invalid JSON chunk");
  const scene = JSON.parse(new TextDecoder().decode(bytes.slice(20, 20 + jsonSize)));
  const binStart = 20 + jsonSize + 8;
  if (view.getUint32(20 + jsonSize + 4, true) !== 0x004e4942) fail("invalid binary chunk");
  const shader = (kind, source) => {
    const s = gl.createShader(kind); gl.shaderSource(s, source); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) fail(gl.getShaderInfoLog(s));
    return s;
  };
  const vertex = `#version 300 es
    in vec3 position; in vec3 normal;
    uniform mat4 projection; uniform vec3 eye; uniform float yaw; uniform float pitch;
    out vec3 shading;
    void main() {
      vec3 p=position-eye;
      float c=cos(yaw), s=sin(yaw);
      p=vec3(c*p.x-s*p.z,p.y,s*p.x+c*p.z);
      float cp=cos(pitch), sp=sin(pitch);
      p=vec3(p.x,cp*p.y-sp*p.z,sp*p.y+cp*p.z);
      gl_Position=projection*vec4(p,1.0);
      vec3 n=normalize(normal);
      float diffuse=max(0.0,dot(n,normalize(vec3(0.35,0.85,0.45))));
      shading=vec3(0.28+0.72*diffuse);
    }`;
  const fragment = `#version 300 es
    precision highp float; in vec3 shading; uniform vec4 color; out vec4 outColor;
    void main(){outColor=vec4(color.rgb*shading,color.a);}`;
  const program = gl.createProgram();
  gl.attachShader(program, shader(gl.VERTEX_SHADER, vertex));
  gl.attachShader(program, shader(gl.FRAGMENT_SHADER, fragment));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) fail(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  const attribPosition = gl.getAttribLocation(program, "position");
  const attribNormal = gl.getAttribLocation(program, "normal");
  const uniforms = Object.fromEntries(["projection", "eye", "yaw", "pitch", "color"].map(k => [k, gl.getUniformLocation(program,k)]));
  const getBytes = (accessorId, component, count) => {
    const acc=scene.accessors[accessorId];
    if (!acc || acc.componentType !== component || acc.count > 2000000) fail("unsupported accessor");
    const bv=scene.bufferViews[acc.bufferView];
    const at=binStart+(bv.byteOffset || 0)+(acc.byteOffset || 0);
    const needed=acc.count*count*4;
    if (bv.byteStride || at < binStart || at+needed > bytes.length) fail("invalid accessor range");
    const output=new Uint8Array(needed); output.set(bytes.subarray(at,at+needed));
    return output;
  };
  const draws=[];
  for(const mesh of scene.meshes || []) for(const primitive of mesh.primitives || []) {
    // The authored ground/roads remain GLB geometry. Building meshes are
    // instantiated separately so edits update actual GPU geometry.
    if(primitive.material > 1) continue;
    const positions=getBytes(primitive.attributes.POSITION,5126,3);
    const normals=getBytes(primitive.attributes.NORMAL,5126,3);
    const indices=getBytes(primitive.indices,5125,1);
    const vao=gl.createVertexArray(); gl.bindVertexArray(vao);
    const upload=(location,payload) => {
      const buffer=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.bufferData(gl.ARRAY_BUFFER,payload,gl.STATIC_DRAW);
      gl.enableVertexAttribArray(location); gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
    };
    upload(attribPosition,positions); upload(attribNormal,normals);
    const element=gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,element);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.STATIC_DRAW);
    const material=scene.materials[primitive.material] || {};
    const color=material.pbrMetallicRoughness?.baseColorFactor || [0.7,0.7,0.7,1];
    draws.push({vao,count:indices.byteLength/4,color});
  }
  gl.bindVertexArray(null);
  if (!draws.length) fail("empty model");
  const worldSHA=window.MGR_WORLD_SHA;
  const storageKey="mgr.forge.world-edits.v1."+worldSHA;
  const baseBuildings=JSON.parse(JSON.stringify(manifest.buildings));
  let buildings=JSON.parse(JSON.stringify(baseBuildings));
  const palette={
    "building-brick":[0.52,0.25,0.19,1],"building-stone":[0.55,0.54,0.51,1],
    "building-blue":[0.16,0.31,0.47,1],"building-gold":[0.68,0.48,0.13,1],
    "building-emerald":[0.12,0.48,0.34,1]
  };
  const edit={building:document.getElementById("building"),x:document.getElementById("edit-x"),
    z:document.getElementById("edit-z"),height:document.getElementById("edit-height"),
    width:document.getElementById("edit-width"),depth:document.getElementById("edit-depth"),
    color:document.getElementById("edit-color"),message:document.getElementById("editor-msg"),
    undo:document.getElementById("undo-world"),redo:document.getElementById("redo-world")};
  const limits={x:manifest.grounds.width/2,z:manifest.grounds.depth/2};
  const originalIds=new Set(baseBuildings.map(b=>b.id));
  const validBuildings=(items)=>{
    if(!Array.isArray(items)||items.length>128)return false;
    const seen=new Set();
    return items.every(b=>{
      if(!b||typeof b.id!=="string"||seen.has(b.id)||
         (!originalIds.has(b.id)&&!/^mgr-created-[0-9]{4,6}$/.test(b.id)))return false;
      seen.add(b.id);
      const original=baseBuildings.find(o=>o.id===b.id);
      return Array.isArray(b.center)&&b.center.length===3&&Array.isArray(b.size)&&b.size.length===3&&
        b.center[1]===0&&b.center.every(Number.isFinite)&&b.size.every(Number.isFinite)&&
        b.size[0]>=2&&b.size[0]<=Math.max(40,original?.size[0]||0)&&
        b.size[2]>=2&&b.size[2]<=Math.max(40,original?.size[2]||0)&&
        b.size[1]>=2&&b.size[1]<=100&&
        Math.abs(b.center[0])+b.size[0]/2<=limits.x&&
        Math.abs(b.center[2])+b.size[2]/2<=limits.z&&Object.hasOwn(palette,b.material);
    });
  };
  const projectDocument=()=>({schema:"mgr.forge.world-edit.v1",asset_sha256:worldSHA,
    buildings:buildings.map(b=>({id:b.id,center:[...b.center],size:[...b.size],material:b.material}))});
  const restoreDocument=(doc)=>{
    if(!doc||doc.schema!=="mgr.forge.world-edit.v1"||doc.asset_sha256!==worldSHA||!validBuildings(doc.buildings))
      throw new Error("Saved scene is not compatible with this world");
    const originals=new Map(baseBuildings.map(b=>[b.id,b]));
    buildings=doc.buildings.map(b=>({...originals.get(b.id),...b}));
  };
  try {const persisted=localStorage.getItem(storageKey);if(persisted)restoreDocument(JSON.parse(persisted));}
  catch(error){edit.message.textContent="Old saved edits were rejected; original world loaded.";buildings=JSON.parse(JSON.stringify(baseBuildings));}
  const gpuBuildings=[];
  const faceGeometry=(b,roof=false)=>{
    const [x,,z]=b.center,[width,height,depth]=b.size;
    const w=roof?width+0.3:width,d=roof?depth+0.3:depth;
    const bottom=roof?height:0,top=roof?height+0.3:height;
    const x0=x-w/2,x1=x+w/2,z0=z-d/2,z1=z+d/2;
    const a=[x0,bottom,z0],bb=[x1,bottom,z0],c=[x1,bottom,z1],d0=[x0,bottom,z1];
    const e=[x0,top,z0],f=[x1,top,z0],g=[x1,top,z1],h=[x0,top,z1];
    const faces=[[a,bb,c,d0],[h,g,f,e],[e,f,bb,a],[f,g,c,bb],[g,h,d0,c],[h,e,a,d0]];
    const positions=[],normals=[],indices=[];
    for(const corners of faces){
      const u=corners[1].map((v,i)=>v-corners[0][i]),v=corners[2].map((n,i)=>n-corners[0][i]);
      const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
      const len=Math.hypot(...n)||1,normal=n.map(q=>q/len),offset=positions.length/3;
      for(const corner of corners){positions.push(...corner);normals.push(...normal);}
      indices.push(offset,offset+1,offset+2,offset,offset+2,offset+3);
    }
    return {positions:new Float32Array(positions),normals:new Float32Array(normals),indices:new Uint32Array(indices)};
  };
  const meshToGpu=(mesh,color)=>{
    const vao=gl.createVertexArray();gl.bindVertexArray(vao);
    const ownedBuffers=[];
    for(const [location,data] of [[attribPosition,mesh.positions],[attribNormal,mesh.normals]]){
      const buffer=gl.createBuffer();ownedBuffers.push(buffer);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);
      gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
    }
    const element=gl.createBuffer();ownedBuffers.push(element);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,element);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,mesh.indices,gl.STATIC_DRAW);
    gl.bindVertexArray(null);
    return {vao,count:mesh.indices.length,color,buffers:ownedBuffers};
  };
  const resetGpuBuildings=()=>{
    for(const model of gpuBuildings)for(const part of model){gl.deleteVertexArray(part.vao);for(const buffer of part.buffers)gl.deleteBuffer(buffer);}
    gpuBuildings.length=0;
    for(const b of buildings)gpuBuildings.push([
      meshToGpu(faceGeometry(b,false),palette[b.material]),
      meshToGpu(faceGeometry(b,true),[0.12,0.13,0.17,1])
    ]);
  };
  const message=(value)=>{edit.message.textContent=value;};
  const undoStack=[],redoStack=[];
  const snapshot=()=>JSON.parse(JSON.stringify(buildings));
  const updateHistoryButtons=()=>{edit.undo.disabled=!undoStack.length;edit.redo.disabled=!redoStack.length;};
  const checkpoint=()=>{
    undoStack.push(snapshot());if(undoStack.length>80)undoStack.shift();
    redoStack.length=0;updateHistoryButtons();
  };
  const travel=(source,destination,label)=>{
    if(!source.length)return;
    destination.push(snapshot());buildings=source.pop();
    resetGpuBuildings();syncBuildingOptions();saveLocal();updateHistoryButtons();message(label);
  };
  edit.undo.addEventListener("click",()=>travel(undoStack,redoStack,"Edit undone."));
  edit.redo.addEventListener("click",()=>travel(redoStack,undoStack,"Edit redone."));
  const saveLocal=()=>{try{localStorage.setItem(storageKey,JSON.stringify(projectDocument()));message("Saved locally. Download a copy to keep permanently.");}
    catch(error){message("Browser storage blocked; use Download World to keep edits.");}};
  const selected=()=>buildings.find(b=>b.id===edit.building.value);
  const refreshEditor=()=>{
    const b=selected();if(!b)return;
    edit.x.value=b.center[0];edit.z.value=b.center[2];edit.height.value=b.size[1];
    edit.width.value=b.size[0];edit.depth.value=b.size[2];edit.color.value=b.material;
  };
  const syncBuildingOptions=(preferred)=>{
    const target=preferred||edit.building.value;
    edit.building.replaceChildren();
    for(const b of buildings){const opt=document.createElement("option");opt.value=b.id;opt.textContent=b.id;edit.building.append(opt);}
    if(buildings.some(b=>b.id===target))edit.building.value=target;
    refreshEditor();
  };
  syncBuildingOptions();
  edit.building.addEventListener("change",refreshEditor);
  const changeBuilding=()=>{
    const b=selected();if(!b)return;
    const x=Number(edit.x.value),z=Number(edit.z.value),height=Number(edit.height.value);
    const width=Number(edit.width.value),depth=Number(edit.depth.value);
    if(!Number.isFinite(x)||!Number.isFinite(z)||!Number.isFinite(height)||
       !Number.isFinite(width)||!Number.isFinite(depth)||width<2||
       width>Math.max(40,baseBuildings.find(o=>o.id===b.id)?.size[0]||0)||depth<2||
       depth>Math.max(40,baseBuildings.find(o=>o.id===b.id)?.size[2]||0)||
       Math.abs(x)+width/2>limits.x||Math.abs(z)+depth/2>limits.z||
       height<2||height>100||!Object.hasOwn(palette,edit.color.value)){
      message("Invalid position/height/material; edit rejected.");return;
    }
    if(b.center[0]===x&&b.center[2]===z&&b.size[1]===height&&
       b.size[0]===width&&b.size[2]===depth&&b.material===edit.color.value)return;
    checkpoint();b.center[0]=x;b.center[2]=z;b.size[1]=height;
    b.size[0]=width;b.size[2]=depth;b.material=edit.color.value;
    resetGpuBuildings();saveLocal();
  };
  for(const control of [edit.x,edit.z,edit.height,edit.width,edit.depth,edit.color])control.addEventListener("change",changeBuilding);
  let createdSequence=1;
  const nextCreatedId=()=>{
    let result;
    do{result=`mgr-created-${String(createdSequence++).padStart(4,"0")}`;}
    while(buildings.some(b=>b.id===result));
    return result;
  };
  const applyScene=(proposed,label,selection)=>{
    if(!validBuildings(proposed)){message("Edit rejected: building count or geometry exceeds world limits.");return false;}
    if(JSON.stringify(buildings)===JSON.stringify(proposed))return true;
    checkpoint();buildings=proposed;resetGpuBuildings();syncBuildingOptions(selection);saveLocal();message(label);return true;
  };
  const duplicateSelected=()=>{
    const b=selected();if(!b)return false;
    const copy=JSON.parse(JSON.stringify(b));copy.id=nextCreatedId();
    copy.center[0]=Math.min(limits.x-copy.size[0]/2,copy.center[0]+copy.size[0]+2);
    copy.center[2]=Math.min(limits.z-copy.size[2]/2,copy.center[2]+copy.size[2]+2);
    return applyScene([...buildings,copy],`Duplicated ${b.id}.`,copy.id);
  };
  document.getElementById("duplicate-building").addEventListener("click",duplicateSelected);
  document.getElementById("delete-building").addEventListener("click",()=>{
    const b=selected();if(b)applyScene(buildings.filter(item=>item.id!==b.id),`Removed ${b.id}.`);
  });
  document.getElementById("reset-world").addEventListener("click",()=>{
    if(JSON.stringify(buildings)===JSON.stringify(baseBuildings))return;
    checkpoint();
    buildings=JSON.parse(JSON.stringify(baseBuildings));resetGpuBuildings();syncBuildingOptions();saveLocal();message("Original world restored.");
  });
  document.getElementById("save-world").addEventListener("click",()=>{
    const blob=new Blob([JSON.stringify(projectDocument(),null,2)+"\n"],{type:"application/json"});
    const url=URL.createObjectURL(blob),a=document.createElement("a");
    a.href=url;a.download="mgr-world-edits.json";document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);message("World changes exported as JSON.");
  });
  document.getElementById("import-world").addEventListener("change",async event=>{
    const file=event.target.files?.[0];if(!file)return;
    if(file.size>1000000){message("Import rejected: file exceeds 1 MB.");return;}
    try{const before=snapshot();restoreDocument(JSON.parse(await file.text()));
      if(JSON.stringify(before)!==JSON.stringify(buildings)){
        undoStack.push(before);if(undoStack.length>80)undoStack.shift();redoStack.length=0;updateHistoryButtons();}
      resetGpuBuildings();syncBuildingOptions();saveLocal();message("World edits loaded.");}
    catch(error){message("Import rejected: incompatible or invalid world edits.");}
    event.target.value="";
  });
  // MGR Creation Director: fixed, auditable scene commands; never eval user text.
  const panel=document.getElementById("director"),toggle=document.getElementById("director-toggle");
  const prompt=document.getElementById("director-prompt"),directorMessage=document.getElementById("director-msg");
  toggle.addEventListener("click",()=>{
    panel.hidden=!panel.hidden;toggle.setAttribute("aria-expanded",String(!panel.hidden));
    toggle.textContent=panel.hidden?"✦ Creation Chat":"✕ Close Creation Chat";
  });
  const numberPattern="(-?(?:[0-9]+(?:\\.[0-9]+)?|\\.[0-9]+))";
  const capture=(source,expression)=>{
    const m=source.match(new RegExp(expression,"i"));return m?Number(m[1]):null;
  };
  const colorNames={"gold":"building-gold","emerald":"building-emerald","green":"building-emerald",
    "brick":"building-brick","red":"building-brick","stone":"building-stone","gray":"building-stone",
    "grey":"building-stone","blue":"building-blue"};
  const commandColor=(source)=>{
    const hit=source.match(/\b(gold|emerald|green|brick|red|stone|gray|grey|blue)\b/i);
    return hit?colorNames[hit[1].toLowerCase()]:null;
  };
  const availableLot=()=>{
    const stride=manifest.spec.lot_size+manifest.spec.road_width;
    for(let row=0;row<manifest.spec.rows;row++)for(let col=0;col<manifest.spec.columns;col++){
      const x=(col-(manifest.spec.columns-1)/2)*stride;
      const z=(row-(manifest.spec.rows-1)/2)*stride;
      if(!buildings.some(b=>Math.abs(b.center[0]-x)<manifest.spec.lot_size/2&&
                            Math.abs(b.center[2]-z)<manifest.spec.lot_size/2))return [x,z];
    }
    return [0,0];
  };
  const executeCommand=(text)=>{
    const source=String(text||"").trim().toLowerCase().replace(/[.,!?]+$/g,"");
    if(!source||source.length>600){directorMessage.textContent="Enter a creation command (600 characters max).";return false;}
    let label="",proposed=snapshot(),target=selected();
    const creating=/\b(create|add|build|generate)\b/.test(source)&&/\b(building|house|tower)\b/.test(source);
    const removing=/\b(delete|remove)\b/.test(source)&&/\b(building|selected|it)\b/.test(source);
    const duplicating=/\b(duplicate|copy|clone)\b/.test(source)&&/\b(building|selected|it)\b/.test(source);
    if(creating){
      const [lotX,lotZ]=availableLot();
      const x=capture(source,`\\bx\\s*(?:=|to|at)?\\s*${numberPattern}`)??lotX;
      const z=capture(source,`\\bz\\s*(?:=|to|at)?\\s*${numberPattern}`)??lotZ;
      const height=capture(source,`\\bheight\\s*(?:=|to|of)?\\s*${numberPattern}`)??
        capture(source,`${numberPattern}\\s*(?:meters?|m)\\s*tall`)??12;
      const width=capture(source,`\\bwidth\\s*(?:=|to|of)?\\s*${numberPattern}`)??8;
      const depth=capture(source,`\\bdepth\\s*(?:=|to|of)?\\s*${numberPattern}`)??8;
      const next={id:nextCreatedId(),center:[x,0,z],size:[width,height,depth],
        material:commandColor(source)||"building-stone"};
      proposed.push(next);target=next;label=`Created ${next.id}. Export saved edits to materialize its GLB.`;
    }else if(removing){
      if(!target){directorMessage.textContent="Select a building before removing it.";return false;}
      proposed=proposed.filter(b=>b.id!==target.id);label=`Removed ${target.id}.`;
    }else if(duplicating){
      const ok=duplicateSelected();directorMessage.textContent=ok?"Building duplicated.":"Duplication rejected by world limits.";
      return ok;
    }else if(target){
      const b=proposed.find(b=>b.id===target.id);
      const height=capture(source,`\\b(?:height|tall)\\s*(?:=|to|of)?\\s*${numberPattern}`);
      const width=capture(source,`\\bwidth\\s*(?:=|to|of)?\\s*${numberPattern}`);
      const depth=capture(source,`\\bdepth\\s*(?:=|to|of)?\\s*${numberPattern}`);
      const x=capture(source,`\\bx\\s*(?:=|to|at)?\\s*${numberPattern}`);
      const z=capture(source,`\\bz\\s*(?:=|to|at)?\\s*${numberPattern}`);
      const material=commandColor(source);
      const movement=/\b(move|position|relocate)\b/.test(source);
      const sizing=/\b(set|change|make|resize|scale|height|width|depth|taller|shorter)\b/.test(source);
      const painting=/\b(paint|color|colour|make|turn)\b/.test(source);
      if((x!==null||z!==null)&&movement){
        if(x!==null)b.center[0]=x;if(z!==null)b.center[2]=z;
      }
      if(sizing){
        if(height!==null)b.size[1]=height;
        if(width!==null)b.size[0]=width;
        if(depth!==null)b.size[2]=depth;
      }
      if(material&&painting)b.material=material;
      if(JSON.stringify(proposed)===JSON.stringify(buildings)){
        directorMessage.textContent="Didn't find a supported change. Try: set height to 24, make it gold, move to x 5 z -8.";
        return false;
      }
      label=`Updated ${b.id} from your instruction.`;
    }else{directorMessage.textContent="No building selected. Try creating a building first.";return false;}
    const ok=applyScene(proposed,label,target?.id);
    directorMessage.textContent=ok?label:"Scene limits rejected that command. Use meters and stay within the world boundary.";
    return ok;
  };
  document.getElementById("director-run").addEventListener("click",()=>executeCommand(prompt.value));
  prompt.addEventListener("keydown",e=>{
    if((e.ctrlKey||e.metaKey)&&e.key==="Enter"){e.preventDefault();executeCommand(prompt.value);}
  });
  const recognitionCtor=window.SpeechRecognition||window.webkitSpeechRecognition;
  const voiceButton=document.getElementById("director-voice");
  if(!recognitionCtor){voiceButton.disabled=true;voiceButton.title="Speech input unavailable in this browser; type a command instead.";}
  else voiceButton.addEventListener("click",()=>{
    try{
      const recognizer=new recognitionCtor();recognizer.lang="en-US";recognizer.interimResults=false;
      recognizer.onresult=e=>{const heard=e.results?.[0]?.[0]?.transcript||"";
        prompt.value=heard;directorMessage.textContent=`Heard: ${heard}. Review then press Create / Change.`;};
      recognizer.onerror=e=>{directorMessage.textContent=`Voice input unavailable: ${e.error}. Type the command instead.`;};
      directorMessage.textContent="Listening. Your browser's speech service may process audio remotely; review the text before running.";
      recognizer.start();
    }catch(error){directorMessage.textContent="Speech input couldn't start. Type the command instead.";}
  });
  let referenceUrl=null;
  const imageColorButton=document.getElementById("director-sample-color");
  const imagePreview=document.getElementById("director-preview");
  imageColorButton.addEventListener("click",()=>{
    const b=selected();if(!b||!referenceUrl||!imagePreview.complete||!imagePreview.naturalWidth){
      directorMessage.textContent="Choose a building and a valid loaded image first.";return;
    }
    const sample=document.createElement("canvas");sample.width=32;sample.height=32;
    const ctx=sample.getContext("2d",{willReadFrequently:true});
    ctx.drawImage(imagePreview,0,0,32,32);
    const data=ctx.getImageData(0,0,32,32).data,totals=[0,0,0];let count=0;
    for(let i=0;i<data.length;i+=4){
      if(data[i+3]<128)continue;
      for(let j=0;j<3;j++)totals[j]+=data[i+j]/255;
      count++;
    }
    if(!count){directorMessage.textContent="Image has no visible color pixels.";return;}
    const rgb=totals.map(v=>v/count);
    const closest=Object.entries(palette).sort((a,b)=>{
        const distance=(item)=>item[1].slice(0,3).reduce((sum,v,i)=>sum+(v-rgb[i])**2,0);
        return distance(a)-distance(b);
      })[0][0];
    const proposed=snapshot().map(item=>item.id===b.id?{...item,material:closest}:item);
    if(applyScene(proposed,`Image-sampled material: ${closest}.`,b.id)){
      directorMessage.textContent=`Applied closest MGR material: ${closest}. The photo did not create 3D geometry.`;
    }
  });
  document.getElementById("director-image").addEventListener("change",e=>{
    const file=e.target.files?.[0];if(!file)return;
    if(file.size>5_000_000||!["image/png","image/jpeg","image/webp"].includes(file.type)){
      directorMessage.textContent="Image rejected: PNG/JPEG/WebP up to 5 MB only.";e.target.value="";return;
    }
    if(referenceUrl)URL.revokeObjectURL(referenceUrl);
    referenceUrl=URL.createObjectURL(file);
    imageColorButton.disabled=true;
    imagePreview.onload=()=>{imageColorButton.disabled=false;};
    imagePreview.onerror=()=>{imageColorButton.disabled=true;directorMessage.textContent="Image decode failed.";};
    imagePreview.src=referenceUrl;imagePreview.hidden=false;
    directorMessage.textContent="Image reference loaded locally. Describe what you want created; image-to-3D inference is not yet connected.";
  });
  // Optional same-origin localhost workstation. Offline files retain all existing editor behavior.
  const forgeToken=window.MGR_FORGE_STUDIO_TOKEN;
  const reliefButton=document.getElementById("director-generate-relief");
  const worldButton=document.getElementById("director-build-world");
  const blenderButton=document.getElementById("director-build-blender");
  const godotButton=document.getElementById("director-build-godot");
  const downloadLinks=document.getElementById("director-downloads");
  let activeStudioJob=null;
  const studioEnabled=typeof forgeToken==="string"&&forgeToken.length>=20&&
    location.protocol==="http:"&&location.hostname==="127.0.0.1";
  if(studioEnabled){worldButton.disabled=false;}
  const studioPost=async(path,data)=>{
    const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json",
      "X-MGR-Forge-Token":forgeToken},body:JSON.stringify(data)});
    const result=await response.json();
    if(!response.ok)throw new Error(result.error||`Studio error ${response.status}`);
    return result;
  };
  const studioLink=(url,label)=>{
    const anchor=document.createElement("a");
    anchor.href=url;anchor.textContent=label;anchor.rel="noopener";
    anchor.style.cssText="display:block;color:#9af4cd;padding:3px";
    downloadLinks.prepend(anchor);
  };
  document.getElementById("director-image").addEventListener("change",e=>{
    reliefButton.disabled=!studioEnabled||e.target.files?.[0]?.type!=="image/png"||
      e.target.files[0].size>900_000;
  });
  reliefButton.addEventListener("click",async()=>{
    const file=document.getElementById("director-image").files?.[0];
    if(!file||!studioEnabled||file.type!=="image/png"||file.size>900_000)return;
    reliefButton.disabled=true;
    try{
      const bytes=new Uint8Array(await file.arrayBuffer());let binary="";
      for(let i=0;i<bytes.length;i+=16384)binary+=String.fromCharCode(...bytes.subarray(i,i+16384));
      const result=await studioPost("/api/relief",{png_base64:btoa(binary)});
      studioLink(result.glb_url,`Download image-derived 3D relief (${result.triangles} triangles)`);
      directorMessage.textContent="True 3D relief file created from your pixels (2.5D). Hidden geometry is not inferred.";
    }catch(error){directorMessage.textContent=`3D relief failed: ${error.message}`;}
    finally{reliefButton.disabled=false;}
  });
  worldButton.addEventListener("click",async()=>{
    if(!studioEnabled)return;
    worldButton.disabled=true;
    try{
      const result=await studioPost("/api/world",{edits:projectDocument()});
      activeStudioJob=result.job_id;blenderButton.disabled=false;godotButton.disabled=false;
      studioLink(result.glb_url,"Download edited 3D world (GLB)");
      studioLink(result.html_url,"Open rebuilt editable 3D world");
      directorMessage.textContent=`Saved actual ${result.buildings}-building world in local Forge workspace.`;
    }catch(error){directorMessage.textContent=`World build failed: ${error.message}`;}
    finally{worldButton.disabled=false;}
  });
  blenderButton.addEventListener("click",async()=>{
    if(!studioEnabled||!activeStudioJob)return;
    blenderButton.disabled=true;
    try{
      let result=await studioPost("/api/blender",{job_id:activeStudioJob});
      for(let attempt=0;result.status==="RUNNING"&&attempt<180;attempt++){
        directorMessage.textContent="Building your editable Blender scene locally…";
        await new Promise(resolve=>setTimeout(resolve,1000));
        result=await studioPost("/api/blender-status",{job_id:activeStudioJob});
      }
      if(result.status!=="PASS")throw new Error(result.error||"Blender did not finish within 3 minutes");
      studioLink(result.blend_url,`Download editable Blender project (${result.editable_buildings} buildings)`);
      directorMessage.textContent="Native Blender project created and verified in the Forge workspace.";
    }catch(error){directorMessage.textContent=`Blender build failed: ${error.message}`;}
  });
  godotButton.addEventListener("click",async()=>{
    if(!studioEnabled||!activeStudioJob)return;
    godotButton.disabled=true;
    try{
      const result=await studioPost("/api/godot",{job_id:activeStudioJob});
      studioLink(result.archive_url,"Download Godot 4 project with world and collisions (ZIP)");
      directorMessage.textContent="Game-engine project packaged. Import/run acceptance in Godot is still required.";
    }catch(error){directorMessage.textContent=`Engine package failed: ${error.message}`;}
    finally{godotButton.disabled=false;}
  });
  resetGpuBuildings();refreshEditor();
  const halfDepth=manifest.grounds.depth/2;
  const camera={x:0,y:Math.max(9,manifest.spec.lot_size*0.6),z:halfDepth+12,yaw:0,pitch:0.12};
  const keys=new Set();
  window.addEventListener("keydown",e=>{
    if(["INPUT","SELECT","TEXTAREA"].includes(document.activeElement?.tagName))return;
    if((e.ctrlKey||e.metaKey)&&e.code==="KeyZ"){
      e.preventDefault();if(e.shiftKey)travel(redoStack,undoStack,"Edit redone.");
      else travel(undoStack,redoStack,"Edit undone.");return;
    }
    if((e.ctrlKey||e.metaKey)&&e.code==="KeyY"){
      e.preventDefault();travel(redoStack,undoStack,"Edit redone.");return;
    }
    if(["Space","ArrowLeft","ArrowRight","ArrowUp","ArrowDown"].includes(e.code))e.preventDefault();
    keys.add(e.code);
  });
  window.addEventListener("keyup",e=>keys.delete(e.code));
  window.addEventListener("blur",()=>keys.clear());
  const pickAt=(clientX,clientY)=>{
    const rect=canvas.getBoundingClientRect();
    const nx=((clientX-rect.left)/rect.width)*2-1;
    const ny=1-((clientY-rect.top)/rect.height)*2;
    const fov=Math.PI/3,scale=Math.tan(fov/2);
    const vx=nx*scale*(rect.width/rect.height),vy=ny*scale,vz=-1;
    const cp=Math.cos(camera.pitch),sp=Math.sin(camera.pitch);
    const ry=cp*vy+sp*vz,rz=-sp*vy+cp*vz;
    const c=Math.cos(camera.yaw),s=Math.sin(camera.yaw);
    const direction=[c*vx+s*rz,ry,-s*vx+c*rz];
    let closest=Infinity,hit=null;
    for(const b of buildings){
      const [x,,z]=b.center,[w,h,d]=b.size;
      const mins=[x-w/2,0,z-d/2],maxs=[x+w/2,h+0.3,z+d/2];
      const origin=[camera.x,camera.y,camera.z];
      let near=0,far=Infinity;
      for(let axis=0;axis<3;axis++){
        if(Math.abs(direction[axis])<1e-9){
          if(origin[axis]<mins[axis]||origin[axis]>maxs[axis]){far=-1;break;}
        } else {
          const a=(mins[axis]-origin[axis])/direction[axis];
          const end=(maxs[axis]-origin[axis])/direction[axis];
          near=Math.max(near,Math.min(a,end));far=Math.min(far,Math.max(a,end));
        }
      }
      if(far>=near&&near<closest){closest=near;hit=b.id;}
    }
    if(hit){edit.building.value=hit;refreshEditor();message(`Selected ${hit}.`);}
    return hit;
  };
  let dragging=false,pointerStart=null;
  canvas.addEventListener("pointerdown",e=>{
    if(e.button!==0)return;
    dragging=true;pointerStart={x:e.clientX,y:e.clientY,moved:false};canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointerup",e=>{
    if(dragging&&pointerStart&&!pointerStart.moved)pickAt(e.clientX,e.clientY);
    dragging=false;pointerStart=null;
  });
  canvas.addEventListener("pointercancel",()=>{dragging=false;pointerStart=null;});
  canvas.addEventListener("pointermove",e=>{
    if(!dragging)return;
    if(pointerStart&&Math.hypot(e.clientX-pointerStart.x,e.clientY-pointerStart.y)>5)pointerStart.moved=true;
    if(pointerStart?.moved){
      camera.yaw+=e.movementX*0.004;
      camera.pitch=Math.max(-1.3,Math.min(1.3,camera.pitch+e.movementY*0.004));
    }
  });
  const blocked=(x,z)=>buildings.some(b=>{
    const [bx,,bz]=b.center,[w,,d]=b.size;
    return Math.abs(x-bx)<=w/2+0.5 && Math.abs(z-bz)<=d/2+0.5;
  });
  function projection(out, fov, ratio, near, far) {
    const f=1/Math.tan(fov/2);out.fill(0);
    out[0]=f/ratio;out[5]=f;out[10]=(far+near)/(near-far);out[11]=-1;out[14]=(2*far*near)/(near-far);
  }
  gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);
  const projectionMatrix=new Float32Array(16);
  let last=performance.now(), frames=0, fpsStart=last, fps=0, hits=0;
  function frame(now){
    const dt=Math.min((now-last)/1000,0.05); last=now;
    const turn=(keys.has("ArrowRight")?1:0)-(keys.has("ArrowLeft")?1:0);
    camera.yaw+=turn*dt*1.5;
    const speed=(keys.has("ShiftLeft")?16:7)*dt;
    const f=(keys.has("KeyW")||keys.has("ArrowUp")?1:0)-(keys.has("KeyS")||keys.has("ArrowDown")?1:0);
    const strafe=(keys.has("KeyD")?1:0)-(keys.has("KeyA")?1:0);
    const dx=(Math.sin(camera.yaw)*-f+Math.cos(camera.y)*strafe)*speed;
    const dz=(-Math.cos(camera.yaw)*f-Math.sin(camera.yaw)*strafe)*speed;
    const nx=camera.x+dx,nz=camera.z+dz;
    if(!blocked(nx,nz)){camera.x=nx;camera.z=nz;} else hits++;
    camera.y=Math.max(2,Math.min(100,camera.y+((keys.has("KeyE")?1:0)-(keys.has("KeyQ")?1:0))*speed));
    const w=canvas.clientWidth,h=canvas.clientHeight;
    const dw=Math.max(1,Math.round(w*devicePixelRatio)),dh=Math.max(1,Math.round(h*devicePixelRatio));
    if(canvas.width!==dw||canvas.height!==dh){canvas.width=dw;canvas.height=dh;}
    gl.viewport(0,0,dw,dh);gl.clearColor(0.045,0.065,0.11,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    projection(projectionMatrix,Math.PI/3,dw/dh,0.05,2500);
    gl.uniformMatrix4fv(uniforms.projection,false,projectionMatrix);
    gl.uniform3f(uniforms.eye,camera.x,camera.y,camera.z);
    gl.uniform1f(uniforms.yaw,camera.yaw);gl.uniform1f(uniforms.pitch,camera.pitch);
    for(const d of draws){gl.bindVertexArray(d.vao);gl.uniform4fv(uniforms.color,d.color);gl.drawElements(gl.TRIANGLES,d.count,gl.UNSIGNED_INT,0);}
    for(let i=0;i<gpuBuildings.length;i++)for(const d of gpuBuildings[i]){
      gl.bindVertexArray(d.vao);
      const color=(buildings[i].id===edit.building.value&&d===gpuBuildings[i][0])?
        d.color.map((v,k)=>k<3?Math.min(1,v*1.28):v):d.color;
      gl.uniform4fv(uniforms.color,color);gl.drawElements(gl.TRIANGLES,d.count,gl.UNSIGNED_INT,0);
    }
    frames++;
    if(now-fpsStart>500){fps=Math.round(frames*1000/(now-fpsStart));frames=0;fpsStart=now;
      status.textContent=`LIVE WebGL2 | ${buildings.length} buildings | ${fps} FPS | X ${camera.x.toFixed(1)} Y ${camera.y.toFixed(1)} Z ${camera.z.toFixed(1)} | collision stops ${hits}`;
    }
    requestAnimationFrame(frame);
  }
  window.MGR_FORGE_RUNTIME={getStatus:()=>({drawCalls:draws.length+2*buildings.length,fps,
    position:[camera.x,camera.y,camera.z],collisions:hits,buildingCount:buildings.length,frameActive:frames>=0}),
    getEdits:()=>projectDocument(),getHistory:()=>({undo:undoStack.length,redo:redoStack.length}),
    pickAt,executeCommand};
  status.textContent="World loaded, opening live 3D view…";
  requestAnimationFrame(frame);
})();
