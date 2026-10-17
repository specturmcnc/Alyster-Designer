const $=s=>document.querySelector(s),RAMPS=" .:-=+*#%@";
const GS={Standard:"█▓▒░▀▄▌▐.+*/\\|-",Box:"─│┌┐└┘├┤┬┴┼═║╔╗╚╝",Blocks:"■□▪▫▖▗▘▝▙▟▛▜",Symbols:"★☆♥♦♣♠•○●◆♪☺"};
const TOOLS=[["brush","✎","Brush"],["line","╱","Line"],["box","▭","Box"],["select","⬚","Select"],["fill","▣","Fill"],["erase","⌫","Erase"],["pick","⌖","Pick"],["symbols","★","Symbols"],["fade","▒","Fade"],["type","Aa","Type"],["textgen","T","Text Gen"]];
const PAL="#000000 #c00000 #00b000 #c06000 #0000d0 #c000c0 #00b0b0 #ffffff #aaaaaa #ff5555 #66ff66 #ffff55 #6666ff #ff55ff #55ffff #ff4d8d #4d7cff #ff9a3c".split(" ");
const PRE={Custom:null,Sunset:["#ff512f","#f09819"],Ocean:["#2193b0","#6dd5ed"],Neon:["#00f5a0","#ff00e5"],Fire:["#f12711","#f5af19"],Purple:["#8e2de2","#4a00e0"],Mint:["#11998e","#38ef7d"],Love:["#0077b6","#ff0080"],Gold:["#bf953f","#fcf6ba"],Ice:["#e0eafc","#4facfe"]};
const MH={"/":"\\","\\":"/","(":")",")":"(","<":">",">":"<","▌":"▐","▐":"▌","▖":"▗","▗":"▖","▘":"▝","▝":"▘","┌":"┐","┐":"┌","└":"┘","┘":"└","├":"┤","┤":"├","╔":"╗","╗":"╔","╚":"╝","╝":"╚"},MV={"▀":"▄","▄":"▀"};
let W=70,H=30,CW=10,CH=18,ch,col,tool="brush",glyph="█",fg="#ffffff",bg=null,hist=[],redo=[],frames=null,lastQ=null,lastBody=null,timer=null,pvF=null,sel=null,start=null,base=null,showGrid=false,dirty=false,caret=null,clip=null,names=[],st={id:0,source:"design",blob:null,seq:0};
const mk=(w,h,v)=>Array.from({length:h},()=>Array(w).fill(v)),cv=$("#cv"),g=cv.getContext("2d");
ch=mk(W,H," ");col=mk(W,H,null);
const note=t=>{$("#msg").textContent=t;setTimeout(()=>$("#msg").textContent="",2200)};
const text=()=>$("#letter").value||"S";
// ---------- history
const state=()=>JSON.stringify({W,H,ch,col});
function snap(){hist.push(state());if(hist.length>80)hist.shift();redo=[];dirty=true}
function restore(s){const o=JSON.parse(s);W=o.W;H=o.H;ch=o.ch;col=o.col;$("#gw").value=W;$("#gh").value=H;draw()}
$("#undo").onclick=()=>{if(hist.length){redo.push(state());restore(hist.pop())}};
$("#redo").onclick=()=>{if(redo.length){hist.push(state());restore(redo.pop())}};
// ---------- colours
const hex=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
function grad(t){const a=hex($("#c1").value),b=hex($("#c2").value);t=Math.max(0,Math.min(1,t));return"#"+a.map((v,i)=>Math.round(v+(b[i]-v)*t).toString(16).padStart(2,"0")).join("")}
const gt=(x,y,w,h)=>{const tx=x/Math.max(1,w-1),ty=y/Math.max(1,h-1),d=$("#dir").value;return d=="x"?tx:d=="y"?ty:(tx+ty)/2};
function regrad(){for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(ch[y][x].trim())col[y][x]=grad(gt(x,y,W,H));draw()}
["dir","c1","c2"].forEach(i=>$("#"+i).oninput=regrad);
$("#gp").innerHTML=Object.keys(PRE).map(k=>`<option>${k}</option>`).join("");
$("#gp").onchange=e=>{const p=PRE[e.target.value];if(p){[$("#c1").value,$("#c2").value]=p;regrad()}};
function cfxColor(x,y,w,h,i,m,F){const t=gt(x,y,w,h),own=F.fromGrid&&col[y]&&col[y][x];
 if(m=="rainbow")return`hsl(${(t*360+i*14)%360},90%,62%)`;
 if(m=="shift"){let u=(t+i*.04)%2;return grad(u>1?2-u:u)}
 if(m=="strobe"&&i%2)return"#ffffff";return own||grad(t)}
