# Pipeline Overview

The breakdown pipeline uses a shared `.tasks` state file.
Scripts read and write that file in sequence; the worker returns the relative path to the final state file.

## Design Philosophy

The breakdown pipeline operates in four self-contained phases.
Each phase loads its own dependencies — content loaded in an earlier phase is evicted
from the context window by the large decomposition output and must not be referenced later.

1. **Phase A — Decomposition** (LLM-driven) — Reads planning-skill files and produces structure-aware TaskDraftList JSON.
2. **Phase B — Script Assignment** (`generate-task-json`) — Derives slug, assigns skills, validates, writes task file.
3. **Phase C — Audit** (LLM-driven) — Loads fresh inventory, reviews script-assigned skills for semantic correctness.
4. **Phase D — Validation** (`validate-task-structure --auto-fix`) — Validates and auto-fixes skills arrays, returns path.

This four-phase separation exists for three reasons:

- **Determinism** — Each phase is independently reproducible. If a phase fails, you can re-run from that phase without affecting upstream work.
- **Context-window awareness** — The large decomposition output (Phase A) would evict earlier planning context. Each phase loads fresh dependencies, preventing stale references.
- **Error isolation** — A failure in one phase (e.g., corrupt LLM output, script-assigned skill mismatch) is caught before it propagates to the next phase.

## Script Order

1. **Phase A — Decomposition** — LLM produces `{summary, tasks}` TaskDraftList JSON (no skills, no slug).
2. **Phase B — Script Assignment** — `generate-task-json` reads TaskDraftList from stdin, derives the kebab-case slug, assigns operation and documentation skills via deterministic weighted scoring, validates against schemas, and atomically writes `.tasks/<epoch>-<slug>.json`.
3. **Phase C — Audit** — LLM loads fresh `collect-skills` inventory, reviews every script-assigned skill for semantic correctness, inventory existence, circular self-references, cross-task consistency, and fallback scrutiny. Only skills arrays may be modified.
4. **Phase D — Validation** — `validate-task-structure --auto-fix` validates the corrected task file, auto-fixes skills-only errors (trim to max 3, remove empty strings, deduplicate), and returns the relative path.

## Uniform CLI Convention

- `generate-task-json` reads root JSON from standard input.
- `generate-task-json` writes to the directory supplied through `--output-dir`.
- `validate-task-structure` reads the task file via `--state-file` and validates its structure.
- `validate-task-structure --auto-fix` resolves skills-only errors deterministically (trim to max 3, remove empty strings, deduplicate).
- Errors are written to stderr.
- Exit 0 on success.
- Exit non-zero on user, validation, file, or runtime errors.

## Pipeline Walkthrough

### Phase A — Decomposition

*Why: The LLM produces structure-aware task drafts with domain understanding. Skills are intentionally absent at this stage — the LLM should focus on work boundaries, not skill matching. Planning skills are loaded first for context, then evicted.*

- **Action:** LLM produces decomposition output.
- **State File I/O:** None.
- **Steps:**
  1. Run `collect-skills --class planning` to load planning skill inventory.
  2. Read the `path` for each materially relevant planning skill for domain understanding.
  3. Read authoring reference docs for task granularity and anti-patterns.
  4. Produce a schema-valid `{summary, tasks}` object where each task includes `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `expectedOutput`, and optional `verification`.
  5. Do **not** write skills. Do **not** derive a summary slug. Do **not** write files.
- **Output:** `TASK_DRAFT_JSON` (captured in memory for Phase B).

### Phase B — Script Assignment

*Why: Skills must be assigned by a deterministic script to ensure consistency, avoid hallucinated assignments, and maintain an audit trail of which skills were selected and why.*

- **Action:** Pipe `TASK_DRAFT_JSON` through `generate-task-json`.
- **State File I/O:** Write.
- **Command:**

```bash
uv run --directory ~/.config/opencode/scripts/python generate-task-json --output-dir "$PWD/.tasks" <<'TASK_DRAFT_JSON'
<complete TaskDraftList JSON>
TASK_DRAFT_JSON
```

`generate-task-json` loads schemas from `~/.config/opencode/skills/breakdown-tasks/schema/`, validates drafts before assignment, derives the kebab-case slug from the summary field, discovers `operation` and `documentation` skills via deterministic weighted scoring, validates against both schemas, and atomically creates `.tasks/<epoch>-<slug>.json` in the supplied output directory.

The script outputs the relative path of the created file. The worker captures this as `GENERATED_PATH` and reads the file into `TASK_PACKET_JSON`.

### Phase C — Audit

*Why: Script-assigned skills are deterministic but may not be semantically correct. A human-quality review catches inventory mismatches, circular self-references, and poor fallback selections.*

- **Action:** LLM reviews every script-assigned skill for semantic correctness.
- **State File I/O:** Read/write (corrects skills arrays in `GENERATED_PATH`).
- **Steps:**
  1. Run `collect-skills --class operation --class documentation` for a fresh executable skill inventory. Do not rely on any earlier skill data.
  2. For each task in `TASK_PACKET_JSON`, evaluate: inventory check, semantic fit, circular self-references, cross-task consistency, and fallback scrutiny.
  3. Only skills arrays may be modified. All other fields stay byte-identical.
  4. Every assigned skill must exist in the fresh inventory. Each task must retain 1–3 skills.
  5. Write the corrected `TASK_PACKET_JSON` back to `GENERATED_PATH`.

### Phase D — Validation

*Why: The corrected task file must be structurally valid before it can be consumed by the delegator. Automated validation catches any remaining structural issues.*

- **Action:** Run `validate-task-structure --auto-fix`.
- **State File I/O:** Read/write (auto-fix may modify skills arrays).
- **Command:**

```bash
uv run --directory ~/.config/opencode/scripts/python validate-task-structure \
  --state-file "$PWD/$GENERATED_PATH" \
  --schema "$PWD/skills/breakdown-tasks/schema/task-packet.schema.json" \
  --auto-fix
```

The `--auto-fix` flag resolves skills-only errors deterministically: trim to max 3, remove empty strings, and deduplicate.

If validation reports errors that `--auto-fix` cannot resolve, the worker fixes only the skills arrays manually, re-writes to `GENERATED_PATH`, re-runs validation, and repeats until success or an unrecoverable error is identified.

### Return Relative Path

- **Action:** Return the state file location to the delegator.
- **Expected output:** `.tasks/<epoch>-<slug>.json`

Return `GENERATED_PATH` as a single string.
