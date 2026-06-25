# zehaojin.com

Personal academic homepage and blog of Zehao Jin (金泽昊) — [zehaojin.com](https://zehaojin.com)

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
  meta description, Open Graph / Twitter cards, JSON-LD, and the article text
  (both languages embedded; the in-page toggle just switches which is shown).
- `sitemap.xml` — clean post URLs with `hreflang` language alternates.
- `blog/feed.xml` — an RSS 2.0 feed for the blog.

Legacy `blog/post.html?slug=<slug>` links redirect to the new `/blog/<slug>/` URLs.
