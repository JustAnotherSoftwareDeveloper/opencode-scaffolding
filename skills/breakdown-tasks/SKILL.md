---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items. Separates planning from execution: the LLM decomposes, the script assigns skills."
tags: [task-decomposition, atomic-tasks, task-planning, request-analysis, generate-task-json, delegation-pipeline]
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
Operates in four self-contained phases. Each phase loads its own dependencies —
do not reference content loaded in an earlier phase. It will have been evicted
from context by the large decomposition output.

## Input Contract

Read `## PURPOSE` and `## DETAILS`.
Return `BLOCKED: missing PURPOSE or DETAILS` if either section is missing.

## Phase A — Decomposition

Goal: produce a TaskDraftList JSON object (no skills, no slug).

Step A1. Run collect-skills for planning context:
    ```bash
    uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning
    ```
    Read the JSON output. This gives you the available planning skills and their
    descriptions — use these to understand what domain context is available for
    shaping your decomposition.

Step A2. Read the `path` for each materially relevant planning skill from the
    returned metadata.
    Read these additional context files directly instead of using the skill tool.
    Understand the class taxonomy, platform conventions, and authoring rules
    they define. Use this knowledge to shape task boundaries.

Step A3. Read the authoring reference docs:
    `skills/breakdown-tasks/reference/authoring/core-rules.md`
    `skills/breakdown-tasks/reference/authoring/task-granularity.md`
    `skills/breakdown-tasks/reference/authoring/anti-patterns.md`
    `skills/breakdown-tasks/reference/authoring/context-preservation.md`

Step A4. Produce a schema-valid `{summary, tasks}` object.
    Each task must have: purpose, context, filesToRead, filesToWrite,
    executionInstructions, expectedOutput, and optional verification.
    Keep every task atomic — one logical change, one output artifact,
    one action verb. Factor planning-skill context into task boundaries.
    Copy relevant goals and constraints verbatim into each context.
    Do not add skills. Do not derive a summary slug. Do not write files.

Step A5. Store the complete JSON in `TASK_DRAFT_JSON` for Phase B.

After Phase A, the planning skills and authoring refs will be evicted from
context by the decomposition output. This is expected — later phases do not
depend on them.

## Phase B — Script Assignment

Goal: pipe `TASK_DRAFT_JSON` through `generate-task-json` to assign skills,
derive the slug, validate, and write the task file.

Step B1. Invoke the script through the bash tool with a quoted here-document.
    Replace the body below with the complete JSON from `TASK_DRAFT_JSON`.
    Do not rely on `TASK_DRAFT_JSON` being a shell environment variable.
    ```bash
    uv run --directory ~/.config/opencode/scripts/python generate-task-json --output-dir "$PWD/.tasks" <<'TASK_DRAFT_JSON'
    <complete TaskDraftList JSON>
    TASK_DRAFT_JSON
    ```
    The script derives the kebab-case slug from the summary field,
    assigns operation and documentation class skills via deterministic
    weighted scoring, validates against both schemas, and atomically
    writes `.tasks/<epoch>-<slug>.json`.

Step B2. Capture the stdout of the command above as `GENERATED_PATH`.
    This is the relative path to the generated task file.

Step B3. Read `GENERATED_PATH` into `TASK_PACKET_JSON`.
    This file now has skills arrays assigned by the deterministic scorer.

## Phase C — Audit

Goal: review every script-assigned skill for semantic correctness.
You must load fresh dependencies here — Phase A's planning skills are gone.

Step C1. Run collect-skills for the executable skill inventory:
    ```bash
    uv run --directory ~/.config/opencode/scripts/python collect-skills --class operation --class documentation
    ```
    Read the JSON output into `SKILL_INVENTORY`. This is a fresh load —
    do not rely on any earlier skill data.

Step C2. For every task in `TASK_PACKET_JSON`, evaluate:
    - **Inventory check**: does each assigned skill exist in `SKILL_INVENTORY`?
    - **Skill-name reasonableness**: is each assigned skill genuinely appropriate
      for the task's purpose and context, not merely present in the inventory?
      A skill may be in the inventory but a poor semantic fit.
    - **Atomicity check (no combined tasks)**: does the task's `purpose` contain
      exactly one action verb? Multiple action verbs (e.g., "create and validate")
      indicate an illegally combined task. Flag such tasks for the delegator.
    - **Semantic fit**: does the skill's purpose match the task's purpose,
      context, and expected output? Lexical overlap may mislead.
    - **Circular self-references**: is the assigned skill the same as the
      target being edited? (e.g., "breakdown-tasks" assigned to a task
      editing breakdown-tasks/SKILL.md)
    - **Cross-task consistency**: do related tasks (variants of the same work,
      sequential pipeline steps) receive aligned skill assignments?
    - **Fallback scrutiny**: when no skill reached the threshold, the scorer
      selected the highest-ranked. Examine these extra carefully.

    Constraints:
    - Only skills arrays may be modified.
    - Every assigned skill must exist in `SKILL_INVENTORY`.
    - Each task must retain 1–3 skills.
    - All other fields stay byte-identical.

    Do not reference planning skills — they are not available at this phase.

Step C3. Write the corrected `TASK_PACKET_JSON` back to `GENERATED_PATH`.

## Phase D — Validation

Goal: validate the corrected task file and return its path.

Step D1. Run validation with auto-fix:
    ```bash
    uv run --directory ~/.config/opencode/scripts/python validate-task-structure \
      --state-file "$PWD/$GENERATED_PATH" \
      --schema "$PWD/skills/breakdown-tasks/schema/task-packet.schema.json" \
      --auto-fix
    ```
    The `--auto-fix` flag resolves skills-only errors deterministically
    (trim to max 3, remove empty strings, and deduplicate).

Step D2. If validation reports errors that `--auto-fix` cannot resolve:
    - Fix only the skills arrays in `TASK_PACKET_JSON`.
    - Re-write to `GENERATED_PATH`.
    - Re-run validation.
    - Repeat until success or an unrecoverable error is identified.
    If unrecoverable, return `BLOCKED: <reason>`.

Step D3. Return `GENERATED_PATH` only.

## Output Contract

Phase A produces TaskDraftList JSON on stdout (captured for piping to Phase B).
Phase B produces `.tasks/<epoch>-<slug>.json` (the script writes it).
Phase C writes corrections to the same file.
Phase D validates and returns `GENERATED_PATH`.

Final return: `.tasks/<epoch>-<slug>.json` (the relative path emitted by
`generate-task-json` in Phase B, validated in Phase D).

## Guardrails

- Do not populate skills manually — `generate-task-json` assigns them.
- Do not derive a summary slug — `generate-task-json` derives it from summary.
- Do not read schema files — the scripts validate against them.
- Each phase loads its own dependencies. Planning skills from Phase A
  will be evicted by Phase C — do not reference them there.
- In Phase C, change only skills arrays. All other fields are immutable.
- Every assigned skill must exist in the Phase C `SKILL_INVENTORY`.
- Return `BLOCKED` for malformed input, script failure, or unrecoverable
  validation errors.

## Docs

See `./reference/README.md` for supporting documentation.
