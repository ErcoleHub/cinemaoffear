# Workflow: Mobile Voice Review (Voice-to-SMS)

## Objective
Speak a horror film review on iPhone → receive 1080×1080 review card via MMS → post manually to Instagram.

## Flow

```
iPhone Siri Shortcut (Dictate Text)
  ↓ POST to GitHub API
GitHub Actions: voice_review.yml
  ↓ tools/parse_voice_review.py   (Claude Haiku → structured dict)
  ↓ tools/fetch_poster.py         (TMDB/OMDB → poster, unchanged)
  ↓ tools/generate_card.py        (Playwright → 1080×1080 PNG, unchanged)
  ↓ tools/send_sms.py             (Imgur public URL → Twilio MMS)
iPhone receives MMS → manual Instagram post
```

Total time: ~60–90 seconds.

## Required Secrets (GitHub Actions)

| Secret | Description |
|---|---|
| `TMDB_API_KEY` | Movie data + posters |
| `OMDB_API_KEY` | Fallback movie data |
| `ANTHROPIC_API_KEY` | Claude review parser |
| `IMGUR_CLIENT_ID` | Anonymous image hosting |
| `TWILIO_ACCOUNT_SID` | Twilio auth |
| `TWILIO_AUTH_TOKEN` | Twilio auth |
| `TWILIO_FROM_NUMBER` | Your Twilio phone number |
| `REVIEW_PHONE_NUMBER` | Your iPhone number (receives MMS) |

## Files Involved

| File | Role |
|---|---|
| `tools/parse_voice_review.py` | Claude API → structured dict |
| `tools/fetch_poster.py` | Fetch poster from TMDB/OMDB (unchanged) |
| `tools/generate_card.py` | Render 1080×1080 PNG (unchanged) |
| `tools/send_sms.py` | Imgur upload → Twilio MMS |
| `.github/workflows/voice_review.yml` | Orchestrates the full pipeline |
| `docs/siri_shortcut_setup.md` | iOS setup guide |

## Error Handling

| Situation | Behavior |
|---|---|
| Claude parse fails validation | Workflow exits; check GitHub Actions log |
| TMDB + OMDB both fail | Card uses placeholder poster, continues |
| Imgur upload fails | Workflow exits; card saved as Actions artifact |
| Twilio send fails | Workflow exits; download card from Actions artifact |
| Review text > 250 chars | Truncated silently by parse_voice_review.py |

## Local Debug Commands

```bash
# Test the parser
python tools/parse_voice_review.py "Just watched Scream 1996. Slasher. Atmosphere 4, characters 5, originality 5, script 5, gore 3. Theater. Craven at his peak."

# Test SMS delivery (needs real credentials in .env)
python tools/send_sms.py .tmp/card_scream.png

# Run all tests
pytest tests/ -v
```
