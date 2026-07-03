#!/usr/bin/env python3
"""Static site builder for zehaojin.com — SEO/GEO-friendly blog pre-rendering.

For every post listed in contents/blog/posts.json this script:

  * renders the Chinese and English Markdown to HTML at build time,
  * writes a static page at  blog/<slug>/index.html  with real, crawlable
    content and fully baked <title>, meta description, Open Graph / Twitter
    cards and JSON-LD (so search engines AND non-JS social scrapers such as
    WeChat, X/Twitter, LinkedIn and Slack get correct titles and previews),
  * pre-renders the blog listing at  blog/index.html  with every post card
    baked in (both languages) plus tag chips and a search box; the JS layer
    only filters/paginates what is already in the HTML,
  * writes llms.txt (site overview for LLM crawlers) and llms-full.txt
    (the complete Markdown of every post) at the site root — GEO,
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
from collections import Counter
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote

import markdown

BASE_URL = "https://zehaojin.com"
ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / "contents" / "blog" / "posts.json"
BLOG_MD_DIR = ROOT / "contents" / "blog"
BLOG_OUT_DIR = ROOT / "blog"
SITEMAP_OUT = ROOT / "sitemap.xml"
FEED_OUT = BLOG_OUT_DIR / "feed.xml"
INDEX_OUT = BLOG_OUT_DIR / "index.html"
LLMS_OUT = ROOT / "llms.txt"
LLMS_FULL_OUT = ROOT / "llms-full.txt"

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
    tag_links = "".join(
        f'<a class="tag" href="/blog/?lang={lang}&amp;tag={quote(t)}">{esc(t)}</a>'
        for t in tags
    )
    foot = (
        '<div class="post-foot fade-up">'
        + (f'<div class="post-tags">{tag_links}</div>' if tag_links else "")
        + '<div class="row">'
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
  <script type="application/ld+json">{{JSON_LD_BREADCRUMB}}</script>

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
  <div class="desk">
    <div class="window">
      <header class="titlebar">
        <a class="tb-brand" href="/blog/"><span class="dot"></span><span>ZEHAO.LOG</span></a>
        <nav class="tb-nav">
          <a href="/" id="nav-home">Homepage</a>
          <button class="px-btn" id="lang-toggle" type="button" aria-label="Switch language"></button>
        </nav>
      </header>

      <div class="win-body">
        <main class="post-pane">
          <article id="article">
{{ARTICLES}}
          </article>
        </main>
      </div>

      <footer class="statusbar">
        <span>{{SLUG}}.md · {{PUB_ISO}}</span>
        <span class="st-right"><span>EN/中文</span><span>© 2026 ZEHAO JIN</span></span>
      </footer>
    </div>
  </div>

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
        ld["dateModified"] = post.get("updated") or post["date"]
    if tags_primary:
        ld["keywords"] = ", ".join(tags_primary)
    json_ld = json.dumps(ld, ensure_ascii=False)

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE_URL}/blog/"},
            {"@type": "ListItem", "position": 3, "name": pick(post["title"], primary), "item": canonical},
        ],
    }
    json_ld_breadcrumb = json.dumps(breadcrumb, ensure_ascii=False)

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
        "{{SLUG}}": esc(slug),
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
        "{{JSON_LD_BREADCRUMB}}": json_ld_breadcrumb,
        "{{POST_META}}": post_meta_json,
        "{{ARTICLES}}": articles_html,
    }
    for token, value in replacements.items():
        page = page.replace(token, value)

    out_dir = BLOG_OUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Blog index (pre-rendered listing: cards, tag chips, search — SEO-crawlable)
# --------------------------------------------------------------------------- #
UI = {
    "en": {"all": "All", "search_ph": "Search title, summary, tags…",
           "more": "More ▾", "less": "Less ▴"},
    "cn": {"all": "全部", "search_ph": "搜索标题、摘要、标签…",
           "more": "更多 ▾", "less": "收起 ▴"},
}
CHIPS_VISIBLE = 12  # incl. the "All" chip; the rest fold behind a More toggle


def raw_tags(post: dict, lang: str) -> list[str]:
    return (post.get("tags") or {}).get(lang) or []


def tag_stats(posts: list[dict], lang: str) -> list[tuple[str, int]]:
    """(tag, count) sorted by frequency then name; case-insensitive merge."""
    counts: Counter[str] = Counter()
    display: dict[str, str] = {}
    for p in posts:
        for t in pick_list(p.get("tags"), lang):
            key = t.strip().lower()
            counts[key] += 1
            display.setdefault(key, t.strip())
    return sorted(
        ((display[k], n) for k, n in counts.items()),
        key=lambda x: (-x[1], x[0]),
    )


def tag_translation_map(posts: list[dict]) -> dict:
    """tags.cn[i] ↔ tags.en[i] are parallel; build a lookup so the client can
    carry an active tag filter across a language switch."""
    en2cn: dict[str, str] = {}
    cn2en: dict[str, str] = {}
    for p in posts:
        ens, cns = raw_tags(p, "en"), raw_tags(p, "cn")
        for a, b in zip(ens, cns):
            en2cn[a] = b
            cn2en[b] = a
    return {"en": en2cn, "cn": cn2en}


def fmt_entry_date(iso: str) -> str:
    """MM.DD — the year lives in the group heading; digits suit the pixel font."""
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
    except (TypeError, ValueError):
        return iso or ""
    return f"{d.month:02d}.{d.day:02d}"


def build_index_entry(post: dict, lang: str) -> str:
    slug = post["slug"]
    title = pick(post["title"], lang)
    summary = pick(post.get("summary"), lang)
    tags = pick_list(post.get("tags"), lang)
    href = f"/blog/{quote(slug)}/?lang={lang}"

    # Search blob spans BOTH languages so "philosophy" finds 哲学 posts too.
    blob_parts: list[str] = []
    for l in LANGS:
        blob_parts.append(pick(post["title"], l))
        blob_parts.append(pick(post.get("summary"), l))
        blob_parts.extend(raw_tags(post, l))
    blob = " ".join(blob_parts).lower()

    tag_line = ""
    if tags:
        tag_line = '<span class="entry-tags">' + " ".join(
            f"#{esc(t)}" for t in tags
        ) + "</span>"

    return (
        f'<a class="post-entry" href="{href}" data-slug="{esc(slug)}"'
        f' data-tags="{esc("|".join(t.lower() for t in tags))}"'
        f' data-search="{esc(blob)}">'
        '<span class="entry-top">'
        f'<span class="entry-date">{esc(fmt_entry_date(post.get("date", "")))}</span>'
        f'<span class="entry-title">{esc(title)}</span>'
        "</span>"
        + (f'<span class="entry-summary">{esc(summary)}</span>' if summary else "")
        + tag_line
        + "</a>"
    )


def build_index_list(posts: list[dict], lang: str) -> str:
    """Year-grouped timeline (posts arrive sorted newest-first)."""
    groups: dict[str, list[str]] = {}
    order: list[str] = []
    for p in posts:
        year = (p.get("date") or "")[:4] or "unknown"
        if year not in groups:
            groups[year] = []
            order.append(year)
        groups[year].append(build_index_entry(p, lang))
    sections = []
    for year in order:
        sections.append(
            f'<section class="year-group"><h2 class="year-head">{esc(year)}</h2>\n'
            '<div class="year-entries">\n'
            + "\n".join(groups[year])
            + "\n</div></section>"
        )
    return "\n".join(sections)


def build_chip_row(posts: list[dict], lang: str, hidden: bool) -> str:
    chips = [
        f'<button type="button" class="chip is-active" data-tag="">{UI[lang]["all"]}</button>'
    ]
    for tag, n in tag_stats(posts, lang):
        chips.append(
            f'<button type="button" class="chip" data-tag="{esc(tag.lower())}">'
            f'{esc(tag)}<span class="count">{n}</span></button>'
        )
    row_cls = "tag-row"
    if len(chips) > CHIPS_VISIBLE:
        row_cls += " collapsed"
        chips.append(
            '<button type="button" class="chip chip-more" data-more'
            f' data-label-more="{esc(UI[lang]["more"])}"'
            f' data-label-less="{esc(UI[lang]["less"])}">{UI[lang]["more"]}</button>'
        )
    h = " hidden" if hidden else ""
    return f'<div class="{row_cls}" data-lang="{lang}"{h}>' + "".join(chips) + "</div>"


INDEX_TEMPLATE = """<!DOCTYPE html>
<!-- GENERATED by tools/build.py — do not edit by hand. -->
<html lang="en">
<head>
  <!-- Redirect legacy GitHub Pages host to the canonical domain, preserving path -->
  <script>(function(){if(location.hostname==='lunamos.github.io'){location.replace('https://zehaojin.com'+location.pathname+location.search+location.hash);}})();</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title id="page-title">Blog · Zehao Jin</title>
  <meta name="description" id="meta-desc" content="Essays and notes by Zehao Jin (金泽昊) — on AI, neuroscience, literature, and life. Bilingual: English / 中文." />
  <meta name="author" content="Zehao Jin" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <link rel="canonical" href="https://zehaojin.com/blog/" />
  <link rel="alternate" hreflang="en" href="https://zehaojin.com/blog/?lang=en" />
  <link rel="alternate" hreflang="zh-Hans" href="https://zehaojin.com/blog/?lang=cn" />
  <link rel="alternate" hreflang="x-default" href="https://zehaojin.com/blog/" />
  <link rel="alternate" type="application/rss+xml" title="Zehao Jin · Blog" href="/blog/feed.xml" />
  <link rel="icon" type="image/x-icon" href="/static/assets/jzh.ico" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Zehao Jin · Blog" />
  <meta property="og:title" content="Blog · Zehao Jin (金泽昊)" />
  <meta property="og:description" content="Essays and notes on AI, neuroscience, literature, and life. Bilingual EN / 中文." />
  <meta property="og:url" content="https://zehaojin.com/blog/" />
  <meta property="og:image" content="https://zehaojin.com/static/assets/img/jzh.jpg" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:locale:alternate" content="zh_CN" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="Blog · Zehao Jin (金泽昊)" />
  <meta name="twitter:description" content="Essays and notes on AI, neuroscience, literature, and life. Bilingual EN / 中文." />
  <meta name="twitter:image" content="https://zehaojin.com/static/assets/img/jzh.jpg" />

  <!-- Structured data (baked at build time) -->
  <script type="application/ld+json">{{JSON_LD}}</script>

  <link rel="stylesheet" href="/static/css/blog.css" />

  <!-- Google Analytics (shared with the main site) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-6RTHNRCWR2"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-6RTHNRCWR2');
  </script>
