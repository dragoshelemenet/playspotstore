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
