/* Blog listing: loads contents/blog/posts.json, renders bilingual cards,
   sorts newest-first, paginates client-side. */
(function () {
  var PER_PAGE = 8;
  var posts = [];
  var page = 1;

  var el = {
    list: document.getElementById('list'),
    pag: document.getElementById('pagination'),
    heroTitle: document.getElementById('hero-title'),
    heroSub: document.getElementById('hero-sub'),
    navAll: null
  };

  function L() { return window.BlogI18n.lang; }
  function pick(field) { return (field && (field[L()] || field.cn || field.en)) || ''; }

  function fmtDate(iso) {
    if (!iso) return '';
    var d = new Date(iso + 'T00:00:00');
    if (isNaN(d)) return iso;
    if (L() === 'cn') return d.getFullYear() + '年' + (d.getMonth() + 1) + '月' + d.getDate() + '日';
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function applyStaticText() {
    document.getElementById('page-title').textContent = window.BlogI18n.t('pageTitle');
    el.heroTitle.innerHTML = '<span class="accent">' + window.BlogI18n.t('writing') + '</span>';
    el.heroSub.textContent = window.BlogI18n.t('heroSub');
    var fc = document.getElementById('footer-copy');
    if (fc) fc.innerHTML = window.BlogI18n.t('footer');
    var hp = document.querySelector('.blog-nav a[href="/"]');
    if (hp) hp.textContent = window.BlogI18n.t('homepage');
  }

  function totalPages() { return Math.max(1, Math.ceil(posts.length / PER_PAGE)); }

  function renderList() {
    applyStaticText();
    if (!posts.length) { el.list.innerHTML = '<div class="empty">' + window.BlogI18n.t('empty') + '</div>'; el.pag.innerHTML = ''; return; }
    if (page > totalPages()) page = totalPages();

    var start = (page - 1) * PER_PAGE;
    var slice = posts.slice(start, start + PER_PAGE);

    el.list.innerHTML = slice.map(function (p, i) {
      var tags = (p.tags && (p.tags[L()] || p.tags.cn || p.tags.en)) || [];
      var tagHtml = tags.length ? '<div class="tags">' + tags.map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('') + '</div>' : '';
      var href = '/blog/post.html?slug=' + encodeURIComponent(p.slug) + '&lang=' + L();
      return '<a class="post-card fade-up" style="animation-delay:' + (i * 55) + 'ms" href="' + href + '">' +
               '<div class="meta"><span>' + fmtDate(p.date) + '</span></div>' +
               '<h2>' + esc(pick(p.title)) + '</h2>' +
               (pick(p.summary) ? '<p class="excerpt">' + esc(pick(p.summary)) + '</p>' : '') +
               tagHtml +
             '</a>';
    }).join('');

    renderPagination();
  }

  function renderPagination() {
    var tp = totalPages();
    if (tp <= 1) { el.pag.innerHTML = ''; return; }
    var html = '';
    html += '<button type="button" ' + (page === 1 ? 'disabled' : '') + ' data-go="' + (page - 1) + '">‹ ' + window.BlogI18n.t('prev') + '</button>';
    for (var i = 1; i <= tp; i++) {
      html += '<span class="pg ' + (i === page ? 'active' : '') + '" data-go="' + i + '" role="button" tabindex="0">' + i + '</span>';
    }
    html += '<button type="button" ' + (page === tp ? 'disabled' : '') + ' data-go="' + (page + 1) + '">' + window.BlogI18n.t('next') + ' ›</button>';
    el.pag.innerHTML = html;
    Array.prototype.forEach.call(el.pag.querySelectorAll('[data-go]'), function (n) {
      n.addEventListener('click', function () { go(parseInt(n.getAttribute('data-go'), 10)); });
    });
  }

  function go(n) {
    if (n < 1 || n > totalPages()) return;
    page = n;
    renderList();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  function load() {
    fetch('/contents/blog/posts.json', { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('no manifest'); return r.json(); })
      .then(function (data) {
        posts = (data.posts || []).slice().sort(function (a, b) { return (b.date || '').localeCompare(a.date || ''); });
        renderList();
      })
      .catch(function () { el.list.innerHTML = '<div class="empty">' + window.BlogI18n.t('empty') + '</div>'; });
  }

  window.BlogI18n.initToggle();
  window.addEventListener('blog-lang-change', function () { renderList(); });
  load();
})();
