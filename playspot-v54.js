/* PlaySpotStore V54 — GTA VI Hero 3D Parallax & Liquid Glass Specular Sheen */
(() => {
  'use strict';

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(pointer: fine) and (hover: hover)');

  // 1. Scroll-reactive Liquid Glass header depth
  const header = document.querySelector('header');
  if (header) {
    const syncHeader = () => {
      header.classList.toggle('p54-scrolled', window.scrollY > 18);
    };
    window.addEventListener('scroll', syncHeader, { passive: true });
    syncHeader();
  }

  // 2. Interactive 3D parallax on the GTA VI hero stage
  const hero = document.querySelector('.hero.p54-gta-hero');
  const stage = hero ? hero.querySelector('.p54-stage') : null;
  if (hero && stage && finePointer.matches && !reducedMotion.matches) {
    let targetX = 0;
    let targetY = 0;
    let curX = 0;
    let curY = 0;
    let rafId = 0;

    const tick = () => {
      rafId = 0;
      curX += (targetX - curX) * 0.11;
      curY += (targetY - curY) * 0.11;
      stage.style.setProperty('--px', curX.toFixed(2) + 'px');
      stage.style.setProperty('--py', curY.toFixed(2) + 'px');
      if (Math.abs(targetX - curX) > 0.05 || Math.abs(targetY - curY) > 0.05) {
        rafId = requestAnimationFrame(tick);
      }
    };

    const schedule = () => {
      if (!rafId) rafId = requestAnimationFrame(tick);
    };

    hero.addEventListener('pointermove', (e) => {
      const rect = hero.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const nx = (e.clientX - rect.left) / rect.width - 0.5;
      const ny = (e.clientY - rect.top) / rect.height - 0.5;
      targetX = nx * 24;
      targetY = ny * 16;
      schedule();
    }, { passive: true });

    hero.addEventListener('pointerleave', () => {
      targetX = 0;
      targetY = 0;
      schedule();
    }, { passive: true });
  }

  // 3. Liquid Glass specular light tracking on glass cards
  if (finePointer.matches && !reducedMotion.matches) {
    const glassSelector = [
      '.category-tile',
      '.social-card',
      '.p29-seo-links a',
      '.p3-photo-grid figure',
      '.feature',
      '.step'
    ].join(',');

    document.querySelectorAll(glassSelector).forEach((el) => {
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        el.style.setProperty('--lg-x', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        el.style.setProperty('--lg-y', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      }, { passive: true });
    });
  }

  // 4. Liquid Glass (i) / ($) info popovers — hover on desktop + tap/click outside to close
  const allTips = Array.from(document.querySelectorAll('details.p54-info-tip'));
  allTips.forEach((tip) => {
    tip.addEventListener('toggle', () => {
      if (tip.open) {
        allTips.forEach((other) => { if (other !== tip) other.removeAttribute('open'); });
      }
    });
    if (finePointer.matches) {
      let closeTimer = 0;
      tip.addEventListener('pointerenter', () => {
        if (closeTimer) { clearTimeout(closeTimer); closeTimer = 0; }
        tip.setAttribute('open', '');
      });
      tip.addEventListener('pointerleave', () => {
        closeTimer = window.setTimeout(() => {
          tip.removeAttribute('open');
          closeTimer = 0;
        }, 160);
      });
    }
  });
  document.addEventListener('click', (e) => {
    document.querySelectorAll('details.p54-info-tip[open]').forEach((tip) => {
      if (!tip.contains(e.target)) tip.removeAttribute('open');
    });
  });

  // 5. Interactive Liquid Glass pagination dots for TikTok Carousel
  const tiktokRail = document.querySelector('#p20-tiktok-gallery .p20-rail');
  const tiktokControls = document.querySelector('#p20-tiktok-gallery .p20-controls');
  if (tiktokRail && tiktokControls) {
    const tiles = Array.from(tiktokRail.querySelectorAll('.p20-tile'));
    const nextBtn = tiktokControls.querySelector('.p20-next');
    if (tiles.length > 1 && nextBtn && !tiktokControls.querySelector('.p54-tiktok-dots')) {
      const dotsWrap = document.createElement('div');
      dotsWrap.className = 'p54-tiktok-dots';
      dotsWrap.setAttribute('role', 'tablist');
      dotsWrap.setAttribute('aria-label', 'TikTok video slides');

      let activeIdx = 0;
      const goTo = (idx) => {
        activeIdx = ((idx % tiles.length) + tiles.length) % tiles.length;
        const tile = tiles[activeIdx];
        const targetLeft = tile.offsetLeft - (tiktokRail.clientWidth - tile.offsetWidth) / 2;
        tiktokRail.scrollTo({ left: Math.max(0, targetLeft), behavior: 'smooth' });
      };

      const dots = tiles.map((tile, idx) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'p54-tiktok-dot' + (idx === 0 ? ' is-active' : '');
        dot.setAttribute('aria-label', 'Video ' + (idx + 1));
        dot.addEventListener('click', () => goTo(idx));
        dotsWrap.appendChild(dot);
        return dot;
      });

      tiktokControls.insertBefore(dotsWrap, nextBtn);

      const syncDots = () => {
        const center = tiktokRail.scrollLeft + tiktokRail.clientWidth / 2;
        let bestIdx = 0;
        let bestDist = Infinity;
        tiles.forEach((tile, i) => {
          const tileCenter = tile.offsetLeft + tile.offsetWidth / 2;
          const dist = Math.abs(tileCenter - center);
          if (dist < bestDist) {
            bestDist = dist;
            bestIdx = i;
          }
        });
        activeIdx = bestIdx;
        dots.forEach((d, i) => d.classList.toggle('is-active', i === bestIdx));
      };

      tiktokRail.addEventListener('scroll', syncDots, { passive: true });
      syncDots();

      // Smooth continuous infinite loop on mobile/scrollable rail; pauses on touch/hover
      if (!reducedMotion.matches) {
        let paused = false;
        let resumeTimer = 0;
        let clonesAdded = false;
        let loopWidth = 0;

        const setupSeamlessLoop = () => {
          if (tiktokRail.scrollWidth <= tiktokRail.clientWidth + 8) return;
          if (!clonesAdded) {
            clonesAdded = true;
            tiles.forEach((tile) => {
              const clone = tile.cloneNode(true);
              clone.setAttribute('aria-hidden', 'true');
              clone.setAttribute('tabindex', '-1');
              tiktokRail.appendChild(clone);
            });
          }
          const firstClone = tiktokRail.children[tiles.length];
          if (firstClone) {
            loopWidth = firstClone.offsetLeft - tiles[0].offsetLeft;
          }
        };

        const pauseBriefly = () => {
          paused = true;
          if (resumeTimer) clearTimeout(resumeTimer);
          resumeTimer = window.setTimeout(() => { paused = false; }, 3500);
        };
        tiktokRail.addEventListener('pointerdown', pauseBriefly, { passive: true });
        tiktokRail.addEventListener('touchstart', pauseBriefly, { passive: true });
        tiktokRail.addEventListener('pointerenter', () => { paused = true; }, { passive: true });
        tiktokRail.addEventListener('pointerleave', () => { paused = false; }, { passive: true });

        setupSeamlessLoop();
        window.addEventListener('resize', setupSeamlessLoop, { passive: true });

        // Disable snap during continuous glide so it moves buttery smooth
        tiktokRail.style.scrollSnapType = 'none';
        let lastTime = performance.now();
        const glide = (now) => {
          const dt = Math.min(48, now - lastTime);
          lastTime = now;
          if (!paused && !document.hidden && loopWidth > 0 && tiktokRail.scrollWidth > tiktokRail.clientWidth + 8) {
            tiktokRail.scrollLeft += dt * 0.042;
            if (tiktokRail.scrollLeft >= loopWidth) {
              tiktokRail.scrollLeft -= loopWidth;
            }
            const relCenter = (tiktokRail.scrollLeft % loopWidth) + tiktokRail.clientWidth / 2;
            let bestIdx = 0;
            let bestDist = Infinity;
            tiles.forEach((tile, i) => {
              const d = Math.abs((tile.offsetLeft + tile.offsetWidth / 2) - relCenter);
              if (d < bestDist) { bestDist = d; bestIdx = i; }
            });
            activeIdx = bestIdx;
            dots.forEach((d, i) => d.classList.toggle('is-active', i === bestIdx));
          }
          requestAnimationFrame(glide);
        };
        requestAnimationFrame(glide);
      }
    }
  }

  // 6. Merge footer copyright + tag button cleanly alongside the 2026 visitor counter
  const mergeFooterVisitorBar = () => {
    const inner = document.querySelector('section.p26-visitor-counter .p26-inner');
    const bottom = document.querySelector('footer.p8-footer .p8-bottom');
    if (!inner || !bottom || inner.dataset.p54Merged === '1') return;
    inner.dataset.p54Merged = '1';

    const visitorGroup = document.createElement('div');
    visitorGroup.className = 'p54-visitor-group';
    while (inner.firstChild) {
      visitorGroup.appendChild(inner.firstChild);
    }

    const copyGroup = document.createElement('div');
    copyGroup.className = 'p54-copyright-group';
    while (bottom.firstChild) {
      copyGroup.appendChild(bottom.firstChild);
    }
    bottom.remove();

    inner.appendChild(visitorGroup);
    inner.appendChild(copyGroup);
  };
  mergeFooterVisitorBar();
  window.addEventListener('load', mergeFooterVisitorBar, { once: true });

  // 7. Interactive 🤑 SALE badge with confetti + -$ burst animation
  const spawnSaleBurst = (anchorEl) => {
    if (reducedMotion.matches) return;
    const rect = anchorEl.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const colors = ['#64ffbb', '#5ce8ff', '#ff64c8', '#ffd85e', '#a8ff88', '#b57cff'];

    for (let i = 0; i < 18; i++) {
      const p = document.createElement('span');
      const isDollar = i < 4;
      p.className = 'p54-burst-particle ' + (isDollar ? 'p54-burst-dollar' : 'p54-burst-confetti');
      if (isDollar) p.textContent = '-$';
      const angle = (Math.PI * 2 * i) / 18 + (Math.random() - 0.5) * 0.45;
      const dist = (isDollar ? 48 : 38) + Math.random() * 48;
      const dx = Math.cos(angle) * dist;
      const dy = Math.sin(angle) * dist - 18;
      p.style.setProperty('--x0', cx.toFixed(1) + 'px');
      p.style.setProperty('--y0', cy.toFixed(1) + 'px');
      p.style.setProperty('--dx', dx.toFixed(1) + 'px');
      p.style.setProperty('--dy', dy.toFixed(1) + 'px');
      p.style.setProperty('--rot', ((Math.random() - 0.5) * 320).toFixed(0) + 'deg');
      p.style.setProperty('--dur', (760 + Math.random() * 340).toFixed(0) + 'ms');
      if (!isDollar) {
        p.style.setProperty('--col', colors[i % colors.length]);
        p.style.setProperty('--w', (6 + Math.random() * 4).toFixed(0) + 'px');
        p.style.setProperty('--h', (3 + Math.random() * 3).toFixed(0) + 'px');
      }
      document.body.appendChild(p);
      window.setTimeout(() => p.remove(), 1150);
    }
  };

  const upgradeSaleStickers = () => {
    document.querySelectorAll('.product-card .sale-sticker').forEach((el) => {
      if (el.dataset.p54SaleReady === '1') return;
      el.dataset.p54SaleReady = '1';
      el.classList.add('p54-money-sale');
      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
      el.setAttribute('aria-label', 'Reducere SALE');
      el.innerHTML = '<span class="p54-money-emoji" aria-hidden="true">🤑</span><span class="p54-sale-word">SALE!</span>';

      let resetTimer = 0;
      const trigger = (e) => {
        e.preventDefault();
        e.stopPropagation();
        el.classList.add('is-open');
        spawnSaleBurst(el);
        if (resetTimer) clearTimeout(resetTimer);
        resetTimer = window.setTimeout(() => el.classList.remove('is-open'), 1900);
      };
      el.addEventListener('click', trigger);
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') trigger(e);
      });
    });
  };

  upgradeSaleStickers();
  const promoHost = document.getElementById('promo-products');
  if (promoHost && window.MutationObserver) {
    new MutationObserver(upgradeSaleStickers).observe(promoHost, { childList: true, subtree: true });
  }
})();
