/* PlaySpotStore V37 — accessible toggle for price/extra filters; V36 performs filtering. */
(() => {
  'use strict';
  const panel = document.querySelector('.seo-category-hero.p37-hero .p36-filter-panel.p37-integrated');
  if (!panel) return;
  const toggle = panel.querySelector('[data-p37-toggle]');
  const extras = panel.querySelector('[data-p37-extras]');
  if (!toggle || !extras || toggle.dataset.p37Ready === '1') return;
  toggle.dataset.p37Ready = '1';
  const setOpen = open => {
    extras.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
  };
  setOpen(false);
  toggle.addEventListener('click', () => setOpen(extras.hidden));

  // Move category fulfilment notice into a compact Liquid Glass (i) beside "Produse în această categorie"
  const note = document.querySelector('.p44-fulfilment.p44-category');
  const listHead = document.querySelector('.seo-list .seo-list-head');
  const listTitle = listHead ? listHead.querySelector('h2') : null;
  if (note && listHead && listTitle && !listHead.querySelector('.p54-cat-info')) {
    const titleWrap = document.createElement('div');
    titleWrap.className = 'p54-cat-title-wrap';
    listTitle.parentNode.insertBefore(titleWrap, listTitle);
    titleWrap.appendChild(listTitle);

    const tip = document.createElement('details');
    tip.className = 'p54-cat-info';
    const summary = document.createElement('summary');
    summary.className = 'p54-cat-info-btn';
    summary.setAttribute('aria-label', 'Informații livrare și comandă');
    summary.textContent = 'i';

    const pop = document.createElement('div');
    pop.className = 'p54-cat-info-popover';
    pop.setAttribute('role', 'note');
    while (note.firstChild) pop.appendChild(note.firstChild);
    note.remove();

    tip.appendChild(summary);
    tip.appendChild(pop);
    titleWrap.appendChild(tip);

    if (window.matchMedia('(pointer: fine) and (hover: hover)').matches) {
      let timer = 0;
      tip.addEventListener('pointerenter', () => {
        if (timer) { clearTimeout(timer); timer = 0; }
        tip.setAttribute('open', '');
      });
      tip.addEventListener('pointerleave', () => {
        timer = window.setTimeout(() => { tip.removeAttribute('open'); timer = 0; }, 160);
      });
    }
    document.addEventListener('click', (e) => {
      if (tip.hasAttribute('open') && !tip.contains(e.target)) tip.removeAttribute('open');
    });
  }
})();
