---
name: review-work
description: Review completed harness work for correctness, config validity, prompt quality, permission safety, and runbook fidelity.
---

# Review Work Skill

Use this skill after execution and before the orchestrator reports success. The review should identify defects, regressions, missing validation, and harness-quality problems.

This skill is intended to be loaded by appropriately sized `analysis-*` workers as an embedded quality check in the workflow.

## Inputs

- User request.
- Proposal and runbook, if available.
- Files changed.
- Worker outputs.
- Validation results.

## Output Format

Return exactly these sections:

## Findings
List findings first. For each finding include severity, file path, line reference when available, and why it matters. If there are no findings, say `No findings.`

## Runbook Fidelity
State whether execution matched the runbook and note any deviations.

## Config And Schema Validity
Review JSON validity, JSON Schema conformance, markdown frontmatter shape, command definitions, skill naming rules, and agent mode/hidden usage.

For v2 TOON runbook workspaces, validate with parser-backed invariant checks:
- `uv run --project scripts/python validate-runbook .runbooks/<runbook-id>/main.toon`

For legacy v1 JSON runbook artifacts, validate against the runbook schema:
- `uv run --project scripts/python validate-json .runbooks/<runbook-id>/runbook.json --schema skills/runbook/schema.json`

For JSON runbook state artifacts, validate against the runbook state schemas:
- `uv run --project scripts/python validate-json .state/<runbook-id>/metadata.json --schema skills/runbook/schemas/state-metadata.schema.json`
- `uv run --project scripts/python validate-json .state/<runbook-id>/MAIN.json --schema skills/runbook/schemas/state-main.schema.json`
- `uv run --project scripts/python validate-json .state/<runbook-id>/<step-id>.json --schema skills/runbook/schemas/state-step.schema.json`

## Permission Safety
Review task permissions, skill permissions, write permissions, and accidental over-broad access.

## Prompt Quality
Review whether prompts are specific, bounded, non-contradictory, and useful for future agents.

## Missing Verification
List checks that should still be run or could not be run.

For changed JSON/YAML artifacts, treat missing validator coverage as a finding when the Python validators are available. Expected commands are:
- `uv run --project scripts/python validate-json <file>`
- `uv run --project scripts/python validate-json <file> --schema <schema-file>` when a local schema exists
- `uv run --project scripts/python validate-yaml <file>` (for legacy YAML artifacts only)

For runbook state artifacts, expect validation against the schemas in `skills/runbook/schemas/`:
- `state-metadata.schema.json` for `metadata.json`
- `state-main.schema.json` for `MAIN.json`
- `state-step.schema.json` for each step file

If the `init-runbook-state` script was not run after creating a new runbook JSON, flag that as a missing validation step.

If execution starts from a v2 TOON runbook, expect `init-runbook-state` to receive `.runbooks/<runbook-id>/main.toon`. If execution starts from legacy v1 JSON, expect `.runbooks/<runbook-id>/runbook.json`.

## Recommendation
State whether to accept, fix before accepting, or redesign.

## Rules

- Findings are the primary output. Do not bury them after a summary.
- Do not modify files while reviewing.
- Be concrete and cite exact files.
- Distinguish correctness problems from style preferences.
- Treat review as part of the active workflow, not a separate artifact lane.
