# -*- coding: utf-8 -*-
"""
Werkstudent Radar — orchestrator.

Run:  py -m radar.main
It searches the Arbeitsagentur API for your themes around Bielefeld,
classifies each job, keeps only NEW ones, writes an HTML report, and
(optionally) emails it.
"""
import os
import sys
import datetime

# allow running both as "py -m radar.main" and "py radar/main.py"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from radar.sources import arbeitsagentur, arbeitnow, universities, uni_portals, company_boards
from radar import filtering, store, digest, emailer

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
FETCH_DESCRIPTIONS = True   # pull full text for better German/sales detection (slower)
# English-only mode needs the full text of every posting to judge its language.
MAX_DESCRIPTION_FETCH = 300 if getattr(config, "ENGLISH_ONLY", False) else 60


def collect():
    by_id = {}
    n_searches = 0

    # --- Arbeitsagentur keyword sweep (adaptive window) --------------------
    aa_window = store.window_days("arbeitsagentur", first_run_default=config.ONLY_LAST_DAYS)
    queries = config.PREF1_QUERIES + config.PREF2_QUERIES
    print(f"Arbeitsagentur: looking back {aa_window} day(s) since last visit")
    for i, q in enumerate(queries, 1):
        found = arbeitsagentur.search(
            q, config.LOCATION, config.RADIUS_KM,
            published_since_days=aa_window, size=50,
        )
        for j in found:
            if j["id"] and j["id"] not in by_id:
                by_id[j["id"]] = j
        n_searches += 1
        print(f"  [{i:>2}/{len(queries)}] {q:<32} -> {len(found):>3} hits (unique so far: {len(by_id)})")
    store.set_last_run("arbeitsagentur")

    # --- Arbeitnow (adaptive window) --------------------------------------
    an_window = store.window_days("arbeitnow", first_run_default=config.ONLY_LAST_DAYS)
    an = arbeitnow.search(config.NEARBY_TOWNS, include_remote=config.INCLUDE_REMOTE, since_days=an_window)
    for j in an:
        if j["id"] not in by_id:
            by_id[j["id"]] = j
    n_searches += 1
    print(f"  [an] Arbeitnow (English/remote, {an_window}d) -> {len(an):>3} hits (unique total: {len(by_id)})")
    store.set_last_run("arbeitnow")

    # --- Universities (EVERY day, all role types) -------------------------
    uni_window = store.window_days("universities", first_run_default=config.ONLY_LAST_DAYS)
    print(f"Universities: looking back {uni_window} day(s)")
    unis = universities.search(config.UNIVERSITIES, config.UNIVERSITY_RADIUS_KM, since_days=uni_window)
    for j in unis:
        if j["id"] and j["id"] not in by_id:
            by_id[j["id"]] = j
    n_searches += len(config.UNIVERSITIES)
    print(f"  [uni] universities total -> {len(unis):>3} roles (unique total: {len(by_id)})")
    store.set_last_run("universities")

    # --- University PORTALS (P1 HiWi/SHK, direct scrape, every day) --------
    print("University portals (HiWi / SHK):")
    portal_jobs = uni_portals.search(config.UNIVERSITY_PORTALS)
    for j in portal_jobs:
        if j["id"] not in by_id:
            by_id[j["id"]] = j
    n_searches += len(config.UNIVERSITY_PORTALS)
    print(f"  [portals] total -> {len(portal_jobs):>3} student roles (unique total: {len(by_id)})")
    store.set_last_run("uni_portals")

    # --- Company job boards (Greenhouse / Lever / Ashby / Personio) ---------
    boards = getattr(config, "COMPANY_BOARDS", [])
    if boards:
        cb_window = store.window_days("company_boards", first_run_default=config.ONLY_LAST_DAYS)
        cb = company_boards.search(boards, config.NEARBY_TOWNS, include_remote=config.INCLUDE_REMOTE,
                                   include_other_cities=getattr(config, "INCLUDE_OTHER_CITIES", False),
                                   since_days=cb_window)
        for j in cb:
            if j["id"] not in by_id:
                by_id[j["id"]] = j
        n_searches += len(boards)
        print(f"  [boards] {len(boards)} company boards ({cb_window}d) -> {len(cb):>3} student roles (unique total: {len(by_id)})")
        store.set_last_run("company_boards")

    return list(by_id.values()), n_searches


def enrich_and_classify(jobs):
    fetched = 0
    for j in jobs:
        # Only Arbeitsagentur jobs need a detail call; Arbeitnow already has text.
        if (j.get("source") == "arbeitsagentur" and not j.get("description")
                and FETCH_DESCRIPTIONS and fetched < MAX_DESCRIPTION_FETCH):
            j["description"] = arbeitsagentur.fetch_description(j["ref"])
            fetched += 1
        filtering.classify(j)
    return jobs


def main():
    print("Werkstudent Radar — starting", datetime.datetime.now().isoformat(timespec="seconds"))
    print(f"Location: {config.LOCATION} +{config.RADIUS_KM} km | last {config.ONLY_LAST_DAYS} days\n")

    jobs, n_queries = collect()
    print(f"\nCollected {len(jobs)} unique jobs. Classifying...")
    enrich_and_classify(jobs)

    new_jobs = store.mark_new(jobs)
    shown = [j for j in new_jobs if j.get("priority") not in (None, "EXCLUDE")]
    excluded = len(new_jobs) - len(shown)
    print(f"New since last run: {len(new_jobs)}  (student-suitable: {len(shown)}, excluded full-time/senior: {excluded})")

    meta = {
        "new_count": len(shown),
        "location": config.LOCATION,
        "radius": config.RADIUS_KM,
        "queries": n_queries,
    }
    html_out = digest.build(new_jobs, meta)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    stamp = datetime.date.today().isoformat()
    path = os.path.join(REPORTS_DIR, f"radar_{stamp}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_out)
    latest = os.path.join(REPORTS_DIR, "latest.html")
    with open(latest, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Report written: {path}")

    subject = f"Werkstudent Radar — {len(shown)} new role(s) — {stamp}"
    ok, info = emailer.send(html_out, subject)
    print("Email:", "sent" if ok else f"not sent ({info})")

    # summary breakdown
    from collections import Counter
    prios = Counter(j.get("priority") for j in shown)
    print("Priority breakdown:", {k: prios[k] for k in ("P1", "P2", "P3", "P4", "P5", "P6") if prios.get(k)})
    print("Done.")


if __name__ == "__main__":
    main()
