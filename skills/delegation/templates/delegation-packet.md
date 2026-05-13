---
artifact_type: delegation-packet-template
schema_version: 1
description: OpenCode-specific delegation packet template for Task tool worker prompts.
---

# Delegation Packet: <task-title>

## Routing

```yaml
target_agent: <exact-worker-name>        # e.g. coding-md, analysis-lg, websearch-md
worker_family: <generic|analysis|coding|doc-writer|websearch|multimodal-looker|explore>
worker_size: <xs|sm|md|lg|xl|null>       # null only for workers without size suffix, e.g. explore
skill: <skill-name-or-null>
plan_id: <plan-id>
step_id: <step-id>
state_file: .state/<plan-slug>/<step-id>.json
```

## Objective

<One bounded objective for this worker.>

## Context Package

### User Requirement Slice

<The exact part of the user/proposal requirement this worker is responsible for.>

### Relevant Proposal Sections

- <section name or excerpt>

### Relevant State Files

- `.state/<plan-slug>/<prior-step>.json`

### Files In Scope

- `<path-or-glob>`

### Files Out Of Scope

- `<path-or-glob>`

### OpenCode Context

- Use the Task tool pattern for worker delegation.
- Load `skill: <skill-name>` only when specified and permitted.
- Follow applicable `AGENTS.md` rules.
- Respect `permission.task`, `permission.skill`, and file-scope constraints.

## Do

- <specific action>

## Do Not

- <explicit prohibition>

## Expected Return Format

<Exact format the worker should return in its final message.>

## State Updates

- Write findings or work log to `.state/<plan-slug>/<step-id>.json` when file writes are in scope.
- Do not edit `.state/<plan-slug>/metadata.json` or `.state/<plan-slug>/MAIN.json` unless explicitly assigned.

## Acceptance Criteria

- <criterion one>
- <criterion two>

## Verification

- <command, parse check, read check, or review criterion>
- For JSON edits, prefer `uv run --project scripts/python validate-json <file>` or `uv run --project scripts/python validate-json <file> --schema <schema-file>`.
- For YAML edits (legacy artifacts only), use `uv run --project scripts/python validate-yaml <file>`.
- For state files, validate against the appropriate schema:
  - `uv run --project scripts/python validate-json .state/<plan-slug>/metadata.json --schema skills/plan/schemas/state-metadata.schema.json`
  - `uv run --project scripts/python validate-json .state/<plan-slug>/MAIN.json --schema skills/plan/schemas/state-main.schema.json`
  - `uv run --project scripts/python validate-json .state/<plan-slug>/<step-id>.json --schema skills/plan/schemas/state-step.schema.json`

## Result Consumption

The orchestrator will consume:

- the worker's final summary,
- any assigned state file updates,
- any explicitly created/modified artifacts listed in the worker's final summary.

## Recovery / Escalation

- If blocked by missing context, report the missing context and stop.
- If blocked by permissions or out-of-scope files, report and stop.
- If task complexity exceeds the assigned worker, recommend a specific larger worker.
- If partial work was completed, list exact files touched and remaining work.

## Example

```yaml
target_agent: coding-md
worker_family: coding
worker_size: md
skill: null
plan_id: 1778710681-json-plan-state-artifacts
step_id: 04-implement-plan-schema-template
state_file: .state/1778710681-json-plan-state-artifacts/04-implement-plan-schema-template.json
objective: Implement JSON plan schema and template files for the JSON-based plan artifact contract.
files_in_scope:
  - skills/plan/schema.json
  - skills/plan/templates/plan.json
files_out_scope:
  - opencode.json
  - agents/
  - node_modules/
expected_return_format: Summary of schema/template edits, validation commands, and residual risks.
acceptance_criteria:
  - skills/plan/schema.json is valid JSON Schema (draft 2020-12).
  - skills/plan/templates/plan.json validates against skills/plan/schema.json.
  - YAML schema/template files are retained as historical references but not referenced as live.
verification:
  - uv run --project scripts/python validate-json skills/plan/schema.json
  - uv run --project scripts/python validate-json skills/plan/templates/plan.json --schema skills/plan/schema.json
  - python JSON parse check for schema and template.
```

> Historical note: Prior delegation packets referenced `.yaml` schemas and `.md` state files. New packets should use the JSON conventions above.
