/* PlaySpotStore V22 — Header Spin & Win trigger, reuses V14 wheel and its state. */
(() => {
  'use strict';
  const button=document.querySelector('header .p22-header-spin');
  if(!button) return;
  button.addEventListener('click',() => {
    const invite=document.getElementById('p14-invite');
    if(invite) invite.click();
  });
})();
