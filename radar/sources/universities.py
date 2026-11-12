# -*- coding: utf-8 -*-
"""
University source — searched EVERY day, regardless of the Bielefeld radius.

Uses the Arbeitsagentur employer search for each university/college so it
catches ALL role types they post publicly: student assistant, research
assistant, wissenschaftliche/studentische Hilfskraft, office and admin roles
(not only Werkstudent). Internal-only HiWi boards on each uni's own website
are a planned follow-up source.
"""
from radar.sources import arbeitsagentur


def search(universities, radius_km, since_days=30, size=100):
    out = {}
    for uni in universities:
        name, city = uni["name"], uni["city"]
        found = arbeitsagentur.search(
            was=None, location=city, radius_km=radius_km,
            published_since_days=since_days, size=size, arbeitgeber=name,
        )
        for j in found:
            j["is_university"] = True
            j["source"] = "university"
            j["university"] = name
            if j["id"] and j["id"] not in out:
                out[j["id"]] = j
        print(f"   [uni] {name:<42} ({city}) -> {len(found):>3} roles")
    return list(out.values())
