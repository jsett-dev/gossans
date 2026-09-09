#!/usr/bin/env python3
"""Renders the secondary pages of www.gossans.com.

The home page stays hand-written. It is also the single source of truth for
the look: this script lifts the font links, the stylesheet and the theme
toggle straight out of public/index.html, so a generated page cannot drift
away from the design.

Output is committed. Cloudflare serves public/ as plain files and runs no
build command, so a mistake in here can never take the site down at deploy
time. Run it after editing tools/pages.py:

    python tools/build.py
"""

import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
HOME = PUBLIC / "index.html"
SITE = "https://www.gossans.com"


def read(path):
    return io.open(path, encoding="utf-8").read()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


def borrow_from_home():
    """Pull the shared head furniture out of the hand-written home page."""
    home = read(HOME)
    fonts = re.search(r'<link rel="preconnect".*?family=Archivo.*?>', home, re.S).group(0)
    style = re.search(r"<style>.*?</style>", home, re.S).group(0)
    script = re.search(r"<script>.*?</script>", home, re.S).group(0)
    return fonts, style, script


FONTS, STYLE, SCRIPT = borrow_from_home()

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{site}{url}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Gossans">
<meta property="og:url" content="{site}{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{site}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{site}/og-image.png">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">

<meta name="theme-color" content="#f1f2ef" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14181a" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">

{fonts}

{style}{schema}
</head>
<body>
<div class="sheet">

  <header class="plate">
    <div class="masthead">
      <div class="wordmark">
        <a class="home" href="/">
          <span class="sq" aria-hidden="true"></span>
          <span class="name">Gossans</span>
        </a>
        <span class="kicker">{kicker}</span>
      </div>
      <nav class="topnav">
        <a href="/findings/">Findings</a>
        <a href="/about/">About</a>
        <a href="/contact/">Contact</a>
      </nav>
    </div>
  </header>
"""

FOOT = """
  <div class="block" style="border-top:none; padding-top: 8px;">
    <div class="rail"><b>Next</b><span>Start here</span></div>
    <div class="col">
      <div class="cta">
        <div>
          <h2>Send us one asset and two spreadsheets.</h2>
          <p>
            The Asset Health Check is the cheapest possible way to find out
            whether we are worth the larger engagement. Two weeks, fixed fee,
            and a written answer either way.
          </p>
        </div>
        <a class="btn" href="/contact/">Book a scoping call</a>
      </div>
    </div>
  </div>

  <footer class="colophon">
    <span>Gossans &middot; Extraction economics and production optimisation</span>
    <button class="theme-btn" type="button" id="theme">Light / dark</button>
  </footer>

</div>

{script}
</body>
</html>
"""

# Styles the home page has no need for: an article measure, an index list and
# prev/next links. The navigation styles live in the home page's own stylesheet,
# because that is what borrow_from_home() lifts.
EXTRA_CSS = """
<style>
.crumb { font-family:var(--f-data); font-size:11px; letter-spacing:.14em;
         text-transform:uppercase; color:var(--ink-3); margin-bottom:16px; }
.crumb a { color:var(--ink-3); }
.crumb a:hover { color:var(--rust); }
.article h1 { max-width:24ch; }
.standfirst { font-size:19px; line-height:1.55; color:var(--ink-2);
              max-width:60ch; margin:0 0 4px; }
.costline { font-family:var(--f-data); font-size:13px; line-height:1.75;
            color:var(--rust); border-left:2px solid var(--rust);
            padding:12px 0 12px 18px; margin:28px 0; }
.indexlist a.row { display:grid; grid-template-columns:3rem 1fr auto; gap:18px;
                   align-items:baseline; padding:22px 0;
                   border-top:1px solid var(--rule-2); text-decoration:none;
                   color:inherit; }
.indexlist a.row:hover h3 { color:var(--rust); }
.indexlist .num { font-family:var(--f-data); font-size:12px; color:var(--ink-3); }
.indexlist h3 { margin:0 0 6px; }
.indexlist p { margin:0; color:var(--ink-2); max-width:62ch; }
.indexlist .tag { font-family:var(--f-data); font-size:11px; color:var(--ink-3);
                  letter-spacing:.1em; text-transform:uppercase; white-space:nowrap; }
.pager { display:flex; justify-content:space-between; gap:24px; margin-top:36px;
         padding-top:20px; border-top:1px solid var(--rule-2);
         font-family:var(--f-data); font-size:12px; line-height:1.6; }
.pager a { color:var(--ink-2); text-decoration:none; max-width:46%; }
.pager a:hover { color:var(--rust); }
.pager .dir { display:block; color:var(--ink-3); letter-spacing:.12em;
              text-transform:uppercase; font-size:10px; margin-bottom:4px; }
@media (max-width:700px) {
  .indexlist a.row { grid-template-columns:2rem 1fr; }
  .indexlist .tag { display:none; }
}
</style>"""


def render(page):
    schema = ""
    if page.get("schema"):
        schema = '\n<script type="application/ld+json">\n%s\n</script>' % page["schema"]

    head = HEAD.format(
        title=page["title"],
        description=page["description"],
        url=page["url"],
        site=SITE,
        fonts=FONTS,
        style=STYLE + EXTRA_CSS,
        schema=schema,
        kicker=page.get("kicker", "Extraction economics &amp; production optimisation"),
    )
    return head + page["body"] + FOOT.format(script=SCRIPT)


def sitemap(pages):
    rows = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    entries = [("/", "1.0", "monthly")]
    entries += [(p["url"], p.get("priority", "0.7"), "yearly") for p in pages]
    for url, priority, freq in entries:
        rows += ["  <url>",
                 "    <loc>%s%s</loc>" % (SITE, url),
                 "    <changefreq>%s</changefreq>" % freq,
                 "    <priority>%s</priority>" % priority,
                 "  </url>"]
    rows.append("</urlset>")
    return "\n".join(rows) + "\n"


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pages import build_pages

    pages = build_pages()
    for page in pages:
        write(PUBLIC / page["url"].strip("/") / "index.html", render(page))
        print(page["url"])

    write(PUBLIC / "sitemap.xml", sitemap(pages))
    print("sitemap.xml  (%d urls)" % (len(pages) + 1))


if __name__ == "__main__":
    main()