// ---------- canvas
function render(get,colf){cv.width=W*CW;cv.height=H*CH;if(bg){g.fillStyle=bg;g.fillRect(0,0,cv.width,cv.height)}
 if(showGrid){g.strokeStyle="#ffffff18";g.beginPath();for(let x=0;x<=W;x++){g.moveTo(x*CW+.5,0);g.lineTo(x*CW+.5,cv.height)}for(let y=0;y<=H;y++){g.moveTo(0,y*CH+.5);g.lineTo(cv.width,y*CH+.5)}g.stroke()}
 g.font=`${CH-3}px "Cascadia Mono",Consolas,"DejaVu Sans Mono","Segoe UI Symbol",monospace`;g.textBaseline="top";g.textAlign="center";
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){const c=get(x,y);if(c&&c.trim()){g.fillStyle=colf(x,y);g.fillText(c,x*CW+CW/2,y*CH+1)}}}
function draw(){render((x,y)=>ch[y][x],(x,y)=>col[y][x]||fg);if(sel){g.strokeStyle="#4df";g.setLineDash([4,3]);g.strokeRect(sel.x0*CW,sel.y0*CH,(sel.x1-sel.x0+1)*CW,(sel.y1-sel.y0+1)*CH);g.setLineDash([])}
 if(caret&&tool=="type"){g.strokeStyle="#4df";g.strokeRect(caret.x*CW,caret.y*CH,CW,CH)}}
function init(w,h){const a=mk(w,h," "),c=mk(w,h,null);for(let y=0;y<Math.min(h,H);y++)for(let x=0;x<Math.min(w,W);x++){a[y][x]=ch[y][x];c[y][x]=col[y][x]}W=w;H=h;ch=a;col=c;draw()}
const sz=()=>{CW=+$("#cw").value||8;CH=+$("#ch").value||14;init(Math.max(4,+$("#gw").value||W),Math.max(1,+$("#gh").value||H))};
["gw","gh","cw","ch"].forEach(i=>$("#"+i).onchange=sz);
function loadLines(L,color=true){snap();const w=Math.min(600,Math.max(4,...L.map(l=>[...l].length))),h=Math.min(300,L.length);W=w;H=h;
 ch=L.slice(0,h).map(l=>{const a=[...l];while(a.length<w)a.push(" ");return a});col=mk(w,h,null);
 for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(ch[y][x].trim())col[y][x]=color?grad(gt(x,y,w,h)):fg;
 $("#gw").value=w;$("#gh").value=h;draw();dirty=false}
// ---------- editing
const put=(x,y,c,f)=>{if(x>=0&&y>=0&&x<W&&y<H){ch[y][x]=c;col[y][x]=c==" "?null:f}};
const rect=(r,fn)=>{for(let y=r.y0;y<=r.y1;y++)for(let x=r.x0;x<=r.x1;x++)fn(x,y)};
const R=(a,b)=>({x0:Math.min(a.x,b.x),y0:Math.min(a.y,b.y),x1:Math.max(a.x,b.x),y1:Math.max(a.y,b.y)});
function line(a,b,fn){let x=a.x,y=a.y,dx=Math.abs(b.x-x),dy=-Math.abs(b.y-y),sx=x<b.x?1:-1,sy=y<b.y?1:-1,e=dx+dy;for(;;){fn(x,y);if(x==b.x&&y==b.y)break;const e2=2*e;if(e2>=dy){e+=dy;x+=sx}if(e2<=dx){e+=dx;y+=sy}}}
const cell=e=>{const r=cv.getBoundingClientRect();return{x:Math.max(0,Math.min(W-1,Math.floor((e.clientX-r.left)/CW))),y:Math.max(0,Math.min(H-1,Math.floor((e.clientY-r.top)/CH)))}};
function paint(p){if(tool=="brush"||tool=="symbols")put(p.x,p.y,glyph,fg);else if(tool=="erase")put(p.x,p.y," ",null);else if(tool=="fade"){const i=RAMPS.indexOf(ch[p.y][p.x]);if(i>0)put(p.x,p.y,RAMPS[i-1],col[p.y][p.x]||fg)}}
function fill(p){const t=ch[p.y][p.x],s=[p];if(t==glyph&&(col[p.y][p.x]||fg)==fg)return;while(s.length){const{x,y}=s.pop();if(x<0||y<0||x>=W||y>=H||ch[y][x]!=t)continue;put(x,y,glyph,fg);s.push({x:x+1,y},{x:x-1,y},{x,y:y+1},{x,y:y-1})}}
cv.onpointerdown=e=>{if(timer){stop();frames=null;lastQ=null}const p=cell(e);cv.setPointerCapture(e.pointerId);
 if(tool=="pick"){const c=ch[p.y][p.x];if(c.trim())setGlyph(c);if(col[p.y][p.x])setFg(col[p.y][p.x]);return}
 if(tool=="type"){caret=p;draw();return}
 snap();start=p;if(tool=="fill"){fill(p);draw();start=null;return}
 if(tool=="select")sel=R(p,p);else if(tool=="line"||tool=="box")base=JSON.stringify({ch,col});else paint(p);draw()};
