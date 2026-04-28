# GCCI — Cybercrime victim resources and reporting guidance

Source for [gcci.io](https://gcci.io). Plain HTML/CSS, no build step. Hosted on Cloudflare Pages.

## Structure

- `index.html` — homepage with the guided resource flow
- `blog/index.html` — blog index page
- `blog/<slug>/index.html` — individual blog posts
- `404.html` — fallback for missing pages

## Adding a blog post

Create a new folder under `blog/` (e.g., `blog/2026-05-01-some-topic/`) with an `index.html` inside it that follows the same template as `blog/welcome/index.html`. Then add a card linking to it in `blog/index.html` at the top of the post list.
