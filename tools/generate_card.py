#!/usr/bin/env python3
import base64
import json
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = Path(__file__).parent / "assets"
TEMPLATES_DIR = Path(__file__).parent / "templates"
TMP_DIR = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

LOGO_PATH = ASSETS_DIR / "logo.jpg"
PLACEHOLDER_PATH = ASSETS_DIR / "poster_placeholder.png"


def _b64_image(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def generate_card(data: dict) -> str:
    """
    data keys: title, year, runtime, ratings (dict), sub_genre, recommendation,
               review_text, poster_path (str or None)
    Returns absolute path to saved 1080×1080 PNG.
    """
    ratings = data["ratings"]
    scores = [ratings["atmosphere"], ratings["characters"],
              ratings["originality"], ratings["script"], ratings["gore"]]
    overall = round(sum(scores) / len(scores))

    review = (data.get("review_text") or "")[:250]

    raw_poster = data.get("poster_path")
    poster_path = Path(raw_poster) if raw_poster else PLACEHOLDER_PATH
    if not poster_path.exists():
        poster_path = PLACEHOLDER_PATH

    context = {
        "title": data["title"],
        "year": data.get("year") or "",
        "runtime": data.get("runtime") or "",
        "poster_src": _b64_image(poster_path),
        "logo_src": _b64_image(LOGO_PATH),
        "ratings": {k: int(v) for k, v in ratings.items()},
        "overall": overall,
        "sub_genre": data["sub_genre"],
        "recommendation": data["recommendation"].lower(),
        "review_text": review,
    }

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    html = env.get_template("card.html").render(**context)

    temp_html = TMP_DIR / "card_render.html"
    temp_html.write_text(html, encoding="utf-8")

    slug = _slug(data["title"])
    out_path = TMP_DIR / f"card_{slug}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 540, "height": 540},
            device_scale_factor=2.0,
        )
        page = ctx.new_page()
        page.goto(f"file://{temp_html.resolve()}", wait_until="networkidle", timeout=15000)
        page.screenshot(path=str(out_path), full_page=False)
        browser.close()

    return str(out_path)


if __name__ == "__main__":
    sample = {
        "title": "Scream",
        "year": "1996",
        "runtime": "1h 51m",
        "ratings": {"atmosphere": 5, "characters": 4, "originality": 5, "script": 5, "gore": 3},
        "sub_genre": "slasher",
        "recommendation": "theater",
        "review_text": "A masterclass in self-aware horror. Craven reinvented the genre with razor-sharp wit and genuine scares that hold up decades later.",
        "poster_path": None,
    }
    if len(sys.argv) > 1:
        sample = json.loads(sys.argv[1])
    out = generate_card(sample)
    print(f"Card saved: {out}")
