/* PlaySpotStore V8. Tags are not placed into the footer DOM or fetched on page
   load. The icon opens an optional, searchable dialog. */
(() => {
  'use strict';
  const trigger = document.getElementById('p8-tags-open');
  const dialog = document.getElementById('p8-tags-dialog');
  const close = document.getElementById('p8-tags-close');
  const search = document.getElementById('p8-tags-search');
  const results = document.getElementById('p8-tags-results');
  if (!trigger || !dialog || !close || !search || !results) return;
  const isRu = document.documentElement.lang.toLowerCase().startsWith('ru');
  const url = isRu ? 'data/tags_ru.json' : 'data/tags.json';
  let source = null;
  let pending = null;
  const render = () => {
    if (!source) return;
    const term = search.value.trim().toLocaleLowerCase();
    const fragment = document.createDocumentFragment();
    let shown = 0;
    for (const place of source.locations) {
      if (shown >= 48) break;
      for (const tag of source.websiteTags) {
        if (shown >= 48) break;
        const value = `${place} — ${tag}`;
        if (term && !value.toLocaleLowerCase().includes(term)) continue;
        const el = document.createElement('span');
        el.className = 'p8-tag-pill';
        el.textContent = value;
        fragment.append(el);
        shown++;
      }
    }
    results.replaceChildren(fragment);
    if (!shown) {
      const text = document.createElement('p');
      text.className = 'p8-state';
      text.textContent = isRu ? 'Ничего не найдено.' : 'Niciun rezultat. Încearcă altă căutare.';
      results.append(text);
    }
  };
  const load = async () => {
    if (source) return render();
    results.textContent = isRu ? 'Загрузка…' : 'Se încarcă…';
    try {
      if (!pending) pending = fetch(url).then(r => {if (!r.ok) throw Error(r.status); return r.json();});
      const data = await pending;
      if (!Array.isArray(data.locations) || !Array.isArray(data.websiteTags)) throw Error('Invalid tag JSON');
      source = data;
      render();
    } catch (e) {
      pending = null;
      results.textContent = isRu ? 'Не удалось загрузить метки.' : 'Nu am putut încărca etichetele.';
      console.warn('Tag dialog:', e);
    }
  };
  trigger.addEventListener('click', () => {
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
    search.value = '';
    load();
    search.focus();
  });
  close.addEventListener('click', () => dialog.close ? dialog.close() : dialog.removeAttribute('open'));
  dialog.addEventListener('click', e => {if (e.target === dialog) dialog.close ? dialog.close() : dialog.removeAttribute('open');});
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && dialog.open) {
      e.preventDefault();
      dialog.close ? dialog.close() : dialog.removeAttribute('open');
    }
  });
  search.addEventListener('input', render);
})();
