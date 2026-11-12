# -*- coding: utf-8 -*-
"""
User settings for Werkstudent Radar.
Edit the values here to tune what the radar looks for.
"""

# ---- Location -------------------------------------------------------------
LOCATION = "Bielefeld"      # centre of the search
RADIUS_KM = 30              # includes Guetersloh, Herford, Halle, Verl, Rheda-Wiedenbrueck ...

# Town names used to keep location-wide sources (e.g. Arbeitnow) local.
NEARBY_TOWNS = [
    "bielefeld", "guetersloh", "gütersloh", "gutersloh", "herford", "halle",
    "verl", "rheda", "wiedenbrueck", "wiedenbrück", "steinhagen", "werther",
    "enger", "spenge", "bad salzuflen", "detmold", "lage", "oerlinghausen",
    "schloss holte", "harsewinkel", "versmold", "borgholzhausen",
    # about one hour by train
    "paderborn", "minden", "bad oeynhausen", "buende", "bünde", "loehne", "löhne",
    "lemgo", "blomberg", "hamm", "oelde", "ahlen", "lippstadt", "soest", "unna", "kamen",
    "osnabrueck", "osnabrück", "osnabruck", "muenster", "münster", "munster",
    "dortmund", "espelkamp", "luebbecke", "lübbecke", "hannover", "hanover",
]
INCLUDE_REMOTE = True       # keep remote roles (you can do them from Bielefeld)

# Extra search centres (about one hour by train). The Arbeitsagentur search runs
# around each of them too, with its own radius. Bielefeld itself is LOCATION above.
EXTRA_LOCATIONS = [
    {"city": "Paderborn", "radius_km": 15},
    {"city": "Minden", "radius_km": 15},
    {"city": "Detmold", "radius_km": 15},     # also covers Lemgo and Blomberg
    {"city": "Hamm", "radius_km": 15},
    {"city": "Lippstadt", "radius_km": 10},
    {"city": "Münster", "radius_km": 10},
    {"city": "Osnabrück", "radius_km": 10},
    {"city": "Dortmund", "radius_km": 10},
    {"city": "Hannover", "radius_km": 10},    # ICE only: about 50 min, not on the Deutschlandticket
]
# Around the extra centres only the Preference-1 (your field) queries are run.

# ---- Universities (searched EVERY day, all role types) --------------------
# Employer-name search on the Arbeitsagentur API. Catches student assistant,
# research assistant, wissenschaftliche/studentische Hilfskraft, office & admin
# roles that these employers post publicly. (radius small = the uni's own city)
UNIVERSITIES = [
    {"name": "Hochschule Bielefeld", "city": "Bielefeld"},
    {"name": "Universität Bielefeld", "city": "Bielefeld"},
    {"name": "Technische Hochschule Ostwestfalen-Lippe", "city": "Lemgo"},
    {"name": "Fachhochschule Bielefeld", "city": "Bielefeld"},
    {"name": "Universität Paderborn", "city": "Paderborn"},
    {"name": "Universität Münster", "city": "Münster"},
    {"name": "Westfälische Wilhelms-Universität", "city": "Münster"},
    {"name": "Fachhochschule Münster", "city": "Münster"},
    {"name": "Universität Osnabrück", "city": "Osnabrück"},
    {"name": "Hochschule Osnabrück", "city": "Osnabrück"},
    {"name": "Technische Universität Dortmund", "city": "Dortmund"},
    {"name": "Fachhochschule Dortmund", "city": "Dortmund"},
    {"name": "Hochschule Hamm-Lippstadt", "city": "Hamm"},
    {"name": "Leibniz Universität Hannover", "city": "Hannover"},
]
UNIVERSITY_RADIUS_KM = 15   # around each university's own city

# ---- University job PORTALS (direct HTML scrape, for P1 HiWi/SHK) ---------
# These carry the internal student/research-assistant roles that never reach
# the national job board. Add more entries any time.
UNIVERSITY_PORTALS = [
    {"name": "Universität Paderborn", "city": "Paderborn",
     "url": "https://www.uni-paderborn.de/zv/4-4/stellenangebote/stellenangebotewhk-shk",
     "base": "https://www.uni-paderborn.de"},
    {"name": "Universität Paderborn (AStA)", "city": "Paderborn",
     "url": "https://jobboerse.asta.upb.de/jobboerse/",
     "base": "https://jobboerse.asta.upb.de"},
    {"name": "Universität Bielefeld (Technische Fakultät)", "city": "Bielefeld",
     "url": "https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/test/stellen/shk-whk/",
     "base": "https://www.uni-bielefeld.de"},
    {"name": "Hochschule Bielefeld", "city": "Bielefeld",
     "url": "https://www.hsbi.de/karriere/stellenangebote",
     "base": "https://www.hsbi.de"},
]

# ---- Freshness ------------------------------------------------------------
ONLY_LAST_DAYS = 30         # ignore postings older than this many days

