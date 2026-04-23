import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from generate_card import generate_card

SAMPLE = {
    "title": "Test Film",
    "year": "2024",
    "runtime": "1h 30m",
    "ratings": {"atmosphere": 4, "characters": 3, "originality": 5, "script": 4, "gore": 2},
    "sub_genre": "slasher",
    "recommendation": "stream",
    "review_text": "A solid test of the Cinema of Fear review card pipeline.",
    "poster_path": None,
}


def test_generate_card_returns_1080x1080_png():
    out_path = generate_card(SAMPLE)
    assert Path(out_path).exists(), f"Output file not found: {out_path}"
    img = Image.open(out_path)
    assert img.size == (1080, 1080), f"Expected (1080, 1080), got {img.size}"
    assert img.mode in ("RGB", "RGBA")
