/* V18: remove any stale V16 notification that browser caches may recreate. */
(() => {
  'use strict';
  const removeLegacyNotice = () => {
    document.querySelectorAll('#p14-spin-overlay .p15-campaign-note').forEach(el => el.remove());
  };
  removeLegacyNotice();
  // Older tabs sometimes load cached versions of v16.js. Remove their notice too.
  document.addEventListener('visibilitychange', () => { if(!document.hidden) removeLegacyNotice(); });
})();