# ---- Search themes --------------------------------------------------------
# Each entry is a keyword handed to the Arbeitsagentur "was" search.
# Preference 1 = your target fields (English / low German).
PREF1_QUERIES = [
    "Werkstudent Data Science",
    "Werkstudent Data Analyst",
    "Werkstudent Machine Learning",
    "Werkstudent Kuenstliche Intelligenz",
    "Werkstudent Data",
    "Werkstudent IT",
    "Werkstudent Software",
    "Werkstudent Python",
    "Werkstudent Marketing",
    "Werkstudent Social Media",
    "Werkstudent Business",
    "Werkstudent Office",
    "Werkstudent Projektmanagement",
    "Working Student Data",
    "Working Student IT",
    "Working Student",
    "Working Student Software",
    "Working Student AI",
    "Working Student Python",
    "Student Assistant",
]

# Preference 2 = anything else you are happy to do (up to medium German, no sales).
PREF2_QUERIES = [
    "Studentische Aushilfe",
    "Minijob",
    "Aushilfe Lager",
    "Werkstudent Logistik",
    "Aushilfe Kueche",
    "Servicekraft Teilzeit",
    "Aushilfe Einzelhandel",
]

# ---- Category detection ---------------------------------------------------
# title/description keyword  ->  category label
CATEGORY_KEYWORDS = {
    "ai_ml_data": [
        "data science", "data scien", "machine learning", "deep learning",
        "kuenstliche intelligenz", "artificial intelligence", " ai ", " ml ",
        "data analy", "data engineer", "data scientist", "nlp", "computer vision",
        "llm", "analytics", "business intelligence", " bi ", "datenanalyse",
    ],
    "it": [
        "software", "developer", "entwickler", "informatik", "frontend", "backend",
        "fullstack", "full-stack", "devops", "cloud", "python", "java", "javascript",
        "react", "it-support", "it support", "programmier", "web", "application",
        "system administrator", "cyber", "netzwerk",
    ],
    "marketing": [
        "marketing", "social media", "seo", "content", "kampagne", "campaign",
        "brand", "communications", "online marketing", "performance marketing",
        "growth", "redaktion", "pr ", "public relations",
    ],
    "business_office": [
        "business", "office", "verwaltung", "administration", "buero", "controlling",
        "human resources", "personal", "projektmanagement", "project management",
        "assistenz", "operations", "finance", "buchhaltung", "hr ", "recruiting",
    ],
    "hospitality_retail": [
        "aushilfe", "servicekraft", "restaurant", "cafe", "barista", "bar ", "pub",
        "baecker", "baker", "gastro", "hotel", "einzelhandel", "verkauf", "lager",
        "logistik", "kueche", "reinigung", "rewe", "aldi", "lidl", "edeka", "kellner",
    ],
    "medical": [
        "pflege", "medical", "krankenhaus", "hospital", "klinik", "labor",
        "pharma", "gesundheit", "arzt", "medizin",
    ],
}

# ---- German-level signals -------------------------------------------------
# Presence of ANY of these => the ad ASKS FOR German => excluded (you are A2).
# "deutschkenntnisse" as a substring catches gute/sehr gute/erforderliche etc.
HIGH_GERMAN_SIGNALS = [
    "deutschkenntnisse", "deutschkenntnis", "verhandlungssicher",
    "fliessend deutsch", "fliessende deutsch", "fliessendes deutsch",
    "muttersprache deutsch", "deutsch als muttersprache",
    "deutsch c1", "deutsch c2", "deutsch b1", "deutsch b2",
    "deutsch (b1", "deutsch (b2", "deutsch (c1",
    "deutsch in wort und schrift", "gute deutsch", "sehr gute deutsch",
    "sehr gutes deutsch", "gutes deutsch", "sichere deutsch", "sicheres deutsch",
    "deutsch erforderlich", "deutsch zwingend", "deutsch fliessend",
    "gute deutsch- und englischkenntnisse", "deutsch- und englischkenntnisse",
    "fluent german", "german language skills", "good german", "german (fluent",
]
# Presence of these => LOW German requirement / English-friendly (good for pref 1).
ENGLISH_FRIENDLY_SIGNALS = [
    "english is our working language", "working language is english",
    "in english", "fluent english", "english (fluent", "good english",
    "german is a plus", "german is not required", "no german required",
    "without german", "english speaking", "english-speaking",
]

# ---- Sales exclusion (you don't want sales) -------------------------------
SALES_SIGNALS = [
    "vertrieb", "sales", "aussendienst", "telemarketing", "telesales",
    "call center", "callcenter", "account manager", "kundenakquise",
    "neukundengewinnung", "cold calling", "outbound",
]

