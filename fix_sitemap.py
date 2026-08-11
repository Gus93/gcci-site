#!/usr/bin/env python3
"""Add any blog posts missing from sitemap.xml. Idempotent."""
import re, glob, os
sm = open("sitemap.xml", encoding="utf-8").read()
present = set(re.findall(r'<loc>(https://gcci\.io/blog/[a-z0-9-]+/)</loc>', sm))
MONTHS = {m:i for i,m in enumerate(
  ["January","February","March","April","May","June","July","August",
   "September","October","November","December"],1)}
def post_date(html):
    m = re.search(r'class="post-meta">([^<&]+)', html)
    if m:
        dm = re.search(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', m.group(1))
        if dm and dm.group(1) in MONTHS:
            return f"{dm.group(3)}-{MONTHS[dm.group(1)]:02d}-{int(dm.group(2)):02d}"
    return "2026-08-01"
new = []
for f in sorted(glob.glob("blog/*/index.html")):
    slug = os.path.basename(os.path.dirname(f))
    url = f"https://gcci.io/blog/{slug}/"
    if url in present: continue
    d = post_date(open(f, encoding="utf-8").read())
    new.append(f'  <url><loc>{url}</loc><lastmod>{d}</lastmod><changefreq>yearly</changefreq><priority>0.7</priority></url>')
if new:
    sm = sm.replace("</urlset>", "\n".join(new) + "\n</urlset>")
    open("sitemap.xml","w",encoding="utf-8").write(sm)
print(f"Added {len(new)} missing posts. Sitemap now lists {sm.count('<loc>')} URLs.")
