/* PlaySpotStore V27 — Artificial baseline visitor counter disabled for legal & privacy compliance. */
(() => {
  'use strict';
  const section = document.getElementById('p26-visitors');
  if (section) section.remove();
})();

/* ==========================================================================
   PlaySpotStore Product Page Enhancement: 3D Flip Card & Liquid Glass Dropdowns
   ========================================================================== */
(() => {
  'use strict';
  function initProductDetail() {
    const detail = document.querySelector('.seo-detail');
    if (!detail) return;
    const imgWrap = detail.querySelector('.seo-detail-image');
    const img = imgWrap ? imgWrap.querySelector('img') : null;
    const descEl = detail.querySelector('.seo-detail-description');
    if (!imgWrap || !img) return;

    const isRu = document.documentElement.lang?.startsWith('ru');
    const tapText = isRu ? 'Нажми для описания' : 'Apasă pentru descriere';
    const flipBackText = isRu ? 'Назад к обложке ↺' : 'Înapoi la copertă ↺';
    const descTitle = isRu ? 'Описание игры' : 'Descriere joc';

    const descHTML = descEl ? descEl.innerHTML : '';

    // Create 3D Flip Card
    const flipCard = document.createElement('div');
    flipCard.className = 'p54-flip-card';
    flipCard.setAttribute('role', 'region');
    flipCard.setAttribute('aria-label', isRu ? '3D обложка и описание' : 'Copertă 3D și descriere');

    flipCard.innerHTML = `
      <div class="p54-flip-inner">
        <div class="p54-flip-front" title="${tapText}">
          <img src="${img.src}" alt="${img.alt}" loading="${img.loading || 'eager'}" decoding="async">
          <div class="p54-tap-hint" aria-hidden="true">
            <span class="p54-tap-icon">👆</span>
            <span>${tapText}</span>
          </div>
        </div>
        <div class="p54-flip-back">
          <div class="p54-flip-back-header">
            <h3 class="p54-flip-back-title">${descTitle}</h3>
            <button type="button" class="p54-flip-back-btn" aria-label="${flipBackText}">${flipBackText}</button>
          </div>
          <div class="p54-flip-back-body">${descHTML}</div>
        </div>
      </div>
    `;

    // Toggle flip on click
    flipCard.addEventListener('click', (e) => {
      if (e.target.closest('a')) return;
      flipCard.classList.toggle('is-flipped');
    });

    // Replace image container contents with the 3D Flip Card
    imgWrap.innerHTML = '';
    imgWrap.appendChild(flipCard);

    // Keep original description for SEO bots while avoiding visual duplication on page
    if (descEl) {
      descEl.style.display = 'none';
    }

    // Wrap specs & catalog facts in a Liquid Glass accordion
    const facts = detail.querySelector('.p40-product-facts');
    if (facts && !facts.closest('details')) {
      const acc = document.createElement('details');
      acc.className = 'p54-prod-accordion';
      acc.innerHTML = `
        <summary class="p54-prod-summary">
          <span class="p54-prod-sum-left"><span class="p54-prod-sum-icon">🎮</span> <span>${isRu ? 'Характеристики и код в каталоге' : 'Specificații & Cod catalog'}</span></span>
          <span class="p54-prod-chevron" aria-hidden="true"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg></span>
        </summary>
        <div class="p54-prod-content"></div>
      `;
      facts.parentNode.insertBefore(acc, facts);
      acc.querySelector('.p54-prod-content').appendChild(facts);
    }

    // Wrap editorial impressions in accordion
    const editorial = detail.querySelector('.p42-editorial');
    if (editorial && !editorial.closest('details')) {
      const acc = document.createElement('details');
      acc.className = 'p54-prod-accordion';
      const h2 = editorial.querySelector('h2');
      const title = h2 ? h2.textContent : (isRu ? 'Впечатление от геймплея' : 'Impresie editorială de gameplay');
      if (h2) h2.remove();
      acc.innerHTML = `
        <summary class="p54-prod-summary">
          <span class="p54-prod-sum-left"><span class="p54-prod-sum-icon">🎯</span> <span>${title}</span></span>
          <span class="p54-prod-chevron" aria-hidden="true"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg></span>
        </summary>
        <div class="p54-prod-content"></div>
      `;
      editorial.parentNode.insertBefore(acc, editorial);
      acc.querySelector('.p54-prod-content').appendChild(editorial);
    }

    // Wrap delivery info in accordion
    const fulfilment = detail.querySelector('.p44-fulfilment');
    if (fulfilment && !fulfilment.closest('details')) {
      const acc = document.createElement('details');
      acc.className = 'p54-prod-accordion';
      acc.innerHTML = `
        <summary class="p54-prod-summary">
          <span class="p54-prod-sum-left"><span class="p54-prod-sum-icon">🚚</span> <span>${isRu ? 'Доставка и получение в Кишинёве' : 'Livrare & Predare Chișinău'}</span></span>
          <span class="p54-prod-chevron" aria-hidden="true"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg></span>
        </summary>
        <div class="p54-prod-content"></div>
      `;
      fulfilment.parentNode.insertBefore(acc, fulfilment);
      acc.querySelector('.p54-prod-content').appendChild(fulfilment);
    }

    // Price disclaimer into inline (i) popover
    const pricebox = detail.querySelector('.seo-pricebox');
    if (pricebox) {
      const subtext = pricebox.querySelector('p');
      const labelSpan = pricebox.querySelector('span');
      if (subtext && labelSpan && !labelSpan.querySelector('.p54-info-tip')) {
        const tipText = subtext.textContent;
        subtext.style.display = 'none';
        const tipWrap = document.createElement('details');
        tipWrap.className = 'p54-info-tip';
        tipWrap.style.display = 'inline-block';
        tipWrap.style.verticalAlign = 'middle';
        tipWrap.style.marginLeft = '6px';
        tipWrap.innerHTML = `
          <summary class="p54-info-btn" aria-label="Info" style="display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;font-size:11px;border-radius:50%;background:rgba(52,255,184,0.15);border:1px solid rgba(52,255,184,0.4);color:#34ffb8;cursor:pointer;">i</summary>
          <div class="p54-info-popover" role="note" style="min-width:210px;font-size:12px;position:absolute;z-index:10;background:rgba(6,20,26,0.95);border:1px solid rgba(52,255,184,0.3);padding:8px 12px;border-radius:10px;color:#d1ece2;"><p style="margin:0;">${tipText}</p></div>
        `;
        labelSpan.appendChild(tipWrap);
      }
    }
  }

  function initFooterCredit() {
    const seoFooter = document.querySelector('.seo-footer-inner');
    if (seoFooter && !seoFooter.querySelector('.p54-wsod-credit')) {
      const isRu = document.documentElement.lang?.startsWith('ru');
      const sep = document.createElement('span');
      sep.textContent = '·';
      const wrap = document.createElement('span');
      wrap.innerHTML = isRu
        ? 'Сайт и SEO: <a href="https://www.wsod.cloud" target="_blank" rel="noopener" class="p54-wsod-credit">www.wsod.cloud</a>'
        : 'Website &amp; SEO de <a href="https://www.wsod.cloud" target="_blank" rel="noopener" class="p54-wsod-credit">www.wsod.cloud</a>';
      seoFooter.appendChild(sep);
      seoFooter.appendChild(wrap);
    }
  }

  const runAll = () => {
    initProductDetail();
    initFooterCredit();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runAll);
  } else {
    runAll();
  }
})();

