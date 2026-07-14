# Pipeline Overview

The breakdown pipeline uses a shared `.tasks` state file.
Scripts read and write that file in sequence; the worker returns the relative path to the final state file.

## Design Philosophy

The breakdown pipeline uses a controlled factory model: each step adds one layer of structure to a shared state file.

1. **Task drafts** (LLM decomposition) — Produces structure-aware content.
2. **Final packets** (generate-task-json) — Assigns skills, validates output, and creates the local task file.

This separation exists for three reasons:

- **Determinism** — Each step is independently reproducible. If a step fails, you can re-run from that step without affecting upstream work.
- **Auditability** — The state file at each step can be inspected, versioned, or compared across runs.
- **Error isolation** — A failure in one step (e.g., corrupt LLM output) is caught before it propagates to the next step.

## Script Order

1. **LLM decomposition** — Produce `TaskDraft` objects without `skills`.
2. **`generate-task-json`** — Validate TaskDraft input, assign skills, validate final TaskPackets, and create the output file.

`validate-task-structure` is not part of the current production pipeline.

## Uniform CLI Convention

- `generate-task-json` reads root JSON from standard input.
- `generate-task-json` writes to the directory supplied through `--output-dir`.
- Errors are written to stderr.
- Exit 0 on success.
- Exit non-zero on user, validation, file, or runtime errors.

## Pipeline Walkthrough

### Step 1: Populate TaskDrafts

*Why: The LLM produces structure-aware task drafts with domain understanding. Skills are intentionally absent at this stage — the LLM should focus on work boundaries, not skill matching.*

- **Action:** LLM writes decomposition output.
- **State File I/O:** None.
- **Description:** Write `{summary, tasks}` where each task includes `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `expectedOutput`, and optional `verification`.
  Do **not** write `skills`.

### Step 2: Generate Final Task JSON

*Why: Skills must be assigned by a deterministic script to ensure consistency, avoid hallucinated assignments, and maintain an audit trail of which skills were selected and why.*

- **Action:** Populate `skills` arrays and validate final TaskPackets.
- **State File I/O:** Write.
- **Command:**

```bash
uv run --project ~/.config/opencode/scripts/python generate-task-json \
  --summary-slug "$SUMMARY_SLUG" \
  --output-dir "$CWD/.tasks" < draft.json
```

`generate-task-json` loads schemas from `~/.config/opencode/skills/breakdown-tasks/schema/`, validates drafts before assignment, discovers `operation` and `documentation` skills, and atomically creates `.tasks/<summary-slug>.json` in the supplied output directory.

### Step 3: Return Relative Path

- **Action:** Return the state file location to the delegator.
- **Expected output:** `.tasks/<summary-slug>.json`

Return `$REL_FILE` as a single string.
