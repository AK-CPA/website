#!/usr/bin/env python3
"""Build the site from Markdown in content/ into _site/.

    python build.py            # build once
    python build.py --serve    # build, then serve on http://localhost:8000 and rebuild on change
"""

import datetime as dt
import re
import shutil
import sys
from itertools import groupby
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "_site"

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)


def read_markdown(path):
    """Return (front-matter dict, rendered HTML) for a Markdown file."""
    text = path.read_text(encoding="utf-8")
    meta = {}
    m = FRONT_MATTER.match(text)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        text = text[m.end():]
    html = markdown.markdown(text, extensions=["smarty", "sane_lists"])
    return meta, html


def inline_markdown(text):
    """Render a one-line Markdown string (e.g. a front-matter field) without a <p> wrapper."""
    html = markdown.markdown(str(text), extensions=["smarty"])
    return re.sub(r"^<p>(.*)</p>$", r"\1", html, flags=re.S)


def load_collection(folder, url_prefix):
    items = []
    for path in sorted((CONTENT / folder).glob("*.md")):
        meta, html = read_markdown(path)
        if meta.get("draft"):
            continue
        slug = meta.get("slug") or path.stem
        items.append({**meta, "slug": slug, "url": f"/{url_prefix}/{slug}/", "content": html})
    return items


def as_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def write(rel_path, html):
    dest = OUT / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def build():
    site = yaml.safe_load((CONTENT / "site.yml").read_text(encoding="utf-8"))
    site["url"] = site.get("url", "").rstrip("/")

    # Home-page sections: each Markdown file in content/home/ is one block of text.
    home = {}
    for path in (CONTENT / "home").glob("*.md"):
        meta, html = read_markdown(path)
        if not meta.get("draft"):
            home[path.stem] = {**meta, "content": html}

    posts = load_collection("posts", "writing")
    for p in posts:
        p["date"] = as_date(p["date"])
    posts.sort(key=lambda p: p["date"], reverse=True)
    posts_by_year = [(year, list(group)) for year, group in groupby(posts, key=lambda p: p["date"].year)]

    books = load_collection("books", "books")
    books.sort(key=lambda b: as_date(b.get("date", "1970-01-01")), reverse=True)
    featured_books = [b for b in books if b.get("featured")] or books[:4]

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "xml"]))
    env.filters["md"] = inline_markdown
    env.filters["date"] = lambda d, fmt="%B %-d, %Y": d.strftime(fmt)
    env.globals.update(site=site, now=dt.datetime.now(dt.timezone.utc))

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)

    def render(template, rel_path, **ctx):
        write(rel_path, env.get_template(template).render(**ctx))

    render("home.html", "index.html", home=home, posts_by_year=posts_by_year, books=featured_books,
           has_more_books=len(books) > len(featured_books))
    for post in posts:
        render("post.html", f"writing/{post['slug']}/index.html", page=post)
    render("books.html", "books/index.html", books=books)
    for book in books:
        render("book.html", f"books/{book['slug']}/index.html", page=book)
    render("feed.xml", "feed.xml", posts=posts[:20])
    render("404.html", "404.html")

    if site.get("domain"):
        write("CNAME", site["domain"] + "\n")

    print(f"Built {len(posts)} posts, {len(books)} book reviews -> {OUT.relative_to(ROOT)}/")


def serve(port=8000):
    import functools
    import http.server
    import threading
    import time

    def snapshot():
        watched = [CONTENT, TEMPLATES, STATIC, Path(__file__)]
        files = [p for d in watched for p in ([d] if d.is_file() else d.rglob("*")) if p.is_file()]
        return {p: p.stat().st_mtime for p in files}

    def watch():
        last = snapshot()
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != last:
                last = current
                try:
                    build()
                except Exception as e:  # keep serving if a file is mid-edit
                    print(f"Build failed: {e}")

    threading.Thread(target=watch, daemon=True).start()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"Serving on http://localhost:{port} (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("", port), handler).serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
