'use strict';
// Progressive enhancement only: every lesson remains readable without JavaScript.
(() => {
  const roadmap = document.querySelector('.roadmap details');
  if (roadmap && window.matchMedia('(max-width: 720px)').matches) roadmap.open = false;
  document.querySelectorAll('header nav a').forEach(link => {
    if (new URL(link.href).pathname === location.pathname) link.setAttribute('aria-current', 'page');
  });
  document.querySelectorAll('.roadmap a').forEach(link => link.addEventListener('click', () => {
    if (roadmap && window.matchMedia('(max-width: 720px)').matches) roadmap.open = false;
    const section = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (section) { section.setAttribute('tabindex', '-1'); setTimeout(() => section.focus({preventScroll: true}), 0); }
  }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && roadmap && roadmap.open) { roadmap.open = false; roadmap.querySelector('summary').focus(); }
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const active = entries.filter(entry => entry.isIntersecting).sort((a,b) => a.boundingClientRect.top-b.boundingClientRect.top)[0];
      if (!active) return;
      document.querySelectorAll('.roadmap a').forEach(link => {
        if (link.hash.slice(1) === active.target.id) link.setAttribute('aria-current','location'); else link.removeAttribute('aria-current');
      });
    }, {rootMargin:'-20% 0px -60% 0px'});
    document.querySelectorAll('.lesson-step').forEach(section => observer.observe(section));
  }
})();
