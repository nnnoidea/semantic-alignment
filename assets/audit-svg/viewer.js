(() => {
function scrollMotion(animate=true){return animate&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches?'smooth':'auto';}
function scrollDelta(start,size,low,high){
 if(size>high-low)return start>=high?start-low:start+size<=low?start+size-high:0;
 return start<low?start-low:Math.max(0,start+size-high);
}
function revealPage(element,preview=160,animate=true){
 const r=element.getBoundingClientRect(),height=Math.min(preview===Infinity?r.height:preview,window.innerHeight-32),dy=scrollDelta(r.top,height,16,window.innerHeight-16);
 if(dy)window.scrollBy({top:dy,behavior:scrollMotion(animate)});
}
// Terminal diagrams stay local to their detail; no new drill-down level or IDs.
function miniSelect(e){
 const item=e.target.closest('[data-mini-select]');if(!item)return;
 if(e.type==='keydown'&&e.key!=='Enter'&&e.key!==' ')return;
 e.preventDefault();const owner=item.closest('.mini-flow');
 owner.querySelectorAll('[data-mini-select]').forEach(n=>{const active=n===item;n.classList.toggle('selected',active);n.setAttribute('aria-pressed',String(active));});
 owner.querySelectorAll('[data-mini-detail]').forEach(n=>{const active=n.dataset.miniDetail===item.dataset.miniSelect;n.hidden=!active;n.open=active;});
}
document.addEventListener('click',miniSelect);document.addEventListener('keydown',miniSelect);
const inspector=document.getElementById('inspector'),sections=[...document.querySelectorAll('.inspect-content')];
const containers=[...document.querySelectorAll('.flow-level')];
let selected=null;
const views=containers.map(container=>{
 const svg=container.querySelector('svg'),canvas=container.querySelector('.flow-canvas');
 const nodes=[...svg.querySelectorAll('[data-key]')],extent=svg.viewBox.baseVal;
 let scale=1,manualZoom=false,drag=null,moved=false;
 function paint(){svg.style.width=extent.width*scale+'px';svg.style.height=extent.height*scale+'px';canvas.style.height=Math.min(extent.height*scale,Math.max(240,window.innerHeight*.58))+'px';}
 function center(){return {x:(canvas.scrollLeft+canvas.clientWidth/2)/scale,y:(canvas.scrollTop+canvas.clientHeight/2)/scale};}
 function place(p){canvas.scrollLeft=p.x*scale-canvas.clientWidth/2;canvas.scrollTop=p.y*scale-canvas.clientHeight/2;}
 function fit(){if(!canvas.clientWidth)return;if(!manualZoom)scale=canvas.clientWidth/extent.width;paint();}
 function zoom(f,cx=.5,cy=.5){const px=canvas.clientWidth*cx,py=canvas.clientHeight*cy,x=(canvas.scrollLeft+px)/scale,y=(canvas.scrollTop+py)/scale;manualZoom=true;scale=Math.max(.001,Math.min(20,scale*f));paint();canvas.scrollLeft=x*scale-px;canvas.scrollTop=y*scale-py;}
 const view={container,svg,canvas,nodes,fit,center,place,depth:Number(container.dataset.depth||1)};
 view.reveal=(node,animate=true)=>{
  const target=node.classList.contains('relation-node')?node.querySelector('text')||node:node;
  let r=target.getBoundingClientRect();const c=canvas.getBoundingClientRect(),left=c.left+canvas.clientLeft,top=c.top+canvas.clientTop;
  if((r.width>canvas.clientWidth-32||r.height>canvas.clientHeight-32)&&node.querySelector('text'))r=node.querySelector('text').getBoundingClientRect();
  const dx=scrollDelta(r.left,r.width,left+16,left+canvas.clientWidth-16),dy=scrollDelta(r.top,r.height,top+16,top+canvas.clientHeight-16);
  if(dx||dy)canvas.scrollBy({left:dx,top:dy,behavior:scrollMotion(animate)});
 };
 view.select=key=>nodes.forEach(n=>{n.classList.toggle('selected',n.dataset.key===key);if(n.dataset.child)n.setAttribute('aria-expanded',String(n.dataset.key===key));});
 svg.addEventListener('click',e=>{if(moved){moved=false;return;}if(e.target.closest('a'))return;const n=e.target.closest('[data-key]');if(n)choose(view,n,true);});
 svg.addEventListener('keydown',e=>{const n=e.target.closest('[data-key]');if(n&&(e.key==='Enter'||e.key===' ')){e.preventDefault();choose(view,n,true);}});
 canvas.addEventListener('keydown',e=>{if(e.key==='+'||e.key==='='){e.preventDefault();zoom(4/3);}else if(e.key==='-'){e.preventDefault();zoom(.75);}});
 canvas.addEventListener('pointerdown',e=>{if(e.button!==0||e.pointerType==='touch')return;const r=canvas.getBoundingClientRect();if(e.clientX>=r.left+canvas.clientWidth||e.clientY>=r.top+canvas.clientHeight)return;drag={x:e.clientX,y:e.clientY,left:canvas.scrollLeft,top:canvas.scrollTop};moved=false;canvas.classList.add('dragging');});
 window.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>5)moved=true;if(moved){canvas.scrollLeft=drag.left-dx;canvas.scrollTop=drag.top-dy;}});
 function endDrag(){drag=null;canvas.classList.remove('dragging');}
 window.addEventListener('pointerup',endDrag);window.addEventListener('pointercancel',endDrag);window.addEventListener('blur',endDrag);
 canvas.addEventListener('wheel',e=>{if(!e.ctrlKey&&!e.metaKey)return;e.preventDefault();const r=canvas.getBoundingClientRect(),unit=e.deltaMode===1?16:e.deltaMode===2?canvas.clientHeight:1;zoom(Math.exp(-Math.max(-100,Math.min(100,e.deltaY*unit))*.005),(e.clientX-r.left)/canvas.clientWidth,(e.clientY-r.top)/canvas.clientHeight);},{passive:false});
 container.querySelector('[data-zoom="in"]').onclick=()=>zoom(4/3);
 container.querySelector('[data-zoom="out"]').onclick=()=>zoom(.75);
 window.addEventListener('resize',()=>{if(container.hidden)return;const p=center();fit();place(p);});
 window.addEventListener('beforeprint',()=>{svg.style.width='100%';svg.style.height='auto';});window.addEventListener('afterprint',paint);
 if(!container.hidden)fit();return view;
});
// Open the complete reading copy for printing, then restore the reader's state.
let printDetails=null;
window.addEventListener('beforeprint',()=>{
 if(printDetails!==null)return;
 printDetails=[...document.querySelectorAll('#source-report:not([open]), #source-report details:not([open]), .map-notes:not([open])')];
 printDetails.forEach(d=>{d.open=true;});
});
window.addEventListener('afterprint',()=>{
 if(printDetails===null)return;
 printDetails.forEach(d=>{d.open=false;});printDetails=null;
});
const byKey=new Map(views.flatMap(v=>v.nodes.map(n=>[n.dataset.key,{view:v,node:n}])));
const byView=new Map(views.map(v=>[v.container.dataset.view,v]));
function close(focus=true,clearSelection=true){const entry=byKey.get(selected),p=entry?.view.center();inspector.hidden=true;sections.forEach(s=>s.hidden=true);if(entry){if(clearSelection)entry.view.select(null);if(p)entry.view.place(p);if(focus)entry.node.focus({preventScroll:true});}selected=null;}
function choose(view,node,scroll=false,detailsOnly=false){
 const key=node.dataset.key,detail=document.getElementById('inspect-'+key);if(!detail)return;
 if(scroll)window.scrollTo({left:window.scrollX,top:window.scrollY,behavior:'auto'});
 const p=view.center(),anchorTop=node.getBoundingClientRect().top,child=detailsOnly?null:byView.get(node.dataset.child);
 view.select(key);selected=key;
 if(detailsOnly&&node.dataset.child)node.setAttribute('aria-expanded','false');
 // Replace content before collapsing old branches; avoid a temporary empty page.
 if(child){
  child.container.hidden=false;child.fit();
  const context=child.container.querySelector('.parent-context'),copy=detail.cloneNode(true);copy.removeAttribute('id');copy.querySelectorAll('[id]').forEach(n=>n.removeAttribute('id'));copy.hidden=false;
  child.container.querySelector('.parent-detail').replaceChildren(copy);context.hidden=false;
  inspector.hidden=true;sections.forEach(s=>s.hidden=true);
 }else{
  detail.hidden=false;sections.forEach(s=>{if(s!==detail)s.hidden=true;});inspector.hidden=false;document.getElementById('inspector-placeholder').hidden=true;inspector.scrollTop=0;
 }
 for(const v of views)if(v.depth>view.depth){v.select(null);if(v!==child){v.container.hidden=true;const context=v.container.querySelector('.parent-context');context.open=false;context.hidden=true;v.container.querySelector('.parent-detail').replaceChildren();}}
 view.place(p);
 if(scroll){
  const shift=node.getBoundingClientRect().top-anchorTop;
  if(shift)window.scrollBy({top:shift,behavior:'auto'});
  revealPage(child?child.container:inspector);
 }
}
document.getElementById('close-inspector').onclick=()=>close();
document.addEventListener('keydown',e=>{
 if(e.key!=='Escape')return;
 if(!inspector.hidden){e.preventDefault();close();return;}
 const last=views.filter(v=>!v.container.hidden).sort((a,b)=>b.depth-a.depth)[0];if(last?.container.dataset.owner){e.preventDefault();last.container.hidden=true;last.select(null);const owner=byKey.get(last.container.dataset.owner);owner.node.setAttribute('aria-expanded','false');owner.node.focus({preventScroll:true});owner.view.reveal(owner.node);revealPage(owner.view.canvas,Infinity);selected=owner.node.dataset.key;}
});
function route(animate=true){
 let key;try{key=decodeURIComponent(location.hash.slice(1));}catch{return;}if(!key)return;
 const detailsOnly=key.startsWith('inspect-'),entry=byKey.get(detailsOnly?key.slice(8):key);
 if(entry){
  function reveal(v){const parent=byKey.get(v.container.dataset.owner);if(parent){reveal(parent.view);choose(parent.view,parent.node);}}
  reveal(entry.view);choose(entry.view,entry.node,false,detailsOnly);entry.view.reveal(entry.node,animate);revealPage(detailsOnly?inspector:entry.view.canvas,detailsOnly?160:Infinity,animate);
 }else{
  const target=document.getElementById(key),report=document.getElementById('source-report');
  if(target&&report.contains(target)){for(let p=target;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;revealPage(target,160,animate);}
 }
}
document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(!a)return;const href=a.getAttribute('href');let key;try{key=decodeURIComponent(href.slice(1));}catch{return;}if(byKey.has(key)||document.getElementById(key)){e.preventDefault();history.replaceState(null,'',href);route();}});
window.addEventListener('hashchange',()=>route());route(false);
})();
