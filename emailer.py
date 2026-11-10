import logging
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

import config

log = logging.getLogger(__name__)


def send_email(subject, text_body, html_body=None, attachments=()):
    if not (config.SMTP_USER and config.SMTP_PASSWORD and config.EMAIL_TO):
        raise RuntimeError("Missing SMTP_USER, SMTP_PASSWORD or EMAIL_TO. Check your .env file.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_FROM
    msg["To"] = ", ".join(config.EMAIL_TO)
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    for path in map(Path, attachments):
        msg.add_attachment(
            path.read_bytes(), maintype="text", subtype="csv", filename=path.name
        )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, context=context, timeout=30) as server:
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
    log.info("Email sent to %s", msg["To"])