cv.onpointermove=e=>{if(!start)return;const p=cell(e);
 if(tool=="select")sel=R(start,p);
 else if(base){const o=JSON.parse(base);ch=o.ch;col=o.col;if(tool=="line")line(start,p,(x,y)=>put(x,y,glyph,fg));else{const r=R(start,p);rect(r,(x,y)=>{if(x==r.x0||x==r.x1||y==r.y0||y==r.y1)put(x,y,glyph,fg)})}}
 else{line(start,p,(x,y)=>paint({x,y}));start=p}draw()};
cv.onpointerup=()=>{start=null;base=null;draw()};
addEventListener("keydown",e=>{if(e.target.matches("input,textarea,select"))return;
 if(e.ctrlKey&&e.key=="z"){e.preventDefault();$("#undo").click();return}if(e.ctrlKey&&e.key=="y"){e.preventDefault();$("#redo").click();return}
 if(e.key=="Delete"&&sel){snap();rect(sel,(x,y)=>put(x,y," ",null));draw();return}
 if(tool!="type"||!caret||e.ctrlKey)return;const k=e.key;
 if(k.length==1){snap();put(caret.x,caret.y,k,fg);caret.x=Math.min(W-1,caret.x+1)}
 else if(k=="Backspace"){caret.x=Math.max(0,caret.x-1);put(caret.x,caret.y," ",null)}
 else if(k=="Enter")caret={x:0,y:Math.min(H-1,caret.y+1)};
 else if(k=="ArrowLeft")caret.x=Math.max(0,caret.x-1);else if(k=="ArrowRight")caret.x=Math.min(W-1,caret.x+1);
 else if(k=="ArrowUp")caret.y=Math.max(0,caret.y-1);else if(k=="ArrowDown")caret.y=Math.min(H-1,caret.y+1);else return;
 e.preventDefault();draw()});
