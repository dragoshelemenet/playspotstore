/* PlaySpotStore V19: TikTok's official Creator Profile Embed loads recent public videos.
   TikTok determines how many it displays and the inner layout (up to 10).
   No scraping, invented video IDs or credentials. */
(() => {
  'use strict';
  const sec = document.getElementById('p19-tiktok-feed');
  if (!sec || sec.dataset.p19Started === 'yes') return;
  const holder = sec.querySelector('#p19-embed-root');
  const state = sec.querySelector('.p19-state');
  if (!holder || !state) return;
  const profile = 'https://www.tiktok.com/@playspotstore/';
  const isRu = document.documentElement.lang.toLowerCase().startsWith('ru');
  const message = {
    loading: isRu ? 'Загружаем последние видео…' : 'Încărcăm cele mai recente videoclipuri…',
    unavailable: isRu ? 'TikTok не разрешил загрузить видео в этом браузере.' : 'TikTok nu a permis afișarea videoclipurilor în acest browser.',
    fallback: isRu ? 'Смотри последние видео напрямую в TikTok.' : 'Poți vedea cele mai recente videoclipuri direct pe TikTok.'
  };
  const strong = state.querySelector('strong');
  const paragraph = state.querySelector('p');
  let timeoutId = 0;
  let mutation = null;
  let ready = false;
  function ok() {
    if (ready) return;
    ready = true;
    window.clearTimeout(timeoutId);
    if (mutation) mutation.disconnect();
    state.hidden = true;
    holder.hidden = false;
    sec.classList.add('p19-loaded');
  }
  function fail() {
    if (ready) return;
    if (mutation) mutation.disconnect();
    holder.hidden = true;
    state.hidden = false;
    strong.textContent = message.unavailable;
    paragraph.textContent = message.fallback;
    const link = document.createElement('a');
    link.href = profile; link.target = '_blank'; link.rel = 'noopener noreferrer';
    link.textContent = isRu ? 'Открыть профиль @playspotstore' : 'Deschide profilul @playspotstore';
    paragraph.append(' ', link);
    sec.classList.add('p19-failed');
  }
  function mount() {
    if (sec.dataset.p19Started === 'yes') return;
    sec.dataset.p19Started = 'yes';
    strong.textContent = message.loading;
    holder.hidden = false;
    const block = document.createElement('blockquote');
    block.className = 'tiktok-embed';
    block.setAttribute('cite', profile);
    block.setAttribute('data-unique-id', 'playspotstore');
    block.setAttribute('data-embed-type','creator');
    block.setAttribute('data-embed-from','website');
    block.style.cssText = 'width:100%;max-width:100%;min-width:0;margin:0 auto;';
    const inner = document.createElement('section');
    const a = document.createElement('a');
    a.href = profile; a.target = '_blank'; a.rel = 'noopener noreferrer';
    a.textContent = '@playspotstore';
    inner.appendChild(a); block.appendChild(inner); holder.appendChild(block);
    // TikTok's own script replaces this blockquote with its official creator carousel.
    mutation = new MutationObserver(() => {if (holder.querySelector('iframe')) ok();});
    mutation.observe(holder,{childList:true,subtree:true});
    timeoutId = window.setTimeout(() => {holder.querySelector('iframe') ? ok() : fail();},14000);
    const existing = document.querySelector('script[src^="https://www.tiktok.com/embed.js"]');
    if (!existing) {
      const script=document.createElement('script');
      script.async=true;script.src='https://www.tiktok.com/embed.js';
      script.onerror=fail;
      document.body.appendChild(script);
    } else if (window.tiktokEmbedLoaded && typeof window.tiktokEmbedLoaded === 'function') {
      try {window.tiktokEmbedLoaded();}catch{}
    }
  }
  if ('IntersectionObserver' in window) {
    const watcher=new IntersectionObserver((entries)=>{if(entries.some(x=>x.isIntersecting)){watcher.disconnect();mount();}},{rootMargin:'700px 0px'});
    watcher.observe(sec);
  } else mount();
})();
