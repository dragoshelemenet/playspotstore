/* PlaySpotStore V15. Shared 30-day campaign end is injected at install time. */
(() => {
  'use strict';
  const invite=document.getElementById('p14-invite');
  if(!invite || document.getElementById('p15-spin-bar'))return;
  const isRu=String(document.documentElement.lang||'').startsWith('ru');
  const campaignEndMs=Date.parse('2026-12-08T14:16:42+02:00');
  const expiryLabel=new Intl.DateTimeFormat(isRu?'ru-RU':'ro-RO',{
    timeZone:'Europe/Chisinau',day:'numeric',month:'long',year:'numeric'
  }).format(campaignEndMs);
  const strings=isRu ? {
    label:'До конца акции',days:'д',hours:'ч',minutes:'м',hide:'Свернуть панель',show:'Развернуть предложение',
    banner:'-10% · Крути!',end:'Акция завершена',note:'Акция действует до'
  } : {
    label:'Expiră în',days:'z',hours:'h',minutes:'m',hide:'Minimizează oferta',show:'Arată oferta',
    banner:'Spin -10%',end:'Campania a expirat',note:'Campanie valabilă până la'
  };
  const bar=document.createElement('aside');bar.id='p15-spin-bar';
  bar.setAttribute('aria-label',isRu?'Акция Spin & Win':'Promoție Rotește și câștigă');
  bar.innerHTML=`<div class="p15-primary"></div>
    <div class="p15-expiry"><span class="p15-expiry-label"></span><strong class="p15-expiry-time"></strong></div>
    <button class="p15-minimize" type="button" aria-label="${strings.hide}" title="${strings.hide}">−</button>
    <button class="p15-compact" type="button" aria-label="${strings.show}" title="${strings.show}">✦ <b>${strings.banner}</b></button>`;
  bar.querySelector('.p15-primary').appendChild(invite);
  document.body.appendChild(bar);
  const countdown=bar.querySelector('.p15-expiry-time'), label=bar.querySelector('.p15-expiry-label');
  label.textContent=strings.label;
  countdown.title=expiryLabel;
  const close=bar.querySelector('.p15-minimize');const small=bar.querySelector('.p15-compact');
  const expiryNote=document.createElement('p');expiryNote.className='p15-campaign-note';
  expiryNote.textContent=strings.note+' '+expiryLabel+'.';
  const terms=document.querySelector('#p14-spin-overlay .p14-terms');
  if(terms)terms.insertAdjacentElement('beforebegin',expiryNote);
  function setMinimized(isMinimized){
    bar.classList.toggle('is-minimized',isMinimized);
    document.body.classList.toggle('p15-bar-expanded',!isMinimized);
    try {sessionStorage.setItem('playspotstore-v15-spin-minimized',isMinimized?'1':'0');}catch{}
  }
  close.addEventListener('click',()=>{setMinimized(true);small.focus({preventScroll:true});});
  small.addEventListener('click',()=>{setMinimized(false);invite.focus({preventScroll:true});});
  try{setMinimized(sessionStorage.getItem('playspotstore-v15-spin-minimized')==='1');}catch{setMinimized(false);}
  function tick(){
    const diff=campaignEndMs-Date.now();
    if(!Number.isFinite(diff)||diff<=0){
      countdown.textContent=strings.end;
      bar.hidden=true;
      bar.style.setProperty('display','none','important');
      document.body.classList.remove('p15-bar-expanded');
      return false;
    }
    const minutes=Math.ceil(diff/60000),days=Math.floor(minutes/1440),hours=Math.floor((minutes%1440)/60),mins=minutes%60;
    countdown.textContent=days>0 ? `${days}${strings.days} ${hours}${strings.hours}` : hours>0 ? `${hours}${strings.hours} ${mins}${strings.minutes}` : `${mins}${strings.minutes}`;
    countdown.setAttribute('aria-label',strings.label+' '+days+' '+strings.days+' '+hours+' '+strings.hours+' '+mins+' '+strings.minutes);
    return true;
  }
  tick();
  const timer=window.setInterval(()=>{if(!tick())window.clearInterval(timer);},30000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)tick();});
})();
