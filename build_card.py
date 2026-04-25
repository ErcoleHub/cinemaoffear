#!/usr/bin/env python3
"""
Build a horror film review card locally.

Usage:
    python build_card.py --title "Hereditary" --year 2018 --atmosphere 5 --characters 4 --originality 5 --script 4 --gore 3 --sub-genre supernatural --recommendation theater --review "Ari Aster's debut is a masterwork..."
"""
import argparse
import sys
from pathlib import Path

from tools.fetch_poster import fetch_poster
from tools.generate_card import generate_card

def main():
    parser = argparse.ArgumentParser(description='Generate a horror film review card')
    parser.add_argument('--title', required=True, help='Movie title')
    parser.add_argument('--year', type=int, help='Release year')
    parser.add_argument('--atmosphere', type=int, required=True, help='Atmosphere rating (1-5)')
    parser.add_argument('--characters', type=int, required=True, help='Characters rating (1-5)')
    parser.add_argument('--originality', type=int, required=True, help='Originality rating (1-5)')
    parser.add_argument('--script', type=int, required=True, help='Script rating (1-5)')
    parser.add_argument('--gore', type=int, required=True, help='Gore rating (1-5)')
    parser.add_argument('--sub-genre', required=True, help='Sub-genre')
    parser.add_argument('--recommendation', required=True, help='Recommendation (skip, stream, theater)')
    parser.add_argument('--review', required=True, help='Review text (max 250 chars)')

    args = parser.parse_args()

    print(f"🎬 Fetching poster for '{args.title}'...")
    try:
        movie = fetch_poster(args.title, str(args.year) if args.year else None)
        print(f"✓ Found poster")
    except Exception as e:
        print(f"✗ Could not fetch poster: {e}")
        sys.exit(1)

    print(f"🎨 Generating card...")
    try:
        card_path = generate_card({
            'title': args.title,
            'year': movie['year'] or (args.year or ''),
            'runtime': movie['runtime'] or '',
            'overview': movie.get('overview') or '',
            'ratings': {
                'atmosphere': args.atmosphere,
                'characters': args.characters,
                'originality': args.originality,
                'script': args.script,
                'gore': args.gore,
            },
            'sub_genre': args.sub_genre,
            'recommendation': args.recommendation.lower(),
            'review_text': args.review[:400],
            'poster_path': movie['poster_path'],
        })
        print(f"✓ Card saved to: {card_path}")
    except Exception as e:
        print(f"✗ Card generation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
