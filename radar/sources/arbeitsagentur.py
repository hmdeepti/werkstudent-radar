# -*- coding: utf-8 -*-
"""
Client for the official Bundesagentur fuer Arbeit job-search API (v6).
Free, official, covers most employers in Germany. Standard library only.
"""
import urllib.request
import urllib.parse
import json
import ssl
import base64
import time

BASE = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
DETAIL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/"
API_KEY = "jobboerse-jobsuche"  # public key used by the official web frontend

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

_HEADERS = {
    "X-API-Key": API_KEY,
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, context=_ctx, timeout=timeout) as r:
        return json.load(r)


def search(was, location, radius_km, published_since_days=30, size=50, arbeitgeber=None):
    """Return a list of normalized job dicts for one keyword (or employer) search."""
    parts = ["angebotsart=1",
             "wo=" + urllib.parse.quote(location),
             "umkreis=" + str(radius_km),
             "veroeffentlichtseit=" + str(published_since_days),
             "page=1", "size=" + str(size), "pav=false"]
    if was:
        parts.insert(0, "was=" + urllib.parse.quote(was))
    if arbeitgeber:
        parts.append("arbeitgeber=" + urllib.parse.quote(arbeitgeber))
    url = BASE + "?" + "&".join(parts)
    try:
        data = _get(url)
    except Exception as e:
        print(f"   [warn] search '{was or arbeitgeber}' failed: {type(e).__name__} {e}")
        return []

    jobs = []
    for j in data.get("ergebnisliste", []):
        locs = j.get("stellenlokationen") or []
        ort = None
        if locs:
            ort = locs[0].get("ort") or locs[0].get("ortStrasse")
        ref = j.get("referenznummer")
        jobs.append({
            "id": ref,
            "source": "arbeitsagentur",
            "title": (j.get("stellenangebotsTitel") or "").strip(),
            "company": (j.get("firma") or "").strip(),
            "location": ort or "",
            "distance_km": j.get("entfernung"),
            "published": j.get("datumErsteVeroeffentlichung") or "",
            "berufe": j.get("alleBerufe") or [],
            "ref": ref,
            "url": _detail_link(ref),
            "description": "",  # filled lazily by fetch_description()
        })
    return jobs


def _detail_link(ref):
    if not ref:
        return "https://www.arbeitsagentur.de/jobsuche/"
    # Public web link a human can open
    return "https://www.arbeitsagentur.de/jobsuche/jobdetail/" + urllib.parse.quote(ref)


def fetch_description(ref, timeout=20):
    """Fetch the full posting text (for language + sales detection). Best effort."""
    if not ref:
        return ""
    try:
        enc = base64.b64encode(ref.encode("utf-8")).decode("ascii")
        data = _get(DETAIL + enc, timeout=timeout)
        txt = data.get("stellenbeschreibung") or ""
        return txt
    except Exception:
        return ""
