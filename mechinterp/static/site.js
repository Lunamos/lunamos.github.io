(() => {
  const params = new URLSearchParams(location.search);
  let language = params.get('lang');
  if (language !== 'cn' && language !== 'en') language = localStorage.getItem('site-lang') || 'en';
  if (language !== 'cn' && language !== 'en') language = 'en';

  function applyLanguage(next, updateUrl) {
    language = next;
    document.documentElement.dataset.lang = language;
    document.documentElement.lang = language === 'cn' ? 'zh-CN' : 'en';
    localStorage.setItem('site-lang', language);
    const button = document.querySelector('[data-language-toggle]');
    if (button) button.textContent = language === 'cn' ? 'EN' : '中文';
    const searchInput = document.querySelector('[data-search]');
    if (searchInput) searchInput.placeholder = language === 'cn' ? searchInput.dataset.placeholderCn : searchInput.dataset.placeholderEn;
    if (updateUrl) {
      const url = new URL(location.href);
      url.searchParams.set('lang', language);
      history.replaceState(null, '', url);
    }
  }
  applyLanguage(language, false);
  document.querySelector('[data-language-toggle]')?.addEventListener('click', () => applyLanguage(language === 'cn' ? 'en' : 'cn', true));

  const search = document.querySelector('[data-search]');
  const cards = [...document.querySelectorAll('[data-paper]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const emptyStates = [...document.querySelectorAll('[data-empty]')];
  let active = 'all';

  function applyFilters() {
    const query = (search?.value || '').trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const matchesText = !query || card.dataset.search.includes(query);
      const matchesTrack = active === 'all' || card.dataset.track === active;
      card.hidden = !(matchesText && matchesTrack);
      if (!card.hidden) visible += 1;
    });
    emptyStates.forEach(empty => { empty.style.display = visible ? 'none' : 'block'; });
  }

  search?.addEventListener('input', applyFilters);
  filters.forEach(button => button.addEventListener('click', () => {
    active = button.dataset.filter;
    filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    applyFilters();
  }));

  const progress = document.querySelector('.reading-progress');
  if (progress) window.addEventListener('scroll', () => {
    const range = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = `${range > 0 ? scrollY / range * 100 : 0}%`;
  }, { passive: true });

  document.querySelectorAll('[data-depth]').forEach(button => button.addEventListener('click', () => {
    document.querySelector(button.dataset.depth)?.scrollIntoView({ behavior: 'smooth' });
  }));

  document.querySelector('[data-copy-citation]')?.addEventListener('click', async event => {
    const button = event.currentTarget;
    const text = button.dataset.copyCitation;
    const original = button.innerHTML;
    await navigator.clipboard.writeText(text);
    button.textContent = language === 'cn' ? '已复制引用' : 'Citation copied';
    setTimeout(() => { button.innerHTML = original; }, 1600);
  });

  const sections = [...document.querySelectorAll('.section[id]')];
  const tocLinks = [...document.querySelectorAll('.toc a')];
  if (sections.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      tocLinks.forEach(link => link.classList.toggle('active', link.hash === `#${visible.target.id}`));
    }, { rootMargin: '-18% 0px -68% 0px', threshold: [0, .2, .6] });
    sections.forEach(section => observer.observe(section));
  }
})();
