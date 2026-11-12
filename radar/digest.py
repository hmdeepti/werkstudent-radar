# -*- coding: utf-8 -*-
"""
Builds the daily HTML digest that lists new jobs, best matches first.
"""
import html
import datetime
from radar import filtering

PRIO_LABEL = {
    "P1": ("P1 · Student / Research Assistant", "#15803d"),
    "P2": ("P2 · Werkstudent — your field", "#0d9488"),
    "P3": ("P3 · Werkstudent — other field", "#7c3aed"),
    "P4": ("P4 · Part-time / Minijob", "#2563eb"),
    "P5": ("P5 · Semester-break full-time", "#ea580c"),
    "P6": ("P6 · On-site, other city", "#6b7280"),
}

CAT_LABEL = {
    "ai_ml_data": "AI / ML / Data",
    "it": "IT / Software",
    "marketing": "Marketing",
    "business_office": "Business / Office",
    "hospitality_retail": "Hospitality / Retail",
    "medical": "Medical",
    "other": "Other",
}

GERMAN_LABEL = {"low": "Low / English OK", "medium": "Medium", "high": "High"}


def build(jobs, meta):
    jobs = [j for j in jobs if j.get("priority") not in (None, "EXCLUDE")]
    # newest first within a priority, then by priority
    jobs.sort(key=lambda j: j.get("published", ""), reverse=True)
    jobs.sort(key=lambda j: filtering.PRIORITY_ORDER.get(j.get("priority"), 8))

    today = datetime.date.today().isoformat()
    rows = []
    for j in jobs:
        label, color = PRIO_LABEL.get(j.get("priority"), ("", "#666"))
        dist = j.get("distance_km")
        dist_s = f"{dist} km" if dist is not None else ""
        uni_badge = ' <span class="uni">🎓 University</span>' if j.get("is_university") else ""
        if j.get("mode") == "remote":
            uni_badge += ' <span class="uni">🏠 Remote</span>'
        lang = {"en": "English posting", "de": "German posting"}.get(j.get("lang"), "")
        company = html.escape(j.get('company') or '')
        rows.append(f"""
        <tr>
          <td><a href="{html.escape(j['url'])}" target="_blank"><strong>{html.escape(j['title'] or '(no title)')}</strong></a>
              <div class="sub">{company}{uni_badge}</div></td>
          <td>{html.escape(j.get('location') or '')}<div class="sub">{dist_s}</div></td>
          <td>{html.escape(CAT_LABEL.get(j.get('category'),'Other'))}</td>
          <td>{html.escape(GERMAN_LABEL.get(j.get('german_level'),'?'))}<div class="sub">{lang}</div></td>
          <td><span class="tag" style="background:{color}">{html.escape(label)}</span></td>
          <td>{html.escape(j.get('published') or '')}</td>
        </tr>""")

    body_rows = "\n".join(rows) if rows else '<tr><td colspan="6" style="padding:24px;text-align:center;color:#666">No new jobs today. 🎉 You are all caught up.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Werkstudent Radar — {today}</title>
<style>
  body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background:#f3f4f6; margin:0; padding:20px; color:#111827; }}
  .wrap {{ max-width: 980px; margin:0 auto; background:#fff; border-radius:14px; overflow:hidden; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
  header {{ background:linear-gradient(135deg,#4f46e5,#7c3aed); color:#fff; padding:22px 28px; }}
  header h1 {{ margin:0; font-size:1.4rem; }}
  header p {{ margin:6px 0 0; opacity:.9; font-size:.9rem; }}
  table {{ width:100%; border-collapse:collapse; }}
  th, td {{ text-align:left; padding:12px 14px; border-bottom:1px solid #eee; font-size:.9rem; vertical-align:top; }}
  th {{ background:#faf9ff; color:#4b5563; font-size:.75rem; text-transform:uppercase; letter-spacing:.03em; }}
  a {{ color:#4f46e5; text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .sub {{ color:#6b7280; font-size:.78rem; margin-top:2px; }}
  .tag {{ color:#fff; padding:3px 8px; border-radius:6px; font-size:.72rem; display:inline-block; }}
  .uni {{ background:#fef3c7; color:#92400e; padding:1px 6px; border-radius:5px; font-size:.72rem; }}
  footer {{ padding:16px 28px; color:#6b7280; font-size:.8rem; }}
</style></head>
<body><div class="wrap">
  <header>
    <h1>Werkstudent Radar — {meta['new_count']} new role(s)</h1>
    <p>{today} · {html.escape(meta['location'])} + {meta['radius']} km · scanned {meta['queries']} searches · sources: Bundesagentur fuer Arbeit, Arbeitnow, universities, company job boards</p>
  </header>
  <table>
    <thead><tr><th>Role / Company</th><th>Location</th><th>Field</th><th>German</th><th>Priority</th><th>Posted</th></tr></thead>
    <tbody>{body_rows}</tbody>
  </table>
  <footer>Only student-suitable roles are shown (Werkstudent, HiWi/SHK, part-time, Minijob, semester-break).
  Permanent full-time and senior/experienced positions are filtered out. Priority P1 (student/research assistant)
  and P2 (Werkstudent in your field) are listed first. New since the last run only.</footer>
</div></body></html>"""
