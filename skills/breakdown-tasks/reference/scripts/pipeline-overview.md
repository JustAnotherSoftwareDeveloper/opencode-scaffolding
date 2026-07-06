# Pipeline Overview

The breakdown pipeline uses a shared `.tasks` state file.
Scripts read and write that file in sequence; the worker returns the relative path to the final state file.

## Script Order

1. **`init-state-file`** — Create an empty state file and print its absolute path.
2. **LLM decomposition** — Write `TaskDraft` objects to the state file without `skills`.
3. **`assign-skills`** — Validate TaskDraft input, rank candidate skills with FlashRank, and add `skills` arrays.
4. **`validate-and-format-output`** — Validate final TaskPacket output and emit JSON for inspection.

`validate-task-structure` is not part of the current production pipeline.

## Uniform CLI Convention

- Scripts read JSON from `--state-file <path>` when applicable.
- Transforming scripts write updates back to `--state-file <path>`.
- Formatting/validation scripts emit JSON to stdout on success.
- Errors are written to stderr.
- Exit 0 on success.
- Exit non-zero on user, validation, file, or runtime errors.

## Pipeline Walkthrough

### Step 1: Initialize State File

- **Action:** Create the state file.
- **State File I/O:** Write.
- **Command:**

```bash
STATE_FILE=$(uv run --directory ~/.config/opencode/scripts/python init-state-file \
  --output-dir ~/.config/opencode/.tasks)
REL_FILE=".tasks/$(basename "$STATE_FILE")"
```

The filename pattern is `<epoch>-decomposition.json`.
The delegator receives `$REL_FILE`.

### Step 2: Populate TaskDrafts

- **Action:** LLM writes decomposition output.
- **State File I/O:** Write.
- **Description:** Write `{summary, tasks}` where each task includes `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `expectedOutput`, and optional `verification`.
  Do **not** write `skills`.

### Step 3: Assign Skills

- **Action:** Populate `skills` arrays automatically.
- **State File I/O:** Read/Write.
- **Command:**

```bash
uv run --directory ~/.config/opencode/scripts/python assign-skills \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-input.schema.json
```

`assign-skills` discovers candidate skills internally, filters to `operation` and `documentation` by default, ranks with FlashRank raw logits, applies floor-only gating, and guarantees at least one discovered/indexed skill per task.

### Step 4: Validate and Format Output

- **Action:** Validate final TaskPacket output.
- **State File I/O:** Read-only.
- **Command:**

```bash
uv run --directory ~/.config/opencode/scripts/python validate-and-format-output \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

If validation fails, fix the decomposition or assignment issue and re-run from the appropriate step.

### Step 5: Return Relative Path

- **Action:** Return the state file location to the delegator.
- **Expected output:** `.tasks/<epoch>-decomposition.json`

Return `$REL_FILE` as a single string.
