/* Progressive image loading (blur-up + fade-in).
   - Wraps target images in a .img-prog container.
   - Shows a tiny blurred LQIP placeholder (from /static/assets/lqip.json)
     immediately, then fades the full image in once it has loaded.
   - Adds loading="lazy" + decoding="async" and reserves space via
     aspect-ratio to avoid layout shift.
   Targets: any <img> inside .prose (blog articles) and any <img class="prog">.
   Safe to include on every page; it never touches other images. */
(function () {
  var MANIFEST = null;
  var queue = [];

  function normKey(src) {
    try { src = new URL(src, location.href).pathname; } catch (e) {}
    return src.replace(/^\/+/, '');
  }

  function info(src) {
    if (!MANIFEST) return null;
    return MANIFEST[normKey(src)] || null;
  }

  function enhanceImg(img) {
    if (img.dataset.prog) return;
    if (img.closest && img.closest('.img-prog')) { img.dataset.prog = '1'; return; }
    img.dataset.prog = '1';
    img.loading = 'lazy';
    img.decoding = 'async';

    var wrap = document.createElement('span');
    wrap.className = 'img-prog';
    var meta = info(img.getAttribute('src') || img.src);
    if (meta) {
      if (meta.lqip) { wrap.style.setProperty('--lqip', 'url("' + meta.lqip + '")'); wrap.classList.add('has-lqip'); }
      if (meta.w && meta.h) { wrap.style.aspectRatio = meta.w + ' / ' + meta.h; }
    }
    if (img.parentNode) {
      img.parentNode.insertBefore(wrap, img);
      wrap.appendChild(img);
    }
    function done() { wrap.classList.add('is-loaded'); }
    if (img.complete && img.naturalWidth) done();
    else { img.addEventListener('load', done); img.addEventListener('error', done); }
  }

  function enhance(root) {
    root = root || document;
    var imgs = root.querySelectorAll('.prose img, img.prog');
    Array.prototype.forEach.call(imgs, enhanceImg);
  }

  window.ProgImg = {
    get ready() { return MANIFEST !== null; },
    enhance: function (root) {
      if (MANIFEST !== null) enhance(root);
      else queue.push(root || document);
    }
  };

  function drain() {
    enhance(document);
    while (queue.length) { var r = queue.shift(); if (r !== document) enhance(r); }
  }

  fetch('/static/assets/lqip.json', { cache: 'force-cache' })
    .then(function (r) { return r.ok ? r.json() : {}; })
    .catch(function () { return {}; })
    .then(function (m) { MANIFEST = m || {}; drain(); });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { if (MANIFEST !== null) enhance(document); else queue.push(document); });
  }
})();
