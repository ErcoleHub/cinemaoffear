# Workflow: Cinema of Fear — Review Card

## Objective
Parse a free-form film review message → fetch poster → generate 1080×1080 card → send for approval → post to Instagram.

## Required Fields

| Field | Required | If Missing |
|---|---|---|
| Movie title | Yes | Ask |
| Year | No | Use TMDB top result |
| Atmosphere (1–5) | Yes | Ask |
| Characters (1–5) | Yes | Ask |
| Originality (1–5) | Yes | Ask |
| Script (1–5) | Yes | Ask |
| Gore (1–5) | Yes | Ask |
| Sub-genre | Yes | Ask (offer list) |
| Recommendation | Yes | Ask (Skip/Stream/Theater) |
| Review text | Yes | Ask (max 250 chars) |

**Overall score** = `round((atmosphere + characters + originality + script + gore) / 5)` — calculated automatically, never asked.

## Sub-Genre Key Mapping

Use these exact string values when calling `generate_card`:

| User says | Key to use |
|---|---|
| Slasher | `slasher` |
| Body Horror | `body_horror` |
| Supernatural / Ghost | `supernatural` |
| Psychological | `psychological` |
| Found Footage | `found_footage` |
| Creature Feature / Monster | `creature_feature` |
| Survival Horror | `survival_horror` |
| Vampire / Werewolf | `vampire_werewolf` |
| Zombie | `zombie` |
| Torture / Extreme Horror | `torture_extreme` |
| Horror Comedy | `comedy` |
| Sci-Fi Horror | `sci_fi` |

## Step 1 — Parse the Message

Extract all required fields from the user's message. If a field is missing, ask ONE question. Do not ask multiple questions at once.

If review text exceeds 250 characters, truncate it and tell the user: "Your review was trimmed to 250 characters to fit the card."

## Step 2 — Fetch Poster

```python
from tools.fetch_poster import fetch_poster
movie = fetch_poster(title, year)
# movie = {"poster_path": "...", "year": "...", "runtime": "..."}
```

- If TMDB returns no result: "I couldn't find [title] on TMDB. Can you confirm the exact title or year?"
- If both APIs fail: proceed silently with the placeholder poster.
- Use `movie["year"]` and `movie["runtime"]` to fill card fields if the user didn't provide them.

## Step 3 — Generate Card

```python
from tools.generate_card import generate_card
card_path = generate_card({
    "title": title,
    "year": movie["year"] or user_provided_year or "",
    "runtime": movie["runtime"] or user_provided_runtime or "",
    "ratings": {
        "atmosphere": atmosphere,
        "characters": characters,
        "originality": originality,
        "script": script,
        "gore": gore,
    },
    "sub_genre": sub_genre_key,
    "recommendation": recommendation.lower(),  # "skip", "stream", or "theater"
    "review_text": review_text,
    "poster_path": movie["poster_path"],
})
```

## Step 4 — Send for Approval

Send the image file at `card_path` to the user. Say:
> "Here's your review card for [Title] ([Year]). Want me to post it to Instagram?"

## Step 5 — Post on Approval

When the user confirms (yes, post it, looks good, go ahead, etc.):

Build the caption:
```
[review_text]

🎬 [Title] ([Year])
Atmosphere [A]/5 · Characters [C]/5 · Originality [O]/5 · Script [S]/5 · Gore [G]/5

#CinemaOfFear #HorrorFilm #HorrorReview
```

Add a genre-specific hashtag (e.g. #Slasher, #BodyHorror, #FoundFootage) after the base hashtags.

```python
from tools.post_instagram import post_to_instagram
post_id = post_to_instagram(card_path, caption)
```

Confirm: "Posted! Check your Instagram grid."

## Error Handling

| Situation | Action |
|---|---|
| TMDB/OMDB both fail | Use placeholder poster, continue |
| Playwright not installed | Tell user: `pip install playwright && playwright install chromium` |
| Instagram post fails | Show the error. Tell user the card is saved at the path shown and they can post manually. |
| Git push fails | Check network/auth. Ensure `../cinemaoffear/` repo exists and is configured for push. |
