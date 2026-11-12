# -*- coding: utf-8 -*-
"""
SQLite store: remembers jobs we've already shown so each run only
highlights what's NEW. Standard library (sqlite3) only.
"""
import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar.sqlite")


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id TEXT PRIMARY KEY,
            title TEXT, company TEXT, location TEXT,
            category TEXT, german_level TEXT, bucket TEXT,
            url TEXT, published TEXT,
            first_seen TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS source_runs (
            source TEXT PRIMARY KEY,
            last_run TEXT
        )
    """)
    return c


def get_last_run(source_key):
    c = _conn()
    row = c.execute("SELECT last_run FROM source_runs WHERE source=?", (source_key,)).fetchone()
    c.close()
    if not row or not row[0]:
        return None
    try:
        return datetime.datetime.fromisoformat(row[0])
    except Exception:
        return None


def set_last_run(source_key, when=None):
    when = when or datetime.datetime.now()
    c = _conn()
    c.execute(
        "INSERT INTO source_runs (source, last_run) VALUES (?,?) "
        "ON CONFLICT(source) DO UPDATE SET last_run=excluded.last_run",
        (source_key, when.isoformat(timespec="seconds")),
    )
    c.commit()
    c.close()


def window_days(source_key, first_run_default=30, floor=1, cap=60):
    """
    How many days back this source should search, based on when it last ran.
    - never run before  -> first_run_default (e.g. 30 days)
    - ran N days ago     -> N + 1 (a 1-day safety overlap; dedup removes repeats)
    Result is clamped to [floor, cap].
    """
    last = get_last_run(source_key)
    if last is None:
        return first_run_default
    days = (datetime.datetime.now() - last).days
    return max(floor, min(cap, days + 1))


def mark_new(jobs):
    """Return only jobs not seen before, and record them as seen."""
    c = _conn()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    fresh = []
    for j in jobs:
        if not j.get("id"):
            continue
        row = c.execute("SELECT 1 FROM seen_jobs WHERE id=?", (j["id"],)).fetchone()
        if row:
            continue
        fresh.append(j)
        c.execute(
            "INSERT OR IGNORE INTO seen_jobs "
            "(id,title,company,location,category,german_level,bucket,url,published,first_seen) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (j["id"], j["title"], j["company"], j["location"], j.get("category"),
             j.get("german_level"), j.get("priority"), j.get("url"), j.get("published"), now),
        )
    c.commit()
    c.close()
    return fresh