$("#tools").innerHTML=TOOLS.map(([k,i,n])=>`<button data-t="${k}"><i>${i}</i>${n}</button>`).join("");
$("#tools").onclick=e=>{const b=e.target.closest("button");if(!b)return;if(b.dataset.t=="textgen"){$("#tg").hidden=false;return}tool=b.dataset.t;if(tool=="symbols")showTab("Symbols");if(tool!="select")sel=null;[...$("#tools").children].forEach(c=>c.classList.toggle("on",c==b));draw()};
$("#tools").children[0].classList.add("on");
function setGlyph(c){glyph=c;[...$("#gl").children].forEach(b=>b.classList.toggle("on",b.textContent==c));if(tool=="erase"||tool=="pick")$("#tools").children[0].click()}
function showTab(n){[...$("#gt").children].forEach(b=>b.classList.toggle("on",b.textContent==n));$("#gl").innerHTML=[...GS[n]].map(c=>`<button class="${c==glyph?"on":""}">${c}</button>`).join("")}
$("#gt").innerHTML=Object.keys(GS).map(n=>`<button>${n}</button>`).join("");$("#gt").onclick=e=>e.target.closest("button")&&showTab(e.target.textContent);
$("#gl").onclick=e=>e.target.closest("button")&&setGlyph(e.target.textContent);$("#gc").oninput=e=>e.target.value&&setGlyph(e.target.value);showTab("Standard");
function setFg(c){fg=c;$("#fg").value=c}$("#fg").oninput=e=>fg=e.target.value;
$("#pal").innerHTML=PAL.map(c=>`<button style="background:${c}" data-c="${c}" aria-label="${c}"></button>`).join("");$("#pal").onclick=e=>e.target.dataset.c&&setFg(e.target.dataset.c);
$("#sg").onchange=e=>{showGrid=e.target.checked;draw()};$("#clr").onclick=()=>{snap();ch=mk(W,H," ");col=mk(W,H,null);frames=null;stop()};
$("#bgc").oninput=e=>{bg=e.target.value;draw()};$("#bgn").onclick=()=>{bg=null;draw()};
const reg=()=>sel||{x0:0,y0:0,x1:W-1,y1:H-1};
function flip(h){snap();const r=reg();
 if(h)for(let y=r.y0;y<=r.y1;y++)for(let a=r.x0,b=r.x1;a<=b;a++,b--){const ca=ch[y][a],cb=ch[y][b],fa=col[y][a],fb=col[y][b];ch[y][a]=MH[cb]||cb;ch[y][b]=MH[ca]||ca;col[y][a]=fb;col[y][b]=fa}
 else for(let x=r.x0;x<=r.x1;x++)for(let a=r.y0,b=r.y1;a<=b;a++,b--){const ca=ch[a][x],cb=ch[b][x],fa=col[a][x],fb=col[b][x];ch[a][x]=MV[cb]||cb;ch[b][x]=MV[ca]||ca;col[a][x]=fb;col[b][x]=fa}draw()}
$("#fh").onclick=()=>flip(true);$("#fv").onclick=()=>flip(false);
$("#mr").onclick=()=>{snap();for(let y=0;y<H;y++)for(let x=0;x<W>>1;x++){const c=ch[y][x];ch[y][W-1-x]=MH[c]||c;col[y][W-1-x]=col[y][x]}draw()};
function copy(cut){const r=reg();clip={w:r.x1-r.x0+1,h:r.y1-r.y0+1,ch:[],col:[]};for(let y=r.y0;y<=r.y1;y++){clip.ch.push(ch[y].slice(r.x0,r.x1+1));clip.col.push(col[y].slice(r.x0,r.x1+1))}
 if(cut){snap();rect(r,(x,y)=>put(x,y," ",null));draw()}}
$("#cp").onclick=()=>copy(false);$("#ct").onclick=()=>copy(true);
$("#ps").onclick=()=>{if(!clip)return;snap();const o=sel||{x0:0,y0:0};for(let y=0;y<clip.h;y++)for(let x=0;x<clip.w;x++)if(clip.ch[y][x].trim())put(o.x0+x,o.y0+y,clip.ch[y][x],clip.col[y][x]||fg);draw()};
const dl=(blob,n)=>{const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=n;a.click()};
$("#sv").onclick=()=>dl(new Blob([JSON.stringify({W,H,ch,col,bg})],{type:"application/json"}),"alyster-project.json");
$("#ld").onclick=()=>$("#ldf").click();
$("#ldf").onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const o=JSON.parse(await f.text());snap();bg=o.bg||null;restore(JSON.stringify(o))}catch{note("Not a saved project file.")}e.target.value=""};
// ---------- generate (designs, photos, GIFs, drawing)
const qs=(src,x={})=>new URLSearchParams({text:text(),id:st.id,wrap:$("#wrap").value,cols:$("#cols").value,ramp:$("#ramp").value,fx:$("#fx").value,src,...x});
async function init0(){const r=await(await fetch("/api/designs")).json();
 r.ramps.forEach(n=>$("#ramp").add(new Option(n,n)));r.effects.forEach(n=>$("#fx").add(new Option(n,n)));names=r.designs.map(d=>d.name);buildGallery();pick(0)}
function buildGallery(){const gl=$("#gallery");gl.innerHTML="";names.forEach((name,i)=>{const b=document.createElement("button");b.className="card"+(i===st.id&&st.source=="design"?" on":"");
 b.innerHTML=`<img alt="${name}" loading="lazy" src="/api/thumb?${new URLSearchParams({text:text().split("\n")[0].slice(0,4),id:i,size:150})}"><div>${i+1}. ${name}</div>`;b.onclick=()=>pick(i);gl.appendChild(b)})}
