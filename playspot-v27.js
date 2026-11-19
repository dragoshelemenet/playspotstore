/* PlaySpotStore V27 — explicitly declared 2026 baseline + shared recorded visits.
   PRESET BASELINE: 330,012 (manual, NOT historical traffic verified by the API).
   API: countapi.mileshilliard.com. One registration per browser via localStorage,
   shared by RO/RU on the same domain. This is an approximation of distinct browsers,
   not verified unique people; visitors prior to deployment cannot be recovered.
   Counter keys are public, so this is NOT a tamper-proof analytics service. */
(() => {
  'use strict';
  const number = document.getElementById('p26-total');
  const note = document.getElementById('p27-status');
  if (!number) return;
  const BASELINE_2026 = 330012;

  const API = 'https://countapi.mileshilliard.com/api/v1';
  const KEY = 'pss_playspotstore_online_v26_browser_visitors_20261108_8f64a2d1';
  const STORAGE_KEY = 'pss_v26_registered_browser_8f64a2d1';
  const SERVICE_URL = `${API}/`;
  const allowedHosts = new Set(['playspotstore.online','www.playspotstore.online']);
  const format = new Intl.NumberFormat(document.documentElement.lang?.startsWith('ru') ? 'ru-RU' : 'ro-RO');
  const isRussian = document.documentElement.lang?.startsWith('ru');

  const render = measured => {
    if (!Number.isSafeInteger(measured) || measured < 0) throw new Error('Invalid counter value');
    const total = BASELINE_2026 + measured;
    if (!Number.isSafeInteger(total)) throw new Error('Counter overflow');
    number.textContent = format.format(total);
    number.dataset.state = 'ready';
    number.title = isRussian ? '330 012 — заданная вручную база 2026 года + ' + measured + ' учтённых посещений' : '330.012 — baza introdusă manual pentru 2026 + ' + measured + ' vizite înregistrate';
    number.setAttribute('aria-label', String(total) + (isRussian ? ' всего, включая заданную вручную базу' : ' total, inclusiv baza setată manual'));
    if (note) note.textContent = isRussian ? 'База 330 012 + ' + format.format(measured) + ' новых браузеров' : 'Bază 330.012 + ' + format.format(measured) + ' browsere noi';
  };
  const unavailable = () => {
    // Show only the declared preset, not a made-up measured value.
    number.textContent = format.format(BASELINE_2026);
    number.dataset.state = 'baseline';
    number.title = isRussian ? 'Показана только заданная вручную база; сервер сейчас недоступен.' : 'Este afișată doar baza setată manual; serviciul nu răspunde momentan.';
    number.setAttribute('aria-label', number.title);
    if (note) note.textContent = isRussian ? 'Только база 2026 · подсчёт недоступен' : 'Doar baza 2026 · contor indisponibil';
  };

  async function fetchCount(operation) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    try {
      const res = await fetch(`${SERVICE_URL}${operation}/${KEY}?_=${Date.now()}`, {
        method:'GET',mode:'cors',credentials:'omit',cache:'no-store',signal:controller.signal
      });
      if (!res.ok) throw new Error('Counter HTTP ' + res.status);
      const json = await res.json();
      if (!json || !Number.isSafeInteger(json.value) || json.value < 0) throw new Error('Bad count');
      return json.value;
    } finally {clearTimeout(timeout);}
  }

  async function start() {
    // Production only: GitHub Codespaces previews and local tests MUST NOT inflate the total.
    // Automated testing browsers also do not register a visit.
    if (!allowedHosts.has(location.hostname.toLowerCase()) || navigator.webdriver === true) {
      try {render(await fetchCount('get'));} catch {unavailable();}
      return;
    }

    let stored;
    try {stored = localStorage.getItem(STORAGE_KEY);}
    catch {stored = 'unavailable';}

    if (stored === 'registered' || stored === 'unavailable' || (stored && stored.startsWith('pending:') && Date.now() - Number(stored.split(':')[1]) < 20000)) {
      try {render(await fetchCount('get'));} catch {unavailable();}
      return;
    }

    // Avoid double-counting concurrent tabs where possible. No tracking cookies, IPs or identities.
    try {localStorage.setItem(STORAGE_KEY,'pending:'+Date.now());}
    catch {try {render(await fetchCount('get'));} catch {unavailable();}return;}

    try {
      const count = await fetchCount('hit');
      localStorage.setItem(STORAGE_KEY,'registered');
      render(count);
    } catch {
      try {localStorage.removeItem(STORAGE_KEY);} catch {}
      try {render(await fetchCount('get'));} catch {unavailable();}
    }
  }

  // Refresh displayed total when returning to the tab, without incrementing again.
  let lastRefresh = Date.now();
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && Date.now() - lastRefresh > 60000) {
      lastRefresh = Date.now();
      fetchCount('get').then(render).catch(unavailable);
    }
  });
  start();
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
