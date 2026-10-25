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
    color:document.getElementById("edit-color"),message:document.getElementById("editor-msg")};
  const limits={x:manifest.grounds.width/2,z:manifest.grounds.depth/2};
  const validBuildings=(items)=>Array.isArray(items)&&items.length===baseBuildings.length&&items.every((b,i)=>{
    const original=baseBuildings[i];
    return b&&b.id===original.id&&Array.isArray(b.center)&&b.center.length===3&&
      Array.isArray(b.size)&&b.size.length===3&&b.center[1]===original.center[1]&&
      Number.isFinite(b.center[0])&&Math.abs(b.center[0])<=limits.x&&
      Number.isFinite(b.center[2])&&Math.abs(b.center[2])<=limits.z&&
      b.size[0]===original.size[0]&&b.size[2]===original.size[2]&&
      Number.isFinite(b.size[1])&&b.size[1]>=2&&b.size[1]<=100&&
      Object.hasOwn(palette,b.material);
  });
  const projectDocument=()=>({schema:"mgr.forge.world-edit.v1",asset_sha256:worldSHA,
    buildings:buildings.map(b=>({id:b.id,center:[...b.center],size:[...b.size],material:b.material}))});
  const restoreDocument=(doc)=>{
    if(!doc||doc.schema!=="mgr.forge.world-edit.v1"||doc.asset_sha256!==worldSHA||!validBuildings(doc.buildings))
      throw new Error("Saved scene is not compatible with this world");
    buildings=baseBuildings.map((b,i)=>({...b,...doc.buildings[i]}));
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
  const saveLocal=()=>{try{localStorage.setItem(storageKey,JSON.stringify(projectDocument()));message("Saved locally. Download a copy to keep permanently.");}
    catch(error){message("Browser storage blocked; use Download World to keep edits.");}};
  const selected=()=>buildings.find(b=>b.id===edit.building.value);
  const refreshEditor=()=>{
    const b=selected();if(!b)return;
    edit.x.value=b.center[0];edit.z.value=b.center[2];edit.height.value=b.size[1];edit.color.value=b.material;
  };
  for(const b of buildings){const opt=document.createElement("option");opt.value=b.id;opt.textContent=b.id;edit.building.append(opt);}
  edit.building.addEventListener("change",refreshEditor);
  const changeBuilding=()=>{
    const b=selected();if(!b)return;
    const x=Number(edit.x.value),z=Number(edit.z.value),height=Number(edit.height.value);
    if(!Number.isFinite(x)||!Number.isFinite(z)||!Number.isFinite(height)||
       Math.abs(x)>limits.x||Math.abs(z)>limits.z||height<2||height>100||!Object.hasOwn(palette,edit.color.value)){
      message("Invalid position/height/material; edit rejected.");return;
    }
    b.center[0]=x;b.center[2]=z;b.size[1]=height;b.material=edit.color.value;
    resetGpuBuildings();saveLocal();
  };
  for(const control of [edit.x,edit.z,edit.height,edit.color])control.addEventListener("change",changeBuilding);
  document.getElementById("reset-world").addEventListener("click",()=>{
    buildings=JSON.parse(JSON.stringify(baseBuildings));resetGpuBuildings();refreshEditor();saveLocal();message("Original world restored.");
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
    try{restoreDocument(JSON.parse(await file.text()));resetGpuBuildings();refreshEditor();saveLocal();message("World edits loaded.");}
    catch(error){message("Import rejected: incompatible or invalid world edits.");}
    event.target.value="";
  });
  resetGpuBuildings();refreshEditor();
  const halfDepth=manifest.grounds.depth/2;
  const camera={x:0,y:Math.max(9,manifest.spec.lot_size*0.6),z:halfDepth+12,yaw:0,pitch:0.12};
  const keys=new Set();
  window.addEventListener("keydown",e=>{
    if(["INPUT","SELECT","TEXTAREA"].includes(document.activeElement?.tagName))return;
    if(["Space","ArrowLeft","ArrowRight","ArrowUp","ArrowDown"].includes(e.code))e.preventDefault();
    keys.add(e.code);
  });
  window.addEventListener("keyup",e=>keys.delete(e.code));
  window.addEventListener("blur",()=>keys.clear());
  let dragging=false;
  canvas.addEventListener("pointerdown",e=>{dragging=true;canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener("pointerup",()=>dragging=false);
  canvas.addEventListener("pointermove",e=>{if(dragging){camera.yaw+=e.movementX*0.004;camera.pitch=Math.max(-1.3,Math.min(1.3,camera.pitch+e.movementY*0.004));}});
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
    getEdits:()=>projectDocument()};
  status.textContent="World loaded, opening live 3D view…";
  requestAnimationFrame(frame);
})();
