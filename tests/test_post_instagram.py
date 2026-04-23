import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import post_instagram as pi


def _mock_post(return_json):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = return_json
    return m


def _mock_get(return_json):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = return_json
    return m


@patch("post_instagram.subprocess.run")
@patch("post_instagram.shutil.copy2")
def test_github_upload_returns_public_url(mock_copy, mock_run, tmp_path, monkeypatch):
    monkeypatch.setattr(pi, "GITHUB_REPO", tmp_path / "cinemaoffear")
    fake_img = tmp_path / "card.png"
    fake_img.write_bytes(b"\x89PNG\r\n\x1a\n")

    url = pi._upload_to_github(str(fake_img))

    assert "raw.githubusercontent.com" in url
    assert "card.png" in url
    assert mock_copy.called
    assert mock_run.call_count >= 3  # pull, add, commit, push


@patch("post_instagram.requests.post")
def test_create_ig_container(mock_post):
    mock_post.return_value = _mock_post({"id": "container_abc"})
    cid = pi._create_ig_container("https://i.imgur.com/xyz.png", "Test caption", "user_123")
    assert cid == "container_abc"
    call_data = mock_post.call_args[1]["data"]
    assert call_data["image_url"] == "https://i.imgur.com/xyz.png"
    assert "user_123" in mock_post.call_args[0][0]


@patch("post_instagram.requests.post")
def test_publish_ig_container(mock_post):
    mock_post.return_value = _mock_post({"id": "post_xyz"})
    post_id = pi._publish_ig_container("container_abc", "user_123")
    assert post_id == "post_xyz"
    assert mock_post.call_args[1]["data"]["creation_id"] == "container_abc"
