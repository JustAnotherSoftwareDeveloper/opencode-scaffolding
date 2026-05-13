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
state_file: .state/<plan-slug>/<step-id>.md
```

## Objective

<One bounded objective for this worker.>

## Context Package

### User Requirement Slice

<The exact part of the user/proposal requirement this worker is responsible for.>

### Relevant Proposal Sections

- <section name or excerpt>

### Relevant State Files

- `.state/<plan-slug>/<prior-step>.md`

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

- Write findings or work log to `.state/<plan-slug>/<step-id>.md` when file writes are in scope.
- Do not edit `.state/<plan-slug>/metadata.json` or `.state/<plan-slug>/MAIN.md` unless explicitly assigned.

## Acceptance Criteria

- <criterion one>
- <criterion two>

## Verification

- <command, parse check, read check, or review criterion>

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
plan_id: 1778702103-proposal-planning-skill-upgrade
step_id: 05-upgrade-plan-skill-schema-template
state_file: .state/1778702103-proposal-planning-skill-upgrade/05-upgrade-plan-skill-schema-template.md
objective: Repair skills/plan/schema.yaml so planning requires accepted proposals and step skill accepts null or lowercase hyphenated strings.
files_in_scope:
  - skills/plan/schema.yaml
  - skills/plan/templates/plan.yaml
files_out_scope:
  - opencode.json
  - agents/
  - node_modules/
expected_return_format: Summary of schema/template edits, validation commands, and residual risks.
acceptance_criteria:
  - skills/plan/schema.yaml parses as YAML.
  - proposal pattern rejects raw-request planning paths.
  - steps.items.properties.skill is a sibling of worker, minimum_capable_tier, context_package, objective, and recovery.
verification:
  - python YAML parse for schema and template.
  - structural check of schema['properties']['steps']['items']['properties'].
```