# ---- Focus switches ---------------------------------------------------------
# ENGLISH_ONLY: drop every posting written in German (detected from its text),
# no matter what the filters on the job board say.
ENGLISH_ONLY = True
# ONLY_MY_FIELD: keep only data / AI / software roles (plus university
# student-assistant roles, which are always shown).
ONLY_MY_FIELD = True
MY_FIELD_CATEGORIES = ["ai_ml_data", "it"]
# Also list German-written postings in your field that do not ask for German
# (shown after the English ones as P7).
SHOW_GERMAN_POSTINGS_IN_FIELD = True
# Company boards: also show on-site roles in other German cities (listed last).
INCLUDE_OTHER_CITIES = False

# ---- Company job boards (read straight from their ATS) ------------------------
# ats: greenhouse | lever | ashby | personio. slug = the company's board name in
# the ATS URL. Add any company whose careers page runs on one of these.
COMPANY_BOARDS = [
    {"company": "Celonis", "ats": "greenhouse", "slug": "celonis"},
    {"company": "N26", "ats": "greenhouse", "slug": "n26"},
    {"company": "Contentful", "ats": "greenhouse", "slug": "contentful"},
    {"company": "HelloFresh", "ats": "greenhouse", "slug": "hellofresh"},
    {"company": "SumUp", "ats": "greenhouse", "slug": "sumup"},
    {"company": "Raisin", "ats": "greenhouse", "slug": "raisin"},
    {"company": "Solaris", "ats": "greenhouse", "slug": "solarisbank"},
    {"company": "commercetools", "ats": "greenhouse", "slug": "commercetools"},
    {"company": "Helsing", "ats": "greenhouse", "slug": "helsing"},
    {"company": "FREENOW", "ats": "greenhouse", "slug": "freenow"},
    {"company": "Wolt", "ats": "greenhouse", "slug": "wolt"},
    {"company": "Staffbase", "ats": "greenhouse", "slug": "staffbase"},
    {"company": "trivago", "ats": "greenhouse", "slug": "trivago"},
    {"company": "Flaconi", "ats": "greenhouse", "slug": "flaconi"},
    {"company": "Grover", "ats": "greenhouse", "slug": "grover"},
    {"company": "Isar Aerospace", "ats": "greenhouse", "slug": "isaraerospace"},
    {"company": "Tensordyne", "ats": "greenhouse", "slug": "tensordyne"},
    {"company": "EggAI", "ats": "greenhouse", "slug": "eggai"},
    {"company": "GetYourGuide", "ats": "ashby", "slug": "getyourguide"},
    {"company": "Babbel", "ats": "ashby", "slug": "babbel"},
    {"company": "Forto", "ats": "ashby", "slug": "forto"},
    {"company": "Choco", "ats": "ashby", "slug": "choco"},
    {"company": "Aleph Alpha", "ats": "ashby", "slug": "alephalpha"},
    {"company": "DeepL", "ats": "ashby", "slug": "deepl"},
    {"company": "Parloa", "ats": "ashby", "slug": "parloa"},
    {"company": "n8n", "ats": "ashby", "slug": "n8n"},
    {"company": "Enpal", "ats": "ashby", "slug": "enpal"},
    {"company": "Moss", "ats": "ashby", "slug": "moss"},
    {"company": "Pleo", "ats": "ashby", "slug": "pleo"},
    {"company": "Qonto", "ats": "ashby", "slug": "qonto"},
    {"company": "Upvest", "ats": "ashby", "slug": "upvest"},
    {"company": "Billie", "ats": "ashby", "slug": "billie"},
    {"company": "Yepoda", "ats": "ashby", "slug": "yepoda"},
    {"company": "Bettermile", "ats": "ashby", "slug": "bettermile"},
    {"company": "Constructor", "ats": "ashby", "slug": "constructor"},
    {"company": "Statista", "ats": "ashby", "slug": "statista"},
    {"company": "Merantix", "ats": "personio", "slug": "merantix"},
    {"company": "Personio", "ats": "personio", "slug": "personio"},
    {"company": "Homeday", "ats": "personio", "slug": "homeday"},
    {"company": "thermondo", "ats": "personio", "slug": "thermondo"},
    {"company": "tado", "ats": "personio", "slug": "tado"},
    {"company": "GENUINE", "ats": "personio", "slug": "genuine"},
]

# ---- Email delivery (fill in to enable emailing) --------------------------
# The radar always writes an HTML report file. To ALSO email it, fill these.
# For Gmail you must create an "App Password" (not your normal password).
EMAIL_ENABLED = False
# Tip for Gmail: send to a plus-alias (you+radar@gmail.com) so the digest is not
# treated as a self-send and is easy to filter.
EMAIL_TO = "you+radar@example.com"
EMAIL_FROM = "you@example.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
# The app password is read from the environment variable RADAR_EMAIL_PASSWORD
# (so it is never written into this file). Set it once in Windows.

# ---- Personal overrides ----------------------------------------------------
# Put your real addresses (and EMAIL_ENABLED = True) in local_settings.py,
# which is git-ignored, so they never end up in the repository.
try:
    from local_settings import *  # noqa: F401,F403
except ImportError:
    pass
