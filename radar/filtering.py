# -*- coding: utf-8 -*-
"""
The filtering brain.

Two jobs:
1. EXCLUDE anything that is not suitable for a student (permanent full-time,
   senior/experienced, degree-required staff positions).
2. Assign a PRIORITY (P1..P5) to the student-suitable roles, best first.
"""
import re
import unicodedata
import config


def _norm(text):
    if not text:
        return ""
    text = text.lower()
    text = (text.replace("ä", "ae").replace("ö", "oe")
                .replace("ü", "ue").replace("ß", "ss"))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " " + text + " "


# ---- signal word lists ----------------------------------------------------
# STRONG = unambiguous student role. A role with any of these is a student job
# even if it also contains a senior word.
STRONG_STUDENT_SIGNALS = [
    "werkstudent", "working student", "working-student", "studentische hilfskraft",
    "wissenschaftliche hilfskraft", "wiss. hilfskraft", "hiwi", "student assistant",
    "research assistant", "studentische aushilfe", "studentenjob", "studierende",
    "studentische", "studentischer", "praktikum", "praktikant", "internship",
    "minijob", "aushilfe", "ferienjob", "nebenjob", "geringfuegig", "geringfugig",
    "shk", "whk",
]
# WEAK = part-time, but NOT proof of a student role (a senior part-time job is
# still senior). Only counts if the role is not otherwise senior.
WEAK_STUDENT_SIGNALS = ["teilzeit", "part-time", "part time"]

# Research / student assistant style (university high-priority)
ASSISTANT_SIGNALS = [
    "studentische hilfskraft", "wissenschaftliche hilfskraft", "hiwi",
    "student assistant", "research assistant", "hilfskraft",
]

# Senior / professional signals => not for a student (unless a STRONG student
# signal is also present, which always wins).
SENIOR_SIGNALS = [
    # seniority levels
    "senior", " lead ", "lead ", " lead", "head of", "teamleiter", "teamleitung",
    "leitung", "leiter", "leiterin", "principal", "director", "geschaeftsfuehr",
    "vorstand", "chief", " cto", " ceo", " cfo",
    # professional job titles (not for students)
    "manager", "managerin", "partner", "consultant", "berater", "beraterin",
    "accountant", "bilanzbuchhalter", "referent", "referentin", "specialist",
    "spezialist", "expert", "experte", "expertin", "koordinator", "koordinatorin",
    "ingenieur", "engineer", "architekt", "meister",
    # experience / degree requirements
    "mehrjaehrige", "jahre berufserfahrung", "jahren berufserfahrung",
    "years of experience", "years experience", "jahre erfahrung",
    "einschlaegige berufserfahrung", "abgeschlossenes studium",
    "abgeschlossene ausbildung", "abgeschlossenes hochschulstudium",
    "promotion", " phd ", "doktorand", "wissenschaftliche mitarbeiter",
    "wissenschaftlicher mitarbeiter", "wissenschaftliche mitarbeiterin",
    "berufserfahrene", "fachkraft mit", "festanstellung", "unbefristet",
]

# Core field for P2
FIELD_CORE = [
    "data science", "data scien", "data analy", "datenanaly", "data analyst",
    "machine learning", "deep learning", "kuenstliche intelligenz",
    "artificial intelligence", " ai ", " ai/", " ml ", "data engineer",
    "data management", "datenmanagement", "business intelligence", " bi ",
    "analytics", "data scientist", "python", "sql", "big data", "software",
    "developer", "entwickler", "programmier", "informatik", "data ",
]

