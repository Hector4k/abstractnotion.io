#!/usr/bin/env python3
"""Builds the static site from _src/pages/*.html.

Each page file starts with a metadata block:
<!--
title: Page title
description: Meta description
path: about/          (output folder; "" for the home page)
nav: about            (which nav item to mark current)
-->
followed by the page body (everything between <nav> and <footer>).

Run:  python3 _src/build.py
The underscore folder is ignored by GitHub Pages, so it never publishes.
"""
import json, re, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src" / "pages"
SITE = "https://abstractnotion.io"

CO = {
    "legal": "Abstract Notion Inc.",
    "street": "326 Valley Edge Dr.",
    "city": "Minneola", "state": "FL", "zip": "34515",
    "phone_display": "(407) 927-8105", "phone_tel": "+14079278105",
    "email": "hector@abstractnotion.io",
}

NAV = [("studio", "/studio/", "Studio"),
       ("pi", "/project-intelligence/", "Project Intelligence"),
       ("about", "/about/", "About"),
       ("contact", "/contact/", "Contact")]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3E"
           "%3Ccircle cx=%278%27 cy=%278%27 r=%276.4%27 fill=%27none%27 stroke=%27%2313161d%27 stroke-width=%271.6%27/%3E"
           "%3Ccircle cx=%278%27 cy=%278%27 r=%272.6%27 fill=%27%231f3fd6%27/%3E%3C/svg%3E")

ORG_LD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": CO["legal"],
    "legalName": CO["legal"],
    "url": SITE + "/",
    "email": CO["email"],
    "telephone": CO["phone_tel"],
    "foundingDate": "2023-01-31",
    "founder": {"@type": "Person", "name": "Hector J. Ortiz"},
    "address": {"@type": "PostalAddress", "streetAddress": CO["street"],
                "addressLocality": CO["city"], "addressRegion": CO["state"],
                "postalCode": CO["zip"], "addressCountry": "US"},
    "description": "Creative studio and software company: motion, VFX, and large-scale visual production, and the maker of Project Intelligence for Adobe After Effects.",
}


def head(meta):
    canonical = f"{SITE}/{meta['path']}"
    ld = ""
    if meta["path"] == "":
        ld = f'\n<script type="application/ld+json">{json.dumps(ORG_LD)}</script>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta['title']}</title>
<meta name="description" content="{meta['description']}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="Abstract Notion">
<meta property="og:title" content="{meta['title']}">
<meta property="og:description" content="{meta['description']}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def nav(current):
    items = "\n".join(
        f'      <li><a href="{href}"{" aria-current=\"page\"" if key == current else ""}>{label}</a></li>'
        for key, href, label in NAV)
    return f"""<nav class="top" aria-label="Main">
  <div class="wrap">
    <a class="brand" href="/"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="8" cy="8" r="2.6" fill="var(--accent)"/></svg>Abstract Notion</a>
    <ul>
{items}
    </ul>
  </div>
</nav>
<main id="main">
"""


def footer():
    year = datetime.date.today().year
    c = CO
    return f"""</main>
<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <h4>{c['legal']}</h4>
        <address>{c['street']}<br>{c['city']}, {c['state']} {c['zip']}<br>United States</address>
        <p style="margin-top:12px"><a href="tel:{c['phone_tel']}">{c['phone_display']}</a><br><a href="mailto:{c['email']}">{c['email']}</a></p>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="/studio/">Studio</a></li>
          <li><a href="/project-intelligence/">Project Intelligence</a></li>
          <li><a href="/about/">About</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="/privacy/">Privacy Policy</a></li>
          <li><a href="/terms/">Terms of Use</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">
      <span>© 2023–{year} {c['legal']} · A Florida corporation</span>
      <span>abstractnotion.io</span>
    </div>
  </div>
</footer>
</body>
</html>
"""


def parse(text):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    meta = dict(line.split(":", 1) for line in m.group(1).strip().splitlines())
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    body = text[m.end():]
    for k, v in CO.items():
        body = body.replace("{{" + k + "}}", v)
    return meta, body


def main():
    urls = []
    for f in sorted(SRC.glob("*.html")):
        meta, body = parse(f.read_text())
        html = head(meta) + nav(meta.get("nav", "")) + body + footer()
        if meta["path"] == "404":
            out = ROOT / "404.html"
        else:
            out = ROOT / meta["path"] / "index.html"
            urls.append(f"{SITE}/{meta['path']}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        print("wrote", out.relative_to(ROOT))
    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("wrote sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
