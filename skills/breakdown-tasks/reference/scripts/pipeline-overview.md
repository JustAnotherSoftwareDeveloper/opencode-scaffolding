# Pipeline Overview

Chain all five scripts in a strict sequence.
Each script reads from and writes to a shared `.tasks` state file rather than piping between stages.

## Script Order

1. **`generate-uuids`** — Produce UUID v4 identifiers, one per task.
   See `./generate-uuids.md`.
2. **`validate-task-structure`** — Validate required keys, types, lengths, and step numbering.
   See `./validate-task-structure.md`.
3. **`validate-dependencies`** — Verify all dependency references exist and the graph is acyclic.
   See `./validate-dependencies.md`.
4. **`topological-sort`** — Order tasks by dependency depth using Kahn's algorithm.
   See `./topological-sort.md`.
5. **`validate-and-format-output`** — Perform final schema validation and emit raw JSON.
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

| Step | Action | State File I/O | Command / Description |
|------|--------|----------------|-----------------------|
| 1 | **Initialize state file** | Write | `STATE_FILE=~/.config/opencode/.tasks/<epoch>-<slug>.json`; write `{"summary":"","tasks":[]}` |
| 2 | **Generate UUIDs** | Read/Write | `uv run --directory "$SCRIPTS_PYTHON" generate-uuids --state-file "$STATE_FILE" <N>` — reads task list from state file, appends a UUID to each task's `id` field, writes result back |
| 3 | **Populate task fields** | Write (manual) | Fill in remaining task fields — `title`, `description`, `priority`, `context` — by editing the state file directly |
| 4 | **Validate task structure** | Read-only | `uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"` — loop on exit 1 until valid |
| 5 | **Populate dependencies** | Write (manual) | Add dependency references between tasks by editing the state file directly |
| 6 | **Validate dependencies** | Read-only | `uv run --directory "$SCRIPTS_PYTHON" validate-dependencies --state-file "$STATE_FILE"` — loop on exit 1 until valid |
| 7 | **Topological sort** | Read/Write | `uv run --directory "$SCRIPTS_PYTHON" topological-sort --state-file "$STATE_FILE"` — reads task list, reorders by dependency depth, writes sorted result back |
| 8 | **Assemble full output** | Read/Write (manual) | Read the current state from `"$STATE_FILE"`, build a JSON object with `summary` and sorted `tasks`, write back |
| 9 | **Validate and format output** | Read-only | `uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"` — loop on exit 1 until valid |
| 10 | **Return raw JSON** | Read-only | Read `"$STATE_FILE"` and emit its raw JSON contents verbatim — no preamble, no fences, no commentary |

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

# Step 1: Generate UUIDs (one per identified task)
uv run --directory "$SCRIPTS_PYTHON" generate-uuids --state-file "$STATE_FILE" 5

# Step 2: Validate task structure (loop on exit 1)
until uv run --directory "$SCRIPTS_PYTHON" validate-task-structure \
  --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"; do
  echo "Fix task structure errors, then re-run this step." >&2
done

# Step 3: Validate dependencies (loop on exit 1)
until uv run --directory "$SCRIPTS_PYTHON" validate-dependencies \
  --state-file "$STATE_FILE"; do
  echo "Fix dependency errors, then re-run this step." >&2
done

# Step 4: Topological sort (replaces task list in state file with sorted order)
uv run --directory "$SCRIPTS_PYTHON" topological-sort --state-file "$STATE_FILE"

# Step 5: Validate and format output (loop on exit 1)
until uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output \
  --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH"; do
  echo "Fix output validation errors, then re-run this step." >&2
done

# Step 6: Emit raw JSON from state file
cat "$STATE_FILE"
```