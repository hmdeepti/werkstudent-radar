# -*- coding: utf-8 -*-
"""
Company job boards read straight from their applicant-tracking system (ATS).

Many startups and international companies in Germany post English-language
working-student roles only on their own careers page. Those pages are powered
by a handful of ATS products with public JSON/XML feeds:

    greenhouse  https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true
    lever       https://api.lever.co/v0/postings/<slug>?mode=json
    ashby       https://api.ashbyhq.com/posting-api/job-board/<slug>
    personio    https://<slug>.jobs.personio.de/xml?language=en

The list of companies lives in config.COMPANY_BOARDS. Only student-type titles
in Germany are kept (on site near you, or remote). Standard library only.
"""
import concurrent.futures as cf
import datetime
import html
import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET

_ctx = ssl.create_default_context()
_HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# A title must match this to count as a student role ("intern" as a whole word,
# so "Internal ..." does not count).
TITLE_SIGNALS = re.compile(r"working[ -]student|werkstudent|student assistant|student job|studentische"
                           r"|\bhiwi\b|\bintern\b|\binternship\b|praktik")
# ...and none of these (thesis offers and full-time graduate roles).
TITLE_EXCLUDE = ["thesis", "abschlussarbeit", "masterarbeit", "bachelorarbeit", "graduate program"]

GERMAN_PLACES = [
    "germany", "deutschland", "berlin", "munich", "muenchen", "münchen", "hamburg",
    "cologne", "koeln", "köln", "frankfurt", "duesseldorf", "düsseldorf", "dusseldorf",
    "stuttgart", "leipzig", "dresden", "hannover", "hanover", "nuremberg", "nürnberg",
    "bielefeld", "guetersloh", "gütersloh", "paderborn", "muenster", "münster", "dortmund",
    "essen", "bonn", "karlsruhe", "heidelberg", "mannheim", "potsdam", "ottobrunn",
    "tübingen", "tuebingen", "würzburg", "wuerzburg", "aachen", "bremen",
]
REMOTE_REGIONS = ["germany", "deutschland", "europe", "emea", "dach", "eu"]


def _get(url, timeout=25, raw=False):
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, context=_ctx, timeout=timeout) as r:
        body = r.read()
    return body if raw else json.loads(body)


def _strip_html(text):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _is_student_title(title):
    t = (title or "").lower()
    return bool(TITLE_SIGNALS.search(t)) and not any(x in t for x in TITLE_EXCLUDE)


def _date(value):
    """ISO date from an ISO string or epoch milliseconds."""
    if not value:
        return ""
    try:
        if isinstance(value, (int, float)):
            return datetime.datetime.fromtimestamp(value / 1000).date().isoformat()
        return str(value)[:10]
    except Exception:
        return ""


# ---- one fetcher per ATS ---------------------------------------------------
def _greenhouse(slug):
    data = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
    for j in data.get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        yield {
            "ext_id": j.get("id"), "title": j.get("title"), "location": loc,
            "remote": "remote" in loc.lower(), "url": j.get("absolute_url"),
            "published": _date(j.get("first_published") or j.get("updated_at")),
            "description": _strip_html(j.get("content")),
        }


def _lever(slug):
    data = _get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    for j in data:
        cats = j.get("categories") or {}
        locs = cats.get("allLocations") or [cats.get("location") or ""]
        yield {
            "ext_id": j.get("id"), "title": j.get("text"), "location": " / ".join(l for l in locs if l),
            "remote": (j.get("workplaceType") or "").lower() == "remote",
            "url": j.get("hostedUrl"), "published": _date(j.get("createdAt")),
            "description": j.get("descriptionPlain") or _strip_html(j.get("description")),
        }


def _ashby(slug):
    data = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    for j in data.get("jobs", []):
        locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        country = (((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry") or "")
        loc = " / ".join(l for l in locs if l)
        if country and country.lower() not in loc.lower():
            loc = f"{loc} ({country})" if loc else country
        yield {
            "ext_id": j.get("id"), "title": j.get("title"), "location": loc,
            # Ashby sets isRemote for hybrid roles too, so trust workplaceType when given.
            "remote": ((j.get("workplaceType") or "").lower() == "remote") if j.get("workplaceType")
                      else bool(j.get("isRemote")),
            "url": j.get("jobUrl"), "published": _date(j.get("publishedAt")),
            "description": j.get("descriptionPlain") or _strip_html(j.get("descriptionHtml")),
        }


def _personio(slug):
    xml = _get(f"https://{slug}.jobs.personio.de/xml?language=en", raw=True)
    root = ET.fromstring(xml)
    for p in root.iter("position"):
        pid = p.findtext("id")
        offices = [p.findtext("office") or ""] + [o.text or "" for o in p.iter("additionalOffice")]
        desc = " ".join((d.findtext("value") or "") for d in p.iter("jobDescription"))
        yield {
            "ext_id": pid, "title": p.findtext("name"), "location": " / ".join(o for o in offices if o),
            "remote": "remote" in " ".join(offices).lower(),
            "url": f"https://{slug}.jobs.personio.de/job/{pid}?language=en",
            "published": _date(p.findtext("createdAt")), "description": _strip_html(desc),
        }


FETCHERS = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby, "personio": _personio}


def _board_jobs(board, nearby_towns, include_remote, include_other_cities, cutoff):
    name, ats, slug = board["company"], board["ats"], board["slug"]
    out = []
    try:
        rows = list(FETCHERS[ats](slug))
    except Exception as e:
        print(f"   [warn] {name} ({ats}) failed: {type(e).__name__} {e}")
        return out
    for r in rows:
        if not _is_student_title(r["title"]):
            continue
        if r["published"] and r["published"] < cutoff:
            continue
        loc = (r["location"] or "").lower()
        local = any(t in loc for t in nearby_towns)
        in_germany = local or any(p in loc for p in GERMAN_PLACES)
        remote_ok = r["remote"] and (in_germany or any(g in loc for g in REMOTE_REGIONS) or not loc)
        if local:
            mode = "onsite"
        elif include_remote and remote_ok:
            mode = "remote"
        elif include_other_cities and in_germany:
            mode = "elsewhere"
        else:
            continue
        out.append({
            "id": f"{ats}:{slug}:{r['ext_id']}",
            "source": "company_board",
            "title": (r["title"] or "").strip(),
            "company": name,
            "location": r["location"] or ("Remote" if r["remote"] else ""),
            "distance_km": None,
            "mode": mode,
            "published": r["published"],
            "berufe": [],
            "ref": str(r["ext_id"]),
            "url": r["url"] or "",
            "description": r["description"] or "",
        })
    return out


def search(boards, nearby_towns, include_remote=True, include_other_cities=False, since_days=30):
    towns = [t.lower() for t in nearby_towns]
    cutoff = (datetime.date.today() - datetime.timedelta(days=since_days)).isoformat()
    jobs = []
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futures = [ex.submit(_board_jobs, b, towns, include_remote, include_other_cities, cutoff) for b in boards]
        for f in futures:
            jobs.extend(f.result())
    return jobs
