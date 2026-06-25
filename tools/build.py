#!/usr/bin/env python3
"""Static site builder for zehaojin.com — SEO-friendly blog pre-rendering.

For every post listed in contents/blog/posts.json this script:

  * renders the Chinese and English Markdown to HTML at build time,
  * writes a static page at  blog/<slug>/index.html  with real, crawlable
    content and fully baked <title>, meta description, Open Graph / Twitter
    cards and JSON-LD (so search engines AND non-JS social scrapers such as
    WeChat, X/Twitter, LinkedIn and Slack get correct titles and previews),
  * regenerates sitemap.xml (clean URLs + hreflang language alternates), and
  * regenerates blog/feed.xml (an RSS 2.0 feed for the blog).

The legacy blog/post.html?slug=... URLs keep working: post.html now redirects
to the matching clean URL.

Run after adding or editing a post:

    python3 tools/build.py

Dependencies: the third-party `markdown` package (pip install markdown).
Everything else is the Python standard library.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

import markdown

BASE_URL = "https://zehaojin.com"
ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / "contents" / "blog" / "posts.json"
BLOG_MD_DIR = ROOT / "contents" / "blog"
BLOG_OUT_DIR = ROOT / "blog"
SITEMAP_OUT = ROOT / "sitemap.xml"
FEED_OUT = BLOG_OUT_DIR / "feed.xml"

DEFAULT_IMAGE = f"{BASE_URL}/static/assets/img/jzh.jpg"
LANGS = ("en", "cn")
EN_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Private-use sentinels keep Markdown from touching protected spans.
CODE_OPEN, CODE_CLOSE = "C", "C"
MATH_OPEN, MATH_CLOSE = "M", "M"


# --------------------------------------------------------------------------- #
# Markdown rendering (math- and code-safe)
# --------------------------------------------------------------------------- #
def render_markdown(md_text: str) -> str:
    """Render Markdown to HTML while leaving TeX math untouched for MathJax.

    Order matters: protect fenced/inline code first so the math regexes never
    fire inside code, then protect $$...$$ and $...$, render, and restore math.
    Code is restored to its original Markdown *before* rendering so Markdown
    still turns it into <pre>/<code>.
    """
    code_store: list[str] = []

    def stash_code(m: re.Match) -> str:
        code_store.append(m.group(0))
        return f"{CODE_OPEN}{len(code_store) - 1}{CODE_CLOSE}"

    text = re.sub(r"```.*?```", stash_code, md_text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", stash_code, text)

    math_store: list[str] = []

    def stash_math(m: re.Match) -> str:
        math_store.append(m.group(0))
        return f"{MATH_OPEN}{len(math_store) - 1}{MATH_CLOSE}"

    text = re.sub(r"\$\$.+?\$\$", stash_math, text, flags=re.DOTALL)
    text = re.sub(r"(?<!\$)\$(?!\s)(?:\\.|[^$\\\n])+?(?<!\s)\$(?!\$)",
                  stash_math, text)

    # Restore code so Markdown renders it normally.
    text = re.sub(
        rf"{CODE_OPEN}(\d+){CODE_CLOSE}",
        lambda m: code_store[int(m.group(1))],
        text,
    )

    # marked on the site uses breaks:false, so we keep nl2br OUT to match it.
    md = markdown.Markdown(
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )
    out = md.convert(text)

    # Restore math spans verbatim for client-side MathJax.
    out = re.sub(
        rf"{MATH_OPEN}(\d+){MATH_CLOSE}",
        lambda m: math_store[int(m.group(1))],
        out,
    )
    return out


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def pick(field: dict | None, lang: str) -> str:
    if not field:
        return ""
    return field.get(lang) or field.get("cn") or field.get("en") or ""


def pick_list(field: dict | None, lang: str) -> list[str]:
    if not field:
        return []
    return field.get(lang) or field.get("cn") or field.get("en") or []


def reading_minutes(md_text: str) -> int:
    chars = len(re.sub(r"\s+", "", md_text or ""))
    return max(1, -(-chars // 900))  # ceil division


def fmt_date(iso: str, lang: str) -> str:
    if not iso:
        return ""
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
    except ValueError:
        return iso
    if lang == "cn":
        return f"{d.year}年{d.month}月{d.day}日"
    return f"{EN_MONTHS[d.month - 1]} {d.day}, {d.year}"


def first_image(html_body: str) -> str | None:
    m = re.search(r'<img[^>]+src="([^"]+)"', html_body)
    if not m:
        return None
    src = m.group(1)
    if src.startswith("http"):
        return src
    if not src.startswith("/"):
        src = "/" + src
    return BASE_URL + src


def load_posts() -> list[dict]:
    data = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts = data.get("posts", [])
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


# --------------------------------------------------------------------------- #
# Per-post page generation
# --------------------------------------------------------------------------- #
BACK_TEXT = {"en": "Back to all posts", "cn": "返回全部文章"}
MIN_LABEL = {"en": "{} min read", "cn": "{} 分钟阅读"}


def build_article_block(post: dict, lang: str, md_text: str) -> tuple[str, str | None]:
    """Return (inner_html, first_image_abs_url) for one language container."""
    title = pick(post["title"], lang)
    summary = pick(post.get("summary"), lang)
    tags = pick_list(post.get("tags"), lang)
    date_str = fmt_date(post.get("date", ""), lang)
    mins = reading_minutes(md_text)
    min_label = MIN_LABEL[lang].format(mins)
    kicker = esc(tags[0]) if tags else ""
    body = render_markdown(md_text)
    img = first_image(body)

    head = (
        '<header class="post-head fade-up">'
        + (f'<div class="kicker">{kicker}</div>' if kicker else "")
        + f"<h1>{esc(title)}</h1>"
        + '<div class="byline">'
        + (f"<span>{esc(date_str)}</span><span>·</span>" if date_str else "")
        + f"<span>{esc(min_label)}</span>"
        + "</div>"
        + '<div class="rule"></div>'
        + "</header>"
    )
    reading = f'<div class="reading prose fade-up" style="animation-delay:90ms">{body}</div>'
    foot = (
        '<div class="post-foot fade-up"><div class="row">'
        f'<a class="back-link" href="/blog/?lang={lang}">‹ {esc(BACK_TEXT[lang])}</a>'
        "</div></div>"
    )
    return head + reading + foot, img


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="{{HTML_LANG}}">
<head>
  <!-- Redirect legacy GitHub Pages host to the canonical domain, preserving path -->
  <script>(function(){if(location.hostname==='lunamos.github.io'){location.replace('https://zehaojin.com'+location.pathname+location.search+location.hash);}})();</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <title>{{TITLE}} · Zehao Jin</title>
  <meta name="description" id="meta-desc" content="{{DESC}}" />
  <meta name="author" content="Zehao Jin" />
  <meta name="keywords" content="{{KEYWORDS}}" />
  <link rel="canonical" href="{{CANONICAL}}" />
  <link rel="alternate" hreflang="en" href="{{CANONICAL}}?lang=en" />
  <link rel="alternate" hreflang="zh-Hans" href="{{CANONICAL}}?lang=cn" />
  <link rel="alternate" hreflang="x-default" href="{{CANONICAL}}" />
  <link rel="alternate" type="application/rss+xml" title="Zehao Jin · Blog" href="/blog/feed.xml" />
  <link rel="icon" type="image/x-icon" href="/static/assets/jzh.ico" />

  <!-- Open Graph -->
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Zehao Jin · Blog" />
  <meta property="og:title" content="{{TITLE}}" />
  <meta property="og:description" content="{{DESC}}" />
  <meta property="og:url" content="{{CANONICAL}}" />
  <meta property="og:image" content="{{IMAGE}}" />
  <meta property="og:locale" content="{{OG_LOCALE}}" />
  <meta property="og:locale:alternate" content="{{OG_LOCALE_ALT}}" />
  <meta property="article:published_time" content="{{PUB_ISO}}" />
  <meta property="article:author" content="Zehao Jin" />
{{ARTICLE_TAGS}}
  <!-- Twitter Card -->
  <meta name="twitter:card" content="{{TW_CARD}}" />
  <meta name="twitter:title" content="{{TITLE}}" />
  <meta name="twitter:description" content="{{DESC}}" />
  <meta name="twitter:image" content="{{IMAGE}}" />

  <!-- Per-article structured data (baked at build time) -->
  <script type="application/ld+json">{{JSON_LD}}</script>

  <link rel="stylesheet" href="/static/css/blog.css" />

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-6RTHNRCWR2"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-6RTHNRCWR2');
  </script>
</head>
<body class="blog">
  <header class="blog-header">
    <div class="wrap">
      <a class="blog-brand" href="/"><span class="dot"></span><span>Zehao Jin&nbsp;·&nbsp;金泽昊</span></a>
      <nav class="blog-nav">
        <a href="/blog/" id="nav-all">All posts</a>
        <button class="aero-btn" id="lang-toggle" type="button" aria-label="Switch language"></button>
      </nav>
    </div>
  </header>

  <main class="blog-main">
    <article id="article">
{{ARTICLES}}
    </article>
  </main>

  <footer class="blog-footer">
    <div>© Zehao Jin 2026 · <a href="/">Academic homepage</a> · <a href="https://github.com/lunamos">GitHub</a></div>
  </footer>

  <script type="application/json" id="post-meta">{{POST_META}}</script>
  <script>
    MathJax = { tex: { inlineMath: [['$', '$']], displayMath: [['$$', '$$']] }, svg: { fontCache: 'global' } };
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
  <script src="/static/js/blog-i18n.js"></script>
  <script src="/static/js/img-progressive.js"></script>
  <script src="/static/js/blog-post-static.js"></script>
</body>
</html>
"""


