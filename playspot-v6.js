/* PlaySpotStore V6 — fullscreen, zoomable gallery for real inventory photos. */
(() => {
  'use strict';
  function setupGallery() {
    const gallery = document.querySelector('#produse-noi .p3-photo-grid');
    if (!gallery || document.getElementById('p6-gallery-dialog')) return;
    const items = Array.from(gallery.querySelectorAll('figure'))
      .map(figure => ({figure, image:figure.querySelector('img'), caption:figure.querySelector('figcaption')}))
      .filter(item => item.image);
    if (!items.length) return;
    const ru = document.documentElement.lang.toLowerCase().startsWith('ru');
    const labels = ru ? {
      close:'Закрыть',previous:'Предыдущее фото',next:'Следующее фото',
      zoomIn:'Увеличить',zoomOut:'Уменьшить',original:'Открыть оригинал',
      inspect:'Открыть полноразмерное фото'
    } : {
      close:'Închide',previous:'Fotografia anterioară',next:'Fotografia următoare',
      zoomIn:'Mărește',zoomOut:'Micșorează',original:'Deschide fotografia originală',
      inspect:'Deschide fotografia la dimensiune mare'
    };
    const dialog = document.createElement('dialog');
    dialog.id = 'p6-gallery-dialog';
    dialog.className = 'p6-lightbox';
    dialog.setAttribute('aria-label', ru ? 'Galerie foto PlaySpotStore' : 'Galerie foto PlaySpotStore');
    dialog.innerHTML = `
      <div class="p6-toolbar">
        <div class="p6-title" id="p6-gallery-title"></div>
        <div class="p6-counter" aria-live="polite"></div>
        <button type="button" class="p6-control p6-close" aria-label="${labels.close}">×</button>
      </div>
      <div class="p6-stage">
        <button type="button" class="p6-control p6-arrow p6-prev" aria-label="${labels.previous}">‹</button>
        <div class="p6-viewer"><img class="p6-image" alt=""></div>
        <button type="button" class="p6-control p6-arrow p6-next" aria-label="${labels.next}">›</button>
      </div>
      <div class="p6-footer">
        <button type="button" class="p6-control p6-zoom" aria-label="${labels.zoomIn}">${labels.zoomIn}</button>
        <a class="p6-open-original" target="_blank" rel="noopener noreferrer">${labels.original}</a>
      </div>`;
    document.body.appendChild(dialog);
    const title=dialog.querySelector('.p6-title');
    const count=dialog.querySelector('.p6-counter');
    const img=dialog.querySelector('.p6-image');
    const viewer=dialog.querySelector('.p6-viewer');
    const zoomButton=dialog.querySelector('.p6-zoom');
    const original=dialog.querySelector('.p6-open-original');
    let current=0,previousFocus=null,previousOverflow='';
    function captionOf(item) {return item.caption?.textContent.trim() || item.image.alt || 'PlaySpotStore';}
    function update() {
      const item=items[current];
      const src=item.image.getAttribute('src') || item.image.currentSrc;
      const caption=captionOf(item);
      dialog.classList.remove('zoomed');
      img.src=src;
      img.alt=caption;
      title.textContent=caption;
      count.textContent=`${current+1} / ${items.length}`;
      original.href=src;
      zoomButton.textContent=labels.zoomIn;
      zoomButton.setAttribute('aria-label',labels.zoomIn);
      viewer.scrollTop=0;viewer.scrollLeft=0;
    }
    function open(index) {
      current=index;
      previousFocus=document.activeElement;
      previousOverflow=document.body.style.overflow;
      update();
      if(typeof dialog.showModal==='function') dialog.showModal();
      else dialog.setAttribute('open','');
      document.body.style.overflow='hidden';
      dialog.querySelector('.p6-close').focus();
    }
    function close() {
      if(typeof dialog.close==='function' && dialog.open) dialog.close();
      else {dialog.removeAttribute('open'); onClose();}
    }
    function onClose() {
      dialog.classList.remove('zoomed');
      document.body.style.overflow=previousOverflow;
      if(previousFocus && typeof previousFocus.focus==='function') previousFocus.focus();
    }
    function shift(delta) {current=(current+delta+items.length)%items.length;update();}
    function toggleZoom() {
      const zoomed=dialog.classList.toggle('zoomed');
      zoomButton.textContent=zoomed?labels.zoomOut:labels.zoomIn;
      zoomButton.setAttribute('aria-label',zoomed?labels.zoomOut:labels.zoomIn);
      viewer.scrollTop=0;viewer.scrollLeft=0;
    }
    items.forEach((item,index) => {
      item.figure.setAttribute('role','button');
      item.figure.setAttribute('tabindex','0');
      item.figure.setAttribute('aria-label',`${labels.inspect}: ${captionOf(item)}`);
      item.figure.addEventListener('click', () => open(index));
      item.figure.addEventListener('keydown',event => {
        if (event.key==='Enter' || event.key===' ') {event.preventDefault();open(index);}
      });
    });
    dialog.querySelector('.p6-close').addEventListener('click',close);
    dialog.querySelector('.p6-prev').addEventListener('click',()=>shift(-1));
    dialog.querySelector('.p6-next').addEventListener('click',()=>shift(1));
    zoomButton.addEventListener('click',toggleZoom);
    img.addEventListener('click',toggleZoom);
    dialog.addEventListener('click', event => {if(event.target===dialog)close();});
    dialog.addEventListener('close',onClose);
    dialog.addEventListener('keydown',event => {
      if(event.key==='ArrowLeft') {event.preventDefault();shift(-1);}
      else if(event.key==='ArrowRight') {event.preventDefault();shift(1);}
      else if(event.key==='Escape' && typeof dialog.close!=='function') {event.preventDefault();close();}
    });
    let touchX=null,touchY=null;
    viewer.addEventListener('touchstart',event => {
      if(dialog.classList.contains('zoomed') || event.touches.length!==1) {touchX=null;return;}
      touchX=event.touches[0].clientX;touchY=event.touches[0].clientY;
    },{passive:true});
    viewer.addEventListener('touchend',event => {
      if(touchX===null || dialog.classList.contains('zoomed') || !event.changedTouches.length) return;
      const dx=event.changedTouches[0].clientX-touchX;
      const dy=event.changedTouches[0].clientY-touchY;
      touchX=null;touchY=null;
      if(Math.abs(dx)>65 && Math.abs(dx)>Math.abs(dy)*1.3) shift(dx<0?1:-1);
    },{passive:true});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',setupGallery,{once:true});
  else setupGallery();
})();
