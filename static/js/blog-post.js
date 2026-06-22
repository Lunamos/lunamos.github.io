/* Single post: reads ?slug=, loads metadata from posts.json and the
   matching markdown (slug.cn.md / slug.en.md), renders with marked + MathJax.
   Language toggle re-renders in place and remembers availability per language. */
(function () {
  var slug = new URLSearchParams(location.search).get('slug') || '';
  var meta = null;
  var article = document.getElementById('article');

  function L() { return window.BlogI18n.lang; }
  function pick(field) { return (field && (field[L()] || field.cn || field.en)) || ''; }

  function fmtDate(iso) {
    if (!iso) return '';
    var d = new Date(iso + 'T00:00:00');
    if (isNaN(d)) return iso;
    if (L() === 'cn') return d.getFullYear() + '年' + (d.getMonth() + 1) + '月' + d.getDate() + '日';
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function applyChrome() {
    var na = document.getElementById('nav-all');
    if (na) na.textContent = window.BlogI18n.t('allPosts');
  }

  function readingTime(text) {
    var chars = (text || '').replace(/\s+/g, '').length;
    return Math.max(1, Math.ceil(chars / 900));
  }

  function render() {
    applyChrome();
    if (!meta) { article.innerHTML = '<div class="empty">' + window.BlogI18n.t('notFound') + '</div>'; return; }

    article.innerHTML = '<div class="loading"><div class="spinner"></div><span>' + window.BlogI18n.t('loading') + '</span></div>';

    var mdPath = '/contents/blog/' + slug + '.' + L() + '.md';
    fetch(mdPath, { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('missing'); return r.text(); })
      .then(function (md) { paint(md); })
      .catch(function () {
        // fall back to the other language if this one is missing
        var other = L() === 'cn' ? 'en' : 'cn';
        fetch('/contents/blog/' + slug + '.' + other + '.md', { cache: 'no-cache' })
          .then(function (r) { return r.ok ? r.text() : Promise.reject(); })
          .then(function (md) { paint(md, true, other); })
          .catch(function () { article.innerHTML = '<div class="empty">' + window.BlogI18n.t('notFound') + '</div>'; });
      });
  }

  function paint(md, fellBack, shownLang) {
    var lang = shownLang || L();
    var title = pick(meta.title);
    var dateStr = fmtDate(meta.date);
    var mins = readingTime(md);
    var minLabel = (lang === 'cn') ? (mins + ' ' + '分钟阅读') : (mins + ' min read');

    var summary = pick(meta.summary);
    var canonical = 'https://zehaojin.com/blog/post.html?slug=' + encodeURIComponent(slug);

    document.title = title + ' · Zehao Jin';
    setAttr('meta-desc', 'content', summary);
    setAttr('og-title', 'content', title);
    setAttr('og-desc', 'content', summary);
    setAttr('og-url', 'content', canonical);
    setAttr('tw-title', 'content', title);
    setAttr('tw-desc', 'content', summary);
    setAttr('canonical', 'href', canonical);
    document.documentElement.lang = (lang === 'cn') ? 'zh' : 'en';

    setArticleJsonLd(title, summary, canonical, lang);

    marked.use({ mangle: false, headerIds: false, gfm: true, breaks: false });
    var bodyHtml = marked.parse(md);

    var kicker = (meta.tags && pick(meta.tags) && pick(meta.tags)[0]) ? esc(pick(meta.tags)[0]) : '';

    var html = '<header class="post-head fade-up">' +
                 (kicker ? '<div class="kicker">' + kicker + '</div>' : '') +
                 '<h1>' + esc(title) + '</h1>' +
                 '<div class="byline">' +
                   (dateStr ? '<span>' + dateStr + '</span><span>·</span>' : '') +
                   '<span>' + minLabel + '</span>' +
                 '</div>' +
                 '<div class="rule"></div>' +
               '</header>' +
               '<div class="reading prose fade-up" style="animation-delay:90ms">' + bodyHtml + '</div>' +
               '<div class="post-foot fade-up"><div class="row">' +
                 '<a class="back-link" href="/blog/?lang=' + L() + '">‹ ' + window.BlogI18n.t('back') + '</a>' +
               '</div></div>';

    article.innerHTML = html;

    if (window.ProgImg) window.ProgImg.enhance(article);

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([article]).catch(function () {});
    }
  }

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  function setAttr(id, attr, val) { var n = document.getElementById(id); if (n) n.setAttribute(attr, val); }

  function setArticleJsonLd(title, summary, canonical, lang) {
    var node = document.getElementById('ld-article');
    if (!node || !meta) return;
    var data = {
      '@context': 'https://schema.org',
      '@type': 'BlogPosting',
      'headline': title,
      'description': summary,
      'inLanguage': (lang === 'cn') ? 'zh-CN' : 'en',
      'url': canonical,
      'mainEntityOfPage': canonical,
      'image': 'https://zehaojin.com/static/assets/img/jzh.jpg',
      'author': { '@type': 'Person', 'name': 'Zehao Jin', 'url': 'https://zehaojin.com/' },
      'publisher': { '@type': 'Person', 'name': 'Zehao Jin', 'url': 'https://zehaojin.com/' }
    };
    if (meta.date) { data.datePublished = meta.date; data.dateModified = meta.date; }
    var keywords = pick(meta.tags);
    if (keywords && keywords.length) data.keywords = keywords.join(', ');
    node.textContent = JSON.stringify(data);
  }

  function load() {
    fetch('/contents/blog/posts.json', { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var arr = (data.posts || []);
        for (var i = 0; i < arr.length; i++) { if (arr[i].slug === slug) { meta = arr[i]; break; } }
        render();
      })
      .catch(function () { article.innerHTML = '<div class="empty">' + window.BlogI18n.t('notFound') + '</div>'; });
  }

  window.BlogI18n.initToggle();
  window.addEventListener('blog-lang-change', function () { render(); });
  load();
})();