def build_post_page(post: dict) -> None:
    slug = post["slug"]
    canonical = f"{BASE_URL}/blog/{slug}/"

    rendered: dict[str, tuple[str, str | None]] = {}
    for lang in LANGS:
        md_path = BLOG_MD_DIR / f"{slug}.{lang}.md"
        if md_path.exists():
            rendered[lang] = build_article_block(post, lang, md_path.read_text(encoding="utf-8"))

    if not rendered:
        print(f"  ! {slug}: no Markdown found, skipping")
        return

    primary = "en" if "en" in rendered else "cn"

    # Language containers (primary visible, the other hidden but crawlable).
    containers = []
    for lang in LANGS:
        if lang in rendered:
            inner, _ = rendered[lang]
            hidden = "" if lang == primary else " hidden"
            containers.append(
                f'<div class="post-lang" data-lang="{lang}"{hidden}>{inner}</div>'
            )
    articles_html = "\n".join(containers)

    title = esc(pick(post["title"], primary))
    desc = esc(pick(post.get("summary"), primary))
    tags_primary = pick_list(post.get("tags"), primary)
    keywords = esc(", ".join(tags_primary))
    image = rendered[primary][1] or DEFAULT_IMAGE
    tw_card = "summary_large_image" if rendered[primary][1] else "summary"
    og_locale = "en_US" if primary == "en" else "zh_CN"
    og_locale_alt = "zh_CN" if primary == "en" else "en_US"
    article_tags_meta = "\n".join(
        f'  <meta property="article:tag" content="{esc(t)}" />' for t in tags_primary
    )

    # JSON-LD BlogPosting (baked).
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": pick(post["title"], primary),
        "description": pick(post.get("summary"), primary),
        "inLanguage": "en" if primary == "en" else "zh-CN",
        "url": canonical,
        "mainEntityOfPage": canonical,
        "image": image,
        "author": {"@type": "Person", "name": "Zehao Jin", "url": f"{BASE_URL}/"},
        "publisher": {"@type": "Person", "name": "Zehao Jin", "url": f"{BASE_URL}/"},
    }
    if post.get("date"):
        ld["datePublished"] = post["date"]
        ld["dateModified"] = post["date"]
    if tags_primary:
        ld["keywords"] = ", ".join(tags_primary)
    json_ld = json.dumps(ld, ensure_ascii=False)

    # Per-language meta for the in-page language toggle.
    post_meta = {
        lang: {
            "title": pick(post["title"], lang),
            "summary": pick(post.get("summary"), lang),
        }
        for lang in LANGS if lang in rendered
    }
    post_meta_json = json.dumps(post_meta, ensure_ascii=False)

    page = PAGE_TEMPLATE
    replacements = {
        "{{HTML_LANG}}": "en" if primary == "en" else "zh",
        "{{TITLE}}": title,
        "{{DESC}}": desc,
        "{{KEYWORDS}}": keywords,
        "{{CANONICAL}}": canonical,
        "{{IMAGE}}": esc(image),
        "{{OG_LOCALE}}": og_locale,
        "{{OG_LOCALE_ALT}}": og_locale_alt,
        "{{PUB_ISO}}": post.get("date", ""),
        "{{ARTICLE_TAGS}}": article_tags_meta,
        "{{TW_CARD}}": tw_card,
        "{{JSON_LD}}": json_ld,
        "{{POST_META}}": post_meta_json,
        "{{ARTICLES}}": articles_html,
    }
    for token, value in replacements.items():
        page = page.replace(token, value)

    out_dir = BLOG_OUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Sitemap (clean URLs + hreflang alternates)
