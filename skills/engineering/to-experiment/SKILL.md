---
name: to-experiment
description: Spin up a sibling `<main>-experiments` repo for throwaway exploration work — `uv`-managed Python project, plain `.py` scripts, no notebooks. Use when the user wants to explore data, prove out a query, or do anything experimental that shouldn't live in the main repo. Triggers on "spin up an experiments repo", "explore this in a sandbox", "set up a scratch project".
---

# To Experiment

Create a sibling repo to the current project for throwaway / exploratory work, so experiments don't pollute the main repo's git history or dependencies.

## When to trigger

The user wants a place to:

- Prototype a query or API call before adding it to the main pipeline
- Pull data into a script and poke at it
- Try an approach without committing to it in the production codebase
- Reproduce a bug in isolation

Do NOT trigger for:

- Real feature work that belongs in the main repo
- A test fixture (those belong in the main repo's test suite)
- A one-off script that the user clearly wants to keep in the main repo
- A single design question with a concrete answer — that's the `/prototype` skill, which lives *inside* the main repo and produces one throwaway artifact. This skill is for open-ended exploration that needs its own project.

## How

### Step 1: Confirm the target path

The default sibling location is:

```
<parent-of-main>/<main-repo-name>-experiments/
```

For example, if the user is in `/Users/user/Desktop/Code/fb-reach-pipeline/`, the experiments repo lands at `/Users/user/Desktop/Code/fb-reach-pipeline-experiments/`.

Detect the main repo name and parent with:

```bash
MAIN_PATH=$(git rev-parse --show-toplevel)
MAIN_NAME=$(basename "$MAIN_PATH")
PARENT=$(dirname "$MAIN_PATH")
TARGET="$PARENT/$MAIN_NAME-experiments"
```

If `$TARGET` already exists, **do not overwrite**. Ask the user: open the existing one, append a new dated subdirectory, or pick a different name.

### Step 2: Scaffold the project

Create the directory and initialise:

```bash
mkdir -p "$TARGET/scripts" "$TARGET/data"
cd "$TARGET"
git init -q
uv init --no-readme --no-pin-python -q .
```

`uv init` creates `pyproject.toml` and `.python-version`. Customise the resulting `pyproject.toml`:

```toml
[project]
name = "<main>-experiments"
version = "0.1.0"
description = "Throwaway experiments adjacent to <main>."
requires-python = ">=3.11"
dependencies = []
```

### Step 3: Write the scaffold files

#### `.gitignore`

```
.venv/
__pycache__/
*.pyc
.env
.env.local
.ipynb_checkpoints/
data/*
!data/.gitkeep
.DS_Store
```

#### `data/.gitkeep`

Empty file. Keeps the directory in git so scripts have somewhere to write CSVs / parquet / etc. without committing the contents.

#### `.env.example`

```
# Copy to .env and fill in. .env is gitignored.
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json
```

Keep this minimal — do not bake in BigQuery or any other client by default. Add only what the experiment actually needs.

#### `README.md`

```markdown
# <main>-experiments

Throwaway / exploratory work adjacent to [<main>](../<main>).

## Setup

\`\`\`bash
uv sync
cp .env.example .env  # fill in any credentials this experiment needs
\`\`\`

## Layout

- `scripts/` — one `.py` file per experiment. Name them by date or topic, not by feature (these are throwaway).
- `data/` — local data files. Gitignored.

## When to graduate code out of here

If a script becomes load-bearing — used more than once, or by anyone else — move it into [<main>](../<main>). Experiments repo is **single-use scratch**.
```

Substitute `<main>` with the actual main repo name throughout.

#### `scripts/01-first-experiment.py`

```python
"""First experiment — rename or replace.

Run with:  uv run scripts/01-first-experiment.py
"""

def main() -> None:
    print("hello from <main>-experiments")


if __name__ == "__main__":
    main()
```

### Step 4: Confirm and report

Print to the user:

- The path of the new repo
- The `uv run` command for the example script
- A reminder that the repo is not yet pushed anywhere (and ask whether they want a GitHub repo created — only do this if they say yes)

Do **not** push to a remote, create a GitHub repo, or make the first commit unless the user explicitly asks. Leave the repo in a clean `git init`'d state with files unstaged.

## What good looks like

- A new sibling repo, `uv`-managed, with `scripts/`, `data/`, `.env.example`, and a README pointing back to the main repo.
- The user can `uv run scripts/01-first-experiment.py` immediately.
- No notebooks, no Jupyter, no BigQuery client baked in — just a clean Python project.

## What to avoid

- **Don't add dependencies the user hasn't asked for.** No `pandas`, no `google-cloud-bigquery`, no `requests`. Add them as the experiment needs them.
- **Don't put the experiments repo inside the main repo.** Sibling, not nested. Nested would pollute the main repo's worktree.
- **Don't auto-commit or auto-push.** The user decides when to make the first commit.
- **Don't scaffold a notebook.** Plain `.py` scripts only.

## Related skills

- For one sharp design question, prefer `/prototype` in the main repo — a logic TUI or a small real result set answers it faster than a whole sandbox project.
- Once an experiment proves something worth keeping, graduate it: run `/to-tickets` in the main repo to turn the finding into implementable tickets (or `/to-spec` first if the finding is big enough to need a spec).
