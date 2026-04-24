# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## Project: Cinema of Fear

A horror film review and rating system producing content for the **3C Films** brand. Outputs include rating cards and other media assets for social distribution.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## Token Optimization: Efficiency Rules

These practices reduce token waste and keep the project moving fast. They're not optional—follow them to stretch your usage budget.

### Don't Read These Directories (Always Disposable)
- **`.tmp/`** — temporary generated files, intermediate exports, scraped data. Never read without explicit reason.
- **`tests/`, `*.jpg`, `*.png`, `*.mp4`** — binary assets and test files only read if debugging a specific test failure.
- **`.superpowers/`, `.claude/`** — internal plugin and session files. Skip entirely.
- **Large files without context** — before reading a 500-line file, ask "do I really need this?" or read only the relevant section (use `offset` + `limit` in Read tool).

### Be Specific, Not Vague

**Vague → Token Waste:**
- ❌ "Help me debug the workflow"
- ❌ "Review the codebase"
- ❌ "Build a new tool for this"

**Specific → Fast Execution:**
- ✅ "The `voice_review.yml` workflow fails at Step 3 (parse_voice_review). Error: [paste exact error]. Fix the tool."
- ✅ "Check if `tools/parse_voice_review.py` validates year as int or None"
- ✅ "Add a `--batch-size` flag to `tools/scrape_single_site.py` following the pattern in `tools/send_sms.py`"

**Pattern:** File path + exact location (line number or section) + what's broken + reference to similar code = Claude works fast with minimal reads.

### Name the Tool, Provide the Structure

Don't ask Claude to figure out which tool to use. Instead:
1. **Name the tool explicitly:** "Run `tools/parse_voice_review.py`" (not "figure out how to parse this")
2. **Show the input shape:** Provide the data structure upfront (JSON example, dict keys, expected types)
3. **Report errors with precision:** "Line 45, `json.JSONDecodeError: ...` when parsing X" (exact line, exact tool, exact input that broke it)

This keeps Claude focused on execution, not exploration.

### Batch Work, Don't Serialize

Instead of asking one task at a time:
- **Bad:** "Add a card for Scream. Then add one for Hereditary. Then add one for The Ring." (3 planning cycles)
- **Good:** "Add cards for these 3 films in one batch: `[{"title": "Scream", ...}, {...}, {...}]`. Run `tools/generate_card.py` once per item." (1 planning cycle)

**Benefits:**
- Reduces token overhead by 2–3x
- One execution context instead of three
- Faster iteration

Provide batch data as JSON arrays when possible, not prose descriptions.

### What You Handle Without Asking Claude

These tasks take <30 seconds. Do them first—don't ask Claude:

- **File structure questions** → `ls tools/` or `find` command
- **Credentials/secrets** → Check `.env` yourself; never paste values into requests
- **Tool availability** → List `tools/` directory; don't ask "do we have a tool for X?"
- **CI/CD failures** → Read GitHub Actions logs directly at `https://github.com/ErcoleHub/cinemaoffear/actions`; paste the exact error here
- **Workflow questions** → Read `workflows/*.md` first; only escalate if the SOP needs updating
- **Recent commits** → Use `git log --oneline -20`; don't ask for history summaries

**Rule of thumb:** If you can verify it in <30 seconds (file system, error logs, `.env`, GitHub UI), do that first. Only ask Claude if you need reasoning or execution.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Slides, etc.) where I can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
.env            # API keys and environment variables (NEVER store secrets anywhere else)
credentials.json, token.json  # Google OAuth (gitignored)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
