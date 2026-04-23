name: Generate Review Card

on:
  workflow_dispatch:
    inputs:
      title:
        description: 'Movie title'
        required: true
      year:
        description: 'Movie year'
        required: false
      atmosphere:
        description: 'Atmosphere rating (1-5)'
        required: true
      characters:
        description: 'Characters rating (1-5)'
        required: true
      originality:
        description: 'Originality rating (1-5)'
        required: true
      script:
        description: 'Script rating (1-5)'
        required: true
      gore:
        description: 'Gore rating (1-5)'
        required: true
      sub_genre:
        description: 'Sub-genre (slasher, body_horror, supernatural, psychological, found_footage, creature_feature, survival_horror, vampire_werewolf, zombie, torture_extreme, comedy, sci_fi)'
        required: true
      recommendation:
        description: 'Recommendation (skip, stream, theater)'
        required: true
      review_text:
        description: 'Review text (max 250 chars)'
        required: true

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          playwright install chromium

      - name: Create .env file
        run: |
          cat > .env << EOF
          TMDB_API_KEY=${{ secrets.TMDB_API_KEY }}
          OMDB_API_KEY=${{ secrets.OMDB_API_KEY }}
          ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}
          IMGUR_CLIENT_ID=${{ secrets.IMGUR_CLIENT_ID }}
          INSTAGRAM_ACCESS_TOKEN=dummy
          YOUTUBE_API_KEY=
          GOOGLE_SHEET_ID=
          OPENAI_API_KEY=
          EOF

      - name: Generate card
        run: python generate_card_cli.py "${{ github.event.inputs.title }}" "${{ github.event.inputs.year }}" "${{ github.event.inputs.atmosphere }}" "${{ github.event.inputs.characters }}" "${{ github.event.inputs.originality }}" "${{ github.event.inputs.script }}" "${{ github.event.inputs.gore }}" "${{ github.event.inputs.sub_genre }}" "${{ github.event.inputs.recommendation }}" "${{ github.event.inputs.review_text }}"

      - name: Upload card as artifact
        uses: actions/upload-artifact@v4
        with:
          name: review-card
          path: .tmp/card_*.png
          retention-days: 7
