# Skill Assignment Procedure

Two-stage procedure for assigning skills to task drafts.
Stage 1 is an automatic weighted-average scorer executed by `generate-task-json`.
Stage 2 is an LLM review step embedded in the `breakdown-tasks` worker.

## Design Rationale

The skill assignment system is designed as a deterministic, auditable, and controllable baseline augmented by LLM semantic review. Key design decisions:

- **Weighted scoring** (vs. FlashRank or LLM-based): Provides deterministic, reproducible results without external model dependencies. Each run produces identical output given identical input. This forms the baseline assignment.
- **Keyword overlap (0.50)** is weighted highest because task purpose and context text are the most reliable indicators of required skill. If a task says "add input validation", the keyword-triggered skill match is the strongest signal.
- **Class match (0.25)** and **tag similarity (0.25)** are supporting signals that refine the ranking. Class match ensures operation/documentation skills are preferred for executable tasks; tag similarity catches semantic matches the keyword overlap might miss.
- **Threshold gating** (vs. top-k) was chosen because it guarantees a minimum quality bar independent of the candidate pool size. With top-k, a large pool of low-quality matches would still produce assignments; threshold gating ensures only sufficiently relevant skills are assigned.
- The **class filter** restricts to `operation` and `documentation` because only these classes have executable worker workflows. Other classes (planning, inline, orchestrated, delegated) are handled at the delegator or orchestrator level and should not be assigned per-task.
- **No synthetic fallback**: If no skill reaches the threshold, the pipeline leaves the skills array empty rather than assigning a misleading skill. The worker then executes the packet directly without specialized skill guidance.
- **LLM review augments the baseline**: The deterministic scorer is reproducible but cannot reason semantically. The LLM review step corrects assignments where lexical matching produces poor results — it does not replace the scorer.

## Prerequisites

1. Standard input contains a root `{summary, tasks}` object that matches `schema/task-input.schema.json`.
2. Each task is a `TaskDraft` and does **not** include a `skills` field.
3. Available skills can be discovered by `collect-skills`.

## Stage 1 — Deterministic Baseline

### 1. Validate TaskDraft Input

`generate-task-json` validates standard input against `schema/task-input.schema.json`.
Any task containing `skills` is invalid at this stage.

### 2. Discover Candidate Skills

By default, `generate-task-json` discovers all skills and filters candidates to these classes:

- `operation`
- `documentation`

The default class filter is canonical for production workflow runs.

### 3. Score Candidate Skills

By default, `generate-task-json` uses deterministic weighted scoring. Each skill
is scored from three normalized criteria:

- keyword overlap between task text and skill `name`/`description`/`tags`
- class match bonus between inferred task class and skill `class`
- tag similarity between task tokens and skill `tags`

Default formula:

```text
final_score = 0.50 * keyword_overlap
            + 0.25 * class_match
            + 0.25 * tag_similarity
```

Task text is built from `purpose`, `context`, and `expectedOutput`.

### 4. Select Skills

Selection rules:

1. Select every skill with score greater than or equal to the canonical threshold.
2. Leave the skills array empty when no candidate reaches the threshold.
3. Keep at most the three highest-ranked selected skills.
4. Do not synthesize fallback skills; selected skills must come from discovered skills.

### 5. Write Final TaskPackets

`generate-task-json` writes the output path with `skills` arrays added to each task.
The resulting object validates against `schema/task-packet.schema.json`.

## Stage 2 — LLM Review and Self-Correction

After `generate-task-json` writes the state file, the `breakdown-tasks` worker
performs a mandatory LLM review before publishing the path under `Deliverable`.

### 1. Read Generated State File

Read the `.tasks/<epoch-milliseconds>-<summary-slug>.json` file written by
`generate-task-json` into `TASK_PACKET_JSON`.

### 2. Load Filtered Skill Inventory

Run `uv run --directory ~/.config/opencode/scripts/python collect-skills --class operation --class documentation`.
This produces the exact same candidate pool that `generate-task-json` used.
Load the returned JSON array into `SKILL_INVENTORY`.

### 3. Reason Across the Full Task List

For every task in `TASK_PACKET_JSON`, evaluate:

- **Semantic fit**: Does each assigned skill's purpose match the task's purpose, context, and expected output? Lexical overlap may indicate a match where none exists, or miss a match where terminology differs.
- **Cross-task consistency**: Do related tasks (variants of the same work, sequential pipeline steps) receive aligned skill assignments? Minor wording differences should not produce divergent assignments for substantively similar tasks.
- **Empty-assignment scrutiny**: When no skill reaches the threshold, confirm direct packet execution is appropriate and do not force an unrelated assignment.

### 4. Constraints on Changes

- Only `skills` arrays may be modified.
- All other fields (`purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `verification`, `expectedOutput`) must remain byte-identical to the `generate-task-json` output.
- Every assigned skill must have a matching entry in the `SKILL_INVENTORY`.
- Each task must retain 0–3 semantically appropriate skills (schema constraint, enforced by validation).
- If no correction is warranted for a given task, leave its `skills` array unchanged.

### 5. Write Corrected State File

Write the modified `TASK_PACKET_JSON` back to the same `.tasks/` path,
overwriting the deterministic output.

### 6. Schema Validation with Self-Correction Loop

Validate the corrected state file:

```bash
uv run --directory ~/.config/opencode/scripts/python validate-task-structure \
  --state-file "$GENERATED_PATH" \
  --schema "$PWD/skills/breakdown-tasks/schema/task-packet.schema.json"
```

If validation succeeds (exit code 0, `{"valid": true}`), proceed to return.

If validation reports errors:

1. Read the error messages from the validator output.
2. Fix only the `skills` arrays to resolve the reported violations.
3. Write the corrected JSON back to the state file.
4. Re-run validation.
5. Repeat until validation succeeds or an unrecoverable skills-only error is identified.

If an error cannot be resolved by changing only `skills` arrays (e.g., a structural
schema violation outside the `skills` field), return `BLOCKED: <reason>`.

Do not fall back to the uncorrected deterministic output — the corrected output
must pass validation.

## Output Format

The final output is a JSON object with:

- `summary` — request summary from decomposition.
- `tasks` — ordered TaskPacket array, each with a `skills` array containing zero to three names.

The worker places the relative `.tasks/<epoch-milliseconds>-<summary-slug>.json` path under `Deliverable` in its result envelope.
`dispatch-decompose` validates the envelope and returns that path to the delegator, not the raw JSON.
The state file at that path contains the LLM-reviewed skill assignments.
