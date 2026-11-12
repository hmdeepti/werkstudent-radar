# Werkstudent Radar

A small Python agent that searches for **working-student, student-assistant and part-time jobs** around one city every day, filters out the ones that don't fit, and sends a ranked digest by email.

I built it for my own job search in Bielefeld. As an international Master's student with A2 German, most job boards showed me hundreds of roles I could not apply to (fluent German required, senior roles, full-time only). The radar removes those automatically, so I only see jobs I can actually apply for, and only once.

## What it does

```
 sources                    filtering                  output
 ---------------------      ----------------------     -----------------------
 Federal Employment    \    category detection         SQLite: seen jobs
 Agency API (v6)        \   student-role check    ->   (only NEW jobs shown)
 Arbeitnow API      ---->   seniority / degree    ->   HTML digest P1..P5
 University employers   /   German-level check         daily email (SMTP)
 University job pages  /    sales exclusion
```

1. **Collects** listings from the Federal Employment Agency (Bundesagentur für Arbeit) API, the Arbeitnow API (English-speaking and remote roles), an employer search for nearby universities, and direct scraping of university HiWi/SHK job pages that never reach the national boards.
2. **Classifies** each job by field (data/AI, IT, marketing, business, retail/logistics, ...) using keyword rules on title and description.
3. **Filters** out roles that need fluent German, senior or "X years of experience" roles, unrelated degrees and sales jobs. Strong student signals (Werkstudent, Hilfskraft, Minijob, SHK/WHK) override the seniority rules.
4. **Ranks** what is left into five priorities: P1 student/research assistant, P2 working student in my field, P3 working student in another field, P4 part-time/Minijob, P5 semester-break jobs.
5. **Remembers** every job in SQLite, so each digest shows only new postings.
6. **Sends** an HTML digest by email and saves a copy to `reports/`.

A typical run looks at about 200 listings around Bielefeld and Gütersloh.

## Design choices

- **Standard library only.** No `pip install` needed (`urllib`, `json`, `sqlite3`, `smtplib`), so the scheduled job never breaks because of a package update.
- **Adaptive search window.** Each source remembers when it was last searched and only asks for jobs posted since then (plus one day of overlap). The first run looks back 30 days.
- **Configuration in one file.** Location, radius, search terms, category keywords, German-level signals and exclusions are all in `config.py`.
- **No secrets in code.** The email password comes from an environment variable. Personal addresses go in a git-ignored `local_settings.py`.

## Project structure

```
config.py                  all settings (location, queries, filter rules, email)
radar/main.py              orchestrator: collect -> filter -> store -> digest -> email
radar/sources/             arbeitsagentur.py, arbeitnow.py, universities.py, uni_portals.py
radar/filtering.py         classification and exclusion rules, priority buckets
radar/store.py             SQLite store: seen jobs and per-source last visit
radar/digest.py            HTML digest
radar/emailer.py           SMTP sender
run.bat                    entry point for Windows Task Scheduler
```

## Run it

Requires Python 3.10+.

```
python -m radar.main
```

The report is written to `reports/latest.html`.

### Daily schedule and email (optional)

1. Create `local_settings.py` next to `config.py`:
   ```python
   EMAIL_ENABLED = True
   EMAIL_TO = "you+radar@gmail.com"
   EMAIL_FROM = "you@gmail.com"
   ```
2. Create a Gmail app password (this needs 2-step verification) and store it as an environment variable:
   ```
   setx RADAR_EMAIL_PASSWORD "your-app-password"
   ```
3. On Windows, add a daily Task Scheduler task that runs `run.bat`. On Linux or macOS, use cron.

## Adapting it

Change `LOCATION`, `RADIUS_KM` and `NEARBY_TOWNS` in `config.py` to search around a different city, and edit the query lists and signal lists to match your own field and language level.

## Ideas for next steps

- More sources through company ATS feeds (Personio, softgarden, Greenhouse, Lever).
- A small score per job instead of fixed buckets.
- Using an LLM to read the full description and extract required skills and German level.
