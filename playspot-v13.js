/* PlaySpotStore V13 — contact platform chooser for all "Comanda" buttons. */
(() => {
  'use strict';
  const isRu = String(document.documentElement.lang || '').toLowerCase().startsWith('ru') || location.pathname.endsWith('/ru.html');
  const whatsappNumber = '37378890580';
  const instagram = 'https://www.instagram.com/PlaySpotStore/';
  const words = isRu ? {
    title: 'Как хотите заказать?', intro: 'Выберите удобный способ связи',
    whatsapp: 'WhatsApp', instagram: 'Instagram', cancel: 'Закрыть',
    generic: 'Товар PlaySpotStore', order: 'Здравствуйте! Хочу заказать', price: 'Цена:',
    confirm: 'Пожалуйста, подтвердите наличие и окончательную цену.'
  } : {
    title: 'Cum dorești să comanzi?', intro: 'Alege unde vrei să ne scrii',
    whatsapp: 'WhatsApp', instagram: 'Instagram', cancel: 'Închide',
    generic: 'Produs PlaySpotStore', order: 'Salut! Doresc să comand', price: 'Preț:',
    confirm: 'Te rog să confirmi disponibilitatea și prețul final.'
  };
  const whatsappIcon = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M12.05 2a9.9 9.9 0 0 0-8.56 14.87L2 22l5.28-1.4A9.96 9.96 0 1 0 12.05 2Zm0 18.04c-1.52 0-3.01-.41-4.31-1.18l-.3-.18-3.12.82.83-3.03-.2-.31a8.05 8.05 0 1 1 7.1 3.88Zm4.41-5.99c-.24-.12-1.43-.71-1.65-.79-.22-.08-.38-.12-.54.12s-.62.79-.76.95c-.14.16-.28.18-.52.06-.24-.12-1.02-.38-1.95-1.2-.72-.64-1.21-1.43-1.35-1.67-.14-.24-.02-.37.1-.49.11-.11.24-.28.36-.42.12-.14.16-.24.24-.4.08-.16.04-.3-.02-.42-.06-.12-.54-1.3-.74-1.78-.2-.47-.4-.4-.54-.4h-.46c-.16 0-.42.06-.64.3-.22.24-.84.82-.84 2s.86 2.33.98 2.49c.12.16 1.69 2.57 4.09 3.61.57.25 1.02.4 1.37.51.58.18 1.1.15 1.52.09.46-.07 1.43-.58 1.63-1.14.2-.56.2-1.04.14-1.14-.06-.1-.22-.16-.46-.28Z"/></svg>';
  const instagramIcon = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.6" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>';
  const overlay = document.createElement('div');
  overlay.id='p13-order-choice';overlay.hidden=true;overlay.setAttribute('role','dialog');
  overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-labelledby','p13-order-title');
  overlay.innerHTML = `<div class="p13-order-panel">
    <button type="button" class="p13-dismiss" aria-label="${words.cancel}">×</button>
    <div class="p13-order-icon" aria-hidden="true">✦</div>
    <h2 id="p13-order-title"></h2>
    <p class="p13-intro"></p>
    <p class="p13-item"></p>
    <a class="p13-platform p13-whatsapp" target="_blank" rel="noopener noreferrer">${whatsappIcon}<span>${words.whatsapp}</span></a>
    <a class="p13-platform p13-instagram" target="_blank" rel="noopener noreferrer">${instagramIcon}<span>${words.instagram}</span></a>
  </div>`;
  overlay.querySelector('h2').textContent=words.title;
  overlay.querySelector('.p13-intro').textContent=words.intro;
  document.body.appendChild(overlay);
  const item=overlay.querySelector('.p13-item');
  const whats=overlay.querySelector('.p13-whatsapp');
  const insta=overlay.querySelector('.p13-instagram');
  const dismiss=overlay.querySelector('.p13-dismiss');
  insta.href=instagram;
  let trigger=null, oldOverflow='';
  function close(){if(overlay.hidden)return;overlay.hidden=true;document.body.style.overflow=oldOverflow;
    if(trigger && trigger.isConnected)trigger.focus({preventScroll:true});trigger=null;}
  function productFrom(button){
    const card=button.closest('.product-card');
    const detail=button.closest('#product-details, #product-modal');
    const title=(card?.querySelector('h4, .product-title')?.textContent || detail?.querySelector('h2')?.textContent || button.dataset.title || '').trim();
    let price='';
    if(card){const ps=[...card.querySelectorAll('p')];price=ps.map(p=>p.textContent.trim()).find(x=>x.includes('MDL')||x.toLowerCase().includes('contact'))||'';}
    else if(detail){const ps=[...detail.querySelectorAll('p')];price=ps.map(p=>p.textContent.trim()).find(x=>/^(preț|pret|цена)\s*:/i.test(x))||'';price=price.replace(/^(preț|pret|цена)\s*:\s*/i,'');}
    return {title:title||words.generic,price:price};
  }
  function open(button){
    trigger=button;const product=productFrom(button);
    item.textContent=product.title;
    const message=`${words.order}: ${product.title}.`+(product.price?` ${words.price} ${product.price}.`:'')+` ${words.confirm}`;
    whats.href=`https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;
    oldOverflow=document.body.style.overflow;document.body.style.overflow='hidden';
    overlay.hidden=false;dismiss.focus({preventScroll:true});
  }
  // Capture before original click handlers, including dynamically inserted product-modal buttons.
  document.addEventListener('click',ev=>{
    if(!overlay.hidden && overlay.contains(ev.target))return;
    const candidate=ev.target.closest('button, a');
    if(!candidate)return;
    const isCheckout=candidate.matches('.shop-now-button, .shop-now-button-modal') ||
      (/^(comand[ăa]|заказать)$/i.test((candidate.textContent||'').trim()) && !!candidate.closest('.product-card, #product-modal'));
    if(!isCheckout)return;
    ev.preventDefault();ev.stopImmediatePropagation();ev.stopPropagation();open(candidate);
  },true);
  dismiss.addEventListener('click',close);
  overlay.addEventListener('click',ev=>{if(ev.target===overlay)close();});
  for(const link of [whats,insta])link.addEventListener('click',()=>{close();});
  document.addEventListener('keydown',ev=>{
    if(overlay.hidden)return;
    if(ev.key==='Escape'){ev.preventDefault();ev.stopImmediatePropagation();close();return;}
    if(ev.key==='Tab'){
      const nodes=[dismiss,whats,insta],i=nodes.indexOf(document.activeElement);
      if(!ev.shiftKey && i===nodes.length-1){ev.preventDefault();nodes[0].focus();}
      if(ev.shiftKey && (i===0||i===-1)){ev.preventDefault();nodes[nodes.length-1].focus();}
    }
  },true);
})();
