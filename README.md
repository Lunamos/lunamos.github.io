# zehaojin.com

Personal academic homepage and blog of Zehao Jin (金泽昊) — [zehaojin.com](https://zehaojin.com).

## Blog build step

Blog posts are authored as bilingual Markdown in `contents/blog/` (`<slug>.en.md`
and `<slug>.cn.md`) and listed in `contents/blog/posts.json`. A build script
pre-renders each post to a static, SEO-friendly page so search engines and
non-JS social scrapers (WeChat, X/Twitter, LinkedIn, Slack) see real content and
correct link previews.

After adding or editing a post (or its metadata), run:

```bash
pip install markdown      # one-time dependency
python3 tools/build.py
```

This regenerates:

- `blog/<slug>/index.html` — one static page per post, with baked-in title,
  meta description, Open Graph / Twitter cards, JSON-LD (BlogPosting +
  BreadcrumbList), and the article text (both languages embedded; the in-page
  toggle just switches which is shown).
- `blog/index.html` — the pre-rendered listing: every post entry (both
  languages), year groups, and tag chips are baked into the HTML; the JS layer
  only filters (search + tags) what is already there.
- `sitemap.xml` — clean post URLs with `hreflang` language alternates.
- `blog/feed.xml` — an RSS 2.0 feed for the blog.
- `llms.txt` / `llms-full.txt` — a site overview and the complete Markdown of
  every post, for LLM crawlers (GEO). AI crawlers are explicitly welcomed in
  `robots.txt`.

Legacy `blog/post.html?slug=<slug>` links redirect to the new `/blog/<slug>/` URLs.

## Blog design

Bones: content-first minimal blog (a centered column, a year-grouped
chronological list, instant search, quiet tags). Flavor: PC-98 / 8-bit /
lo-fi / vaporwave — warm paper + dusk indigo, cyan↔magenta accents, a pixel
font (DotGothic16) for UI labels and dates only, hard offset shadows,
checkerboard dither strips, scanlines confined to the header/footer bars.
The reading column itself stays calm; the retro layer never touches body text.
All of it lives in `static/css/blog.css` and the templates in `tools/build.py`.