# Specific UNRELATED degree fields -> exclude (unless a tech/data/business
# field is also mentioned). You have a Computer/Data Science degree.
UNRELATED_DEGREE_SIGNALS = [
    "maschinenbau", "mechanical engineering", "bauingenieur", "civil engineering",
    "hochbau", "tiefbau", "elektrotechnik", "electrical engineering", "elektronik",
    "electronic engineering", "mechatronik", "mechatronics", "architektur",
    "architect", "chemie", "chemistry", "chemieingenieur", "biologie", "biology",
    "medizin", "medicine", "pharmaz", "pharmacy", "jura", "rechtswissenschaft",
    "verfahrenstechnik", "produktionstechnik", "werkstofftechnik",
]
# Business / economics that is fine to keep (often tech/data-adjacent).
BUSINESS_KEEP_SIGNALS = [
    "wirtschaft", "business", "economics", "betriebswirtschaft", "bwl", "vwl",
    "economic", "management", "marketing", "finance", "controlling",
    "wirtschaftsinformatik", "wirtschaftsingenieur",
]

PART_TIME_SIGNALS = ["minijob", "aushilfe", "teilzeit", "part-time",
                     "part time", "geringfuegig", "geringfugig", "nebenjob"]
BREAK_SIGNALS = ["ferienjob", "semesterferien", "semester break",
                 "werkstudent vollzeit", "vollzeit in den semesterferien"]
WERKSTUDENT_SIGNALS = ["werkstudent", "working student", "working-student"]


def _has(text, words):
    return any(_norm(w).strip() in text for w in words)


# ---- category (kept for display) -----------------------------------------
def categorize(job):
    hay = _norm(job["title"] + " " + " ".join(job.get("berufe", [])) + " " + job.get("description", ""))
    for cat, words in config.CATEGORY_KEYWORDS.items():
        for w in words:
            if _norm(w).strip() in hay:
                return cat
    return "other"


def german_level(job):
    hay = _norm(job["title"] + " " + job.get("description", ""))
    if _has(hay, config.ENGLISH_FRIENDLY_SIGNALS):
        return "low"
    if _has(hay, config.HIGH_GERMAN_SIGNALS):
        return "high"
    desc = job.get("description", "")
    if desc and _looks_english(desc):
        return "low"
    return "medium"


_EN_HINTS = (" the ", " and ", " with ", " you ", " your ", " for ", " our ",
             " we ", " are ", " will ", " work ", " team ", " skills ")
_DE_HINTS = (" und ", " die ", " der ", " das ", " mit ", " fuer ", " wir ",
             " sie ", " ein ", " eine ", " im ", " zu ", " bei ")


def _looks_english(text):
    t = _norm(text)
    en = sum(t.count(h) for h in _EN_HINTS)
    de = sum(t.count(h) for h in _DE_HINTS)
    return en > de and en >= 3


_TAGS = re.compile(r"<[^>]+>")
_EN_TITLE = ("working student", "student assistant", "intern", "research assistant", "student job")


def posting_language(job):
    """'en', 'de' or 'unknown', judged by which language the posting is written in."""
    text = _TAGS.sub(" ", job.get("description") or "")
    t = _norm(text)
    en = sum(t.count(h) for h in _EN_HINTS)
    de = sum(t.count(h) for h in _DE_HINTS)
    if en + de >= 8:
        return "en" if en >= de else "de"
    # Too little text: fall back to the title.
    title = _norm(job.get("title", ""))
    if any(s in title for s in _EN_TITLE):
        return "en"
    if text.strip() or "werkstudent" in title or "(m/w/d)" in title or "(w/m/d)" in title:
        return "de"
    return "unknown"


# Strong data / software terms, for roles whose title doesn't name the field.
_FIELD_DESC_TERMS = [
    "python", " sql", "machine learning", "data analy", "data science", "data engineer",
    "power bi", "tableau", "pandas", "deep learning", " llm", "javascript", "typescript",
    "react", "backend", "frontend", "software development", "kuenstliche intelligenz",
]


def in_my_field(job):
    title = _norm(job["title"] + " " + " ".join(job.get("berufe", [])))
    for cat in config.MY_FIELD_CATEGORIES:
        if any(_norm(w).strip() in title for w in config.CATEGORY_KEYWORDS.get(cat, [])):
            return True
    if _has(title, FIELD_CORE):
        return True
    desc = _norm(_TAGS.sub(" ", job.get("description") or ""))
    return sum(1 for w in _FIELD_DESC_TERMS if _norm(w).strip() in desc) >= 3


