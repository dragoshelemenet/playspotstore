/* PlaySpotStore V20 — accessible mobile scroll controls for five real TikTok cards. */
(() => {
  'use strict';
  const section = document.getElementById('p20-tiktok-gallery');
  if (!section) return;
  const rail=section.querySelector('.p20-rail'),cards=[...section.querySelectorAll('.p20-tile')];
  const prev=section.querySelector('.p20-prev'),next=section.querySelector('.p20-next'),progress=section.querySelector('.p20-rail-progress i');
  if(!rail || cards.length!==5) return;
  const reduce=window.matchMedia && window.matchMedia('(prefers-reduced-motion:reduce)').matches;
  function goto(delta){
    const left=rail.scrollLeft;
    const pos=c=>c.getBoundingClientRect().left-rail.getBoundingClientRect().left+rail.scrollLeft;
    const index=cards.reduce((best,c,i)=>Math.abs(pos(c)-left)<Math.abs(pos(cards[best])-left)?i:best,0);
    const target=Math.max(0,Math.min(cards.length-1,index+delta));
    rail.scrollTo({left:pos(cards[target]),behavior:reduce?'instant':'smooth'});
  }
  prev.addEventListener('click',()=>goto(-1));next.addEventListener('click',()=>goto(1));
  rail.addEventListener('keydown',event=>{
    if(event.target!==rail)return;
    if(event.key==='ArrowRight'){event.preventDefault();goto(1)}
    if(event.key==='ArrowLeft'){event.preventDefault();goto(-1)}
  });
  function update(){
    const max=rail.scrollWidth-rail.clientWidth,ratio=max>0?Math.max(0,Math.min(1,rail.scrollLeft/max)):0;
    progress.style.transform=`translateX(${ratio*400}%)`;
    prev.disabled=rail.scrollLeft<4;next.disabled=max<4 || rail.scrollLeft>=max-4;
  }
  rail.addEventListener('scroll',update,{passive:true});window.addEventListener('resize',update,{passive:true});update();
})();
