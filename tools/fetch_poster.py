#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TMP_DIR = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)
PLACEHOLDER_PATH = str(Path(__file__).parent / "assets" / "poster_placeholder.png")

TMDB_KEY = os.getenv("TMDB_API_KEY")
OMDB_KEY = os.getenv("OMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"


def _minutes_to_hm(minutes: int) -> str:
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m}m" if h else f"{m}m"


def _download_image(url: str) -> str:
    resp = requests.get(url, timeout=20, stream=True)
    resp.raise_for_status()
    out = str(TMP_DIR / "poster.jpg")
    with open(out, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return out


def _fetch_from_tmdb(title: str, year: str | None) -> dict | None:
    params = {"api_key": TMDB_KEY, "query": title}
    if year:
        params["year"] = year
    resp = requests.get(f"{TMDB_BASE}/search/movie", params=params, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None

    top = results[0]
    movie_id = top["id"]
    release_year = (top.get("release_date") or "")[:4] or None

    detail = requests.get(f"{TMDB_BASE}/movie/{movie_id}", params={"api_key": TMDB_KEY}, timeout=10)
    detail.raise_for_status()
    runtime_min = detail.json().get("runtime")
    runtime = _minutes_to_hm(runtime_min) if runtime_min else None

    poster_path = top.get("poster_path")
    if not poster_path:
        return {"poster_path": PLACEHOLDER_PATH, "year": release_year, "runtime": runtime}

    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    dl_path = _download_image(image_url)
    return {"poster_path": dl_path, "year": release_year, "runtime": runtime}


def _fetch_from_omdb(title: str, year: str | None) -> dict | None:
    params = {"apikey": OMDB_KEY, "t": title, "type": "movie"}
    if year:
        params["y"] = year
    resp = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    poster_url = data.get("Poster", "N/A")
    omdb_year = data.get("Year")
    runtime_str = data.get("Runtime", "")
    runtime = None
    if runtime_str and runtime_str != "N/A":
        try:
            runtime = _minutes_to_hm(int(runtime_str.split()[0]))
        except (ValueError, IndexError):
            pass

    if not poster_url or poster_url == "N/A":
        return {"poster_path": PLACEHOLDER_PATH, "year": omdb_year, "runtime": runtime}

    dl_path = _download_image(poster_url)
    return {"poster_path": dl_path, "year": omdb_year, "runtime": runtime}


def fetch_poster(title: str, year: str | None = None) -> dict:
    """
    Returns dict: {poster_path: str, year: str|None, runtime: str|None}
    poster_path is an absolute path to the downloaded poster or the placeholder.
    """
    try:
        result = _fetch_from_tmdb(title, year)
        if result:
            return result
    except Exception:
        pass

    try:
        result = _fetch_from_omdb(title, year)
        if result:
            return result
    except Exception:
        pass

    return {"poster_path": PLACEHOLDER_PATH, "year": None, "runtime": None}


if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "Scream"
    year = sys.argv[2] if len(sys.argv) > 2 else None
    result = fetch_poster(title, year)
    print(json.dumps(result, indent=2))
