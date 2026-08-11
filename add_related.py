#!/usr/bin/env python3
"""Add a topic-clustered 'Related reading' block to every GCCI blog post.
Idempotent: re-running updates the block instead of duplicating it.
Run from the repo root:  python3 add_related.py
"""
import os, re, glob, html
from collections import defaultdict

POSTS = "blog"
START = "<!-- RELATED-POSTS:START (auto-generated) -->"
END   = "<!-- RELATED-POSTS:END -->"
N_LINKS = 4

# When a category has too few siblings, borrow from these adjacent topics.
ADJ = {
    "Sextortion":          ["Online harassment", "Impersonation", "Account takeover"],
    "Online harassment":   ["Sextortion", "Impersonation", "Identity theft"],
    "Impersonation":       ["Identity theft", "Impersonation scam", "Online harassment"],
    "Impersonation scam":  ["Impersonation", "Scam alert", "Identity theft"],
    "Identity theft":      ["Impersonation", "Account takeover", "Scam alert"],
    "Account takeover":    ["Identity theft", "Impersonation", "Sextortion"],
    "Crypto fraud":        ["Scam alert", "Impersonation scam"],
    "Tech support scam":   ["Scam alert", "Account takeover"],
    "Scam alert":          ["Impersonation scam", "Crypto fraud", "Tech support scam"],
}

def rd(f):
    with open(f, encoding="utf-8") as h: return h.read()
def wr(f, c):
    with open(f, "w", encoding="utf-8") as h: h.write(c)

# ---- collect posts ----
posts = {}
for f in sorted(glob.glob(f"{POSTS}/*/index.html")):
    slug = os.path.basename(os.path.dirname(f))
    c = rd(f)
    tm = re.search(r'og:title"\s+content="([^"]+)"', c) or re.search(r"<h1>([^<]+)</h1>", c)
    title = html.unescape(tm.group(1).strip()) if tm else slug
    cm = re.search(r'class="post-meta">([^<]*)</div>', c)
    cat = ""
    if cm:
        parts = re.split(r'&middot;|·|&#183;', cm.group(1))
        if len(parts) > 1:
            cat = html.unescape(parts[-1].strip())
    posts[slug] = dict(slug=slug, title=title, cat=cat, raw=c, file=f)

articles = {s: p for s, p in posts.items() if p["cat"]}
bycat = defaultdict(list)
for p in articles.values():
    bycat[p["cat"]].append(p["slug"])

def related(slug):
    cat = articles[slug]["cat"]
    out = [s for s in bycat[cat] if s != slug]
    for a in ADJ.get(cat, []):
        for s in bycat.get(a, []):
            if s != slug and s not in out: out.append(s)
    for s in articles:                       # last-resort fill
        if s != slug and s not in out: out.append(s)
    return out[:N_LINKS]

CSS = (
'<style>'
'.related-posts{margin:44px 0 4px;padding-top:26px;border-top:1px solid rgba(255,255,255,.12)}'
'.related-posts h2{font-size:12px;text-transform:uppercase;letter-spacing:.14em;color:var(--muted,#9a958c);margin:0 0 16px;font-weight:700}'
'.related-posts ul{list-style:none;margin:0;padding:0;display:grid;gap:10px}'
'@media(min-width:640px){.related-posts ul{grid-template-columns:1fr 1fr}}'
'.related-posts a{display:block;text-decoration:none;color:inherit;padding:13px 15px;border:1px solid rgba(255,255,255,.10);border-radius:11px;transition:border-color .15s}'
'.related-posts a:hover{border-color:var(--accent,#d6a14a)}'
'.related-posts .rp-cat{display:block;font-size:10.5px;text-transform:uppercase;letter-spacing:.12em;color:var(--accent,#d6a14a);margin-bottom:5px}'
'.related-posts .rp-title{font-size:15px;line-height:1.35}'
'</style>'
)

def block(slug):
    lis = "\n".join(
        f'            <li><a href="/blog/{s}/"><span class="rp-cat">{html.escape(articles[s]["cat"])}</span>'
        f'<span class="rp-title">{html.escape(articles[s]["title"])}</span></a></li>'
        for s in related(slug)
    )
    return (
        f"{START}\n        {CSS}\n"
        f'        <nav class="related-posts" aria-label="Related articles">\n'
        f"          <h2>Related reading</h2>\n"
        f"          <ul>\n{lis}\n          </ul>\n"
        f"        </nav>\n        {END}"
    )

# ---- inject ----
changed = 0
for slug, p in articles.items():
    c = p["raw"]
    c = re.sub(re.escape(START) + r".*?" + re.escape(END), "", c, flags=re.S)  # strip old block
    nav = '<div class="post-footer-nav">'
    if nav not in c:
        print("!! no footer-nav in", slug); continue
    c = c.replace(nav, block(slug) + "\n\n        " + nav, 1)
    wr(p["file"], c)
    changed += 1

print(f"Updated {changed} posts across {len(bycat)} categories.")
for cat in sorted(bycat): print(f"  {cat}: {len(bycat[cat])} posts")