/* PLAYSPOT-DELIVERY-TIP-JS-START */
(function(){
  var tips = document.querySelectorAll('details.seo-delivery-tip');
  if (!tips.length) return;
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  tips.forEach(function(tip){
    if (fine) {
      var timer = 0;
      tip.addEventListener('pointerenter', function(){ if (timer) { clearTimeout(timer); timer = 0; } tip.setAttribute('open', ''); });
      tip.addEventListener('pointerleave', function(){ timer = setTimeout(function(){ tip.removeAttribute('open'); }, 180); });
    }
  });
  document.addEventListener('click', function(e){
    tips.forEach(function(tip){ if (tip.open && !tip.contains(e.target)) tip.removeAttribute('open'); });
  });
})();
/* PLAYSPOT-DELIVERY-TIP-JS-END */


/* ============================================================================
 * WSOD COOKIE CONSENT (LEGEA 133/2011 RM & GDPR) + GOOGLE CONSENT MODE V2 + META PIXEL
 * Implicit (până la „Acceptă”): 0 cookies de marketing, ad_storage = denied.
 * ============================================================================ */
(() => {
  const CONSENT_KEY = 'playspot_cookie_consent_v2';
  const isRu = document.documentElement.lang?.toLowerCase().startsWith('ru');
  const CFG = Object.assign({ metaPixelId: '', ga4Id: '', googleAdsId: '' }, window.WSOD_PIXEL_CONFIG || {});
  window.dataLayer = window.dataLayer || [];
  function gtag(){ window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  window.gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    analytics_storage: 'denied', functionality_storage: 'granted', security_storage: 'granted', wait_for_update: 500
  });
  function clearMarketingCookies() {
    ['_fbp', '_fbc', '_ga', '_gid', '_gat', '_gcl_au', '_ttp'].forEach(name => {
      document.cookie = `${name}=; Max-Age=0; path=/; SameSite=Lax`;
      document.cookie = `${name}=; Max-Age=0; path=/; domain=${location.hostname}; SameSite=Lax`;
    });
  }
  let pixelsBooted = false;
  function bootConsentedPixels() {
    if (pixelsBooted) return;
    pixelsBooted = true;
    window.gtag('consent', 'update', { ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted', analytics_storage: 'granted' });
    const gId = CFG.ga4Id || CFG.googleAdsId;
    if (gId) {
      const s = document.createElement('script'); s.async = true;
      s.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(gId)}`;
      document.head.appendChild(s);
      window.gtag('js', new Date());
      if (CFG.ga4Id) window.gtag('config', CFG.ga4Id, { anonymize_ip: true });
      if (CFG.googleAdsId) window.gtag('config', CFG.googleAdsId);
    }
    if (CFG.metaPixelId) {
      !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
      n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
      n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window, document,'script',
      'https://connect.facebook.net/en_US/fbevents.js');
      window.fbq('consent', 'grant');
      window.fbq('init', CFG.metaPixelId);
      window.fbq('track', 'PageView');
    }
  }
  document.addEventListener('click', e => {
    try { if (localStorage.getItem(CONSENT_KEY) !== 'accepted') return; } catch { return; }
    const a = e.target.closest && e.target.closest('a'); if (!a) return;
    const href = a.getAttribute('href') || '';
    const eid = 'gb_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
    if (href.startsWith('tel:')) {
      window.gtag?.('event', 'contact_phone', { event_id: eid, page_path: location.pathname });
      window.fbq?.('track', 'Contact', { channel: 'phone', page_path: location.pathname }, { eventID: eid });
    } else if (href.includes('maps.app.goo.gl') || href.includes('google.com/maps')) {
      window.gtag?.('event', 'find_location', { event_id: eid, page_path: location.pathname });
      window.fbq?.('track', 'FindLocation', { page_path: location.pathname }, { eventID: eid });
    } else if (href.includes('instagram.com') || href.includes('wa.me')) {
      window.gtag?.('event', 'contact_social', { event_id: eid, page_path: location.pathname });
      window.fbq?.('track', 'Lead', { channel: 'social', page_path: location.pathname }, { eventID: eid });
    }
  }, { passive: true });
  function renderBanner() {
    document.getElementById('wsod-cookie-bar')?.remove();
    const bar = document.createElement('aside');
    bar.id = 'wsod-cookie-bar';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', isRu ? 'Настройки cookie' : 'Preferințe cookies');
    bar.style.cssText = 'position:fixed;bottom:18px;left:50%;transform:translateX(-50%);width:min(750px,calc(100vw - 28px));z-index:99999;padding:13px 18px;border-radius:14px;background:rgba(7,10,18,0.94);color:#e2f8ff;border:1px solid rgba(16,255,235,0.38);box-shadow:0 0 18px rgba(241,5,232,0.22),0 14px 36px rgba(0,0,0,0.72);font-family:Roboto Mono,system-ui,sans-serif;font-size:12px;line-height:1.45;backdrop-filter:blur(14px)';
    bar.innerHTML = `<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px"><div style="flex:1 1 400px"><strong style="color:#10ffeb">${isRu ? 'COOKIES & КОНФИДЕНЦИАЛЬНОСТЬ (Закон № 133/2011):' : 'COOKIES & CONFIDENȚIALITATE (Legea nr. 133/2011):'}</strong> ${isRu ? 'Используем технически необходимые файлы cookie и, только с вашего согласия, статистику и оценку рекламы (Google / Meta).' : 'Folosim cookies strict necesare și, doar cu acordul tău, statistici și măsurarea reclamelor (Google / Meta).'} <a href="${isRu ? '/ru/confidentialitate.html' : '/confidentialitate.html'}" style="color:#10ffeb;text-decoration:underline;font-weight:700">${isRu ? 'Политика Cookies' : 'Politica Cookies'}</a>.</div><div style="display:flex;gap:8px;align-items:center;margin-left:auto"><button type="button" data-consent="rejected" style="padding:7px 13px;border-radius:999px;border:1px solid rgba(16,255,235,0.35);background:rgba(255,255,255,0.04);color:#e2f8ff;font-size:11.5px;font-weight:600;cursor:pointer">${isRu ? 'Только необходимые' : 'Doar Necesare'}</button><button type="button" data-consent="accepted" style="padding:7px 16px;border-radius:999px;border:1px solid #10ffeb;background:linear-gradient(90deg,#10ffeb,#f105e8);color:#041014;font-size:11.5px;font-weight:800;cursor:pointer">${isRu ? 'Принять' : 'Acceptă'}</button></div></div>`;
    bar.addEventListener('click', ev => {
      const btn = ev.target.closest('button[data-consent]'); if (!btn) return;
      const choice = btn.dataset.consent;
      try { localStorage.setItem(CONSENT_KEY, choice); } catch {}
      bar.remove();
      if (choice === 'accepted') bootConsentedPixels(); else clearMarketingCookies();
    });
    document.body.appendChild(bar);
  }
  window.openWsodCookieSettings = renderBanner;
  let saved = null; try { saved = localStorage.getItem(CONSENT_KEY); } catch {}
  if (saved === 'accepted') bootConsentedPixels();
  else if (saved !== 'rejected') renderBanner();

  // 100% cookieless, zero-IP aggregate counter (vizite, țară în memorie, timp pe pagină, apeluri)
  const _t0 = Date.now();
  const _sendPulse = (ev, dur) => {
    try {
      navigator.sendBeacon?.('https://wsod.cloud/api/public/pulse-hit', JSON.stringify({
        s: 'playspot', e: ev, p: location.pathname || '/', r: ev === 'view' ? (document.referrer || '') : '', d: dur || 0
      }));
    } catch {}
  };
  _sendPulse('view');
  let _left = false;
  const _onLeave = () => { if (_left) return; _left = true; const s = Math.round((Date.now() - _t0) / 1000); if (s >= 1) _sendPulse('leave', s); };
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') _onLeave(); });
  window.addEventListener('pagehide', _onLeave);
  document.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('a'); if (!a) return;
    const h = a.getAttribute('href') || '';
    if (h.startsWith('tel:')) _sendPulse('call');
    else if (h.includes('wa.me') || h.includes('whatsapp') || h.includes('t.me') || h.includes('instagram.com')) _sendPulse('lead');
  }, { passive: true });
})();
