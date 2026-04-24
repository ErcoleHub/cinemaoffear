#!/usr/bin/env python3
"""
Upload a card image to Imgur (for public URL) and send it via Twilio MMS.

Usage:
    python tools/send_sms.py /path/to/card.png
"""
import base64
import os
import sys
from pathlib import Path

import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client

if not os.getenv('GITHUB_ACTIONS'):
    load_dotenv('.env')

IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"
SMS_BODY = "Cinema of Fear review card — ready to post to Instagram."


def upload_to_imgur(card_path: str, client_id: str) -> str:
    """Upload PNG to Imgur anonymously. Returns public HTTPS URL."""
    path = Path(card_path)
    if not path.exists():
        raise FileNotFoundError(f"Card not found: {card_path}")
    image_data = base64.b64encode(path.read_bytes()).decode("utf-8")
    response = requests.post(
        IMGUR_UPLOAD_URL,
        headers={"Authorization": f"Client-ID {client_id}"},
        data={"image": image_data, "type": "base64"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["data"]["link"]


def send_mms(image_url: str, to_number: str, from_number: str,
             account_sid: str, auth_token: str) -> str:
    """Send MMS via Twilio. Returns message SID."""
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=SMS_BODY,
        from_=from_number,
        to=to_number,
        media_url=[image_url],
    )
    return message.sid


def deliver_card(card_path: str, imgur_client_id: str, twilio_account_sid: str,
                 twilio_auth_token: str, twilio_from_number: str,
                 review_phone_number: str) -> dict:
    """Full delivery: Imgur upload -> Twilio MMS. Returns {imgur_url, message_sid}."""
    print(f"Uploading to Imgur: {card_path}")
    imgur_url = upload_to_imgur(card_path, client_id=imgur_client_id)
    print(f"Imgur URL: {imgur_url}")
    print(f"Sending MMS to {review_phone_number}")
    sid = send_mms(imgur_url, review_phone_number, twilio_from_number,
                   twilio_account_sid, twilio_auth_token)
    print(f"Sent! SID: {sid}")
    return {"imgur_url": imgur_url, "message_sid": sid}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/send_sms.py <card_path>")
        sys.exit(1)
    result = deliver_card(
        card_path=sys.argv[1],
        imgur_client_id=os.environ["IMGUR_CLIENT_ID"],
        twilio_account_sid=os.environ["TWILIO_ACCOUNT_SID"],
        twilio_auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        twilio_from_number=os.environ["TWILIO_FROM_NUMBER"],
        review_phone_number=os.environ["REVIEW_PHONE_NUMBER"],
    )
    print(result)
