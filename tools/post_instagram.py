#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

IG_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
GRAPH_BASE = "https://graph.facebook.com/v18.0"


def _upload_to_imgur(image_path: str) -> str:
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://api.imgur.com/3/image",
            headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"},
            files={"image": f},
            timeout=60,
        )
    resp.raise_for_status()
    return resp.json()["data"]["link"]


def _get_ig_user_id() -> str:
    resp = requests.get(
        f"{GRAPH_BASE}/me",
        params={"fields": "id", "access_token": IG_TOKEN},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _create_ig_container(image_url: str, caption: str, ig_user_id: str) -> str:
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={"image_url": image_url, "caption": caption, "access_token": IG_TOKEN},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _publish_ig_container(container_id: str, ig_user_id: str) -> str:
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        data={"creation_id": container_id, "access_token": IG_TOKEN},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def post_to_instagram(image_path: str, caption: str) -> str:
    """Upload to Imgur, create IG container, publish. Returns IG post ID."""
    public_url = _upload_to_imgur(image_path)
    ig_user_id = _get_ig_user_id()
    container_id = _create_ig_container(public_url, caption, ig_user_id)
    return _publish_ig_container(container_id, ig_user_id)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python post_instagram.py <image_path> <caption>")
        sys.exit(1)
    post_id = post_to_instagram(sys.argv[1], sys.argv[2])
    print(f"Posted! ID: {post_id}")
