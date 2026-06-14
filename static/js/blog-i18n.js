/* Shared bilingual helpers for the blog (EN / 中文).
   Language resolution order:
     1. ?lang= in the URL
     2. saved preference (localStorage)
     3. browser language (navigator.language)
     4. fallback: 'cn'
*/
(function () {
  var KEY = 'blog-lang';

  var UI = {
    cn: {
      langButton: 'EN',           // button shows the language you can switch TO
      allPosts: '全部文章',
      homepage: '学术主页',
      writing: '随笔',
      heroSub: '关于 AI、神经科学、文学与生活的随笔与札记。',
      loading: '加载中…',
      empty: '还没有文章。',
      notFound: '没有找到这篇文章。',
      back: '返回全部文章',
      readEN: '阅读英文版',
      readCN: '阅读中文版',
      minRead: '分钟阅读',
      pageTitle: '随笔 · 金泽昊',
      prev: '上一页',
      next: '下一页',
      footer: '© 金泽昊 2026 · <a href="/">学术主页</a> · <a href="https://github.com/lunamos">GitHub</a>'
    },
    en: {
      langButton: '中文',
      allPosts: 'All posts',
      homepage: 'Homepage',
      writing: 'Writing',
      heroSub: 'Essays and notes on AI, neuroscience, literature, and life.',
      loading: 'Loading…',
      empty: 'No posts yet.',
      notFound: 'This post could not be found.',
      back: 'Back to all posts',
      readEN: 'Read in English',
      readCN: '阅读中文版',
      minRead: ' min read',
      pageTitle: 'Writing · Zehao Jin',
      prev: 'Prev',
      next: 'Next',
      footer: '© Zehao Jin 2026 · <a href="/">Academic homepage</a> · <a href="https://github.com/lunamos">GitHub</a>'
    }
  };

  function detect() {
    try {
      var p = new URLSearchParams(location.search).get('lang');
      if (p === 'cn' || p === 'en') return p;
      var saved = localStorage.getItem(KEY);
      if (saved === 'cn' || saved === 'en') return saved;
    } catch (e) {}
    var nav = (navigator.language || navigator.userLanguage || '').toLowerCase();
    return nav.indexOf('zh') === 0 ? 'cn' : (nav ? 'en' : 'cn');
  }

  var lang = detect();

  function apply() {
    document.documentElement.lang = (lang === 'cn') ? 'zh' : 'en';
    var btn = document.getElementById('lang-toggle');
    if (btn) btn.textContent = UI[lang].langButton;
  }

  window.BlogI18n = {
    get lang() { return lang; },
    t: function (k) { return UI[lang][k]; },
    set: function (newLang) {
      if (newLang !== 'cn' && newLang !== 'en') return;
      lang = newLang;
      try { localStorage.setItem(KEY, lang); } catch (e) {}
      apply();
      // update ?lang= without reloading, then notify listeners
      try {
        var url = new URL(location.href);
        url.searchParams.set('lang', lang);
        history.replaceState(null, '', url);
      } catch (e) {}
      window.dispatchEvent(new CustomEvent('blog-lang-change', { detail: lang }));
    },
    toggle: function () { this.set(lang === 'cn' ? 'en' : 'cn'); },
    initToggle: function () {
      apply();
      var btn = document.getElementById('lang-toggle');
      if (btn) btn.addEventListener('click', function () { window.BlogI18n.toggle(); });
    }
  };

  apply();
})();
