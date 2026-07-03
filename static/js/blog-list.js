/* Blog listing — progressive enhancement over the PRE-RENDERED index.
   tools/build.py bakes the full year-grouped post list (both languages),
   the tag chip rows, and a tag translation map into blog/index.html.
   This script only:
     * shows the active language's list / chip row,
     * filters entries by search query + selected tag (hiding empty years),
     * keeps ?tag= and ?q= in the URL so filtered views are shareable.
   Without JS the whole list stays visible and crawlable. */
(function () {
  var state = { q: '', tag: '' };

  var el = {
    lists: document.querySelectorAll('.post-list'),
    chipRows: document.querySelectorAll('.tag-row'),
    heroTitle: document.getElementById('hero-title'),
    heroSub: document.getElementById('hero-sub'),
    search: document.getElementById('post-search'),
    searchClear: document.getElementById('search-clear'),
    note: document.getElementById('result-note'),
    empty: document.getElementById('no-results')
  };

  var tagMap = {};
  var ui = {};
  try { tagMap = JSON.parse(document.getElementById('tag-map').textContent || '{}'); } catch (e) {}
  try { ui = JSON.parse(document.getElementById('ui-strings').textContent || '{}'); } catch (e) {}

  function L() { return window.BlogI18n.lang; }

  function activeList() {
    for (var i = 0; i < el.lists.length; i++) {
      if (el.lists[i].getAttribute('data-lang') === L()) return el.lists[i];
    }
    return el.lists[0];
  }

  function applyStaticText() {
    document.getElementById('page-title').textContent = window.BlogI18n.t('pageTitle');
    el.heroTitle.innerHTML = '<span class="accent">' + window.BlogI18n.t('writing') + '</span>';
    el.heroSub.textContent = window.BlogI18n.t('heroSub');
    var hp = document.querySelector('.blog-nav a[href="/"]');
    if (hp) hp.textContent = window.BlogI18n.t('homepage');
    if (el.search && ui[L()]) el.search.placeholder = ui[L()].search_ph;
  }

  /* ---- filtering ---- */
  function entryMatches(entry) {
    if (state.tag) {
      var tags = (entry.getAttribute('data-tags') || '').split('|');
      if (tags.indexOf(state.tag) === -1) return false;
    }
    if (state.q) {
      var blob = entry.getAttribute('data-search') || '';
      var words = state.q.toLowerCase().split(/\s+/).filter(Boolean);
      for (var i = 0; i < words.length; i++) {
        if (blob.indexOf(words[i]) === -1) return false;
      }
    }
    return true;
  }

  function render() {
    applyStaticText();

    // show the active language's list & chip row
    Array.prototype.forEach.call(el.lists, function (n) {
      n.hidden = n.getAttribute('data-lang') !== L();
    });
    Array.prototype.forEach.call(el.chipRows, function (n) {
      n.hidden = n.getAttribute('data-lang') !== L();
      // sync active chip; unfold the row if the active chip sits in the folded tail
      Array.prototype.forEach.call(n.querySelectorAll('.chip:not(.chip-more)'), function (c, idx) {
        var active = (c.getAttribute('data-tag') || '') === state.tag;
        c.classList.toggle('is-active', active);
        if (active && idx >= 12) n.classList.remove('collapsed');
      });
    });

    // filter entries; hide year groups that end up empty
    var list = activeList();
    var total = 0;
    Array.prototype.forEach.call(list.querySelectorAll('.year-group'), function (group) {
      var visibleInGroup = 0;
      Array.prototype.forEach.call(group.querySelectorAll('.post-entry'), function (entry) {
        var ok = entryMatches(entry);
        entry.hidden = !ok;
        if (ok) visibleInGroup++;
      });
      group.hidden = visibleInGroup === 0;
      total += visibleInGroup;
    });

    // result note + empty state
    var filtering = !!(state.q || state.tag);
    el.note.hidden = !filtering;
    if (filtering) {
      el.note.textContent = (L() === 'cn')
        ? '► 找到 ' + total + ' 篇文章'
        : '► ' + total + ' post' + (total === 1 ? '' : 's') + ' found';
    }
    el.empty.hidden = total > 0;
    if (!total) el.empty.textContent = window.BlogI18n.t('empty');

    syncUrl();
  }

  function syncUrl() {
    try {
      var url = new URL(location.href);
      if (state.tag) url.searchParams.set('tag', state.tag); else url.searchParams.delete('tag');
      if (state.q) url.searchParams.set('q', state.q); else url.searchParams.delete('q');
      history.replaceState(null, '', url);
    } catch (e) {}
  }

  /* ---- events ---- */
  Array.prototype.forEach.call(el.chipRows, function (row) {
    row.addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      if (chip.hasAttribute('data-more')) {
        var folded = row.classList.toggle('collapsed');
        chip.textContent = chip.getAttribute(folded ? 'data-label-more' : 'data-label-less');
        return;
      }
      var t = chip.getAttribute('data-tag') || '';
      state.tag = (t && t === state.tag) ? '' : t;  // click active chip again = clear
      render();
    });
  });

  var debounce;
  if (el.search) {
    el.search.addEventListener('input', function () {
      clearTimeout(debounce);
      debounce = setTimeout(function () {
        state.q = el.search.value.trim();
        el.searchClear.hidden = !state.q;
        render();
      }, 120);
    });
    el.searchClear.addEventListener('click', function () {
      el.search.value = '';
      state.q = '';
      el.searchClear.hidden = true;
      render();
      el.search.focus();
    });
  }

  // Carry the active tag across a language switch via the baked tag map
  // (tags.cn[i] ↔ tags.en[i] are parallel translations).
  window.addEventListener('blog-lang-change', function () {
    if (state.tag) {
      var from = (L() === 'cn') ? 'en' : 'cn';
      var display = null;
      // tagMap keys are display-cased; state.tag is lowercased — find it
      Object.keys(tagMap[from] || {}).some(function (k) {
        if (k.toLowerCase() === state.tag) { display = tagMap[from][k]; return true; }
        return false;
      });
      state.tag = display ? display.toLowerCase() : '';
    }
    render();
  });

  /* ---- init from URL ---- */
  try {
    var params = new URLSearchParams(location.search);
    state.tag = (params.get('tag') || '').toLowerCase();
    state.q = params.get('q') || '';
    if (el.search && state.q) { el.search.value = state.q; el.searchClear.hidden = false; }
  } catch (e) {}

  window.BlogI18n.initToggle();
  render();
})();
