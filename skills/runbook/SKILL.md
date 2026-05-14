---
name: runbook
description: Generate executable runbook directory workspaces from approved markdown plans. Use for .runbooks/<id>/runbook.json creation, validation, state initialization, and runbook-driven execution handoff.
---

# Runbook Skill

Use this skill after a markdown plan has been approved and before execution begins. The runbook is the machine-readable execution contract for orchestrators and workers.

This skill does **not** implement the requested changes directly. It converts an approved human engineering plan into an executable runbook workspace, validates that workspace, and prepares it for runbook-keyed state initialization.

## Artifact Contract

Runbook workspaces live at:

```text
.runbooks/<unix-timestamp>-slug/
  runbook.json        # required primary executable manifest
  <future-files>.json # optional future expansion files
```

The primary manifest is validated against:

```text
skills/runbook/schema.json
```

Runbook-owned state schemas live at:

```text
skills/runbook/schemas/
  state-metadata.schema.json
  state-main.schema.json
  state-step.schema.json
```

## Plan Intake Validation

Before creating a runbook, verify:

1. The plan path exists and matches `.plans/<timestamp>-slug.md`.
2. The plan is a markdown engineering specification produced by the `plan` skill.
3. The plan frontmatter has `status: approved` or the user explicitly authorizes runbook generation from its current status.
4. The plan links to an accepted proposal.
5. The plan contains enough detail to derive executable steps: objective, scope, artifact impact, implementation strategy, validation, rollback/recovery, and acceptance criteria.

If the plan is too vague to execute safely, stop and repair the plan with the `plan` skill before generating a runbook.

## Runbook Generation Workflow

1. **Extract source context**
   - Proposal path and accepted decisions.
   - Plan goal, non-goals, constraints, implementation strategy, artifact impact, validation, rollback/recovery, and acceptance criteria.

2. **Derive executable steps**
   - Split plan phases into bounded runbook steps.
   - Each step should have one objective, clear file scope, expected output, acceptance criteria, verification, and recovery.
   - Keep steps small enough for the smallest capable worker tier.

3. **Build dependency graph and parallel groups**
   - Serialize steps that read/delete the same files, mutate the same state, or depend on prior outputs.
   - Parallelize independent steps only when file scopes do not conflict.

4. **Select worker guidance**
   - Load `delegation` for dynamic family/size selection.
   - Record worker hints in `delegation_map` and each step's `worker` object.
   - Do not hardcode larger workers when the task can be decomposed.

5. **Create `.runbooks/<id>/runbook.json`**
   - Use `skills/runbook/templates/runbook.json` as the starting shape.
   - Fill every required schema field.
   - Keep optional future JSON files in the same runbook directory only when the runbook truly needs them.

6. **Validate and prepare state initialization**
   - Validate the runbook manifest against `skills/runbook/schema.json`.
   - Run `init-runbook-state` only after the runbook is approved or execution is authorized.

## Required Manifest Fields

The primary manifest requires, at minimum:

- `artifact_type: "runbook"`
- `schema_version: 1`
- `id`
- `title`
- `status`
- `created_at`
- `updated_at`
- `proposal`
- `plan`
- `state_dir`
- `active_step`
- `objective`
- `plan_summary`
- `inputs`
- `constraints`
- `execution_strategy`
- `delegation_map`
- `steps`
- `dependency_graph`
- `parallel_groups`
- `state_initialization`
- `verification_gates`
- `embedded_quality_check`
- `rollback_recovery`
- `final_report_contract`

## Path Conventions

Because `runbook.json` lives inside `.runbooks/<id>/`, relative paths must resolve from that directory:

```json
{
  "proposal": "../../.proposals/<proposal_id>.md",
  "plan": "../../.plans/<plan_id>.md",
  "state_dir": "../../.state/<runbook_id>/"
}
```

The runbook directory name, manifest `id`, and `state_dir` runbook ID must match. `init-runbook-state` enforces this.

## State Initialization

After creating an approved runbook, initialize state with:

```text
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/runbook.json
```

The initializer:

1. Validates the manifest against `skills/runbook/schema.json`.
2. Requires the file path `.runbooks/<runbook_id>/runbook.json`.
3. Requires `runbook.id == <runbook_id>`.
4. Requires `state_dir == ../../.state/<runbook_id>/`.
5. Creates `.state/<runbook_id>/` only when absent or empty.
6. Seeds `metadata.json`, `MAIN.json`, and step files when required.
7. Validates generated state against `skills/runbook/schemas/`.

## Validation Commands

Use these commands when creating or reviewing runbooks:

```text
uv run --project scripts/python validate-json skills/runbook/schema.json
uv run --project scripts/python validate-json .runbooks/<runbook_id>/runbook.json --schema skills/runbook/schema.json
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/runbook.json
uv run --project scripts/python validate-json .state/<runbook_id>/metadata.json --schema skills/runbook/schemas/state-metadata.schema.json
uv run --project scripts/python validate-json .state/<runbook_id>/MAIN.json --schema skills/runbook/schemas/state-main.schema.json
uv run --project scripts/python validate-json .state/<runbook_id>/<step-id>.json --schema skills/runbook/schemas/state-step.schema.json
```

## Embedded Quality Check

Every non-trivial runbook should include or trigger an embedded quality check using `review-work` and an appropriately sized `analysis-*` worker. The review should check:

- Fidelity to the approved plan and accepted proposal.
- Step granularity and dependency correctness.
- Worker routing and skill choices.
- File scope safety.
- Runbook schema validity.
- State initialization validity.
- Recovery and rollback coverage.

## Rules

- Do not execute implementation changes while generating the runbook.
- Do not create `.plans/*.json` executable artifacts.
- Do not use `init-plan-state`; use `init-runbook-state` only.
- Do not store runbooks as single files directly under `.runbooks/`; use `.runbooks/<id>/runbook.json`.
- Do not modify worker agent names, model IDs, provider settings, or fallback ordering.
- Do not write outside `.runbooks/`, `.state/`, or explicitly authorized harness files.
- Do not hide unresolved assumptions; either encode them in the runbook or return to the plan/proposal stage.
- Validate JSON artifacts with the Python validators before declaring the runbook ready.
