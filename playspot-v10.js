/* PlaySpotStore V10 — no global popups. Banners only exist in the Sale section.
   Autoplay runs only while Sale carousel is in the viewport and document visible. */
(function () {
  'use strict';
  const carousel = document.getElementById('p10-sale-carousel');
  if (!carousel || carousel.dataset.initialized === 'yes') return;
  carousel.dataset.initialized = 'yes';
  const stage = carousel.querySelector('.p10-stage');
  const slides = Array.from(carousel.querySelectorAll('.p10-slide'));
  const dots = Array.from(carousel.querySelectorAll('.p10-dot'));
  const previous = carousel.querySelector('.p10-previous');
  const next = carousel.querySelector('.p10-next');
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let selected = 0, interval = null, visible = false, focusWithin = false, hover = false;
  let startX = null, startY = null, justSwiped = false;

  function update(index, wasManual) {
    selected = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      const diff = (i - selected + slides.length) % slides.length;
      const pos = diff === 0 ? 'active' : diff === 1 ? 'next' : 'prev';
      slide.dataset.position = pos;
      slide.tabIndex = pos === 'active' || (window.innerWidth > 700 && pos !== 'active') ? 0 : -1;
      if (pos === 'active') slide.setAttribute('aria-current', 'true');
      else slide.removeAttribute('aria-current');
    });
    dots.forEach((dot, i) => {
      const active = i === selected;
      dot.setAttribute('aria-current', String(active));
      dot.setAttribute('aria-label', (dot.dataset.label || 'Banner') + ' ' + (i + 1) + (active ? ' • activ' : ''));
    });
    if (wasManual) {stop(); restart();}
  }
  function stop() {if (interval !== null) {clearInterval(interval); interval = null;}}
  function restart() {
    stop();
    if (visible && !document.hidden && !hover && !focusWithin && !reduceMotion) {
      interval = window.setInterval(() => update(selected + 1, false), 4800);
    }
  }
  function manual(index) { update(index, true); }
  previous?.addEventListener('click', () => manual(selected - 1));
  next?.addEventListener('click', () => manual(selected + 1));
  dots.forEach((dot, i) => dot.addEventListener('click', () => manual(i)));

  slides.forEach((slide, i) => slide.addEventListener('click', (ev) => {
    if (justSwiped) {ev.preventDefault();return;}
    if (i !== selected) {ev.preventDefault(); manual(i);}
    // Clicking an active slide follows the real #promo-products anchor.
  }));
  stage?.addEventListener('keydown', ev => {
    if (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') {
      ev.preventDefault(); manual(selected + (ev.key === 'ArrowRight' ? 1 : -1));
    }
  });
  carousel.addEventListener('pointerenter', () => { hover = true; stop(); });
  carousel.addEventListener('pointerleave', () => { hover = false; restart(); });
  carousel.addEventListener('focusin', () => { focusWithin = true; stop(); });
  carousel.addEventListener('focusout', ev => {
    if (!carousel.contains(ev.relatedTarget)) { focusWithin = false; restart(); }
  });
  stage?.addEventListener('touchstart', ev => {
    const t = ev.changedTouches[0];startX = t.clientX;startY = t.clientY;
  }, {passive:true});
  stage?.addEventListener('touchend', ev => {
    if (startX === null) return;
    const t = ev.changedTouches[0], dx = t.clientX-startX, dy=t.clientY-startY;
    startX=null; startY=null;
    if (Math.abs(dx)>44 && Math.abs(dx)>Math.abs(dy)*1.25) {
      justSwiped = true;manual(selected + (dx<0?1:-1));
      window.setTimeout(() => {justSwiped=false;},450);
    }
  }, {passive:true});
  document.addEventListener('visibilitychange', restart);
  window.addEventListener('resize', () => update(selected, false), {passive:true});
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      visible = entries.some(entry => entry.isIntersecting && entry.intersectionRatio > .12);
      restart();
    }, {threshold:[0,.13,.25,.5]});
    observer.observe(carousel);
  } else {visible=true;restart();}
  update(0,false);
})();
