---
name: runbook
description: Generate executable runbook directory workspaces from approved markdown plans. Use for .runbooks/<id>/main.xml (v2 default) or .runbooks/<id>/runbook.json (v1 legacy) creation, validation, state initialization, and runbook-driven execution handoff.
---

# Runbook Skill

Use this skill after a markdown plan has been approved and before execution begins. The runbook is the machine-readable execution contract for orchestrators and workers.

This skill does **not** implement requested changes directly. It converts an approved human engineering plan into an executable runbook workspace, validates that workspace, and prepares it for runbook-keyed state initialization.

## Artifact Contract (v2 Default)

Runbook workspaces follow the **v2 XML format** by default:

```text
.runbooks/<unix-timestamp>-slug/
  main.xml
  steps/
    01-<step-slug>.xml
    02-<step-slug>.xml
```

The primary manifest is `main.xml`. Each step is defined in its own XML file under `steps/`, referenced by `step_ref` entries in `main.xml`.

Legacy v1 JSON workspaces may contain `.runbooks/<id>/runbook.json`; use those only for explicit legacy compatibility.

## Plan Intake Validation

Before creating a runbook, verify:

1. The plan path exists and matches `.plans/<timestamp>-slug/INDEX.md`.
2. The plan is a markdown engineering specification produced by the `plan` skill.
3. The plan frontmatter has `status: approved` or the user explicitly authorizes runbook generation.
4. The plan links to an accepted proposal.
5. The plan contains enough detail to derive executable steps: objective, scope, artifact impact, implementation strategy, validation, rollback/recovery, and acceptance criteria.

If the plan is too vague to execute safely, stop and repair the plan with the `plan` skill before generating a runbook.

## Runbook Generation Workflow (v2 XML Default)

1. Extract proposal and plan context.
2. Split plan phases into bounded executable steps.
3. Build dependency graph and parallel groups.
4. Load `delegation` for dynamic worker family/size guidance.
5. Create `.runbooks/<id>/main.xml` and `steps/<step-id>.xml` files using `skills/runbook/templates/main.xml` and `skills/runbook/templates/step.xml`.
6. Validate with `uv run --project scripts/python validate-runbook .runbooks/<id>/main.xml`.
7. Initialize state only when execution is authorized: `uv run --project scripts/python init-runbook-state .runbooks/<id>/main.xml`.

## XML Shape Requirements

- `main.xml` root: `<runbook artifact_type="runbook" format_version="2" id="<runbook-id>">`.
- Step references: `<step_ref id="01-step" file="steps/01-step.xml" />`.
- Step files root: `<step id="01-step">`.
- Paths are relative to `.runbooks/<id>/`.
- Step references must start with `steps/`, end with `.xml`, avoid `..`, and stay within the runbook directory.
- The runbook directory name, manifest `id`, and `state_dir` runbook ID must match.

## Validation

v2 XML runbooks use XSD structure validation plus parser-backed invariants in `scripts/python/lib/runbook_xml.py`.

Validate v2 XML:

```text
uv run --project scripts/python validate-runbook .runbooks/<runbook_id>/main.xml
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/main.xml
```

Validate legacy v1 JSON:

```text
uv run --project scripts/python validate-json .runbooks/<runbook_id>/runbook.json --schema skills/runbook/schema.json
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/runbook.json
```

Shared state validation:

```text
uv run --project scripts/python validate-json .state/<runbook_id>/metadata.json --schema skills/runbook/schemas/state-metadata.schema.json
uv run --project scripts/python validate-json .state/<runbook_id>/MAIN.json --schema skills/runbook/schemas/state-main.schema.json
uv run --project scripts/python validate-json .state/<runbook_id>/<step-id>.json --schema skills/runbook/schemas/state-step.schema.json
```

## Embedded Quality Check

Every non-trivial runbook should include or trigger an embedded quality check using `review-work` and an appropriately sized `worker-*` worker with review-mode instructions. The review should check plan fidelity, step granularity, dependency correctness, worker routing, file scope safety, runbook validation, state initialization, and recovery coverage.

## Rules

- Do not execute implementation changes while generating the runbook.
- Do not create `.plans/*.json` executable artifacts.
- Do not use `init-plan-state`; use `init-runbook-state` only.
- Do not store runbooks as single files directly under `.runbooks/`; use `.runbooks/<id>/main.xml` (v2) or `.runbooks/<id>/runbook.json` (v1 legacy).
- Do not create new v2 runbooks with TOON; TOON support was hard-cut over to XML.
- Do not modify worker agent names, model IDs, provider settings, or fallback ordering.
- Do not write outside `.runbooks/`, `.state/`, or explicitly authorized harness files.
- Do not hide unresolved assumptions; either encode them in the runbook or return to the plan/proposal stage.
