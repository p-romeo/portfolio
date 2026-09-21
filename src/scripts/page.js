// scroll reveals, active nav, hero typing, progress bar (ported from the previous generator)
(function () {
  'use strict';
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // scroll reveals
  var items = document.querySelectorAll('[data-reveal]');
  if (!reduced && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }); }, { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { el.classList.add('reveal-pending'); io.observe(el); });
  } else { items.forEach(function (el) { el.classList.add('in'); }); }
  // active nav
  var links = [].slice.call(document.querySelectorAll('nav a[href^="/#"]'));
  var map = {}; links.forEach(function (a) { map[a.getAttribute('href').slice(2)] = a; });
  if ('IntersectionObserver' in window) {
    var nio = new IntersectionObserver(function (es) { es.forEach(function (e) {
      var a = map[e.target.id]; if (!a) return;
      if (e.isIntersecting) { links.forEach(function (l) { l.classList.remove('active'); }); a.classList.add('active'); }
    }); }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) nio.observe(s); });
  }
  // hero typing
  var roles = ['phishing defense', 'EDR management', 'security monitoring', 'SIEM & detection'];
  var el = document.getElementById('typed');
  if (!reduced && el) {
    var ri = 0, ci = 0, del = false;
    (function tick() {
      var w = roles[ri];
      el.textContent = w.slice(0, ci);
      var t = del ? 40 : 75;
      if (!del && ci === w.length) { t = 1600; del = true; }
      else if (del && ci === 0) { del = false; ri = (ri + 1) % roles.length; t = 350; }
      else ci += del ? -1 : 1;
      setTimeout(tick, t);
    })();
  } else if (el) { el.textContent = 'phishing defense · EDR · security monitoring'; }
  // progress bar
  var bar = document.getElementById('progress'), raf = 0;
  function upd() {
    raf = 0;
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    bar.style.transform = 'scaleX(' + (max > 0 ? (h.scrollTop || document.body.scrollTop) / max : 1) + ')';
  }
  addEventListener('scroll', function () { if (!raf) raf = requestAnimationFrame(upd); }, { passive: true });
  upd();
})();