function pick(i){st.id=i;st.source="design";document.querySelectorAll(".card").forEach((c,k)=>c.classList.toggle("on",k===i));update()}
async function update(){const mine=++st.seq;stop();let q,opt={};
 if(st.source=="design")q=qs("design");else{q=qs(/gif$/i.test(st.blob.type)?"gif":"image");opt={method:"POST",body:st.blob}}
 try{const j=await(await fetch("/api/frames?"+q,opt)).json();if(mine!==st.seq)return;if(j.error)return note(j.error);
  frames=j.frames;lastQ=q;lastBody=st.source=="design"?null:st.blob;loadLines(frames[0].lines);if(frames.length>1)play()}
 catch{note("Server not reachable – is server.py running?")}}
let tm;$("#letter").oninput=()=>{clearTimeout(tm);tm=setTimeout(()=>{buildGallery();if(st.source=="design")update()},350)};
$("#cols").oninput=()=>{$("#colsv").textContent=$("#cols").value;clearTimeout(tm);tm=setTimeout(update,150)};
["wrap","ramp","fx"].forEach(i=>$("#"+i).onchange=update);
$("#file").onchange=e=>{const f=e.target.files[0];if(!f)return;st.source="blob";st.blob=f;document.querySelectorAll(".card").forEach(c=>c.classList.remove("on"));update()};
document.querySelectorAll(".tabs button[data-tab]").forEach(b=>b.onclick=()=>{document.querySelectorAll(".tabs button[data-tab]").forEach(x=>x.classList.toggle("on",x===b));
 ["gallery","draw"].forEach(k=>$("#"+k).hidden=b.dataset.tab!==k)});
const pad=$("#pad"),px=pad.getContext("2d");let drawing=false,last=null;
const clearPad=()=>{px.fillStyle="#fff";px.fillRect(0,0,pad.width,pad.height)};clearPad();px.lineCap=px.lineJoin="round";
const pos=e=>{const r=pad.getBoundingClientRect();return[(e.clientX-r.left)*pad.width/r.width,(e.clientY-r.top)*pad.height/r.height]};
function stroke(p){px.strokeStyle="#000";px.lineWidth=$("#brush").value;px.beginPath();px.moveTo(last[0],last[1]);px.lineTo(p[0],p[1]);px.stroke();last=p}
pad.onpointerdown=e=>{drawing=true;last=pos(e);pad.setPointerCapture(e.pointerId);stroke(last)};pad.onpointermove=e=>{if(drawing)stroke(pos(e))};
pad.onpointerup=()=>{if(!drawing)return;drawing=false;pad.toBlob(b=>{st.source="blob";st.blob=b;document.querySelectorAll(".card").forEach(c=>c.classList.remove("on"));update()})};
$("#clear").onclick=clearPad;
// ---------- effects on the grid + preview
async function animateGrid(){if($("#fx").value=="none")return note("Pick an Effect first.");stop();const body=JSON.stringify({lines:ch.map(r=>r.join(""))}),q=new URLSearchParams({fx:$("#fx").value,src:"lines"});
 const j=await(await fetch("/api/frames?"+q,{method:"POST",body})).json();if(j.error)return note(j.error);frames=j.frames;frames.fromGrid=true;lastQ=q;lastBody=new Blob([body]);dirty=false;play()}
$("#afx").onclick=animateGrid;
function play(){stop();const F=frames&&frames.length>1?frames:pvF;let i=0;const w=Math.max(...F[0].lines.map(l=>l.length)),h=F[0].lines.length;$("#prev").classList.add("on");
 const step=()=>{const f=F[i%F.length],m=$("#cfx").value;render((x,y)=>f.lines[y]&&f.lines[y][x],(x,y)=>cfxColor(x,y,w,h,i,m,F));timer=setTimeout(step,f.dur);i++};step()}
function stop(){clearTimeout(timer);timer=null;$("#prev").classList.remove("on");draw()}
$("#prev").onclick=()=>{if(timer)return stop();if(frames&&frames.length>1)return play();
 if($("#cfx").value!="none"){pvF=[{lines:ch.map(r=>r.join("")),dur:70}];pvF.fromGrid=true;return play()}
 if($("#fx").value!="none")return animateGrid();note("Choose an Effect or Color motion first.")};
