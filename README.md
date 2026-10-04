# kornrei.ch

Personal site. All the text lives in Markdown files under `content/`; `build.py` turns them into static HTML in `_site/`.

## Editing content

| What | Where |
| --- | --- |
| Name, page title, domain, newsletter link | `content/site.yml` |
| "Some things about me" | `content/home/about.md` |
| "Some things I believe" (set `draft: true` to hide) | `content/home/beliefs.md` |
| Writing — one file per post | `content/posts/*.md` |
| Book reviews — one file per book | `content/books/*.md` |
| Book reviews heading/intro | `content/home/books.md` |
| Projects list | `content/home/projects.md` (front matter) |
| Contact | `content/home/contact.md` |

### New post

Create `content/posts/my-post.md`:

```markdown
---
title: My post
date: 2026-10-04
---
Write in Markdown here.
```

It shows up on the home page under its year and at `/writing/my-post/`, and in the RSS feed at `/feed.xml`. Add `draft: true` to keep it unpublished.

### New book review

Create `content/books/some-book.md`:

```markdown
---
title: Some Book
author: Some Author
rating: 4
date: 2026-10-04     # used for ordering, newest first
note: One-line take shown in the list.
featured: true       # optional; if any book is featured, only featured ones show on the home page
---
Optional longer review, shown on /books/some-book/.
```

## Running locally

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py --serve     # http://localhost:8000, rebuilds when files change
```

## Deploying

Every push to `main` builds the site and publishes it to GitHub Pages via `.github/workflows/deploy.yml`.