</head>
<body class="blog blog-list">
  <div class="desk">
    <div class="window">
      <header class="titlebar">
        <a class="tb-brand" href="/blog/"><span class="dot"></span><span>ZEHAO.LOG</span></a>
        <nav class="tb-nav">
          <a href="/" id="nav-home">Homepage</a>
          <button class="px-btn" id="lang-toggle" type="button" aria-label="Switch language"></button>
        </nav>
      </header>

      <div class="win-body">
        <aside class="rail">
          <div class="rail-sticky">
            <span class="kicker">C:\ZEHAOJIN\BLOG&gt;<span class="cursor" aria-hidden="true"></span></span>
            <h1 id="hero-title">Writing</h1>
            <p class="sub" id="hero-sub"></p>

            <div class="rail-block">
              <p class="rail-label" id="label-search">SEARCH</p>
              <div class="searchwrap">
                <svg class="s-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg>
                <input type="search" id="post-search" placeholder="Search…" autocomplete="off" aria-label="Search posts" />
                <button type="button" id="search-clear" class="s-clear" aria-label="Clear search" hidden>×</button>
              </div>
            </div>

            <div class="rail-block">
              <p class="rail-label" id="label-tags">TAGS</p>
{{CHIP_ROWS}}
            </div>

            <div class="rail-block">
              <p class="rail-label">LINKS</p>
              <nav class="rail-nav">
                <a href="/" id="rail-home">Academic homepage</a>
                <a href="https://github.com/lunamos">GitHub</a>
                <a href="/blog/feed.xml">RSS</a>
                <a href="/llms.txt">llms.txt</a>
              </nav>
            </div>
          </div>
        </aside>

        <main class="main-pane">
{{POST_LISTS}}
          <div class="empty" id="no-results" hidden></div>
        </main>
      </div>

      <footer class="statusbar">
        <span id="status-note">READY · {{POST_COUNT}} POSTS</span>
        <span class="st-right"><span>EN/中文</span><span>© 2026 ZEHAO JIN</span></span>
      </footer>
    </div>
  </div>

  <script type="application/json" id="tag-map">{{TAG_MAP}}</script>
  <script type="application/json" id="ui-strings">{{UI_STRINGS}}</script>
  <script src="/static/js/blog-i18n.js"></script>
  <script src="/static/js/blog-list.js"></script>
