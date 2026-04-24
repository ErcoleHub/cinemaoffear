# Workflow: Mobile Voice Review (Voice-to-Email)

## Objective
Speak a horror film review on iPhone → receive 1080×1080 review card via email → post manually to Instagram.

## Flow

```
iPhone Siri Shortcut (Dictate Text)
  ↓ POST to GitHub API
GitHub Actions: voice_review.yml
  ↓ tools/parse_voice_review.py   (Claude Haiku → structured dict)
  ↓ tools/fetch_poster.py         (TMDB/OMDB → poster, unchanged)
  ↓ tools/generate_card.py        (Playwright → 1080×1080 PNG, unchanged)
  ↓ tools/send_card.py            (Gmail SMTP → email attachment)
Gmail receives card → manual Instagram post
```

Total time: ~45–60 seconds.

## Required Secrets (GitHub Actions)

| Secret | Description |
|---|---|
| `TMDB_API_KEY` | Movie data + posters |
| `OMDB_API_KEY` | Fallback movie data |
| `ANTHROPIC_API_KEY` | Claude review parser |
| `GMAIL_USER` | Your Gmail address (sender) |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not regular password) |
| `REVIEW_EMAIL` | Email to receive cards (can be same as GMAIL_USER) |

## Files Involved

| File | Role |
|---|---|
| `tools/parse_voice_review.py` | Claude API → structured dict |
| `tools/fetch_poster.py` | Fetch poster from TMDB/OMDB (unchanged) |
| `tools/generate_card.py` | Render 1080×1080 PNG (unchanged) |
| `tools/send_card.py` | Gmail SMTP → email with card attached |
| `.github/workflows/voice_review.yml` | Orchestrates the full pipeline |
| `docs/siri_shortcut_setup.md` | iOS setup guide |

## Error Handling

| Situation | Behavior |
|---|---|
| Claude parse fails validation | Workflow exits; check GitHub Actions log |
| TMDB + OMDB both fail | Card uses placeholder poster, continues |
| Gmail auth fails | Workflow exits; verify GMAIL_USER and GMAIL_APP_PASSWORD secrets |
| Email send fails | Workflow exits; card saved as Actions artifact |
| Review text > 250 chars | Truncated silently by parse_voice_review.py |

## Local Debug Commands

```bash
# Test the parser
python tools/parse_voice_review.py "Just watched Scream 1996. Slasher. Atmosphere 4, characters 5, originality 5, script 5, gore 3. Theater. Craven at his peak."

# Test email delivery (needs real credentials in .env)
python tools/send_card.py .tmp/card_scream.png

# Run all tests
pytest tests/ -v
```
