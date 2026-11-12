# -*- coding: utf-8 -*-
"""
Direct scraper for university job portals — the internal HiWi / SHK / WHK
student & research-assistant postings that never appear on the national board.
Standard library only. Generic anchor extraction, one entry per portal in
config.UNIVERSITY_PORTALS.
"""
import urllib.request
import urllib.parse
import ssl
import re
import html as _html

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE
_H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "text/html"}

# Anchor text must contain one of these to count as a student role.
ROLE_RE = re.compile(r"(?i)hilfskraft|\bWHK\b|\bSHK\b|\bWHB\b|werkstudent|studentische|"
                     r"student assistant|research assistant|wiss\.?\s*hilfskraft")
# Ignore obvious navigation / heading self-links.
SKIP_RE = re.compile(r"(?i)^(stellenangebote|stellenausschreibung|whk|shk|zur\s|mehr|weiter|home)\b")

_ANCHOR = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)


def _clean(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = _html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _absolute(href, base):
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base.rstrip("/") + href
    return urllib.parse.urljoin(base.rstrip("/") + "/", href)


def _scrape_one(portal):
    try:
        req = urllib.request.Request(portal["url"], headers=_H)
        with urllib.request.urlopen(req, context=_ctx, timeout=30) as r:
            html = r.read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"   [warn] portal '{portal['name']}' failed: {type(e).__name__} {getattr(e,'code','')}")
        return []

    out = {}
    for href, inner in _ANCHOR.findall(html):
        title = _clean(inner)
        if len(title) < 10 or not ROLE_RE.search(title) or SKIP_RE.match(title):
            continue
        url = _absolute(href, portal["base"])
        jid = "uniportal:" + url + "|" + title[:40]
        if jid in out:
            continue
        out[jid] = {
            "id": jid,
            "source": "uni_portal",
            "title": title,
            "company": portal["name"],
            "location": portal["city"],
            "distance_km": None,
            "published": "",
            "berufe": [],
            "ref": url,
            "url": url,
            "description": title,          # PDF body not fetched; title carries the role
            "is_university": True,
            "university": portal["name"],
        }
    print(f"   [portal] {portal['name']:<42} -> {len(out):>3} student roles")
    return list(out.values())


def search(portals):
    jobs = {}
    for p in portals:
        for j in _scrape_one(p):
            jobs[j["id"]] = j
    return list(jobs.values())
