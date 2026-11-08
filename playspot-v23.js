/* PlaySpotStore V23: navigation, mobile unavailable-game modal, clickable offer, border lights. */
(() => {
  'use strict';
  const menu = document.getElementById('main-menu');
  const burger = document.getElementById('hamburger');
  const unavailable = document.querySelector('[data-p23-unavailable]');
  if (menu && unavailable && burger) {
    unavailable.addEventListener('click', event => {
      event.preventDefault();
      menu.classList.remove('active');
      burger.classList.remove('active');
      burger.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('p5-menu-open');
      const section = document.getElementById('how-to-order');
      if (section) {
        // Navigate to the real section first so closing its modal leaves the visitor here.
        if (window.location.hash !== '#how-to-order') history.replaceState(null,'','#how-to-order');
        section.scrollIntoView({behavior:'instant',block:'start'});
      }
      const openModalButton = document.getElementById('btn-unavailable');
      if (openModalButton) window.requestAnimationFrame(() => openModalButton.click());
    });
  }
  // Reuse the existing wheel button instead of creating a second promotion state.
  const bar = document.getElementById('p15-spin-bar');
  const invite = document.getElementById('p14-invite');
  if (bar && invite) {
    const offer = bar.querySelector('.p15-expiry');
    if (offer) {
      const lang = (document.documentElement.lang || 'ro').toLowerCase();
      offer.classList.add('p23-clickable');
      offer.setAttribute('role','button');
      offer.setAttribute('tabindex','0');
      offer.setAttribute('aria-haspopup','dialog');
      offer.setAttribute('aria-controls','p14-spin-overlay');
      offer.setAttribute('aria-label',lang.startsWith('ru')?'Открыть Spin & Win — ограниченная акция':'Deschide Spin & Win — ofertă limitată');
      offer.addEventListener('click',()=>invite.click());
      offer.addEventListener('keydown',ev=>{
        if (ev.key==='Enter' || ev.key===' ') {ev.preventDefault();invite.click();}
      });
    }
    if (!bar.querySelector('.p23-edge-lights')) {
      const ns='http://www.w3.org/2000/svg';
      const svg=document.createElementNS(ns,'svg');
      svg.classList.add('p23-edge-lights');
      svg.setAttribute('viewBox','0 0 515 70');
      svg.setAttribute('preserveAspectRatio','none');
      svg.setAttribute('aria-hidden','true');
      for (const cl of ['p23-light-a','p23-light-b']) {
        const rect=document.createElementNS(ns,'rect');
        rect.setAttribute('x','1.4');rect.setAttribute('y','1.4');
        rect.setAttribute('width','512.2');rect.setAttribute('height','67.2');
        rect.setAttribute('rx','19');rect.setAttribute('pathLength','1000');
        rect.classList.add(cl);svg.appendChild(rect);
      }
      bar.appendChild(svg);
    }
  }
})();
