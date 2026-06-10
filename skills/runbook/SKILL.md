---
name: runbook
description: Use when converting approved markdown plans into executable v3 XML runbook workspaces with delegated backing skills for input validation, specification analysis, workspace creation, step writing, and validation/QA before state initialization handoff.
class: orchestrated
---

# Runbook Skill (Orchestrator)

Coordinates multi-phase runbook generation from approved plans using delegated backing skills. This orchestrator owns routing, state transitions, reconciliation, failure handling, and quality gates; it does **not** perform worker tasks directly.

Uses the `delegation` skill as the routing source of truth; all worker assignments flow through delegation packets constructed per `skills/delegation/templates/delegation-packet.md`.

## Delegated Backing Skills

| Lane Name | Purpose | Input From Orchestrator | Output To Orchestrator |
|-----------|---------|------------------------|------------------------|
| runbook-intake-lane | Validate approved plan and extract runbook-generation handoff data | Plan path, proposal path | Structured JSON with goal, constraints, scope boundaries, acceptance criteria |
| runbook-specification-analyst | Transform validated intake JSON into runbook workspace specification | Intake JSON, runbook_id_slug | Structured JSON defining step units, dependency edges, delegation map, manifest requirements |
| runbook-workspace-creator | Create `.runbooks/<id>/` v3 XML scaffold directory structure | runbook_id, target_workspace, spec_content | Workspace path, files created, verification summary |
| runbook-step-writer | Generate individual v3 XML step files from plan tasks | runbook_id, target_workspace, steps_spec | Steps created, verification summary |
| runbook-validation-analyst | Validate v3 XML runbook workspace completeness and readiness | workspace_path, checklist, validation_depth | Quality gates status, blockers, recommendation |

## Orchestration Protocol

### When to Use This Skill

Use when a markdown plan has been approved and you need to generate an executable runbook workspace before execution begins. The runbook is the machine-readable execution contract for orchestrators and workers.

Trigger conditions:
- Plan exists at `.plans/<timestamp>-slug/INDEX.md` with `status: approved`
- Linked proposal has `status: accepted`
- Plan contains enough detail for executable steps: objective, scope, artifact impact, implementation strategy, validation, rollback/recovery, and acceptance criteria

### Do Not Use When

- Direct implementation without runbook generation is required
- The task is trivial (typo fix, surface change)—no runbook needed
- Plan is too vague to execute safely—repair the plan first

## Serial Delegation Workflow

1. **Launch intake lane** — Delegate to `runbook-intake-lane` with plan path and proposal path to validate plan status and extract structured handoff data.
2. **Synthesize specification** — After intake completes, delegate to `runbook-specification-analyst` with intake JSON and runbook_id_slug to produce runbook workspace specification.
3. **Create workspace scaffold** — After specification completes, delegate to `runbook-workspace-creator` with runbook_id, target_workspace, and spec_content to materialize the `.runbooks/<id>/` directory structure.
4. **Write step files** — After workspace creation, delegate to `runbook-step-writer` with runbook_id, target_workspace, and steps_spec to create individual v3 XML step files.
5. **Validate workspace** — After step writing, delegate to `runbook-validation-analyst` with workspace_path and checklist to verify schema compliance, manifest presence, step granularity, dependency correctness, and state initialization readiness.
6. **Initialize state** — Only after all validations pass, initialize state via `uv run --project scripts/python init-runbook-state .runbooks/<id>/main.xml`.

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

## Lane Packet Requirements (Per Delegation Skill)

For each delegated backing skill, construct a bounded handoff packet via the delegation template that includes:

| Item | Requirement |
|------|-------------|
 | Objective | One clear, bounded goal for the lane |
 | Source / file boundaries | Exact paths or URLs in scope |
 | Out-of-scope | Explicit exclusions to prevent scope creep |
 | Output contract | Required format with facts/inferences/assumptions and confidence levels |
 | Do / do-not rules | Must reject implementation steps per runbook boundary rule |

## Evidence Ledger Mapping

Accept worker findings into discovery results using this structure:

| Lane | Worker | Source | Claim/Fact | Inference | Assumption | Confidence | Relevance | Fit Caveat | Decision Impact |
|------|--------|--------|------------|-----------|------------|------------|-----------|------------|-----------------|

External-source facts must include `[Source: URL]` citations. Historical and local findings map to lane origin per packet receipt.

## Validation Commands

```bash
# Validate orchestrator skill framework compliance
uv run --project scripts/python validate-skill-framework skills/runbook/SKILL.md

# Validate all five delegated backing skills
uv run --project scripts/python validate-skill-framework skills/runbook-intake-lane/SKILL.md
uv run --project scripts/python validate-skill-framework skills/runbook-specification-analyst/SKILL.md
uv run --project scripts/python validate-skill-framework skills/runbook-workspace-creator/SKILL.md
uv run --project scripts/python validate-skill-framework skills/runbook-step-writer/SKILL.md
uv run --project scripts/python validate-skill-framework skills/runbook-validation-analyst/SKILL.md

# Grep verification for delegation matrix
grep -E "runbook-intake-lane|runbook-specification-analyst|runbook-workspace-creator|runbook-step-writer|runbook-validation-analyst" skills/runbook/SKILL.md
```

## Quality Gate Checklist

Before user decision, verify:
- **Completeness**: All 5 backing skills present with required content
- **Class identification**: `class: orchestrated` confirmed
- **Delegation matrix**: All five skill names appear exactly as listed
- **Workflow integrity**: Serial sequence matches intake → specification → workspace → steps → validation → state init
- **Boundary preservation**: No dependency graphs, task breakdowns, or implementation steps leaked from proposal/plan

## Rules

- Do not execute implementation changes while generating the runbook.
- Do not create `.plans/*.json` executable artifacts.
- Do not use `init-plan-state`; use `init-runbook-state` only after validation passes.
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