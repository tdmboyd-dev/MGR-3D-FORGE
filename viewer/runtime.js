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
  const halfDepth=manifest.grounds.depth/2;
  const camera={x:0,y:Math.max(9,manifest.spec.lot_size*0.6),z:halfDepth+12,yaw:0,pitch:0.12};
  const keys=new Set();
  window.addEventListener("keydown",e=>{if(["Space","ArrowLeft","ArrowRight","ArrowUp","ArrowDown"].includes(e.code))e.preventDefault();keys.add(e.code);});
  window.addEventListener("keyup",e=>keys.delete(e.code));
  window.addEventListener("blur",()=>keys.clear());
  let dragging=false;
  canvas.addEventListener("pointerdown",e=>{dragging=true;canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener("pointerup",()=>dragging=false);
  canvas.addEventListener("pointermove",e=>{if(dragging){camera.yaw+=e.movementX*0.004;camera.pitch=Math.max(-1.3,Math.min(1.3,camera.pitch+e.movementY*0.004));}});
  const blocked=(x,z)=>manifest.buildings.some(b=>{
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
    frames++;
    if(now-fpsStart>500){fps=Math.round(frames*1000/(now-fpsStart));frames=0;fpsStart=now;
      status.textContent=`LIVE WebGL2 | ${manifest.buildings.length} buildings | ${fps} FPS | X ${camera.x.toFixed(1)} Y ${camera.y.toFixed(1)} Z ${camera.z.toFixed(1)} | collision stops ${hits}`;
    }
    requestAnimationFrame(frame);
  }
  window.MGR_FORGE_RUNTIME={getStatus:()=>({drawCalls:draws.length,fps,position:[camera.x,camera.y,camera.z],collisions:hits,frameActive:frames>=0})};
  status.textContent="World loaded, opening live 3D view…";
  requestAnimationFrame(frame);
})();
