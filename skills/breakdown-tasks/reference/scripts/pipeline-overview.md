# Pipeline Overview

Chain both scripts in a strict sequence.
Each script reads from and writes to a shared `.tasks` state file rather than piping between stages.

## Script Order

1. **`validate-task-structure`** — Validate required keys, types, lengths, and step numbering.
   See `./validate-task-structure.md`.
2. **`validate-and-format-output`** — Perform final schema validation and emit raw JSON.
   See `./validate-and-format-output.md`.

## Uniform CLI Convention

All scripts follow the same convention.

- Read JSON from `--state-file <path>` or stdin.
- Write JSON to `--state-file <path>` (if the script transforms data) or stdout (if the script emits output).
- Write error messages to stderr.
  Never pollute stdout with errors.
- Exit 0 on success.
- Exit 1 on validation failure or semantic error.
- Exit 2 on parse, file, or internal error.

## Pipeline Walkthrough

The ordered steps below show the full pipeline flow.
Each step documents its State File I/O mode:

- **Write** — creates or overwrites the state file.
- **Read/Write** — reads from the state file, processes, and writes back.
- **Read-only** — reads from the state file without modifying it.

### Step 1: Initialize State File
- **Action:** Initialize state file
- **State File I/O:** Write
- **Command:** `STATE_FILE=~/.config/opencode/.tasks/<epoch>-<slug>.json`; write `{"summary":"","tasks":[]}`

### Step 2: Populate Task Fields
- **Action:** Populate task fields manually
- **State File I/O:** Write (manual)
- **Description:** Fill in remaining task fields — `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput` — by editing the state file directly

### Step 3: Validate Task Structure
- **Action:** Validate task structure
- **State File I/O:** Read-only
- **Command:** `uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"` — loop on exit 1 until valid

### Step 4: Assemble Full Output
- **Action:** Assemble full output
- **State File I/O:** Read/Write (manual)
- **Description:** Read the current state from `"$STATE_FILE"`, build a JSON object with `summary` and the task list, write back

### Step 5: Validate and Format Output
- **Action:** Validate and format output
- **State File I/O:** Read-only
- **Command:** `uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"` — loop on exit 1 until valid

### Step 6: Return Raw JSON
- **Action:** Return raw JSON
- **State File I/O:** Read-only
- **Description:** Read `"$STATE_FILE"` and emit its raw JSON contents verbatim — no preamble, no fences, no commentary

## Shell Pipeline Integration

Use these commands to invoke each script step by step.
All scripts operate on a shared state file instead of piping between stages.

```bash
# --- Setup: derive and initialize the state file ---
EPOCH=$(date +%s)
SLUG="my-decomposition"
STATE_FILE="$HOME/.config/opencode/.tasks/${EPOCH}-${SLUG}.json"
mkdir -p "$(dirname "$STATE_FILE")"
echo '{"summary":"","tasks":[]}' > "$STATE_FILE"

# Step 1: Validate task structure (loop on exit 1)
until uv run --directory "$SCRIPTS_PYTHON" validate-task-structure \
  --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"; do
  echo "Fix task structure errors, then re-run this step." >&2
done

# Step 2: Validate and format output (loop on exit 1)
until uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output \
  --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"; do
  echo "Fix output validation errors, then re-run this step." >&2
done

# Step 3: Emit raw JSON from state file
cat "$STATE_FILE"
```