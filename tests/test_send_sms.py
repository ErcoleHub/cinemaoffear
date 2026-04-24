"""Tests for tools/send_sms.py — run: pytest tests/test_send_sms.py -v"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import send_sms as ss

FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
IMGUR_URL = "https://i.imgur.com/abc123.png"

def _imgur_ok():
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = {"data": {"link": IMGUR_URL}, "success": True}
    return m

def _imgur_fail():
    m = MagicMock()
    m.raise_for_status.side_effect = Exception("403 Forbidden")
    return m

@patch("send_sms.requests.post")
def test_upload_to_imgur_returns_url(mock_post, tmp_path):
    img = tmp_path / "card.png"
    img.write_bytes(FAKE_PNG)
    mock_post.return_value = _imgur_ok()
    url = ss.upload_to_imgur(str(img), client_id="FAKE_ID")
    assert url == IMGUR_URL
    assert "Client-ID FAKE_ID" == mock_post.call_args[1]["headers"]["Authorization"]

@patch("send_sms.requests.post")
def test_upload_to_imgur_raises_on_failure(mock_post, tmp_path):
    img = tmp_path / "card.png"
    img.write_bytes(FAKE_PNG)
    mock_post.return_value = _imgur_fail()
    with pytest.raises(Exception):
        ss.upload_to_imgur(str(img), client_id="BAD")

@patch("send_sms.Client")
def test_send_mms_correct_params(MockClient):
    mock_msg = MagicMock()
    mock_msg.sid = "SM_test_123"
    MockClient.return_value.messages.create.return_value = mock_msg
    sid = ss.send_mms(IMGUR_URL, "+15551234567", "+15559999999", "AC_fake", "tok")
    assert sid == "SM_test_123"
    kwargs = MockClient.return_value.messages.create.call_args[1]
    assert kwargs["to"] == "+15551234567"
    assert kwargs["media_url"] == [IMGUR_URL]
    assert "Cinema of Fear" in kwargs["body"]

@patch("send_sms.Client")
def test_send_mms_raises_on_error(MockClient):
    MockClient.return_value.messages.create.side_effect = Exception("Twilio auth failed")
    with pytest.raises(Exception):
        ss.send_mms(IMGUR_URL, "+15551234567", "+15559999999", "AC_fake", "bad")

@patch("send_sms.send_mms")
@patch("send_sms.upload_to_imgur")
def test_deliver_card_chains_imgur_then_twilio(mock_imgur, mock_sms, tmp_path):
    img = tmp_path / "card.png"
    img.write_bytes(FAKE_PNG)
    mock_imgur.return_value = IMGUR_URL
    mock_sms.return_value = "SM_abc"
    result = ss.deliver_card(str(img), "IMGUR_ID", "AC_fake", "tok", "+15559999999", "+15551234567")
    mock_imgur.assert_called_once_with(str(img), client_id="IMGUR_ID")
    assert result["imgur_url"] == IMGUR_URL
    assert result["message_sid"] == "SM_abc"