# --------------------------------------------------------------------------- #
def hreflang_links(loc: str) -> str:
    base = loc.rstrip("/") + "/" if loc.endswith("/") else loc
    return (
        f'        <xhtml:link rel="alternate" hreflang="en" href="{esc(loc)}?lang=en"/>\n'
        f'        <xhtml:link rel="alternate" hreflang="zh-Hans" href="{esc(loc)}?lang=cn"/>\n'
        f'        <xhtml:link rel="alternate" hreflang="x-default" href="{esc(loc)}"/>\n'
    )


def url_entry(loc: str, lastmod: str, changefreq: str, priority: str, alts: bool) -> str:
    out = "    <url>\n"
    out += f"        <loc>{esc(loc)}</loc>\n"
    if alts:
        out += hreflang_links(loc)
    out += f"        <lastmod>{lastmod}</lastmod>\n"
    out += f"        <changefreq>{changefreq}</changefreq>\n"
    out += f"        <priority>{priority}</priority>\n"
    out += "    </url>"
    return out


def build_sitemap(posts: list[dict]) -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    newest = posts[0]["date"] if posts else today

    entries = [
        url_entry(f"{BASE_URL}/", today, "monthly", "1.0", True),
        url_entry(f"{BASE_URL}/blog/", newest, "weekly", "0.8", True),
    ]
    for p in posts:
        loc = f"{BASE_URL}/blog/{p['slug']}/"
        entries.append(url_entry(loc, p.get("date", today), "yearly", "0.6", True))

    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{body}\n"
        "</urlset>\n"
    )


