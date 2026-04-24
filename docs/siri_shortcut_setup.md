# Siri Shortcut: Voice Review → Cinema of Fear Card

Speak a review → GitHub Actions generates the card → Email arrives with card attached.

## Prerequisites
- iPhone iOS 16+
- GitHub PAT with `workflow` scope
- `voice_review.yml` deployed to repo

## Step 1: Create GitHub PAT
1. Go to https://github.com/settings/tokens
2. New token (classic) → name: `Cinema of Fear Shortcut`
3. Scope: check only `workflow`
4. Copy the token (you won't see it again)

## Step 2: Build the Shortcut

Open **Shortcuts** app → tap **+**

**Action 1 — Dictate Text**
- Search: "Dictate Text"
- Language: English (United States)

**Action 2 — Get Contents of URL**
- URL: `https://api.github.com/repos/ErcoleHub/cinemaoffear/actions/workflows/voice_review.yml/dispatches`
- Method: POST
- Headers:
  - `Authorization` → `token YOUR_PAT_HERE`
  - `Content-Type` → `application/json`
  - `Accept` → `application/vnd.github.v3+json`
- Request Body: JSON
  - `ref` → `main`
  - `inputs` → Dictionary
    - `review_text` → **Dictated Text** (the variable from Action 1)

**Action 3 — Show Notification**
- Title: `Cinema of Fear`
- Body: `Review submitted! Card arriving via email in ~60 seconds.`

## Step 3: Add to Home Screen
Settings (shortcut name at top) → **Add to Home Screen**

## How to Speak a Review

Say all of these clearly:
1. Film title and year: *"Just watched The Substance from 2024..."*
2. All five ratings: *"Atmosphere 5, characters 3, originality 5, script 4, gore 5"*
3. Sub-genre: *"body horror"*
4. Recommendation: *"stream it"* or *"theater"* or *"skip"*
5. Your review: *"Coralie Fargeat weaponizes body horror to say something genuinely profound."*

Full example:
> *"Just watched Hereditary from 2018. Supernatural horror. Atmosphere 5, characters 4, originality 5, script 4, gore 3. Theater watch. Ari Aster's debut is a masterwork of grief and dread that lingers for days."*

## Troubleshooting

| Error | Fix |
|---|---|
| 401 Unauthorized | PAT expired — regenerate at github.com/settings/tokens |
| 404 Not Found | Check workflow filename is `voice_review.yml` |
| 422 Unprocessable | `ref` field wrong — should be `main` |
| No email after 2 min | Check run log at github.com/ErcoleHub/cinemaoffear/actions; check spam folder |
| Gmail authentication failed | Verify `GMAIL_USER` and `GMAIL_APP_PASSWORD` secrets are correct |
