/* PlaySpotStore V39: short visual feedback before ordinary same-tab category nav.
   Modified clicks, middle click, context menu and reduced-motion stay native. */
(() => {
  'use strict';
  if (window.__playspotV39CategoryClick) return;
  window.__playspotV39CategoryClick = true;

  let navigating = false;
  const SELECTOR = '.hero .category-deck > a.category-tile';

  document.addEventListener('click', (event) => {
    if (event.defaultPrevented || navigating || event.button !== 0 ||
        event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const origin = event.target;
    const link = origin && origin.closest ? origin.closest(SELECTOR) : null;
    if (!link || link.hasAttribute('download') ||
        (link.target && link.target !== '_self')) return;
    const href = link.getAttribute('href');
    if (!href || href[0] === '#') return;
    let destination;
    try { destination = new URL(link.href, window.location.href); }
    catch (_) { return; }
    if (destination.origin !== window.location.origin ||
        !/\/(?:ru\/)?categorii\/[\w-]+\.html$/.test(destination.pathname)) return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    event.preventDefault();
    navigating = true;
    link.classList.add('p39-opening');
    // Fixed short cap: no dependency on animationend or slow-loading resources.
    window.setTimeout(() => window.location.assign(destination.href), 245);
  });

  // Remove transient state if the visitor returns via the back/forward cache.
  window.addEventListener('pageshow', () => {
    navigating = false;
    document.querySelectorAll(SELECTOR + '.p39-opening').forEach((link) => {
      link.classList.remove('p39-opening');
    });
  });
})();
