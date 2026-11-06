/* V12: recover broken product artwork safely, with the right product name.
   Never substitute another game's picture. Product JSON original URL is preserved. */
(() => {
  const failed = new Set();
  const ST = /\/steam\/apps\/(\d+)\/[^?#]+/i;
  const isRelevant = img => !!img.closest('.product-card, #product-modal, .modal-products');
  const nonempty = url => typeof url === 'string' && url.trim() !== '' && url !== '#';
  const unique = list => [...new Set(list.filter(nonempty))];
  function safeText(text) { return String(text || 'Joc video').slice(0, 65); }
  function escapeXml(text) {
    return safeText(text).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');
  }
  function placeholder(img) {
    const ru = document.documentElement.lang.toLowerCase().startsWith('ru');
    const title = escapeXml(img.alt || img.closest('.product-card')?.querySelector('h4')?.textContent || (ru?'Игра':'Joc video'));
    const words = title.split(/\s+/);
    const lines=[];let line='';
    words.forEach(word => {if((line+' '+word).trim().length>21 && line){lines.push(line);line=word;}else line=(line+' '+word).trim();});
    if(line)lines.push(line);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="510" viewBox="0 0 360 510"><defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#163e3e"/><stop offset="1" stop-color="#12162f"/></linearGradient></defs><rect width="360" height="510" rx="20" fill="url(#g)"/><rect x="18" y="18" width="324" height="474" rx="12" fill="none" stroke="#3f9f96" stroke-width="2" opacity=".6"/><g transform="translate(180 168)" fill="none" stroke="#75efd0" stroke-width="7" stroke-linecap="round"><rect x="-80" y="-37" width="160" height="74" rx="32"/><path d="M-47 -12v26m-13 -13h26"/><circle cx="37" cy="-5" r="5"/><circle cx="54" cy="9" r="5"/></g><text x="180" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-weight="700" font-size="21" fill="#dbfff3">${lines.slice(0,3).map((l,i)=>`<tspan x="180" dy="${i?28:0}">${l}</tspan>`).join('')}</text><text x="180" y="405" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" fill="#80e6cc">${ru?'Обложка недоступна':'Copertă indisponibilă'}</text></svg>`;
    img.onerror = null;
    img.classList.remove('lazy');
    img.classList.add('p12-cover-unavailable');
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    if(!img.dataset.p12Reported){
      console.warn('[PlaySpotStore] Missing product artwork:', img.alt || title, '| Original:', img.dataset.p12Original || img.dataset.src || '(none)');
      img.dataset.p12Reported='yes';
    }
  }
  function recover(ev) {
    const img = ev.target;
    if(!(img instanceof HTMLImageElement) || !isRelevant(img)) return;
    ev.stopImmediatePropagation(); // Overrides older one-step onerror handlers that can loop.
    if(img.dataset.p12Final==='yes') return;
    if(!img._p12Queue) {
      const original=img.getAttribute('data-src') || img.currentSrc || img.getAttribute('src') || '';
      img.dataset.p12Original=original;
      const queue=[];
      const backup=img.getAttribute('data-p12-fallback');
      if(nonempty(backup)) queue.push(backup);
      const steam=original.match(ST);
      if(steam) {
        queue.push('https://shared.fastly.steamstatic.com/steam/apps/'+steam[1]+'/header.jpg');
        queue.push('https://cdn.akamai.steamstatic.com/steam/apps/'+steam[1]+'/header.jpg');
      }
      if(/^https?:\/\//i.test(original)) {
        // Proxy is last resort for retailers that block off-site image hotlinks.
        queue.push('https://images.weserv.nl/?url='+encodeURIComponent(original)+'&w=600&output=webp');
      }
      img._p12Queue=unique(queue).filter(u=>u!==original);
    }
    let next;
    while(img._p12Queue.length && !next) {
      const candidate=img._p12Queue.shift();
      if(!failed.has(candidate))next=candidate;
    }
    if(next) {
      // Do not rewrite product JSON: try a fallback only for this failed image.
      img.src=next;
      // A remote proxy can stall without emitting an error, so never leave a blank image forever.
      window.setTimeout(() => {
        if(!img.isConnected || img.dataset.p12Final==='yes' || img.src!==next) return;
        if(img.complete && img.naturalWidth>0) return;
        recover({target:img,stopImmediatePropagation(){}});
      }, 4600);
    } else {
      img.dataset.p12Final='yes';
      placeholder(img);
    }
  }
  document.addEventListener('error', recover, true);
})();
