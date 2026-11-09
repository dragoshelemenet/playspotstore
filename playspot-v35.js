/* PlaySpotStore V35: light scroll parallax layered on top of V34 floating animations.
   No scroll animations on prefers-reduced-motion, no GIF, no new image downloads. */
(() => {
  'use strict';
  const layers = document.querySelector('.hero .p34-layers');
  if (!layers || layers.dataset.p35Ready === '1') return;
  layers.dataset.p35Ready = '1';
  const hero = layers.closest('.hero');
  if (!hero) return;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const vars = ['--p35-main-x','--p35-main-y','--p35-sparks-x','--p35-sparks-y','--p35-symbols-x','--p35-symbols-y'];
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  let progress = 0, goal = 0, frame = 0, start = 0, distance = 500;

  function geometry() {
    // Begin near the hero's natural location and reach the maximum depth
    // just before it is scrolled out of view.
    start = window.scrollY + hero.getBoundingClientRect().top - 90;
    distance = Math.max(330, Math.min(hero.offsetHeight || 600, 900) * 0.78);
    measure();
  }
  function measure() {
    if (motion.matches) return;
    goal = clamp((window.scrollY - start) / distance, 0, 1);
    if (!frame) frame = requestAnimationFrame(draw);
  }
  function draw() {
    frame = 0;
    if (motion.matches) return;
    // Critically damped-feeling smoothing, including fast mouse-wheel scroll.
    progress += (goal - progress) * 0.135;
    if (Math.abs(goal - progress) < 0.001) progress = goal;
    const narrow = window.innerWidth <= 540;
    const tablet = !narrow && window.innerWidth <= 950;
    const factor = narrow ? 0.48 : tablet ? 0.72 : 1;
    const p = progress * factor;
    // Preserve the logo's position, but separate the three depth planes.
    layers.style.setProperty('--p35-main-x', (1.5 * p).toFixed(2) + 'px');
    layers.style.setProperty('--p35-main-y', (-23 * p).toFixed(2) + 'px');
    layers.style.setProperty('--p35-sparks-x', (-7 * p).toFixed(2) + 'px');
    layers.style.setProperty('--p35-sparks-y', (17 * p).toFixed(2) + 'px');
    layers.style.setProperty('--p35-symbols-x', (12 * p).toFixed(2) + 'px');
    layers.style.setProperty('--p35-symbols-y', (-43 * p).toFixed(2) + 'px');
    if (progress !== goal) frame = requestAnimationFrame(draw);
  }
  function reset() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0; progress = 0; goal = 0;
    vars.forEach(name => layers.style.removeProperty(name));
    if (!motion.matches) geometry();
  }
  window.addEventListener('scroll', measure, { passive: true });
  window.addEventListener('resize', geometry, { passive: true });
  if (motion.addEventListener) motion.addEventListener('change', reset);
  else if (motion.addListener) motion.addListener(reset);
  if (!motion.matches) geometry();
})();
