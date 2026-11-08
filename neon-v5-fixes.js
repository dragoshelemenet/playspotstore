/* Mobile nav repair: move the real menu node outside the fixed/backdrop-filter
   header so it can overlay the viewport without clipping. No duplicated links
   and no replacement of existing click handlers. */
(function () {
  'use strict';
  const menu = document.getElementById('main-menu');
  const toggle = document.getElementById('hamburger');
  if (!menu || !toggle || !window.matchMedia) return;
  const initialParent = menu.parentNode;
  const initialNextSibling = menu.nextSibling;
  const mq = window.matchMedia('(max-width: 1430px), (min-width: 1431px) and (max-width: 1535px) and (any-pointer: coarse)');

  const close = () => {
    menu.classList.remove('active');
    toggle.classList.remove('active');
    toggle.setAttribute('aria-expanded', 'false');
  };
  const sync = () => {
    const open = mq.matches && menu.classList.contains('active');
    document.body.classList.toggle('p5-menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? (document.documentElement.lang === 'ru' ? 'Закрыть меню' : 'Închide meniul')
                                          : (document.documentElement.lang === 'ru' ? 'Открыть меню' : 'Deschide meniul'));
  };
  const relocate = () => {
    if (mq.matches) {
      if (menu.parentNode !== document.body) document.body.appendChild(menu);
    } else {
      close();
      if (menu.parentNode !== initialParent) initialParent.insertBefore(menu, initialNextSibling);
    }
    sync();
  };
  new MutationObserver(sync).observe(menu, {attributes: true, attributeFilter: ['class']});
  if (mq.addEventListener) mq.addEventListener('change', relocate);
  else if (mq.addListener) mq.addListener(relocate);
  // The original click listener keeps controlling the active state.
  // This listener only closes on selections and keeps keyboard support.
  menu.addEventListener('click', event => {
    if (event.target.closest('a[href]')) close();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.classList.contains('active')) {
      close(); toggle.focus();
    }
  });
  relocate();
})();
