// ════════════════════════════════════════════════════════════
//  GLWORLD — Temple-Run-principled outdoor world renderer.
//  Renders into the #glC WebGL canvas BENEATH fxC; drawT leaves the
//  background transparent on outdoor stages so this world shows through.
//  One projection (identical to prjT), terrain mesh with rolling hills,
//  mirrored-tiling ground, cross-quad scenery pool with blob shadows,
//  depth fog into a gradient sky. Chunk recycling via scroll phase.
// ════════════════════════════════════════════════════════════
var GLWORLD=(function(){
  var gl,cv,Wp,Hp,vpY,gNear,corrW,ps;
  var progT,progS,progP,meshT,skyBuf,dynBuf=null;
  var texGround=[],texProps=null,texBlob=null;
  var propPool=[],curShift=0;
  var LOOK=[
    {fog:[0.86,0.76,0.58],skyTop:[0.55,0.42,0.30],sun:[0.5,0.30,1.0,0.5],tint:[1.05,0.98,0.88],hill:0,props:[]},
    {fog:[0.98,0.85,0.70],skyTop:[0.44,0.62,0.94],sun:[0.30,0.30,1.0,0.85],tint:[1,1,1],hill:60,props:[0,1,11]},
    {fog:[0.99,0.90,0.92],skyTop:[0.55,0.70,0.95],sun:[0.72,0.26,0.9,0.7],tint:[0.86,0.96,0.82],hill:44,props:[2,2,11]},
    {fog:[0.88,0.95,0.99],skyTop:[0.40,0.64,0.97],sun:[0.6,0.22,1.0,0.8],tint:[0.98,1.02,0.98],hill:34,props:[4,6,5]},
    {fog:[0.70,0.85,0.95],skyTop:[0.36,0.62,0.93],sun:[0.35,0.26,0.55,0.35],tint:[0.70,0.82,0.94],hill:26,props:[3,10,4]},
    {fog:[0.55,0.65,0.72],skyTop:[0.18,0.28,0.52],sun:[0.5,0.24,0.55,0.5],tint:[0.9,1.0,0.95],hill:52,props:[7,7,11]},
    {fog:[0.99,0.95,0.78],skyTop:[0.36,0.60,0.96],sun:[0.5,0.24,1.3,1.0],tint:[1.06,1.02,0.9],hill:38,props:[8,8,11]},
    {fog:[0.94,0.96,1.0],skyTop:[0.35,0.55,0.95],sun:[0.62,0.24,1.1,0.8],tint:[1,1,1.04],hill:80,props:[9,9,6]},
    {fog:[0.99,0.72,0.50],skyTop:[0.44,0.30,0.55],sun:[0.5,0.28,1.6,1.2],tint:[1.08,0.94,0.86],hill:30,props:[6,5,4]}
  ];
  function sh2(t,src){var s=gl.createShader(t);gl.shaderSource(s,src);gl.compileShader(s);
    if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(s);return s;}
  function prog2(vs,fs){var p=gl.createProgram();gl.attachShader(p,sh2(gl.VERTEX_SHADER,vs));
    gl.attachShader(p,sh2(gl.FRAGMENT_SHADER,fs));gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw gl.getProgramInfoLog(p);return p;}
  var PROJ='float s=300.0/(300.0+z);float sx=uW*0.5+wx*s+uShift;float sy=uVpy+(uGnear-uVpy)*s-wy*s;gl_Position=vec4(sx/uW*2.0-1.0,1.0-sy/uH*2.0,z/1600.0*1.9-0.9,1.0);';
  var VS_T='attribute vec2 aXZ;uniform float uW,uH,uVpy,uGnear,uCorrW,uWz,uHill,uShift;varying vec2 vUV;varying float vZ;varying float vHgt;'+
    'float hill(vec2 p){return (sin(p.x*1.9+p.y*0.011)*0.55+sin(p.x*3.7+p.y*0.023+1.7)*0.30+sin(p.y*0.017+p.x)*0.35);}'+
    'void main(){float zw=aXZ.y+uWz;float wx=aXZ.x*uCorrW;float edge=max(0.0,abs(aXZ.x)-0.85);'+
    'float h=uHill*edge*(0.6+0.4*hill(vec2(aXZ.x,zw)))*(0.5+0.5*hill(vec2(aXZ.x*0.7+3.0,zw*0.7)));'+
    'float wy=h;float z=aXZ.y;vUV=vec2(aXZ.x*3.2,zw*0.045);vZ=z;vHgt=h;'+PROJ+'}';
  var FS_T='precision mediump float;uniform sampler2D uTex;uniform vec3 uFog;uniform vec3 uTint;uniform float uFogStart,uFogEnd;varying vec2 vUV;varying float vZ;varying float vHgt;'+
    'void main(){vec2 uv=abs(fract(vUV*0.5)*2.0-1.0);vec3 c=texture2D(uTex,uv).rgb*uTint;c*=(1.0-min(0.25,vHgt*0.002));'+
    'float f=smoothstep(uFogStart,uFogEnd,vZ);gl_FragColor=vec4(mix(c,uFog,f),1.0);}';
  var VS_S='attribute vec2 aP;varying vec2 vP;void main(){vP=aP;gl_Position=vec4(aP,0.9995,1.0);}';
  var FS_S='precision mediump float;uniform vec3 uFog;uniform vec3 uSkyTop;uniform vec4 uSun;uniform float uHorizonY;varying vec2 vP;'+
    'void main(){float t=clamp((vP.y-uHorizonY)/(1.0-uHorizonY),0.0,1.0);vec3 c=mix(uFog,uSkyTop,pow(t,0.8));'+
    'vec2 sp=vec2(uSun.x*2.0-1.0,1.0-uSun.y*2.0);float d=length(vec2((vP.x-sp.x)*1.78,vP.y-sp.y));'+
    'c+=vec3(1.0,0.92,0.7)*uSun.z*0.35*exp(-d*d*18.0);c+=vec3(1.0,0.85,0.6)*uSun.w*0.12*exp(-d*3.0);gl_FragColor=vec4(c,1.0);}';
  var VS_P='attribute vec4 aQ;attribute vec2 aUV;uniform float uW,uH,uVpy,uGnear,uShift;varying vec2 vUV;varying float vZ;'+
    'void main(){float wx=aQ.x;float wy=aQ.y;float z=aQ.z;vUV=aUV;vZ=z;'+PROJ+'}';
  var FS_P='precision mediump float;uniform sampler2D uTex;uniform vec3 uFog;uniform float uFogStart,uFogEnd;uniform float uAlpha;varying vec2 vUV;varying float vZ;'+
    'void main(){vec4 c=texture2D(uTex,vUV);if(c.a<0.35)discard;float f=smoothstep(uFogStart,uFogEnd,vZ);gl_FragColor=vec4(mix(c.rgb,uFog,f),c.a*uAlpha);}';
  function buildTerrain(){
    var rows=72,cols=30,verts=[],idx=[],r,c2;
    for(r=0;r<=rows;r++){var t=r/rows,z=-60+1560*t*t*0.75+1560*t*0.25;
      for(c2=0;c2<=cols;c2++)verts.push(-3.8+7.6*c2/cols,z);}
    for(r=0;r<rows;r++)for(c2=0;c2<cols;c2++){
      var a=r*(cols+1)+c2,b=a+1,c3=a+cols+1,d=c3+1;idx.push(a,b,c3,b,d,c3);}
    var vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(verts),gl.STATIC_DRAW);
    var ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(idx),gl.STATIC_DRAW);
    return {vb:vb,ib:ib,n:idx.length};
  }
  function mkTex(img,mirror){
    var t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,mirror?gl.MIRRORED_REPEAT:gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,mirror?gl.MIRRORED_REPEAT:gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    return t;
  }
  function seedProps(stage){
    propPool=[];var pk=LOOK[stage].props;if(!pk.length)return;
    for(var i=0;i<26;i++){
      var seq=i,kind=(seq%5===4)?pk[2]:(seq%2?pk[1]:pk[0]);
      var side=(seq%2)*2-1,far=(seq%3===2),critter=(kind===10||kind===11);
      var s=(critter?0.5:1)*(far?0.62:1)*(0.85+((seq*29)%30)/100);
      propPool.push({zw:i*115+((i*37)%60),kind:kind,side:side,
        xn:(far?1.65:1.0)*side+((seq*13)%9-4)*0.03,s:s,critter:critter,seq:seq});
    }
  }
  function setProj(pr){
    gl.uniform1f(gl.getUniformLocation(pr,'uW'),Wp);
    gl.uniform1f(gl.getUniformLocation(pr,'uH'),Hp);
    gl.uniform1f(gl.getUniformLocation(pr,'uVpy'),vpY);
    gl.uniform1f(gl.getUniformLocation(pr,'uGnear'),gNear);
    var u=gl.getUniformLocation(pr,'uShift');if(u)gl.uniform1f(u,curShift);
  }
  function drawDyn(pr,arr){
    if(!dynBuf)dynBuf=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,dynBuf);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(arr),gl.DYNAMIC_DRAW);
    var aQ=gl.getAttribLocation(pr,'aQ'),aUV=gl.getAttribLocation(pr,'aUV');
    gl.enableVertexAttribArray(aQ);gl.enableVertexAttribArray(aUV);
    gl.vertexAttribPointer(aQ,3,gl.FLOAT,false,20,0);
    gl.vertexAttribPointer(aUV,2,gl.FLOAT,false,20,12);
    gl.drawArrays(gl.TRIANGLES,0,arr.length/5);
  }
  function drawProps(stage,wz){
    var pk=LOOK[stage].props;if(!pk.length||!texProps)return;
    var L=LOOK[stage],i,p;
    for(i=0;i<propPool.length;i++){p=propPool[i];while(p.zw<wz-80)p.zw+=26*115;}
    var quads=[],shadows=[];
    for(i=0;i<propPool.length;i++){
      p=propPool[i];var z=p.zw-wz;if(z<-60||z>1500)continue;
      var wx=p.xn*corrW,u0=p.kind/12,u1=(p.kind+1)/12;
      var pw=340*ps*p.s,ph=560*ps*p.s;
      var hop=p.critter?Math.abs(Math.sin(wz*0.05+p.seq))*26*ps:0;
      quads.push([wx-pw/2,0+hop,z,wx+pw/2,ph+hop,z,u0,u1]);
      quads.push([wx-pw*0.28,0+hop,z-pw*0.10,wx+pw*0.28,ph*0.985+hop,z+pw*0.10,u0,u1]);
      shadows.push([wx,z,pw*0.42]);
    }
    var sb=[];
    for(i=0;i<shadows.length;i++){var sd=shadows[i];
      sb.push(sd[0]-sd[2],2,sd[1],0,0, sd[0]+sd[2],2,sd[1],1,0, sd[0]-sd[2],-8,sd[1],0,1,
        sd[0]+sd[2],2,sd[1],1,0, sd[0]+sd[2],-8,sd[1],1,1, sd[0]-sd[2],-8,sd[1],0,1);}
    var pb=[];
    for(i=0;i<quads.length;i++){var q=quads[i];
      pb.push(q[0],q[4],q[2],q[6],1, q[3],q[4],q[5],q[7],1, q[0],q[1],q[2],q[6],0,
        q[3],q[4],q[5],q[7],1, q[3],q[1],q[5],q[7],0, q[0],q[1],q[2],q[6],0);}
    gl.useProgram(progP);setProj(progP);
    gl.uniform3fv(gl.getUniformLocation(progP,'uFog'),L.fog);
    gl.uniform1f(gl.getUniformLocation(progP,'uFogStart'),500.0);
    gl.uniform1f(gl.getUniformLocation(progP,'uFogEnd'),1400.0);
    gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
    if(sb.length){gl.uniform1f(gl.getUniformLocation(progP,'uAlpha'),0.35);
      gl.bindTexture(gl.TEXTURE_2D,texBlob);drawDyn(progP,sb);}
    gl.uniform1f(gl.getUniformLocation(progP,'uAlpha'),1.0);
    gl.bindTexture(gl.TEXTURE_2D,texProps);gl.depthMask(true);
    drawDyn(progP,pb);gl.disable(gl.BLEND);
  }
  function init(canvas){
    cv=canvas;
    gl=cv.getContext('webgl',{alpha:false,antialias:true,depth:true})||cv.getContext('experimental-webgl');
    if(!gl)throw 'no webgl';
    progT=prog2(VS_T,FS_T);progS=prog2(VS_S,FS_S);progP=prog2(VS_P,FS_P);
    meshT=buildTerrain();
    skyBuf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,skyBuf);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,-1,1,1,-1,1]),gl.STATIC_DRAW);
    var bc=document.createElement('canvas');bc.width=bc.height=64;
    var b2=bc.getContext('2d');
    var g2=b2.createRadialGradient(32,32,2,32,32,30);
    g2.addColorStop(0,'rgba(0,0,0,1)');g2.addColorStop(1,'rgba(0,0,0,0)');
    b2.fillStyle=g2;b2.fillRect(0,0,64,64);
    texBlob=mkTex(bc,false);
    gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
  }
  function setTextures(groundImgs,propsImg){
    for(var i=0;i<groundImgs.length;i++)texGround[i]=groundImgs[i]?mkTex(groundImgs[i],true):null;
    if(propsImg)texProps=mkTex(propsImg,false);
  }
  function render(stage,wz,shift){
    curShift=shift||0;
    Wp=cv.width;Hp=cv.height;vpY=Hp*0.34;gNear=Hp*0.90;corrW=Wp*0.62;ps=Wp/960;
    var L=LOOK[stage];
    gl.viewport(0,0,Wp,Hp);
    gl.clearColor(L.fog[0],L.fog[1],L.fog[2],1);
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.useProgram(progS);gl.depthMask(false);
    gl.uniform3fv(gl.getUniformLocation(progS,'uFog'),L.fog);
    gl.uniform3fv(gl.getUniformLocation(progS,'uSkyTop'),L.skyTop);
    gl.uniform4fv(gl.getUniformLocation(progS,'uSun'),L.sun);
    gl.uniform1f(gl.getUniformLocation(progS,'uHorizonY'),1.0-(vpY/Hp)*2.0);
    gl.bindBuffer(gl.ARRAY_BUFFER,skyBuf);
    var aP=gl.getAttribLocation(progS,'aP');
    gl.enableVertexAttribArray(aP);gl.vertexAttribPointer(aP,2,gl.FLOAT,false,0,0);
    gl.drawArrays(gl.TRIANGLES,0,6);gl.depthMask(true);
    if(texGround[stage]){
      gl.useProgram(progT);setProj(progT);
      gl.uniform1f(gl.getUniformLocation(progT,'uCorrW'),corrW);
      gl.uniform1f(gl.getUniformLocation(progT,'uWz'),wz);
      gl.uniform1f(gl.getUniformLocation(progT,'uHill'),LOOK[stage].hill*ps);
      gl.uniform3fv(gl.getUniformLocation(progT,'uFog'),L.fog);
      gl.uniform3fv(gl.getUniformLocation(progT,'uTint'),L.tint);
      gl.uniform1f(gl.getUniformLocation(progT,'uFogStart'),520.0);
      gl.uniform1f(gl.getUniformLocation(progT,'uFogEnd'),1380.0);
      gl.bindTexture(gl.TEXTURE_2D,texGround[stage]);
      gl.bindBuffer(gl.ARRAY_BUFFER,meshT.vb);
      var aXZ=gl.getAttribLocation(progT,'aXZ');
      gl.enableVertexAttribArray(aXZ);
      gl.vertexAttribPointer(aXZ,2,gl.FLOAT,false,0,0);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshT.ib);
      gl.drawElements(gl.TRIANGLES,meshT.n,gl.UNSIGNED_SHORT,0);
    }
    drawProps(stage,wz);
  }
  return {init:init,setTextures:setTextures,render:render,seedProps:seedProps};
})();
// GLW — lazy bootstrap wrapper: decodes GLWDATA textures once, then renders
// the outdoor world into #glC each frame. draw() returns true only when the
// world actually rendered (drawT uses that to skip its 2D background).
var GLW=(function(){
  var booted=false,failed=false,texset=false,lastStage=-1;
  var imgs=new Array(9),propsImg=null,pend=10;
  function done(){if(--pend>0)return;
    try{GLWORLD.setTextures(imgs,propsImg);texset=true;}catch(e){failed=true;}}
  function boot(){
    if(booted||failed)return;booted=true;
    try{GLWORLD.init(document.getElementById('glC'));}catch(e){failed=true;return;}
    for(var i=0;i<9;i++)(function(k){var im=new Image();
      im.onload=function(){imgs[k]=im;done();};im.onerror=done;
      im.src=GLWDATA.grounds[k];})(i);
    var pm=new Image();pm.onload=function(){propsImg=pm;done();};pm.onerror=done;
    pm.src=GLWDATA.props;
  }
  return {draw:function(stage,wz,shift){
    if(failed)return false;
    if(!booted){boot();return false;}
    if(!texset)return false;
    try{
      if(stage!==lastStage){GLWORLD.seedProps(stage);lastStage=stage;}
      GLWORLD.render(stage,wz,shift);
    }catch(e){failed=true;return false;}
    return true;
  }};
})();
