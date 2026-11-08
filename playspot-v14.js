/* PlaySpotStore V14 — 3 daily spins, 10% off one randomly drawn game.
   Static-site promotion: day limit is per browser; receipts require manual store validation. */
(() => {
  'use strict';
  if (window.__p14SpinMounted) return;
  window.__p14SpinMounted = true;
  const ru = (document.documentElement.lang || '').toLowerCase().startsWith('ru');
  const t = ru ? {
    cta:'КРУТИ И ПОЛУЧИ -10%', mini:'3 попытки каждый день', wheelTitle:'Крути и выигрывай!',
    intro:'3 попытки в день · Каждое вращение даёт скидку 10% на случайную игру',
    spin:'КРУТИТЬ', loading:'Загружаем каталог игр…', wait:'Колесо вращается…',
    left:'Осталось сегодня:', win:'ТВОЙ ПРИЗ · СКИДКА 10%', claim:'Отправить в WhatsApp',
    save:'Сохранить подтверждение PNG', history:'Мои призы сегодня', none:'У тебя пока нет выигрышей сегодня',
    close:'Закрыть колесо', error:'Не удалось загрузить весь каталог. Проверь интернет и попробуй ещё раз.',
    retry:'Повторить', complete:'Все 3 попытки сегодня использованы. Приходи завтра!',
    rule:'Скидка действует только на выпавшую игру и подтверждается после проверки наличия и итоговой цены. Для подтверждения отправь PNG в WhatsApp.',
    snap:'Сохрани PNG, затем прикрепи его к сообщению WhatsApp. Скриншот сам не отправляется.',
    message:(p)=>`Здравствуйте! Мне выпала скидка 10% на игру «${p.title}» (${p.platform}). Код подтверждения: ${p.code}. Дата: ${p.date}. Хочу подтвердить наличие и цену. Я прикреплю PNG с призом.`,
    downloaded:'PNG с подтверждением сохранён. Прикрепи его в WhatsApp.', noImage:'Нет обложки',
    receiptTitle:'МОЙ ПРИЗ PLAYSPOTSTORE', receiptDate:'Дата', receiptCode:'Код', receiptFooter:'Покажи это изображение магазину в WhatsApp', receiptCondition:'10% скидка · наличие и окончательная цена уточняются',
    today:'Сегодня', plays:'попыток', spinLabel:'Испытай удачу'
  } : {
    cta:'ROTEȘTE & CÂȘTIGĂ -10%', mini:'3 rotiri în fiecare zi', wheelTitle:'Rotește și câștigă!',
    intro:'3 rotiri pe zi · La fiecare rotire primești 10% reducere la un joc aleatoriu',
    spin:'ROTEȘTE', loading:'Încărcăm toate jocurile…', wait:'Roata se învârte…',
    left:'Rotiri rămase azi:', win:'PREMIUL TĂU · 10% REDUCERE', claim:'Revendică pe WhatsApp',
    save:'Salvează dovada PNG', history:'Premiile tale de azi', none:'N-ai premii obținute astăzi',
    close:'Închide roata', error:'Nu am putut încărca tot catalogul. Verifică internetul și încearcă din nou.',
    retry:'Încearcă din nou', complete:'Ai folosit toate cele 3 rotiri azi. Revino mâine!',
    rule:'Reducerea este pentru jocul extras și se confirmă în limita stocului, la prețul final agreat prin contact. Pentru verificare, trimite dovada PNG pe WhatsApp.',
    snap:'Salvează dovada PNG, apoi atașeaz-o în conversația WhatsApp. Imaginea nu se trimite automat.',
    message:(p)=>`Salut! Am câștigat 10% reducere la ${p.title} (${p.platform}). Cod de referință: ${p.code}. Data: ${p.date}. Vreau să confirm disponibilitatea și prețul final. Atașez dovada PNG a rotirii.`,
    downloaded:'Dovada PNG a fost salvată. Atașeaz-o pe WhatsApp.', noImage:'Copertă indisponibilă',
    receiptTitle:'PREMIUL MEU PLAYSPOTSTORE', receiptDate:'Data', receiptCode:'Cod', receiptFooter:'Trimite această imagine pe WhatsApp', receiptCondition:'10% reducere · prețul final și stocul se confirmă',
    today:'Astăzi', plays:'rotiri', spinLabel:'Încearcă-ți norocul'
  };
  const maxSpins = 3;
  const p15ExpiresAt = Date.parse('2026-12-08T14:16:42+02:00');
  const p15CampaignExpired = () => Date.now() >= p15ExpiresAt;
  const p15ExpiryLabel = new Intl.DateTimeFormat(ru ? 'ru-RU' : 'ro-RO',{timeZone:'Europe/Chisinau', day:'numeric',month:'long',year:'numeric'}).format(p15ExpiresAt);
  const catalogPaths = [
    ['PS4','data/ps4.json'],['PS5','data/ps5.json'],['PS2','data/ps2.json'],
    ['Nintendo','data/nintendo.json'],['Xbox','data/xbox.json']
  ];
  const keyPrefix = 'playspotstore-wheel-v14-';
  let volatileState = null;
  const cashPhone = '37378890580';
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  const dateParts = () => {
    try {const p=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Chisinau',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
      const obj=Object.fromEntries(p.filter(v=>v.type!=='literal').map(v=>[v.type,v.value]));return `${obj.year}-${obj.month}-${obj.day}`;
    }catch {return new Date().toISOString().slice(0,10);}
  };
  const rnd = n => {
    if(n<=1)return 0;
    if(window.crypto && window.crypto.getRandomValues){
      const x=new Uint32Array(1),span=4294967296,limit=Math.floor(span/n)*n;
      do{window.crypto.getRandomValues(x);}while(x[0]>=limit);
      return x[0]%n;
    }
    return Math.floor(Math.random()*n);
  };
  const getState=()=>{
    const date=dateParts();let v={date,wins:[]};
    try {const data=JSON.parse(localStorage.getItem(keyPrefix+date)||'null');if(data && data.date===date && Array.isArray(data.wins))v={date,wins:data.wins.slice(0,maxSpins)};}catch{if(volatileState?.date===date)v={date,wins:volatileState.wins.slice(0,maxSpins)};}
    return v;
  };
  const putState=(s)=>{volatileState=s;try{localStorage.setItem(keyPrefix+s.date,JSON.stringify(s));}catch{}};
  const candidatesFrom=(games)=>{
    // Uniform without replacement: eight different entries from the FULL catalogue.
    const sample=[];
    const keys=Array.from({length:games.length},(_,i)=>i);
    for(let i=0;i<8 && i<keys.length;i++){
      const j=i+rnd(keys.length-i);[keys[i],keys[j]]=[keys[j],keys[i]];
      sample.push(games[keys[i]]);
    }
    return sample;
  };
  const safeCover=(url)=>{const x=String(url||'');return /^(https?:\/\/|\/?media\/|\/?neon-assets\/|\/?[0-9]+\.jpeg)/i.test(x)?x:'media/play-spot-logo-v4.webp';};
  // This always-visible ribbon sits next to the navigation without shrinking the menu.
  const invite=document.createElement('button');invite.type='button';invite.id='p14-invite';invite.setAttribute('aria-haspopup','dialog');
  invite.innerHTML=`<span class="p14-invite-icon" aria-hidden="true">✦</span><span class="p14-invite-text"><strong>${t.cta}</strong><small>${t.mini}</small></span><span class="p14-invite-count" aria-hidden="true">3/3</span>`;
  const hero=document.querySelector('section.hero') || document.querySelector('header');
  hero.insertAdjacentElement(hero.matches('header')?'afterend':'afterbegin',invite);
  const backdrop=document.createElement('div');backdrop.id='p14-spin-overlay';backdrop.hidden=true;
  backdrop.innerHTML=`<section class="p14-panel" role="dialog" aria-modal="true" aria-labelledby="p14-title" tabindex="-1">
    <button class="p14-close" type="button" aria-label="${t.close}" title="${t.close}">×</button>
    <div class="p14-eyebrow">PLAYSPOTSTORE <span>•</span> <strong>SPIN & WIN</strong></div>
    <h2 id="p14-title">${t.wheelTitle}</h2>
    <p class="p14-subtitle">${t.intro}</p>
    <div class="p14-progress"><span>${t.left}</span><strong class="p14-left">3 / 3</strong></div>
    <div class="p14-wheel-wrap"><div class="p14-pointer" aria-hidden="true"></div><div class="p14-wheel-disc" aria-label="${t.wheelTitle}"></div><span class="p14-wheel-hub" aria-hidden="true">10<span>%</span></span></div>
    <p class="p14-status" role="status" aria-live="polite"></p>
    <button class="p14-spin" type="button">${t.spin}</button>
    <div class="p14-result" hidden><div class="p14-win-label">${t.win}</div><h3 class="p14-win-title"></h3><p class="p14-win-platform"></p><small class="p14-win-code"></small>
      <div class="p14-result-actions"><button type="button" class="p14-save">${t.save}</button><a class="p14-claim" target="_blank" rel="noopener noreferrer">${t.claim}</a></div>
      <p class="p14-proof-help">${t.snap}</p>
    </div>
    <details class="p14-history"><summary>${t.history} <span class="p14-history-count"></span></summary><div class="p14-history-list"></div></details>
    <p class="p14-terms">${t.rule}</p>
  </section>`;
  document.body.appendChild(backdrop);
  const panel=backdrop.querySelector('.p14-panel'), disc=backdrop.querySelector('.p14-wheel-disc'), spinBtn=backdrop.querySelector('.p14-spin');
  const leftText=backdrop.querySelector('.p14-left'), status=backdrop.querySelector('.p14-status'), result=backdrop.querySelector('.p14-result');
  const titleEl=backdrop.querySelector('.p14-win-title'), platformEl=backdrop.querySelector('.p14-win-platform'), codeEl=backdrop.querySelector('.p14-win-code');
  const saveBtn=backdrop.querySelector('.p14-save'),claim=backdrop.querySelector('.p14-claim');
  const histList=backdrop.querySelector('.p14-history-list'),histNum=backdrop.querySelector('.p14-history-count');
  let pool=null, poolPromise=null, activeCandidates=[],currentWin=null,spinning=false,focusFrom=null,lastOverflow='', animationTimer=0;
  const remaining=()=>Math.max(0,maxSpins-getState().wins.length);
  const refreshCounter=()=>{const left=remaining();leftText.textContent=`${left} / ${maxSpins}`;invite.querySelector('.p14-invite-count').textContent=`${left}/${maxSpins}`;
    spinBtn.disabled=spinning || left===0 || !pool || p15CampaignExpired();
    if(p15CampaignExpired())status.textContent=ru?'Акция завершилась.':'Campania a expirat.';
    else if(left===0 && !spinning)status.textContent=t.complete;
  };
  const textLabel=(value)=>String(value||'').replace(/\s+/g,' ').trim();
  const buildWheel=(list)=>{
    activeCandidates=list;disc.innerHTML='';
    list.forEach((g,i)=>{
      const part=document.createElement('div');part.className='p14-piece';part.style.setProperty('--piece-angle',`${i*45}deg`);
      const img=document.createElement('img');img.alt='';img.loading='lazy';img.decoding='async';img.src=safeCover(g.image);
      img.onerror=()=>{img.onerror=null;img.src='media/play-spot-logo-v4.webp';};
      const small=document.createElement('small');small.textContent=g.title;
      part.append(img,small);disc.appendChild(part);
    });
  };
  const loadGames=async()=>{
    if(pool)return pool;
    if(poolPromise)return poolPromise;
    poolPromise=Promise.all(catalogPaths.map(async ([platform,path])=>{
      const response=await fetch(path,{cache:'no-store'});
      if(!response.ok)throw new Error(path+' HTTP '+response.status);
      const raw=await response.json();if(!Array.isArray(raw))throw new Error('Invalid JSON: '+path);
      return raw.filter(x=>x && typeof x.title==='string' && x.title.trim() && x.id).map(x=>({id:String(x.id),platform,title:textLabel(x.title),image:x.image||'',price:x.price||''}));
    })).then(groups=>{
      const all=[...new Map(groups.flat().map(g=>[g.platform+'::'+g.id,g])).values()];if(all.length<8)throw new Error('Not enough games in catalogue');
      pool=all;buildWheel(candidatesFrom(all));refreshCounter();status.textContent='';return all;
    }).catch(err=>{console.error('[PlaySpotStore Spin]',err);poolPromise=null;status.textContent=t.error;spinBtn.disabled=true;throw err;});
    return poolPromise;
  };
  const prettyDate=()=>new Intl.DateTimeFormat(ru?'ru-RU':'ro-RO',{dateStyle:'medium',timeZone:'Europe/Chisinau'}).format(new Date());
  const codeFor=()=>{
    const bytes=new Uint8Array(5);if(window.crypto?.getRandomValues)window.crypto.getRandomValues(bytes);else for(let i=0;i<bytes.length;i++)bytes[i]=rnd(256);
    return 'PSS-'+dateParts().replace(/-/g,'')+'-'+Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('').toUpperCase();
  };
  const showResult=(win)=>{
    currentWin=win;result.hidden=false;titleEl.textContent=win.title;platformEl.textContent=win.platform+(win.price?' · '+win.price:'');
    codeEl.textContent=win.code;claim.href='https://wa.me/'+cashPhone+'?text='+encodeURIComponent(t.message(win)+(ru?' Срок акции: до ':' Campanie valabilă până la ')+p15ExpiryLabel+'.');
  };
  const renderHistory=()=>{
    const s=getState();histList.innerHTML='';histNum.textContent=`(${s.wins.length}/${maxSpins})`;
    if(!s.wins.length){const p=document.createElement('p');p.textContent=t.none;histList.appendChild(p);return;}
    s.wins.slice().reverse().forEach((w)=>{
      const btn=document.createElement('button');btn.type='button';btn.className='p14-previous-win';
      const name=document.createElement('strong');name.textContent='-10% · '+w.title;
      const info=document.createElement('small');info.textContent=w.code;
      btn.append(name,info);btn.addEventListener('click',()=>{showResult(w);result.scrollIntoView({block:'nearest',behavior:'smooth'});});histList.append(btn);
    });
  };
  const open=()=>{
    if(p15CampaignExpired())return;
    focusFrom=document.activeElement;lastOverflow=document.body.style.overflow;document.body.style.overflow='hidden';
    backdrop.hidden=false;panel.focus({preventScroll:true});status.textContent=t.loading;
    result.hidden=true;currentWin=null;refreshCounter();renderHistory();const last=getState().wins.at(-1);if(last)showResult(last);
    loadGames().catch(()=>{});
  };
  const close=()=>{backdrop.hidden=true;document.body.style.overflow=lastOverflow;
    if(focusFrom && focusFrom.isConnected)focusFrom.focus({preventScroll:true});};
  invite.addEventListener('click',open);
  backdrop.querySelector('.p14-close').addEventListener('click',close);
  backdrop.addEventListener('click',e=>{if(e.target===backdrop)close();});
  document.addEventListener('keydown',e=>{
    if(backdrop.hidden)return;
    if(e.key==='Escape'){e.preventDefault();close();return;}
    if(e.key==='Tab'){
      const nodes=[...panel.querySelectorAll('button:not([disabled]),a[href],summary')].filter(el=>el.getClientRects().length&&el.offsetParent!==null);
      if(!nodes.length)return;const first=nodes[0],last=nodes.at(-1);
      if(e.shiftKey && document.activeElement===first){e.preventDefault();last.focus();}
      else if(!e.shiftKey && document.activeElement===last){e.preventDefault();first.focus();}
    }
  });
  spinBtn.addEventListener('click',async()=>{
    if(spinning || p15CampaignExpired())return;
    if(!pool){status.textContent=t.loading;try{await loadGames();}catch{return;}}
    if(p15CampaignExpired()){refreshCounter();return;}
    const state=getState();if(state.wins.length>=maxSpins){refreshCounter();return;}
    // Refresh the eight candidates for every spin; all catalogue entries have the same chance.
    const sample=candidatesFrom(pool);if(sample.length<8)return;
    const index=rnd(8),game=sample[index];
    const win={id:game.id,platform:game.platform,title:game.title,price:game.price,date:dateParts(),dateLabel:prettyDate(),code:codeFor()};
    state.wins.push(win);putState(state); // Reserve immediately, preventing free rerolls on refresh.
    spinning=true;result.hidden=true;currentWin=null;status.textContent=t.wait;
    disc.style.transition='none';disc.style.transform='rotate(0deg)';buildWheel(sample);
    // Force reflow to make each new rotation animate from zero.
    void disc.offsetWidth;
    const duration=reduceMotion?.matches?350:4800;
    const target=1800 + ((90-index*45+360)%360); // right-hand pointer at 3 o'clock.
    disc.style.transition=`transform ${duration}ms cubic-bezier(.13,.72,.12,1)`;
    disc.style.transform=`rotate(${target}deg)`;
    refreshCounter();clearTimeout(animationTimer);
    animationTimer=window.setTimeout(()=>{spinning=false;status.textContent='';showResult(win);renderHistory();refreshCounter();},duration+90);
  });
  const drawRound=(ctx,x,y,w,h,r)=>{ctx.beginPath();ctx.roundRect(x,y,w,h,r);};
  const wrap=(ctx,value,maxWidth)=>{
    let lines=[],line='';for(const word of String(value).split(/\s+/)){
      const next=(line?line+' ':'')+word;
      if(ctx.measureText(next).width>maxWidth && line){lines.push(line);line=word;}else line=next;
    }if(line)lines.push(line);return lines.slice(0,4);
  };
  const makeProof=async(win)=>{
    const canvas=document.createElement('canvas');canvas.width=1100;canvas.height=650;const c=canvas.getContext('2d');
    if(!c)throw new Error('Canvas unavailable');
    const gr=c.createLinearGradient(0,0,1100,650);gr.addColorStop(0,'#071d25');gr.addColorStop(.58,'#082c2a');gr.addColorStop(1,'#160d37');c.fillStyle=gr;c.fillRect(0,0,1100,650);
    c.strokeStyle='#66ffd3';c.lineWidth=3;drawRound(c,26,26,1048,598,29);c.stroke();
    c.fillStyle='#61fbd1';c.font='800 30px Arial';c.fillText('PLAYSPOTSTORE',95,100);
    try {const logo=new Image();logo.src='media/play-spot-logo-v4.webp';await logo.decode();c.drawImage(logo,945,62,80,80);}catch{}
    c.fillStyle='#dffff7';c.font='800 45px Arial';c.fillText(t.receiptTitle,95,178);
    c.fillStyle='#55ffae';c.font='900 98px Arial';c.fillText('10%',95,299);
    c.font='700 38px Arial';c.fillText(ru?'СКИДКА':'REDUCERE',335,288);
    c.fillStyle='#f5fff9';c.font='750 34px Arial';
    const lines=wrap(c,win.title,880).slice(0,2);lines.forEach((line,i)=>c.fillText(line,95,362+i*42));
    let pos=463;
    c.fillStyle='#a2dacf';c.font='500 24px Arial';c.fillText(win.platform+'  •  '+t.receiptDate+': '+win.dateLabel,95,pos);
    c.fillStyle='#86ffe2';c.font='700 26px monospace';c.fillText(t.receiptCode+': '+win.code,95,pos+44);
    c.fillStyle='#afc9cb';c.font='500 20px Arial';c.fillText(t.receiptCondition,95,565);
    c.font='600 20px Arial';c.fillText(t.receiptFooter+' · '+p15ExpiryLabel,95,596);
    return new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error('PNG conversion failed')),'image/png'));
  };
  saveBtn.addEventListener('click',async()=>{
    if(!currentWin)return;saveBtn.disabled=true;
    try {const blob=await makeProof(currentWin),url=URL.createObjectURL(blob),a=document.createElement('a');
      a.href=url;a.download=`PlaySpotStore-10procente-${currentWin.code}.png`;document.body.appendChild(a);a.click();a.remove();
      window.setTimeout(()=>URL.revokeObjectURL(url),10000);status.textContent=t.downloaded;
    }catch(err){console.error('[PlaySpotStore] Receipt PNG:',err);status.textContent=t.snap;}
    finally{saveBtn.disabled=false;}
  });
  window.addEventListener('storage',e=>{if(e.key?.startsWith(keyPrefix)){refreshCounter();renderHistory();}});
  refreshCounter();renderHistory();
})();
