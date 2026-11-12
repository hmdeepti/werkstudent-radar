# -*- coding: utf-8 -*-
"""
Sends the HTML digest by email (optional). Uses stdlib smtplib.
The password is read from the RADAR_EMAIL_PASSWORD environment variable,
so no secret is ever stored in the code.
"""
import os
import smtplib
from email.mime.text import MIMEText
import config


def send(html_body, subject):
    if not config.EMAIL_ENABLED:
        return False, "email disabled in config"

    password = os.environ.get("RADAR_EMAIL_PASSWORD")
    if not password:
        return False, "RADAR_EMAIL_PASSWORD env var not set"

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_FROM
    msg["To"] = config.EMAIL_TO

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as s:
            s.starttls()
            s.login(config.EMAIL_FROM, password)
            s.sendmail(config.EMAIL_FROM, [config.EMAIL_TO], msg.as_string())
        return True, "sent"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
