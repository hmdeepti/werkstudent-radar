# -*- coding: utf-8 -*-
"""
Client for the Arbeitnow job-board API — English-speaking / visa-friendly
jobs across Germany. Free, no key. We fetch several pages and keep only
roles near Bielefeld or remote. Standard library only.
"""
import urllib.request
import json
import ssl
import datetime

API = "https://www.arbeitnow.com/api/job-board-api"

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE
_HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, context=_ctx, timeout=timeout) as r:
        return json.load(r)


def search(nearby_towns, include_remote=True, max_pages=8, since_days=30):
    """Return normalized jobs near Bielefeld (or remote), posted within since_days."""
    towns = [t.lower() for t in nearby_towns]
    cutoff = (datetime.date.today() - datetime.timedelta(days=since_days)).isoformat()
    out = {}
    for page in range(1, max_pages + 1):
        try:
            data = _get(f"{API}?page={page}")
        except Exception as e:
            print(f"   [warn] arbeitnow page {page} failed: {type(e).__name__} {e}")
            break
        rows = data.get("data", [])
        if not rows:
            break
        for j in rows:
            loc = (j.get("location") or "").lower()
            is_remote = bool(j.get("remote"))
            local = any(t in loc for t in towns)
            if not (local or (include_remote and is_remote)):
                continue
            slug = j.get("slug") or j.get("url")
            jid = "arbeitnow:" + str(slug)
            if jid in out:
                continue
            ts = j.get("created_at")
            try:
                pub = datetime.datetime.fromtimestamp(int(ts)).date().isoformat()
            except Exception:
                pub = ""
            if pub and pub < cutoff:
                continue
            out[jid] = {
                "id": jid,
                "source": "arbeitnow",
                "title": (j.get("title") or "").strip(),
                "company": (j.get("company_name") or "").strip(),
                "location": (j.get("location") or "").strip(),
                "distance_km": None,
                "mode": "remote" if is_remote else "onsite",
                "published": pub,
                "berufe": j.get("tags") or [],
                "ref": slug,
                "url": j.get("url") or "https://www.arbeitnow.com/",
                "description": j.get("description") or "",  # full HTML text, good for filtering
            }
    return list(out.values())
