# Pipeline Overview

The breakdown pipeline uses a shared `.tasks` state file.
Scripts read and write that file in sequence; the worker returns the relative path to the final state file.

## Design Philosophy

The breakdown pipeline uses a controlled factory model: each step adds one layer of structure to a shared state file.

1. **Empty file** (init-state-file) — Establishes the shared artifact.
2. **Task drafts** (LLM decomposition) — Populates the structure-aware content.
3. **Assigned skills** (assign-skills) — Adds deterministic skill selections.
4. **Validated packets** (validate-and-format-output) — Confirms structural correctness.

This separation exists for three reasons:

- **Determinism** — Each step is independently reproducible. If a step fails, you can re-run from that step without affecting upstream work.
- **Auditability** — The state file at each step can be inspected, versioned, or compared across runs.
- **Error isolation** — A failure in one step (e.g., corrupt LLM output) is caught before it propagates to the next step.

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

*Why: Creates the shared file handle that all subsequent stages read and write. The empty structure prevents partial-write races and gives the pipeline a well-defined starting point.*

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

*Why: The LLM produces structure-aware task drafts with domain understanding. Skills are intentionally absent at this stage — the LLM should focus on work boundaries, not skill matching.*

- **Action:** LLM writes decomposition output.
- **State File I/O:** Write.
- **Description:** Write `{summary, tasks}` where each task includes `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `expectedOutput`, and optional `verification`.
  Do **not** write `skills`.

### Step 3: Assign Skills

*Why: Skills must be assigned by a deterministic script to ensure consistency, avoid hallucinated assignments, and maintain an audit trail of which skills were selected and why.*

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

*Why: Schema validation catches structural errors (missing fields, wrong types, constraint violations) before the output reaches the delegator. Without this gate, malformed packets would cause worker failures downstream.*

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