$("#cfx").onchange=()=>{if(timer)return;if($("#cfx").value=="none")draw()};
// ---------- export
const gridText=()=>ch.map(r=>r.join("").replace(/\s+$/,"")).join("\n");
$("#copy").onclick=async()=>{try{await navigator.clipboard.writeText(gridText());note("Copied")}catch{note("Copy failed – use Download .txt")}};
$("#save").onclick=()=>dl(new Blob([gridText()],{type:"text/plain"}),"alyster.txt");
$("#png").onclick=()=>{const was=showGrid;showGrid=false;if(timer)stop();draw();cv.toBlob(b=>{dl(b,"alyster.png");showGrid=was;draw()})};
$("#gif").onclick=async()=>{let q,opt={};
 if(!dirty&&lastQ){q=new URLSearchParams(lastQ);if(lastBody)opt={method:"POST",body:lastBody}}
 else{q=new URLSearchParams({src:"lines",fx:$("#fx").value});opt={method:"POST",body:JSON.stringify({lines:ch.map(r=>r.join(""))})}}
 q.set("format","gif");q.set("stops",$("#c1").value+","+$("#c2").value);q.set("dir",$("#dir").value);q.set("bg",bg?"white":"dark");q.set("cell",String(Math.max(6,Math.min(40,CW+4))));
 note("Building GIF…");const r=await fetch("/api/export?"+q,opt);if(!r.ok)return note("GIF failed");dl(await r.blob(),"alyster.gif");note("")};
const esc=c=>c=="&"?"&amp;":c=="<"?"&lt;":c;
$("#html").onclick=()=>{const anim=frames&&frames.length>1&&!dirty,F=anim?frames.map(f=>f.lines):[ch.map(r=>r.join(""))],w=Math.max(...F[0].map(l=>l.length)),h=F[0].length;
 const cf=(x,y)=>anim?grad(gt(x,y,w,h)):col[y]&&col[y][x]||fg;
 const rows=F.map(L=>L.map((l,y)=>[...l].map((c,x)=>c.trim()?`<span style="color:${cf(x,y)}">${esc(c)}</span>`:" ").join("")).join("\n"));
 dl(new Blob([`<!doctype html><meta charset=utf-8><body style="margin:0;background:${bg||"#080304"}"><pre id=p style="font:12px/1.1 monospace;padding:20px;margin:0"></pre><script>const F=${JSON.stringify(rows).replace(/</g,"\\u003c")},D=${JSON.stringify(anim?frames.map(f=>f.dur):[100])};let i=0;(function s(){p.innerHTML=F[i%F.length];setTimeout(s,D[i++%D.length])})()<\/script>`],{type:"text/html"}),"alyster.html")};
// ---------- .tfx export (text frames + delay). NOTE: layout is an assumption - adjust tfxBuild() if your tfx format differs.
function tfxBuild(){const anim=frames&&frames.length>1&&!dirty,F=anim?frames:[{lines:ch.map(r=>r.join("")),dur:40}];
 const w=Math.max(...F[0].lines.map(l=>l.length)),h=F[0].lines.length;
 return["TFX",`width=${w}`,`height=${h}`,`frames=${F.length}`,...F.flatMap((f,i)=>[`#frame ${i+1} delay=${f.dur}`,...f.lines.map(l=>l.padEnd(w))])].join("\n")+"\n"}
$("#tfx").onclick=()=>{dl(new Blob([tfxBuild()],{type:"text/plain"}),"alyster.tfx");note("Saved alyster.tfx")};

init0();

// ---------- Zyre-style shell: import, code editor, text-gen window, export menu
$("#imp").onclick=()=>$("#file").click();
$("#tgx").onclick=()=>$("#tg").hidden=true;
$("#tg").onclick=e=>{if(e.target.id=="tg")$("#tg").hidden=true};
$("#exp").onclick=e=>{e.stopPropagation();$("#expm").classList.toggle("open")};
addEventListener("click",()=>$("#expm").classList.remove("open"));
const view=c=>{$("#stage").hidden=c;$("#code").hidden=!c;$("#vC").classList.toggle("on",c);$("#vD").classList.toggle("on",!c)};
$("#vC").onclick=()=>{stop();$("#code").value=gridText();view(true)};
$("#vD").onclick=()=>{if(!$("#code").hidden&&$("#code").value!==gridText()){loadLines($("#code").value.split("\n"));frames=null}view(false)};
