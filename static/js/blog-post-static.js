/* Static post pages: the article HTML for both languages is baked into the
   page at build time (see tools/build.py). This script only toggles which
   language container is visible, keeps <title>/<meta>/<html lang> in sync for
   in-browser navigation, and (re)runs MathJax + progressive images on the
   visible container. No network fetch, no client-side Markdown rendering. */
(function () {
  var article = document.getElementById('article');
  if (!article) return;

  var meta = {};
  try { meta = JSON.parse(document.getElementById('post-meta').textContent || '{}'); } catch (e) {}

  function L() { return window.BlogI18n.lang; }
  function node(l) { return article.querySelector('.post-lang[data-lang="' + l + '"]'); }
  function setAttr(id, attr, val) { var n = document.getElementById(id); if (n) n.setAttribute(attr, val); }

  function show() {
    var l = L();
    if (!node(l)) l = (l === 'cn' ? 'en' : 'cn');   // fall back if a language is missing
    var visible = null;
    Array.prototype.forEach.call(article.querySelectorAll('.post-lang'), function (n) {
      var on = n.getAttribute('data-lang') === l;
      n.hidden = !on;
      if (on) visible = n;
    });

    var m = meta[l] || meta.en || meta.cn || {};
    if (m.title) document.title = m.title + ' · Zehao Jin';
    if (m.summary) setAttr('meta-desc', 'content', m.summary);
    document.documentElement.lang = (l === 'cn') ? 'zh' : 'en';

    var na = document.getElementById('nav-all');
    if (na) na.textContent = window.BlogI18n.t('allPosts');

    if (visible) {
      if (window.ProgImg) window.ProgImg.enhance(visible);
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([visible]).catch(function () {});
      }
    }
  }

  window.BlogI18n.initToggle();
  window.addEventListener('blog-lang-change', show);
  show();
})();
