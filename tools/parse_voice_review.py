#!/usr/bin/env python3
"""
Parse free-form voice review text into structured fields using Claude API.

Usage:
    python tools/parse_voice_review.py "Just watched Hereditary..."
"""
import json
import os
import re
import sys

import anthropic
import os
from dotenv import load_dotenv

if not os.getenv('GITHUB_ACTIONS'):
    load_dotenv('.env')

VALID_SUB_GENRES = {
    "slasher", "body_horror", "supernatural", "psychological",
    "found_footage", "creature_feature", "survival_horror",
    "vampire_werewolf", "zombie", "torture_extreme", "comedy", "sci_fi",
}
VALID_RECOMMENDATIONS = {"skip", "stream", "theater"}
RATING_FIELDS = ("atmosphere", "characters", "originality", "script", "gore")

SYSTEM_PROMPT = """\
You are a JSON extractor for a horror film review app.
Extract the following fields from the user's spoken review and return ONLY valid JSON.
Do not include any explanation or markdown fences.

JSON schema:
{
  "title": "<string, required>",
  "year": <integer or null>,
  "ratings": {
    "atmosphere": <integer 1-5>,
    "characters": <integer 1-5>,
    "originality": <integer 1-5>,
    "script": <integer 1-5>,
    "gore": <integer 1-5>
  },
  "sub_genre": "<one of: slasher, body_horror, supernatural, psychological, found_footage, creature_feature, survival_horror, vampire_werewolf, zombie, torture_extreme, comedy, sci_fi>",
  "recommendation": "<one of: skip, stream, theater>",
  "review_text": "<string, max 250 chars>"
}

Rules:
- If the user does not mention a year, set year to null.
- If a rating is not clearly stated, infer from context (e.g. "not very scary" -> atmosphere: 2).
- sub_genre must be exactly one of the listed values (map synonyms: "ghost" -> supernatural, "monster" -> creature_feature).
- recommendation must be exactly one of: skip, stream, theater.
- review_text is the user's review condensed to 250 chars max. Do not include rating numbers.
- Return ONLY the JSON object. No markdown, no prose.
"""


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _validate(data: dict) -> dict:
    if not data.get("title") or not isinstance(data["title"], str):
        raise ValueError("Missing or invalid 'title' in parsed review.")

    ratings = data.get("ratings")
    if not isinstance(ratings, dict):
        raise ValueError("Missing 'ratings' dict in parsed review.")
    for field in RATING_FIELDS:
        val = ratings.get(field)
        if not isinstance(val, int) or not (1 <= val <= 5):
            raise ValueError(f"Rating '{field}' must be integer 1-5, got: {val!r}")

    sub_genre = data.get("sub_genre")
    if sub_genre not in VALID_SUB_GENRES:
        raise ValueError(f"'sub_genre' must be one of {sorted(VALID_SUB_GENRES)}, got: {sub_genre!r}")

    recommendation = data.get("recommendation")
    if recommendation not in VALID_RECOMMENDATIONS:
        raise ValueError(f"'recommendation' must be skip/stream/theater, got: {recommendation!r}")

    data["review_text"] = (data.get("review_text") or "")[:250]
    return data


def parse_voice_review(raw_text: str, api_key: str | None = None) -> dict:
    """
    Parse free-form review text into structured dict using Claude API.

    Returns dict with: title, year, ratings, sub_genre, recommendation, review_text
    Raises ValueError if response fails validation.
    """
    client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw_text}],
    )
    raw_json = _strip_markdown_fences(message.content[0].text)
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned non-JSON: {raw_json!r}") from e
    return _validate(data)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/parse_voice_review.py '<review text>'")
        sys.exit(1)
    result = parse_voice_review(" ".join(sys.argv[1:]))
    print(json.dumps(result, indent=2))