# --------------------------------------------------------------------------- #
# RSS feed
# --------------------------------------------------------------------------- #
def rss_date(iso: str) -> str:
    try:
        d = datetime.strptime(iso, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        d = datetime.now(timezone.utc)
    return format_datetime(d)


def build_feed(posts: list[dict]) -> str:
    newest = rss_date(posts[0]["date"]) if posts else format_datetime(datetime.now(timezone.utc))
    items = []
    for p in posts:
        loc = f"{BASE_URL}/blog/{p['slug']}/"
        title = pick(p["title"], "en")
        summary = pick(p.get("summary"), "en")
        cats = "".join(
            f"\n      <category>{esc(c)}</category>" for c in pick_list(p.get("tags"), "en")
        )
        items.append(
            "    <item>\n"
            f"      <title>{esc(title)}</title>\n"
            f"      <link>{esc(loc)}</link>\n"
            f'      <guid isPermaLink="true">{esc(loc)}</guid>\n'
            f"      <pubDate>{rss_date(p.get('date', ''))}</pubDate>\n"
            f"      <description>{esc(summary)}</description>"
            f"{cats}\n"
            "    </item>"
        )
    items_xml = "\n".join(items)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Zehao Jin · Blog</title>\n"
        f"    <link>{BASE_URL}/blog/</link>\n"
        f'    <atom:link href="{BASE_URL}/blog/feed.xml" rel="self" type="application/rss+xml"/>\n'
        "    <description>Essays and notes by Zehao Jin (金泽昊) on AI, neuroscience, "
        "literature, and life.</description>\n"
        "    <language>en</language>\n"
        f"    <lastBuildDate>{newest}</lastBuildDate>\n"
        f"{items_xml}\n"
        "  </channel>\n"
        "</rss>\n"
    )


# --------------------------------------------------------------------------- #
def main() -> None:
    posts = load_posts()

    print(f"Rendering {len(posts)} blog posts → blog/<slug>/index.html")
    for p in posts:
        build_post_page(p)

    SITEMAP_OUT.write_text(build_sitemap(posts), encoding="utf-8")
    print(f"Wrote {SITEMAP_OUT.relative_to(ROOT)} ({SITEMAP_OUT.read_text().count('<url>')} URLs)")

    FEED_OUT.write_text(build_feed(posts), encoding="utf-8")
    print(f"Wrote {FEED_OUT.relative_to(ROOT)} ({len(posts)} items)")


if __name__ == "__main__":
    main()
