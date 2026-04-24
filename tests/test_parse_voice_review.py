"""Tests for tools/parse_voice_review.py — run: pytest tests/test_parse_voice_review.py -v"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import parse_voice_review as pvr

FULL_REVIEW = (
    "Just watched Hereditary from 2018. Absolutely terrifying psychological horror. "
    "Atmosphere 5, characters 4, originality 5, script 4, gore 3. "
    "Definitely a theater watch. Sub-genre is supernatural. "
    "Review: Ari Aster's debut is a masterwork of grief and dread."
)

VALID_PARSED = {
    "title": "Hereditary",
    "year": 2018,
    "ratings": {"atmosphere": 5, "characters": 4, "originality": 5, "script": 4, "gore": 3},
    "sub_genre": "supernatural",
    "recommendation": "theater",
    "review_text": "Ari Aster's debut is a masterwork of grief and dread.",
}

def _mock_claude(content):
    msg = MagicMock()
    msg.content = [MagicMock(text=content)]
    return msg

@patch("parse_voice_review.anthropic.Anthropic")
def test_returns_valid_structured_dict(MockAnthropic):
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(json.dumps(VALID_PARSED))
    result = pvr.parse_voice_review(FULL_REVIEW)
    assert result["title"] == "Hereditary"
    assert result["ratings"]["atmosphere"] == 5
    assert result["sub_genre"] == "supernatural"
    assert result["recommendation"] == "theater"

@patch("parse_voice_review.anthropic.Anthropic")
def test_review_text_truncated_to_250_chars(MockAnthropic):
    long = dict(VALID_PARSED, review_text="x" * 300)
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(json.dumps(long))
    result = pvr.parse_voice_review(FULL_REVIEW)
    assert len(result["review_text"]) <= 250

@patch("parse_voice_review.anthropic.Anthropic")
def test_year_is_none_when_not_spoken(MockAnthropic):
    no_year = dict(VALID_PARSED, year=None)
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(json.dumps(no_year))
    result = pvr.parse_voice_review("Hereditary is scary.")
    assert result["year"] is None

@patch("parse_voice_review.anthropic.Anthropic")
def test_invalid_rating_raises_value_error(MockAnthropic):
    bad = dict(VALID_PARSED, ratings={**VALID_PARSED["ratings"], "atmosphere": 6})
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(json.dumps(bad))
    try:
        pvr.parse_voice_review(FULL_REVIEW)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "atmosphere" in str(e).lower() or "rating" in str(e).lower()

@patch("parse_voice_review.anthropic.Anthropic")
def test_invalid_sub_genre_raises_value_error(MockAnthropic):
    bad = dict(VALID_PARSED, sub_genre="romcom")
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(json.dumps(bad))
    try:
        pvr.parse_voice_review(FULL_REVIEW)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "sub_genre" in str(e).lower()

@patch("parse_voice_review.anthropic.Anthropic")
def test_invalid_recommendation_raises_value_error(MockAnthropic):
    bad = dict(VALID_PARSED, recommendation="rent")
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(json.dumps(bad))
    try:
        pvr.parse_voice_review(FULL_REVIEW)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "recommendation" in str(e).lower()

@patch("parse_voice_review.anthropic.Anthropic")
def test_strips_markdown_fences(MockAnthropic):
    fenced = f"```json\n{json.dumps(VALID_PARSED)}\n```"
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(fenced)
    result = pvr.parse_voice_review(FULL_REVIEW)
    assert result["title"] == "Hereditary"

@patch("parse_voice_review.anthropic.Anthropic")
def test_missing_title_raises_value_error(MockAnthropic):
    no_title = {k: v for k, v in VALID_PARSED.items() if k != "title"}
    MockAnthropic.return_value.messages.create.return_value = _mock_claude(json.dumps(no_title))
    try:
        pvr.parse_voice_review(FULL_REVIEW)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "title" in str(e).lower()
