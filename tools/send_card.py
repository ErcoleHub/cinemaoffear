#!/usr/bin/env python3
"""
Send a generated review card via Gmail using OAuth2 API.

First run: authenticate (opens browser), saves token to .env
Subsequent runs: use saved token

Usage:
    python tools/send_card.py /path/to/card.png
"""
import base64
import json
import os
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

if not os.getenv('GITHUB_ACTIONS'):
    load_dotenv('.env')

EMAIL_SUBJECT = "Cinema of Fear — Review Card"
EMAIL_BODY = "Your horror film review card is attached. Ready to post to Instagram."
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _get_oauth_token(credentials_file: str = None) -> str:
    """
    Get Gmail API OAuth2 token.
    If GMAIL_OAUTH_TOKEN in .env: use saved token (GitHub Actions).
    If credentials_file provided: authenticate locally and save token.
    Returns the access token string.
    """
    # Check if token already exists in .env (GitHub Actions case)
    token_str = os.getenv("GMAIL_OAUTH_TOKEN")
    if token_str:
        try:
            creds = UserCredentials.from_authorized_user_info(json.loads(token_str))
            if creds.valid:
                return creds.token
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                _save_token_to_env(creds)
                return creds.token
        except Exception:
            pass

    # Local authentication: credentials_file required
    if not credentials_file:
        raise ValueError(
            "No GMAIL_OAUTH_TOKEN in .env. "
            "Run locally with credentials_file to authenticate first."
        )
    if not Path(credentials_file).exists():
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")

    # First run: authenticate and save token
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token_to_env(creds)
    return creds.token


def _save_token_to_env(creds) -> None:
    """Save OAuth2 token to .env file for future runs."""
    token_dict = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    token_json = json.dumps(token_dict)

    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        if "GMAIL_OAUTH_TOKEN=" in content:
            content = "\n".join(
                line for line in content.split("\n") if not line.startswith("GMAIL_OAUTH_TOKEN=")
            )
        content += f"\nGMAIL_OAUTH_TOKEN={token_json}\n"
    else:
        content = f"GMAIL_OAUTH_TOKEN={token_json}\n"

    env_path.write_text(content)
    print(f"✓ Token saved to .env")


def send_card_email(
    card_path: str, to_email: str, from_email: str, credentials_file: str
) -> str:
    """
    Send review card via Gmail API. Returns message ID.

    Args:
        card_path: Path to the PNG card file
        to_email: Recipient email address
        from_email: Sender email address (must be the authenticated Gmail account)
        credentials_file: Path to credentials.json from Google Cloud
    """
    path = Path(card_path)
    if not path.exists():
        raise FileNotFoundError(f"Card not found: {card_path}")

    # Authenticate and get OAuth token
    access_token = _get_oauth_token(credentials_file)

    # Build Gmail service
    creds = UserCredentials(token=access_token)
    service = build("gmail", "v1", credentials=creds)

    # Create message
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = EMAIL_SUBJECT

    # Attach body
    msg.attach(MIMEText(EMAIL_BODY, "plain"))

    # Attach card image
    with open(path, "rb") as attachment:
        part = MIMEBase("image", "png")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)

    part.add_header("Content-Disposition", f"attachment; filename={path.name}")
    msg.attach(part)

    # Send via Gmail API
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    try:
        result = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return result["id"]
    except Exception as e:
        raise Exception(f"Gmail API error: {e}")


def deliver_card(
    card_path: str, to_email: str, from_email: str, credentials_file: str = None
) -> dict:
    """Full delivery: email the card. Returns {email_address, message_id}."""
    if credentials_file is None:
        credentials_file = "credentials.json" if Path("credentials.json").exists() else None
    print(f"Sending card via Gmail to {to_email}: {card_path}")
    message_id = send_card_email(card_path, to_email, from_email, credentials_file)
    print(f"✓ Sent! Message ID: {message_id}")
    return {"email_address": to_email, "message_id": message_id}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/send_card.py <card_path>")
        sys.exit(1)
    result = deliver_card(
        card_path=sys.argv[1],
        to_email=os.environ["REVIEW_EMAIL"],
        from_email=os.environ["GMAIL_USER"],
        credentials_file="credentials.json",
    )
    print(result)
