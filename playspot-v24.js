/* PlaySpotStore V24 — searchable category-only catalogue dock.  */
(() => {
  'use strict';
  if (document.getElementById('p24-search-dock')) return;
  const ru = (document.documentElement.lang || '').toLowerCase().startsWith('ru');
  const nameMap = {ps4:'PS4',ps5:'PS5',nintendo:'Nintendo',xbox:'Xbox',ps2:'PS2',console:ru?'Консоли':'Console',accessories:ru?'Аксессуары':'Accesorii'};
  const keys = Object.keys(nameMap);
  const labels = ru ? {
    search:'Поиск в категории',hint:'Результаты только для',change:'Для PS5, Nintendo или другой платформы выберите нужную категорию:',
    placeholder:'Найти игру / товар...',empty:'Ничего не найдено в этой категории.',start:'Начни вводить название для поиска.',
    error:'Не удалось загрузить товары. Попробуйте ещё раз.',result:'результатов',one:'результат',close:'Свернуть поиск',category:'Выбрать категорию'
  } : {
    search:'Căutare în categoria',hint:'Rezultate filtrate doar pentru',change:'Pentru PS5, Nintendo sau altă platformă, alege categoria corectă:',
    placeholder:'Caută joc / produs...',empty:'Niciun rezultat în această categorie.',start:'Scrie numele jocului sau produsului pentru a căuta.',
    error:'Nu am putut încărca produsele. Încearcă din nou.',result:'rezultate',one:'rezultat',close:'Restrânge căutarea',category:'Alege categoria'
  };
  const normalize = v => String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
  const files = {ps4:'ps4',ps5:'ps5',nintendo:'nintendo',xbox:'xbox',ps2:'ps2',console:'consoles',accessories:'accessories'};
  const cache = new Map();
  const dock = document.createElement('aside');
  dock.id = 'p24-search-dock';dock.hidden=true;
  dock.setAttribute('role','search');dock.setAttribute('aria-label',ru?'Поиск товаров в открытой категории':'Caută produse doar în categoria deschisă');
  dock.innerHTML = `<div class="p24-search-row">
    <svg class="p24-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.6"/><path d="m16 16 5 5"/></svg>
    <input class="p24-input" type="search" placeholder="${labels.placeholder}" autocomplete="off" aria-label="${labels.placeholder}" aria-controls="p24-search-results" />
    <span class="p24-current" aria-live="polite"></span>
    <button class="p24-close" type="button" aria-label="${labels.close}" title="${labels.close}">×</button>
  </div>
  <div class="p24-detail">
    <div class="p24-status" role="status" aria-live="polite"></div>
    <p class="p24-hint"></p>
    <div class="p24-results" id="p24-search-results" aria-live="polite"></div>
    <p class="p24-category-label"></p>
    <div class="p24-categories" role="group" aria-label="${labels.category}"></div>
  </div>`;
  document.body.append(dock);
  const input=dock.querySelector('.p24-input');
  const current=dock.querySelector('.p24-current');
  const close=dock.querySelector('.p24-close');
  const status=dock.querySelector('.p24-status');
  const hint=dock.querySelector('.p24-hint');
  const results=dock.querySelector('.p24-results');
  const categoryText=dock.querySelector('.p24-category-label');
  const categories=dock.querySelector('.p24-categories');
  const searchRow=dock.querySelector('.p24-search-row');
  let activeCat=null,requestId=0,pending=null;
  const fileFor=k=> 'data/'+files[k]+(ru?'_ru':'')+'.json';
  async function load(cat) {
    if(cache.has(cat))return cache.get(cat);
    const promise=(async()=>{
      let rsp=await fetch(fileFor(cat));
      if(!rsp.ok && ru)rsp=await fetch('data/'+files[cat]+'.json');
      if(!rsp.ok)throw Error('Fetch '+cat);
      const items=await rsp.json();return Array.isArray(items)?items:[];
    })();
    cache.set(cat,promise);
    try{return await promise;}catch(e){cache.delete(cat);throw e;}
  }
  function expand(){if(!activeCat)return;dock.classList.add('p24-expanded');render();}
  function collapse(){dock.classList.remove('p24-expanded');}
  function categoryControls(){
    categories.replaceChildren();
    keys.forEach(cat=>{
      const btn=document.createElement('button');btn.type='button';btn.className='p24-cat';btn.textContent=nameMap[cat];
      if(cat===activeCat)btn.setAttribute('aria-current','true');
      btn.addEventListener('click',()=>goCategory(cat));categories.appendChild(btn);
    });
  }
  function goCategory(cat){
    if(cat===activeCat){input.focus();return;}
    // Switch in the existing catalog system, not to a separate search index.
    document.querySelectorAll('#modal-ps4.active,#modal-ps5.active,#modal-console.active,#modal-accessories.active')
      .forEach(modal=>{modal.classList.remove('active');modal.setAttribute('aria-hidden','true');});
    const dynamic=document.getElementById('p3-platform-dialog');
    if(dynamic)dynamic.querySelector('button.close')?.click();
    const other=document.getElementById('platform-notice');if(other)other.querySelector('button.close')?.click();
    if(['nintendo','xbox','ps2'].includes(cat)){
      if(typeof window.showPlatformNotice==='function')window.showPlatformNotice(cat);
    }else if(typeof window.openCategoryModal==='function')window.openCategoryModal(cat);
    activeCat=cat;current.textContent=nameMap[cat];categoryControls();
    // Preserve a typed query so visitors can quickly compare categories, but only results from selected one.
    expand();input.focus({preventScroll:true});render();
  }
  function appendResult(item,cat){
    const btn=document.createElement('button');btn.type='button';btn.className='p24-item';
    const img=document.createElement('img');img.alt='';img.loading='lazy';img.decoding='async';
    img.src=item.image||'media/play-spot-logo-v4.webp';img.onerror=()=>{img.onerror=null;img.src='media/play-spot-logo-v4.webp';};
    const copy=document.createElement('span');copy.className='p24-item-copy';
    const title=document.createElement('strong');title.textContent=item.title||'';
    const price=document.createElement('small');price.textContent=item.price|| (ru?'Цена по запросу':'Preț la cerere');
    copy.append(title,price);
    const arrow=document.createElement('span');arrow.className='p24-item-arrow';arrow.textContent='›';arrow.setAttribute('aria-hidden','true');
    btn.append(img,copy,arrow);
    btn.addEventListener('click',()=>{
      collapse();if(typeof window.openGame==='function')window.openGame(String(item.id),cat);
    });results.appendChild(btn);
  }
  async function render(){
    if(!activeCat||!dock.classList.contains('p24-expanded'))return;
    const cat=activeCat,id=++requestId,q=normalize(input.value);
    current.textContent=nameMap[cat];categoryText.textContent=labels.change;categoryControls();
    hint.textContent=labels.hint+' '+nameMap[cat]+'.';
    if(!q){status.textContent=labels.search+' '+nameMap[cat];results.replaceChildren();
      const p=document.createElement('p');p.className='p24-empty';p.textContent=labels.start;results.appendChild(p);return;}
    status.textContent=labels.search+' '+nameMap[cat]+'…';
    results.replaceChildren();
    try {
      const items=await load(cat);
      if(id!==requestId||cat!==activeCat||!dock.classList.contains('p24-expanded'))return;
      const matches=items.filter(v=>normalize(v.title).includes(q));
      status.textContent=(ru?'Только ':'Doar ') +nameMap[cat]+' · '+matches.length+' '+(matches.length===1?labels.one:labels.result);
      if(!matches.length){const p=document.createElement('p');p.className='p24-empty';p.textContent=labels.empty;results.appendChild(p);return;}
      // Cap the visible list to keep scrolling inside the compact panel.
      matches.slice(0,50).forEach(item=>appendResult(item,cat));
    }catch(e){if(id!==requestId)return;status.textContent=labels.error;results.replaceChildren();}
  }
  input.addEventListener('focus',expand);
  input.addEventListener('click',expand);
  input.addEventListener('input',()=>{clearTimeout(pending);pending=setTimeout(render,130);});
  close.addEventListener('click',()=>{collapse();input.blur();});
  document.addEventListener('pointerdown',e=>{if(!dock.contains(e.target)&&dock.classList.contains('p24-expanded')){collapse();input.blur();}},{passive:true});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dock.classList.contains('p24-expanded')){collapse();input.blur();}});
  function detect(){
    const wheel=document.getElementById('p14-spin-overlay');
    if(wheel && !wheel.hidden){if(!dock.hidden){dock.hidden=true;collapse();}return;}
    const active=[...document.querySelectorAll('.modal.active')];
    // Hide while a single-product or unrelated popup covers the category.
    if(active.some(el=>!['modal-ps4','modal-ps5','modal-console','modal-accessories','p3-platform-dialog'].includes(el.id))){
      if(!dock.hidden){dock.hidden=true;collapse();}return;
    }
    const list=active.filter(el=>['modal-ps4','modal-ps5','modal-console','modal-accessories','p3-platform-dialog'].includes(el.id));
    const modal=list[list.length-1];
    if(!modal){if(!dock.hidden){dock.hidden=true;collapse();}activeCat=null;return;}
    const cat=modal.id==='p3-platform-dialog'?(modal.querySelector('h2')?.textContent||'').toLowerCase().includes('nintendo')?'nintendo':
      (modal.querySelector('h2')?.textContent||'').toLowerCase().includes('xbox')?'xbox':'ps2':modal.id.replace('modal-','');
    if(!keys.includes(cat))return;
    if(cat!==activeCat){activeCat=cat;input.value='';collapse();current.textContent=nameMap[cat];requestId++;}
    if(dock.hidden)dock.hidden=false;
  }
  let queued=false;
  const obs=new MutationObserver(()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;detect();});});
  obs.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','aria-hidden','hidden']});
  detect();
})();
