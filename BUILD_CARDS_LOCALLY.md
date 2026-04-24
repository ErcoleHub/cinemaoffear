# Building Cards Locally in VS Code

## Setup (One Time)

1. **Open Terminal in VS Code** (`Ctrl+`` or `Cmd+`` on Mac)
2. **Activate the Python environment:**
   ```bash
   source .venv/bin/activate
   ```

## Generate a Card

Run the script with movie details:

```bash
python build_card.py \
  --title "Movie Title" \
  --year 2024 \
  --atmosphere 5 \
  --characters 4 \
  --originality 5 \
  --script 4 \
  --gore 3 \
  --sub-genre supernatural \
  --recommendation theater \
  --review "Your review text here"
```

### Arguments

| Flag | Required | Example |
|------|----------|---------|
| `--title` | ✅ | "Hereditary" |
| `--year` | ❌ | 2018 |
| `--atmosphere` | ✅ | 5 (1-5) |
| `--characters` | ✅ | 4 (1-5) |
| `--originality` | ✅ | 5 (1-5) |
| `--script` | ✅ | 4 (1-5) |
| `--gore` | ✅ | 3 (1-5) |
| `--sub-genre` | ✅ | slasher, supernatural, psychological, body_horror, found_footage, creature_feature, zombie, survival_horror, vampire_werewolf, torture_extreme, comedy, sci_fi |
| `--recommendation` | ✅ | skip, stream, theater |
| `--review` | ✅ | "Your review (max 250 chars)" |

## Output

Cards are saved to `.tmp/card_*.png`

View them directly in VS Code's file explorer or your image viewer.

## Examples

**Hereditary (2018):**
```bash
python build_card.py --title "Hereditary" --year 2018 --atmosphere 5 --characters 4 --originality 5 --script 4 --gore 3 --sub-genre supernatural --recommendation theater --review "Ari Aster's debut is a masterwork of grief and dread that lingers for days."
```

**The Shining (1980):**
```bash
python build_card.py --title "The Shining" --year 1980 --atmosphere 5 --characters 5 --originality 5 --script 5 --gore 3 --sub-genre psychological --recommendation theater --review "Kubrick's masterpiece of psychological horror that redefined the genre."
```

**A Quiet Place (2018):**
```bash
python build_card.py --title "A Quiet Place" --year 2018 --atmosphere 5 --characters 4 --originality 4 --script 4 --gore 2 --sub-genre creature_feature --recommendation theater --review "Innovative creature-feature that weaponizes silence as its greatest threat."
```
