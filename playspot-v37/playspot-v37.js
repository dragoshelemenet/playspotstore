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
})();