</body>
</html>
"""


def build_blog_index(posts: list[dict]) -> None:
    lists = []
    for lang in LANGS:
        body = build_index_list(posts, lang)
        hidden = "" if lang == "en" else " hidden"
        lists.append(
            f'    <div class="post-list" data-lang="{lang}"{hidden}>\n{body}\n    </div>'
        )
    chip_rows = "\n".join(
        build_chip_row(posts, lang, hidden=(lang != "en")) for lang in LANGS
    )

    ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Zehao Jin · Blog",
        "url": f"{BASE_URL}/blog/",
        "inLanguage": ["en", "zh-CN"],
        "author": {"@type": "Person", "name": "Zehao Jin", "url": f"{BASE_URL}/"},
        "description": "Essays and notes by Zehao Jin (金泽昊) on AI, neuroscience, literature, and life.",
        "blogPost": [
            {
                "@type": "BlogPosting",
                "headline": pick(p["title"], "en"),
                "url": f"{BASE_URL}/blog/{p['slug']}/",
                "datePublished": p.get("date", ""),
                "keywords": ", ".join(pick_list(p.get("tags"), "en")),
            }
            for p in posts
        ],
    }

    page = INDEX_TEMPLATE
    for token, value in {
        "{{JSON_LD}}": json.dumps(ld, ensure_ascii=False),
        "{{CHIP_ROWS}}": chip_rows,
        "{{POST_LISTS}}": "\n".join(lists),
        "{{POST_COUNT}}": str(len(posts)),
        "{{TAG_MAP}}": json.dumps(tag_translation_map(posts), ensure_ascii=False),
        "{{UI_STRINGS}}": json.dumps(UI, ensure_ascii=False),
    }.items():
        page = page.replace(token, value)
    INDEX_OUT.write_text(page, encoding="utf-8")


# --------------------------------------------------------------------------- #
# llms.txt / llms-full.txt — GEO: a site overview + full content for LLMs
# --------------------------------------------------------------------------- #
LLMS_INTRO = """# Zehao Jin (金泽昊)

