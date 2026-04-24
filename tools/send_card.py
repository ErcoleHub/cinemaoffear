#!/usr/bin/env python3
"""
Send a generated review card via email using Gmail SMTP.

Usage:
    python tools/send_card.py /path/to/card.png
"""
import mimetypes
import os
import smtplib
import sys
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

EMAIL_SUBJECT = "Cinema of Fear — Review Card"
EMAIL_BODY = "Your horror film review card is attached. Ready to post to Instagram."


def send_card_email(card_path: str, to_email: str, gmail_user: str,
                    gmail_app_password: str) -> str:
    """
    Send review card via Gmail SMTP. Returns message ID.

    Args:
        card_path: Path to the PNG card file
        to_email: Recipient email address
        gmail_user: Gmail address to send from
        gmail_app_password: Gmail App Password (not regular password)
    """
    path = Path(card_path)
    if not path.exists():
        raise FileNotFoundError(f"Card not found: {card_path}")

    # Create message
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = EMAIL_SUBJECT

    # Attach body
    msg.attach(MIMEText(EMAIL_BODY, 'plain'))

    # Attach card image
    with open(path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())

    part.add_header('Content-Disposition', f'attachment; filename= {path.name}')
    msg.attach(part)

    # Send via Gmail SMTP
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise ValueError("Gmail authentication failed. Check credentials and App Password.")
    except smtplib.SMTPException as e:
        raise Exception(f"SMTP error: {e}")

    return f"Sent to {to_email}"


def deliver_card(card_path: str, to_email: str, gmail_user: str,
                 gmail_app_password: str) -> dict:
    """Full delivery: email the card. Returns {email_address, status}."""
    print(f"Sending card via email to {to_email}: {card_path}")
    status = send_card_email(card_path, to_email, gmail_user, gmail_app_password)
    print(f"✓ {status}")
    return {"email_address": to_email, "status": status}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/send_card.py <card_path>")
        sys.exit(1)
    result = deliver_card(
        card_path=sys.argv[1],
        to_email=os.environ["REVIEW_EMAIL"],
        gmail_user=os.environ["GMAIL_USER"],
        gmail_app_password=os.environ["GMAIL_APP_PASSWORD"],
    )
    print(result)
