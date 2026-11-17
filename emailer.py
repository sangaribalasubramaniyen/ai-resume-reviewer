"""Minimal email sender for password resets.

Configure SMTP via environment variables (see .env.example). If SMTP is not
configured, the message is printed to the server console instead, so the
feature still works in local development.
"""
import os
import smtplib
from email.message import EmailMessage


def send_email(to: str, subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM") or user
    port = int(os.getenv("SMTP_PORT", "587"))

    if not (host and user and password and sender):
        print(f"\n[DEV EMAIL - SMTP not configured]\nTo: {to}\nSubject: {subject}\n\n{body}\n")
        return False

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    return True
