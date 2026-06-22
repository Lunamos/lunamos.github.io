#!/usr/bin/env python3
"""Generate sitemap.xml for zehaojin.com.

Reads the blog manifest (contents/blog/posts.json) and emits a sitemap that
covers the homepage, the blog index, and every individual blog post. Re-run
this whenever you publish a new post:

    python3 tools/generate_sitemap.py

The script is intentionally dependency-free (standard library only).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

BASE_URL = "https://zehaojin.com"
ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / "contents" / "blog" / "posts.json"
SITEMAP_OUT = ROOT / "sitemap.xml"


def load_posts() -> list[dict]:
    data = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts = data.get("posts", [])
    # newest first, matching the on-site listing order
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


def url_entry(loc: str, lastmod: str, changefreq: str, priority: str) -> str:
    return (
        "    <url>\n"
        f"        <loc>{escape(loc)}</loc>\n"
        f"        <lastmod>{lastmod}</lastmod>\n"
        f"        <changefreq>{changefreq}</changefreq>\n"
        f"        <priority>{priority}</priority>\n"
        "    </url>"
    )


def build_sitemap() -> str:
    posts = load_posts()
    today = date.today().isoformat()
    newest_post = posts[0]["date"] if posts else today

    entries = [
        url_entry(f"{BASE_URL}/", today, "monthly", "1.0"),
        url_entry(f"{BASE_URL}/blog/", newest_post, "weekly", "0.8"),
    ]

    for p in posts:
        slug = p["slug"]
        loc = f"{BASE_URL}/blog/post.html?slug={slug}"
        lastmod = p.get("date", today)
        entries.append(url_entry(loc, lastmod, "yearly", "0.6"))

    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def main() -> None:
    sitemap = build_sitemap()
    SITEMAP_OUT.write_text(sitemap, encoding="utf-8")
    n = sitemap.count("<url>")
    print(f"Wrote {SITEMAP_OUT.relative_to(ROOT)} with {n} URLs.")


if __name__ == "__main__":
    main()
