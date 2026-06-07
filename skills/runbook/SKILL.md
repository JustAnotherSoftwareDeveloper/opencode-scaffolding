---
name: runbook
description: Generate executable runbook directory workspaces from approved markdown plans. Use for .runbooks/<id>/main.xml (v3 target) creation, validation, state initialization, and runbook-driven execution handoff.
---

# Runbook Skill

Use this skill after a markdown plan has been approved and before execution begins. The runbook is the machine-readable execution contract for orchestrators and workers.

This skill does **not** implement requested changes directly. It converts an approved human engineering plan into an executable runbook workspace, validates that workspace, and prepares it for runbook-keyed state initialization.

## Artifact Contract (v3 Target)

Runbook workspaces follow the **v3 XML/XSD-first format** as the target contract:

```text
.runbooks/<runbook_id>/
  main.xml
  state.xml
  steps/
    <step-id>.xml
  evidence/
    index.xml
  snippets/
    index.xml
  reference/
    index.xml
```

The primary manifest is `main.xml`. Each step is defined in its own XML file under `steps/`. The runbook-local `state.xml` replaces retired `.state/<id>/` JSON state for the new target workflow. Manifests `evidence/index.xml`, `snippets/index.xml`, and `reference/index.xml` are created by default.

Legacy v1 JSON workspaces with `.runbooks/<id>/runbook.json` are deprecated and not created for new target workflows.

## Plan Intake Validation

Before creating a runbook, verify:

1. The plan path exists and matches `.plans/<timestamp>-slug/INDEX.md`.
2. The plan is a markdown engineering specification produced by the `plan` skill.
3. The plan frontmatter has `status: approved` or the user explicitly authorizes runbook generation.
4. The plan links to an accepted proposal.
5. The plan contains enough detail to derive executable steps: objective, scope, artifact impact, implementation strategy, validation, rollback/recovery, and acceptance criteria.

If the plan is too vague to execute safely, stop and repair the plan with the `plan` skill before generating a runbook.

## Runbook Generation Workflow (v3 Target)

1. **Extract proposal and plan context.** Verify plan path, status, and linked proposal acceptance.
2. **Plan task decomposition pass.** Convert `tasks/*.md` human instructions into SUPER-atomic steps: each must be exactly one primary operation, at most one skill routing target per step, with explicit input/output artifacts and precise file scope. Broad tasks are split; empty/missing scope is a defect requiring repair before proceeding.
3. **Split decomposed units into bounded executable steps.** One operation, one skill target, clear boundaries.
4. **Build dependency graph** from decomposition output (one step at a time; no parallel dispatch).
5. **Load `delegation`** for worker routing guidance.
6. Create `.runbooks/<id>/main.xml`, `state.xml`, and `steps/<step-id>.xml` files using XSDs under `skills/runbook/schemas/` as the only schema/template contract.
7. Validate with `uv run --project scripts/python validate-runbook .runbooks/<id>/main.xml`.
8. Initialize state only when execution is authorized: `uv run --project scripts/python init-runbook-state .runbooks/<id>/main.xml`.

## Execution Model

Runbooks use **strict serial execution**. Steps are ordered by the dependency graph and dispatched one at a time. The `dependency_graph` element encodes precedence constraints; it is **not** a parallel dispatch mechanism. There are no executable parallel groups.

## XML Shape Requirements

- `main.xml` root: `<runbook artifact_type="runbook" format_version="3" id="<runbook-id>">`.
- Step references: `<step_ref id="01-step" file="steps/01-step.xml" />`.
- Step files root: `<step id="01-step">`.
- Paths are relative to `.runbooks/<id>/`.
- Step references must start with `steps/`, end with `.xml`, avoid `..`, and stay within the runbook directory.
- The runbook directory name, manifest `id`, and `state.xml` runbook ID must match.
- Required manifests: `evidence/index.xml`, `snippets/index.xml`, `reference/index.xml`.

## Validation

v3 XML runbooks use XSD structure validation under `skills/runbook/schemas/` as the only schema contract, plus parser-backed invariants in `scripts/python/lib/runbook_xml.py` and `scripts/python/lib/runbook_state.py`.

Validation must be script-backed (Python/bash), not LLM judgment.

Validate v3 XML:

```text
uv run --project scripts/python validate-runbook .runbooks/<runbook_id>/main.xml
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/main.xml
```

Legacy validation is not supported for new target workflows.

## Embedded Quality Check

Every non-trivial runbook should include or trigger an embedded quality check using `review-work` and the configured text worker (`worker`) with review-mode instructions. The review should check plan fidelity, step granularity, dependency correctness,  file scope safety, runbook validation, state initialization, and recovery coverage.

## Rules

- Do not execute implementation changes while generating the runbook.
- Do not create `.plans/*.json` executable artifacts.
- Do not use `init-plan-state`; use `init-runbook-state` only.
- Do not store runbooks as single files directly under `.runbooks/`; use `.runbooks/<id>/main.xml` (v3 target).
- Do not create new v3 runbooks with TOON or JSON; use XML/XSD-first format.
- Do not modify worker agent names, model IDs, provider settings, or fallback ordering.
- Do not write outside `.runbooks/`, or explicitly authorized harness files.
- Do not hide unresolved assumptions; either encode them in the runbook or return to the plan/proposal stage.

## Atomic Step Criteria (SUPER Atomics)

Each step must meet **exactly** these criteria before a v3 XML file is created:

1. **Single primary operation**: One clear action that, if completed successfully, satisfies the step's objective.
2. **At most one skill routing target per step**: Either `worker` or another specific skill—never multiple skills dispatched within a single step.
3. **Explicit input artifacts**: Specific file paths, state locations, or prior outputs the worker must read before starting.
4. **Explicit output artifacts/evidence**: Exact files that will be created/modified and how to verify success.
5. **Precise `files_in_scope`**: Actual file paths—not directories or globs—unless the operation is explicitly inventorying a directory.
6. **Clear `files_out_scope`**: Explicitly excluded items to prevent scope creep.
7. **Expected return format**: Structured response with evidence markers, validation output, or defined artifacts.

**Repair guidance:** If a plan task describes "update documentation" or lacks file-level scope, split into multiple atomic steps rather than copying the broad task directly into a step XML. Empty `files_in_scope` or directory-only scope is treated as a defect requiring repair before runbook creation proceeds.
