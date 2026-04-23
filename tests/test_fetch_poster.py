import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import fetch_poster as fp


def _tmdb_resp(results):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = {"results": results}
    return m


def _detail_resp(runtime_min):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = {"runtime": runtime_min, "release_date": "1996-12-20"}
    return m


def _download_resp():
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.iter_content.return_value = [b"FAKEIMAGE"]
    return m


def _omdb_resp(poster_url):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = {"Poster": poster_url, "Year": "1996", "Runtime": "111 min"}
    return m


@patch("fetch_poster.requests.get")
def test_tmdb_success(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "TMP_DIR", tmp_path)
    mock_get.side_effect = [
        _tmdb_resp([{"id": 42, "poster_path": "/abc.jpg", "release_date": "1996-12-20"}]),
        _detail_resp(111),
        _download_resp(),
    ]
    result = fp.fetch_poster("Scream", "1996")
    assert Path(result["poster_path"]).name == "poster.jpg"
    assert result["year"] == "1996"
    assert result["runtime"] == "1h 51m"


@patch("fetch_poster.requests.get")
def test_tmdb_no_results_falls_back_to_omdb(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "TMP_DIR", tmp_path)
    mock_get.side_effect = [
        _tmdb_resp([]),
        _omdb_resp("http://example.com/poster.jpg"),
        _download_resp(),
    ]
    result = fp.fetch_poster("Obscure Film")
    assert Path(result["poster_path"]).name == "poster.jpg"
    assert result["runtime"] == "1h 51m"


@patch("fetch_poster.requests.get")
def test_both_apis_fail_returns_placeholder(mock_get):
    mock_get.side_effect = Exception("Network error")
    result = fp.fetch_poster("No Such Film")
    assert result["poster_path"] == fp.PLACEHOLDER_PATH
    assert result["year"] is None
    assert result["runtime"] is None
