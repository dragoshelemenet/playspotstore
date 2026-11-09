/* PlaySpotStore V36 – local, accessible RO/RU filtering on each SEO category page. */
(() => {
  'use strict';
  const panel = document.querySelector('.p36-filter-panel');
  const grid = document.querySelector('.seo-list .seo-grid');
  if (!panel || !grid || panel.dataset.ready === '1') return;
  panel.dataset.ready = '1';

  const ru = (document.documentElement.lang || 'ro').toLowerCase().startsWith('ru');
  const $ = selector => panel.querySelector(selector);
  const search = $('[data-p36-search]');
  const min = $('[data-p36-min]');
  const max = $('[data-p36-max]');
  const sort = $('[data-p36-sort]');
  const onlyNew = $('[data-p36-new]');
  const onlyPriced = $('[data-p36-priced]');
  const counter = $('[data-p36-count]');
  const reset = $('[data-p36-reset]');
  const presets = Array.from(panel.querySelectorAll('[data-p36-range]'));
  const listCount = document.querySelector('.seo-list-head > span');
  const empty = document.createElement('p');
  empty.className = 'p36-empty';
  empty.hidden = true;
  empty.textContent = ru ? 'По вашему запросу ничего не найдено. Измените фильтры.' : 'Niciun produs gasit. Modifica filtrele sau reseteaza cautarea.';
  grid.insertAdjacentElement('afterend', empty);

  const normalized = value => (value || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().trim();
  const numericPrice = value => {
    if (!/\bMDL\b/i.test(value || '')) return null;
    const match = value.match(/\d[\d.,\s\u00a0\u202f]*/);
    if (!match) return null;
    const result = Number(match[0].replace(/\D/g,''));
    return Number.isFinite(result) && result > 0 ? result : null;
  };
  const cards = Array.from(grid.querySelectorAll(':scope > .seo-product-card')).map((node,index) => ({
    node, index,
    title: (node.querySelector('.seo-product-body h3')?.textContent || node.querySelector('a')?.getAttribute('aria-label') || '').trim(),
    newArrival: !!node.querySelector('.seo-new'),
    price: numericPrice(node.querySelector('.seo-product-price')?.textContent || '')
  }));
  cards.forEach(card => {card.searchTitle = normalized(card.title);});
  const priceCount = cards.filter(card => card.price !== null).length;
  if (!priceCount) {
    min.disabled = true; max.disabled = true; onlyPriced.disabled = true;
    presets.forEach(button => {button.disabled = true;});
    Array.from(sort.options).filter(option => option.value.startsWith('price-')).forEach(option => {option.disabled = true;});
  }
  if (!cards.some(card => card.newArrival)) onlyNew.disabled = true;
  const collator = new Intl.Collator(ru ? 'ru' : 'ro', {sensitivity:'base', numeric:true});
  let activeRange = '';

  const update = () => {
    const query = normalized(search.value);
    const low = min.value === '' ? null : Number(min.value);
    const high = max.value === '' ? null : Number(max.value);
    let visible = 0;
    cards.forEach(card => {
      const priceMatch = (!onlyPriced.checked || card.price !== null) &&
        ((low === null && high === null) ||
         (card.price !== null && (low === null || card.price >= low) && (high === null || card.price <= high)));
      const show = (!query || card.searchTitle.includes(query)) && priceMatch && (!onlyNew.checked || card.newArrival);
      card.node.hidden = !show;
      if (show) visible += 1;
    });
    const ordered = cards.slice().sort((a,b) => {
      if (sort.value === 'name-asc') return collator.compare(a.title,b.title) || a.index-b.index;
      if (sort.value === 'name-desc') return collator.compare(b.title,a.title) || a.index-b.index;
      if (sort.value === 'new') return Number(b.newArrival)-Number(a.newArrival) || a.index-b.index;
      if (sort.value.startsWith('price-')) {
        if (a.price === null) return b.price === null ? a.index-b.index : 1;
        if (b.price === null) return -1;
        return (sort.value === 'price-asc' ? a.price-b.price : b.price-a.price) || a.index-b.index;
      }
      return a.index-b.index;
    });
    const fragment = document.createDocumentFragment();
    ordered.forEach(card => fragment.appendChild(card.node));
    grid.appendChild(fragment);
    const countLabel = ru ? `${visible} из ${cards.length} товаров` : `${visible} din ${cards.length} produse`;
    counter.textContent = countLabel;
    if (listCount) listCount.textContent = countLabel;
    empty.hidden = visible !== 0;
    presets.forEach(button => button.setAttribute('aria-pressed',String(button.dataset.p36Range === activeRange)));
  };
  [search,min,max,sort,onlyNew,onlyPriced].forEach(control => control.addEventListener(control.tagName === 'SELECT' || control.type === 'checkbox' ? 'change' : 'input',() => {
    if (control === min || control === max) activeRange = '';
    update();
  }));
  presets.forEach(button => button.addEventListener('click',() => {
    const key = button.dataset.p36Range;
    if (activeRange === key) {activeRange='';min.value='';max.value='';}
    else {
      activeRange = key;
      const [lo,hi] = key.split(':');
      min.value=lo;max.value=hi;
    }
    update();
  }));
  reset.addEventListener('click',() => {
    search.value=''; min.value='';max.value='';sort.value='default';
    onlyNew.checked=false;onlyPriced.checked=false;activeRange='';update();
    search.focus({preventScroll:true});
  });
  update();
})();