# ---- the priority decision ------------------------------------------------
def classify(job):
    hay = _norm(job["title"] + " " + " ".join(job.get("berufe", [])) + " " + job.get("description", ""))
    job["category"] = categorize(job)
    job["german_level"] = german_level(job)
    job["lang"] = posting_language(job)

    strong = _has(hay, STRONG_STUDENT_SIGNALS)   # werkstudent, hilfskraft, minijob, praktikum...
    # Company-board jobs were already kept only for student titles (see company_boards.py).
    strong = strong or job.get("source") == "company_board"
    weak = _has(hay, WEAK_STUDENT_SIGNALS)        # teilzeit / part-time only
    assistant = _has(hay, ASSISTANT_SIGNALS)
    senior = _has(hay, SENIOR_SIGNALS)
    field = _has(hay, FIELD_CORE)
    business = _has(hay, BUSINESS_KEEP_SIGNALS)
    werk = _has(hay, WERKSTUDENT_SIGNALS)
    part_time = _has(hay, PART_TIME_SIGNALS)
    on_break = _has(hay, BREAK_SIGNALS)
    unrelated_degree = _has(hay, UNRELATED_DEGREE_SIGNALS)

    # A genuine student role: a STRONG signal, OR merely part-time but not senior.
    student_suitable = strong or (weak and not senior)

    # --- exclusion rules (order matters) ---
    # 1. Senior / professional role and NOT an explicit student role -> out.
    if senior and not strong:
        job["priority"] = "EXCLUDE"; job["reason"] = "senior"; return job
    # 2. Not a student-suitable role at all -> out.
    if not student_suitable:
        job["priority"] = "EXCLUDE"; job["reason"] = "not a student role"; return job
    # 3. Requires a specific UNRELATED degree and isn't tech/business -> out.
    if unrelated_degree and not (field or business):
        job["priority"] = "EXCLUDE"; job["reason"] = "unrelated degree"; return job
    # 4. You are at A2 German: any role that ASKS FOR German is out.
    if job["german_level"] == "high":
        job["priority"] = "EXCLUDE"; job["reason"] = "asks for German"; return job
    # 4b. No sales roles (checked on the title only, so "work with our sales team" is fine).
    if _has(_norm(job["title"]), getattr(config, "SALES_SIGNALS", [])):
        job["priority"] = "EXCLUDE"; job["reason"] = "sales"; return job
    # 5. English-only mode: the posting itself must be written in English.
    #    University assistant roles are exempt: they are posted in German by
    #    policy even in English-speaking labs (rule 4 already drops any that ask for German).
    uni_assistant = assistant and job.get("is_university")
    if getattr(config, "ENGLISH_ONLY", False) and job["lang"] != "en" and not uni_assistant:
        job["priority"] = "EXCLUDE"; job["reason"] = "posting not in English"; return job
    # 6. Field focus: data / AI / software only (university assistant roles always pass).
    if (getattr(config, "ONLY_MY_FIELD", False) and not in_my_field(job)
            and not (assistant and job.get("is_university"))):
        job["priority"] = "EXCLUDE"; job["reason"] = "not my field"; return job

    # --- priority assignment among student roles ---
    if assistant:                      # HiWi / SHK / WHK / (research) assistant
        job["priority"] = "P1"
    elif werk and field:               # Werkstudent in your field
        job["priority"] = "P2"
    elif werk:                         # Werkstudent, other field
        job["priority"] = "P3"
    elif on_break:                     # semester-break full-time for students
        job["priority"] = "P5"
    elif part_time:                    # part-time / minijob
        job["priority"] = "P4"
    else:
        job["priority"] = "P4"

    # A university student/assistant role always ranks top.
    if job.get("is_university") and (assistant or werk):
        job["priority"] = "P1"
    # On-site in another German city (company boards, only if enabled): list last.
    if job.get("mode") == "elsewhere":
        job["priority"] = "P6"
    return job


PRIORITY_ORDER = {"P1": 0, "P2": 1, "P3": 2, "P4": 3, "P5": 4, "P6": 5, "EXCLUDE": 9}
