/* PlaySpotStore V27 — explicitly declared 2026 baseline + shared recorded visits.
   PRESET BASELINE: 330,012 (manual, NOT historical traffic verified by the API).
   API: countapi.mileshilliard.com. One registration per browser via localStorage,
   shared by RO/RU on the same domain. This is an approximation of distinct browsers,
   not verified unique people; visitors prior to deployment cannot be recovered.
   Counter keys are public, so this is NOT a tamper-proof analytics service. */
(() => {
  'use strict';
  const number = document.getElementById('p26-total');
  const note = document.getElementById('p27-status');
  if (!number) return;
  const BASELINE_2026 = 330012;

  const API = 'https://countapi.mileshilliard.com/api/v1';
  const KEY = 'pss_playspotstore_online_v26_browser_visitors_20261108_8f64a2d1';
  const STORAGE_KEY = 'pss_v26_registered_browser_8f64a2d1';
  const SERVICE_URL = `${API}/`;
  const allowedHosts = new Set(['playspotstore.online','www.playspotstore.online']);
  const format = new Intl.NumberFormat(document.documentElement.lang?.startsWith('ru') ? 'ru-RU' : 'ro-RO');
  const isRussian = document.documentElement.lang?.startsWith('ru');

  const render = measured => {
    if (!Number.isSafeInteger(measured) || measured < 0) throw new Error('Invalid counter value');
    const total = BASELINE_2026 + measured;
    if (!Number.isSafeInteger(total)) throw new Error('Counter overflow');
    number.textContent = format.format(total);
    number.dataset.state = 'ready';
    number.title = isRussian ? '330 012 — заданная вручную база 2026 года + ' + measured + ' учтённых посещений' : '330.012 — baza introdusă manual pentru 2026 + ' + measured + ' vizite înregistrate';
    number.setAttribute('aria-label', String(total) + (isRussian ? ' всего, включая заданную вручную базу' : ' total, inclusiv baza setată manual'));
    if (note) note.textContent = isRussian ? 'База 330 012 + ' + format.format(measured) + ' новых браузеров' : 'Bază 330.012 + ' + format.format(measured) + ' browsere noi';
  };
  const unavailable = () => {
    // Show only the declared preset, not a made-up measured value.
    number.textContent = format.format(BASELINE_2026);
    number.dataset.state = 'baseline';
    number.title = isRussian ? 'Показана только заданная вручную база; сервер сейчас недоступен.' : 'Este afișată doar baza setată manual; serviciul nu răspunde momentan.';
    number.setAttribute('aria-label', number.title);
    if (note) note.textContent = isRussian ? 'Только база 2026 · подсчёт недоступен' : 'Doar baza 2026 · contor indisponibil';
  };

  async function fetchCount(operation) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    try {
      const res = await fetch(`${SERVICE_URL}${operation}/${KEY}?_=${Date.now()}`, {
        method:'GET',mode:'cors',credentials:'omit',cache:'no-store',signal:controller.signal
      });
      if (!res.ok) throw new Error('Counter HTTP ' + res.status);
      const json = await res.json();
      if (!json || !Number.isSafeInteger(json.value) || json.value < 0) throw new Error('Bad count');
      return json.value;
    } finally {clearTimeout(timeout);}
  }

  async function start() {
    // Production only: GitHub Codespaces previews and local tests MUST NOT inflate the total.
    // Automated testing browsers also do not register a visit.
    if (!allowedHosts.has(location.hostname.toLowerCase()) || navigator.webdriver === true) {
      try {render(await fetchCount('get'));} catch {unavailable();}
      return;
    }

    let stored;
    try {stored = localStorage.getItem(STORAGE_KEY);}
    catch {stored = 'unavailable';}

    if (stored === 'registered' || stored === 'unavailable' || (stored && stored.startsWith('pending:') && Date.now() - Number(stored.split(':')[1]) < 20000)) {
      try {render(await fetchCount('get'));} catch {unavailable();}
      return;
    }

    // Avoid double-counting concurrent tabs where possible. No tracking cookies, IPs or identities.
    try {localStorage.setItem(STORAGE_KEY,'pending:'+Date.now());}
    catch {try {render(await fetchCount('get'));} catch {unavailable();}return;}

    try {
      const count = await fetchCount('hit');
      localStorage.setItem(STORAGE_KEY,'registered');
      render(count);
    } catch {
      try {localStorage.removeItem(STORAGE_KEY);} catch {}
      try {render(await fetchCount('get'));} catch {unavailable();}
    }
  }

  // Refresh displayed total when returning to the tab, without incrementing again.
  let lastRefresh = Date.now();
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && Date.now() - lastRefresh > 60000) {
      lastRefresh = Date.now();
      fetchCount('get').then(render).catch(unavailable);
    }
  });
  start();
})();
