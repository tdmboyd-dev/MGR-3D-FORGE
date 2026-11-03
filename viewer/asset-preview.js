"use strict";
// Bounded static GLB geometry preview. No network, textures, animation or model inference.
window.MGR_ASSET_PREVIEW=(canvas,buffer)=>{
  if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<28||buffer.byteLength>64000000)throw Error('Preview file outside supported size.');
  const raw=new DataView(buffer),size=raw.getUint32(12,true),start=28+size;
  if(buffer.byteLength<28||raw.getUint32(0,true)!==0x46546c67||raw.getUint32(8,true)!==buffer.byteLength||start>buffer.byteLength)throw Error('Invalid preview GLB.');
  const doc=JSON.parse(new TextDecoder().decode(new Uint8Array(buffer,20,size)));
  if(doc.skins?.length||doc.animations?.length||doc.extensionsRequired?.length)throw Error('Preview supports static uncompressed geometry only.');
  const identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
  const multiply=(a,b)=>Array.from({length:16},(_,i)=>{const r=i%4,c=Math.floor(i/4);return [0,1,2,3].reduce((v,k)=>v+a[k*4+r]*b[c*4+k],0);});
  function matrix(n){
    if(n.matrix)return n.matrix;
    const [x,y,z,w]=n.rotation||[0,0,0,1],s=n.scale||[1,1,1],t=n.translation||[0,0,0];
    return [(1-2*y*y-2*z*z)*s[0],(2*x*y+2*z*w)*s[0],(2*x*z-2*y*w)*s[0],0,
      (2*x*y-2*z*w)*s[1],(1-2*x*x-2*z*z)*s[1],(2*y*z+2*x*w)*s[1],0,
      (2*x*z+2*y*w)*s[2],(2*y*z-2*x*w)*s[2],(1-2*x*x-2*y*y)*s[2],0,...t,1];
  }
  function accessor(index,width){
    const a=doc.accessors?.[index],v=doc.bufferViews?.[a?.bufferView];
    const sizes={5121:1,5123:2,5125:4,5126:4},types={1:'SCALAR',2:'VEC2',3:'VEC3',4:'VEC4'};
    if(!a||!v||v.buffer!==0||a.sparse||a.type!==types[width]||!sizes[a.componentType]||!Number.isInteger(a.count)||a.count>1500000)throw Error('Unsupported preview accessor.');
    const unit=sizes[a.componentType],stride=v.byteStride||width*unit,at=start+(v.byteOffset||0)+(a.byteOffset||0);
    if(stride<width*unit||at<start||at+(a.count-1)*stride+width*unit>Math.min(buffer.byteLength,start+(v.byteOffset||0)+v.byteLength))throw Error('Invalid preview accessor bounds.');
    const read=a.componentType===5126?(p)=>raw.getFloat32(p,true):a.componentType===5125?(p)=>raw.getUint32(p,true):a.componentType===5123?(p)=>raw.getUint16(p,true):(p)=>raw.getUint8(p);
    const out=Array.from({length:a.count},(_,i)=>Array.from({length:width},(_,k)=>read(at+i*stride+k*unit)));
    if(out.some(row=>row.some(v=>!Number.isFinite(v))))throw Error('Nonfinite preview geometry.');
    return out;
  }
  const vertices=[],colors=[],low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity],active=new Set();
  let triangles=0,nodes=0;
  function visit(id,parent){
    const n=doc.nodes?.[id];if(!n||active.has(id)||++nodes>10000)throw Error('Invalid preview scene hierarchy.');
    active.add(id);const m=multiply(parent,matrix(n));
    if(n.mesh!==undefined)for(const p of doc.meshes?.[n.mesh]?.primitives||[]){
      if((p.mode??4)!==4||p.targets||p.extensions)throw Error('Unsupported preview primitive.');
      const positions=accessor(p.attributes.POSITION,3),indices=p.indices===undefined?positions.map((_,i)=>[i]):accessor(p.indices,1);
      if(indices.length%3||triangles+indices.length/3>100000)throw Error('Preview exceeds 100,000 triangles.');
      const color=doc.materials?.[p.material]?.pbrMetallicRoughness?.baseColorFactor||[.6,.75,.85,1];
      for(let i=0;i<indices.length;i+=3){
        const tri=indices.slice(i,i+3).map(([index])=>{const p=positions[index];if(!p)throw Error('Invalid preview index.');return [0,1,2].map(r=>m[r]*p[0]+m[4+r]*p[1]+m[8+r]*p[2]+m[12+r]);});
        const a=tri[1].map((v,k)=>v-tri[0][k]),b=tri[2].map((v,k)=>v-tri[0][k]),normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],len=Math.hypot(...normal)||1;
        const light=.3+.7*Math.abs((normal[0]*.35+normal[1]*.8+normal[2]*.45)/len);
        for(const point of tri){point.forEach((v,k)=>{low[k]=Math.min(low[k],v);high[k]=Math.max(high[k],v);});vertices.push(...point);colors.push(...color.slice(0,3).map(v=>Math.max(0,Math.min(1,v*light))));}
        triangles++;
      }
    }
    for(const child of n.children||[])visit(child,m);active.delete(id);
  }
  for(const id of doc.scenes?.[doc.scene??0]?.nodes||[])visit(id,identity);
  if(!triangles)throw Error('No supported static preview triangles.');
  const center=low.map((v,k)=>(v+high[k])/2),extent=Math.max(...high.map((v,k)=>v-low[k]));
  if(!Number.isFinite(extent)||extent<=0)throw Error('Invalid preview extent.');
  const positions=new Float32Array(vertices.map((v,i)=>(v-center[i%3])/extent));
  const gl=canvas.getContext('webgl2',{antialias:true,preserveDrawingBuffer:true});if(!gl)throw Error('WebGL2 preview unavailable.');
  if(canvas.mgrDispose)canvas.mgrDispose();
  const shader=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error('Preview shader failed.');return s;};
  const vs=shader(gl.VERTEX_SHADER,`#version 300 es
    in vec3 position;in vec3 color;out vec3 c;uniform vec2 orbit;uniform float zoom;uniform float aspect;
    void main(){float a=cos(orbit.x),b=sin(orbit.x),d=cos(orbit.y),e=sin(orbit.y);vec3 p=vec3(a*position.x+b*position.z,position.y,-b*position.x+a*position.z);p=vec3(p.x,d*p.y-e*p.z,e*p.y+d*p.z);float z=p.z+2.2;gl_Position=vec4(p.x*zoom/aspect,p.y*zoom,p.z*.2,z);c=color;}`);
  const fs=shader(gl.FRAGMENT_SHADER,`#version 300 es
    precision highp float;in vec3 c;out vec4 outputColor;void main(){outputColor=vec4(c,1.0);}`);
  const program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('Preview shader linking failed.');
  const vao=gl.createVertexArray(),buffers=[];gl.bindVertexArray(vao);
  for(const [name,data] of [['position',positions],['color',new Float32Array(colors)]]){const b=gl.createBuffer();buffers.push(b);gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);const loc=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,0);}
  let yaw=.55,pitch=-.25,zoom=3.2,drag=null;
  const render=()=>{canvas.width=Math.max(1,Math.round(canvas.clientWidth*devicePixelRatio));canvas.height=Math.max(1,Math.round(canvas.clientHeight*devicePixelRatio));gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(.035,.055,.09,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.useProgram(program);gl.bindVertexArray(vao);gl.uniform2f(gl.getUniformLocation(program,'orbit'),yaw,pitch);gl.uniform1f(gl.getUniformLocation(program,'zoom'),zoom);gl.uniform1f(gl.getUniformLocation(program,'aspect'),canvas.width/canvas.height);gl.drawArrays(gl.TRIANGLES,0,triangles*3);};
  canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);};
  canvas.onpointermove=e=>{if(drag){yaw+=(e.clientX-drag[0])*.01;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-drag[1])*.01));drag=[e.clientX,e.clientY];render();}};
  canvas.onpointerup=canvas.onpointercancel=()=>{drag=null;};
  canvas.onwheel=e=>{e.preventDefault();zoom=Math.max(.5,Math.min(8,zoom*Math.exp(-e.deltaY*.001)));render();};
  const observer=new ResizeObserver(render);observer.observe(canvas);
  canvas.mgrDispose=()=>{observer.disconnect();buffers.forEach(b=>gl.deleteBuffer(b));gl.deleteVertexArray(vao);gl.deleteProgram(program);gl.deleteShader(vs);gl.deleteShader(fs);};
  canvas.dataset.triangles=String(triangles);canvas.dataset.bounds=JSON.stringify({min:low,max:high});render();
  return {triangles,bounds:{min:low,max:high},rendering:'static geometry and material colors; no textures or animation'};
};
