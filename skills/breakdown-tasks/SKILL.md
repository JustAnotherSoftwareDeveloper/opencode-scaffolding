---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items. Separates planning from execution: the LLM decomposes, the script assigns skills."
tags: [task-decomposition, atomic-tasks, task-planning, request-analysis, generate-task-json, delegation-pipeline]
class: delegated
---

# Breakdown Tasks — Delegated Worker

Decompose a request into atomic work items suitable for serial worker delegation.
Produce `TaskDraft` objects without a `skills` field.

## Input Contract

Read `## PURPOSE` and `## DETAILS`.
Return `BLOCKED: missing PURPOSE or DETAILS` if either section is missing.

## Execution Steps

1. Read `./schema/task-input.schema.json`.
2. Read `./reference/authoring/core-rules.md`, `./reference/authoring/task-granularity.md`, `./reference/authoring/anti-patterns.md`, and `./reference/authoring/context-preservation.md`.
3. Run `uv run --directory ~/.config/opencode/scripts/python collect-skills --class planning`.
4. Read the returned planning-skill metadata.
5. Select and load zero to three applicable planning skills by name.
6. Produce a schema-valid `{summary, tasks}` object.
   Keep every task atomic.
   Copy relevant goals and constraints verbatim into each `context`.
   Do not add `skills`.
   Do not execute tasks.
7. Derive a lowercase kebab-case summary slug from `summary`.
8. Store the complete draft JSON object in `TASK_DRAFT_JSON`.
9. Pipe `TASK_DRAFT_JSON` to:

```bash
printf '%s' "$TASK_DRAFT_JSON" | uv run --directory ~/.config/opencode/scripts/python generate-task-json \
  --summary-slug "$SUMMARY_SLUG" \
  --output-dir "$CWD/.tasks"
```

10. Capture the generator stdout as `GENERATED_PATH`.
11. Read `GENERATED_PATH` into `TASK_PACKET_JSON`.
12. Run `uv run --directory ~/.config/opencode/scripts/python collect-skills --class operation --class documentation`.
13. Read the returned operation/documentation skill metadata into `SKILL_INVENTORY`.
14. Reason over every task in `TASK_PACKET_JSON`:
    - Compare each assigned skill against the `SKILL_INVENTORY`.
    - Evaluate semantic fit: does the skill capability match the task purpose, context, and expected output?
    - Check cross-task consistency: do related tasks receive aligned skill assignments?
    - Scrutinize fallback assignments where no deterministic score reached the threshold.
    - Change only `skills` arrays — never modify `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `verification`, or `expectedOutput`.
    - Every assigned skill must have a matching entry in the `SKILL_INVENTORY`.
15. Write the corrected `TASK_PACKET_JSON` back to `GENERATED_PATH`.
16. Validate the corrected state file:
    ```bash
    uv run --directory ~/.config/opencode/scripts/python validate-task-structure \
      --state-file "$GENERATED_PATH" \
      --schema ./schema/task-packet.schema.json
    ```
17. If validation reports errors, fix only the `skills` arrays in `TASK_PACKET_JSON`, re-write to `GENERATED_PATH`, and re-run validation.
    Repeat until validation succeeds or the error cannot be resolved by skills-only changes.
    If an unrecoverable skills-only validation error is identified, return `BLOCKED: <reason>`.
18. Return `GENERATED_PATH` only.

Do not use `--output-file`; that destination mode belongs to other shared-generator consumers.

## Output Contract

Return only the `.tasks/<epoch-milliseconds>-<summary-slug>.json` path emitted by `generate-task-json`.
Match the path format requested by `## EXPECTED OUTPUT`.

## Verification

- Verify that the generated path is relative and matches `.tasks/<epoch-milliseconds>-<lowercase-kebab-case-slug>.json`.
- Verify that the path contains no Markdown formatting or explanatory text.
- Verify that `validate-task-structure --state-file` exits with code 0 against the final state file.
- Verify that every assigned skill name exists in the `collect-skills --class operation --class documentation` output.
- Verify that non-`skills` fields are byte-identical to the `generate-task-json` output.

## Guardrails

- Do not populate `skills` manually — the deterministic scorer and optional LLM review handle assignment.
- Pipe the complete root JSON object to `generate-task-json` through standard input.
- Derive the lowercase kebab-case summary slug from `summary`.
- Do not create `.tasks` or write a task-draft file manually.
- Use the legacy summary-slug and output-directory destination mode only.
- Do not bundle dependent changes.
- During LLM review: change only `skills` arrays; never modify `purpose`, `context`, `filesToRead`, `filesToWrite`, `executionInstructions`, `verification`, or `expectedOutput`.
- Every assigned skill must be present in the `collect-skills --class operation --class documentation` output.
- The corrected state file must pass `validate-task-structure --state-file --schema ./schema/task-packet.schema.json` before return.
- If `generate-task-json` fails, skip review and propagate `BLOCKED: <reason>`.
- Return `BLOCKED: <reason>` for malformed input, generator failure, or unrecoverable review validation failure.

## Cross-References

- Load selected planning skills by name.
- See `./reference/skill-assignment.md` for the full skill-assignment procedure including deterministic baseline and LLM review.
- See `./reference/scripts/generate-task-json.md` for generator behavior.
- See `./schema/task-packet.schema.json` for the output schema validated during review.

## Docs

See `./reference/README.md` for supporting documentation.