> Personal website and bilingual (English / 简体中文) blog of Zehao Jin (金泽昊),
> an M.S. student in Computational Science and Engineering at Georgia Tech who
> researches the alignment of large language models — mechanistic
> interpretability, safety alignment, AI agents, and harness engineering
> ("the neuroscience of LLMs").

Zehao Jin is advised by Prof. Chao Zhang at Georgia Tech and received his B.S.
from Tsinghua University (Xingjian College) in 2025, where he worked with
Prof. Yanan Sui. He has interned with the foundation-model teams at StepFun and
Meituan LongCat. His blog collects essays on AI, neuroscience, philosophy,
literature, and life; every post is available in both English and Chinese.

## Pages

- [Homepage](https://zehaojin.com/): bio, news, experience, publications, awards
- [Blog index](https://zehaojin.com/blog/): all essays, with tags and search
- [RSS feed](https://zehaojin.com/blog/feed.xml)
- [CV, English (PDF)](https://zehaojin.com/docs/CV_Zehao_Jin_EN.pdf)
- [CV, Chinese (PDF)](https://zehaojin.com/docs/CV_Zehao_Jin_CN.pdf)

## Contact & profiles

- Email: lunamos.thu@gmail.com
- GitHub: https://github.com/lunamos
- Google Scholar: https://scholar.google.com/citations?user=C2givFIAAAAJ
- LinkedIn: https://www.linkedin.com/in/zehaojin
- Hugging Face: https://huggingface.co/Lunamos
"""


def build_llms_txt(posts: list[dict]) -> str:
    lines = [LLMS_INTRO, "## Blog posts (newest first)", ""]
    for p in posts:
        url = f"{BASE_URL}/blog/{p['slug']}/"
        title_en = pick(p["title"], "en")
        title_cn = pick(p["title"], "cn")
        summary = pick(p.get("summary"), "en")
        tags = ", ".join(pick_list(p.get("tags"), "en"))
        title = title_en if title_en == title_cn else f"{title_en} / {title_cn}"
        lines.append(f"- [{title}]({url}) ({p.get('date', '')}): {summary}"
                     + (f" [Tags: {tags}]" if tags else ""))
    lines += [
        "",
        "## Full content",
        "",
        f"- [llms-full.txt]({BASE_URL}/llms-full.txt): complete Markdown text of"
        " every blog post, both languages",
        f"- Per-post raw Markdown: {BASE_URL}/contents/blog/<slug>.en.md and"
        f" {BASE_URL}/contents/blog/<slug>.cn.md",
        "",
    ]
    return "\n".join(lines)


def build_llms_full_txt(posts: list[dict]) -> str:
    chunks = [
        "# Zehao Jin (金泽昊) — full blog content",
        "",
        "Every post from https://zehaojin.com/blog/ in Markdown, newest first.",
        "Each post appears in English and then in Chinese (both written by the author).",
        "",
    ]
    for p in posts:
        url = f"{BASE_URL}/blog/{p['slug']}/"
        chunks += ["", "---", ""]
        chunks.append(f"# {pick(p['title'], 'en')}")
        chunks.append("")
        chunks.append(f"- URL: {url}")
        chunks.append(f"- Date: {p.get('date', '')}")
        tags = ", ".join(pick_list(p.get("tags"), "en"))
        if tags:
            chunks.append(f"- Tags: {tags}")
        for lang, label in (("en", "English version"), ("cn", "中文版")):
            md_path = BLOG_MD_DIR / f"{p['slug']}.{lang}.md"
            if not md_path.exists():
                continue
            chunks += ["", f"## {label} · {pick(p['title'], lang)}", ""]
            chunks.append(md_path.read_text(encoding="utf-8").strip())
    chunks.append("")
    return "\n".join(chunks)


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
        lastmod = p.get("updated") or p.get("date", today)
        entries.append(url_entry(loc, lastmod, "yearly", "0.6", True))

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

    build_blog_index(posts)
    print(f"Wrote {INDEX_OUT.relative_to(ROOT)} (pre-rendered listing, {len(posts)} posts × {len(LANGS)} languages)")

    SITEMAP_OUT.write_text(build_sitemap(posts), encoding="utf-8")
    print(f"Wrote {SITEMAP_OUT.relative_to(ROOT)} ({SITEMAP_OUT.read_text().count('<url>')} URLs)")

    FEED_OUT.write_text(build_feed(posts), encoding="utf-8")
    print(f"Wrote {FEED_OUT.relative_to(ROOT)} ({len(posts)} items)")

    LLMS_OUT.write_text(build_llms_txt(posts), encoding="utf-8")
    LLMS_FULL_OUT.write_text(build_llms_full_txt(posts), encoding="utf-8")
    print(f"Wrote llms.txt ({LLMS_OUT.stat().st_size // 1024} KB) and "
          f"llms-full.txt ({LLMS_FULL_OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
