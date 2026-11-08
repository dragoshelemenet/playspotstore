/* V16 — rolling 30-day promotion; 30-day validity belongs to EACH prize. */
(() => {
  'use strict';
  const invite = document.getElementById('p14-invite');
  if (!invite || document.getElementById('p15-spin-bar')) return;
  const isRu = String(document.documentElement.lang || '').toLowerCase().startsWith('ru');
  // This is the START of the original promotion, shared by all visitors.
  const anchor = Date.parse('2026-11-08T14:16:42+02:00');
  const cycleMs = 30 * 24 * 60 * 60 * 1000;
  const words = isRu ? {
    label: 'До обновления', unit: 'д', hide: 'Свернуть предложение', show: 'Открыть предложение',
    button: '-10% · Крути!',note: 'Предложение обновляется каждые 30 дней. Следующее обновление:',
    prize: 'Каждый выигранный код действителен 30 дней с момента выигрыша.'
  } : {
    label: 'Expiră în', unit: 'z', hide: 'Minimizează oferta', show: 'Arată oferta',
    button: 'Spin -10%',note: 'Promoția se reînnoiește la fiecare 30 de zile. Următoarea reînnoire:',
    prize: 'Fiecare cod câștigat este valabil 30 de zile de la rotire.'
  };
  const formatDate = ms => new Intl.DateTimeFormat(isRu ? 'ru-RU' : 'ro-RO', {
    timeZone: 'Europe/Chisinau', day: 'numeric', month: 'long', year: 'numeric'
  }).format(new Date(ms));
  // After each 30-day window, the next window starts automatically. Never expire the entire promotion.
  function currentCycle(now = Date.now()) {
    const elapsed = Math.max(0, now - anchor);
    const ordinal = Math.floor(elapsed / cycleMs);
    const end = anchor + (ordinal + 1) * cycleMs;
    const remaining = Math.max(1, Math.min(30, Math.ceil((end - now) / (24 * 60 * 60 * 1000))));
    return { end, remaining };
  }
  const bar = document.createElement('aside');
  bar.id = 'p15-spin-bar';
  bar.setAttribute('aria-label', isRu ? 'Колесо PlaySpotStore' : 'Roata PlaySpotStore');
  bar.innerHTML = `<div class="p15-primary"></div>
    <div class="p15-expiry"><span class="p15-expiry-label"></span><strong class="p15-expiry-time"></strong></div>
    <button class="p15-minimize" type="button" aria-label="${words.hide}" title="${words.hide}">−</button>
    <button class="p15-compact" type="button" aria-label="${words.show}" title="${words.show}">✦ <b>${words.button}</b></button>`;
  bar.querySelector('.p15-primary').appendChild(invite);
  document.body.appendChild(bar);
  const countdown = bar.querySelector('.p15-expiry-time');
  const label = bar.querySelector('.p15-expiry-label');
  const minimize = bar.querySelector('.p15-minimize');
  const compact = bar.querySelector('.p15-compact');
  const note = document.createElement('p');
  note.className = 'p15-campaign-note';
  const terms = document.querySelector('#p14-spin-overlay .p14-terms');
  if (terms) terms.insertAdjacentElement('beforebegin', note);
  label.textContent = words.label;
  function minimized(value) {
    bar.classList.toggle('is-minimized', value);
    document.body.classList.toggle('p15-bar-expanded', !value);
    try { sessionStorage.setItem('playspotstore-v15-spin-minimized', value ? '1' : '0'); } catch {}
  }
  minimize.addEventListener('click', () => {minimized(true); compact.focus({preventScroll:true});});
  compact.addEventListener('click', () => {minimized(false); invite.focus({preventScroll:true});});
  try { minimized(sessionStorage.getItem('playspotstore-v15-spin-minimized') === '1'); }
  catch { minimized(false); }
  function update() {
    const data = currentCycle();
    // Never show hours; day count resets to 30 at the next cycle.
    countdown.textContent = data.remaining + words.unit;
    const endDate = formatDate(data.end);
    countdown.title = endDate;
    countdown.setAttribute('aria-label', words.label + ' ' + data.remaining + (isRu ? ' дней' : ' zile'));
    note.textContent = words.note + ' ' + endDate + '. ' + words.prize;
  }
  update();
  window.setInterval(update, 60_000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) update(); });
})();
