---
name: plan
description: Use when a spawning orchestrator delegates creation of directory-based markdown engineering plans from accepted proposals, coordinating named delegated backing skills to produce structured workspace artifacts.
class: orchestrated
---

# Plan Skill (Orchestrator)

**Heavy-procedure coordinator-only.** Orchestrated skills own routing, state transitions, reconciliation, failure handling, and quality gates. **Does not perform worker tasks directly.** Everything is delegated to workers or named delegated backing skills spawned via delegation packets constructed using `skills/delegation/templates/delegation-packet.md`.

Coordinates the post-acceptance phase of the proposal→plan→runbook lifecycle: transforms accepted proposals into structured plan workspace artifacts ready for downstream runbook execution.

## Delegated Backing Skills

This orchestrator spawns five named delegated backing skills in sequence. Each has explicit input/output contracts per delegation packets referencing this skill's taxonomy requirements.

| Delegated Skill | Purpose | Input From Orchestrator | Output To Orchestrator |
|-----------------|---------|------------------------|------------------------|
| `plan-intake-lane` | Validate accepted proposal artifact and extract structured handoff data | Proposal path (`.proposals/<timestamp>-<slug>/INDEX.md`) from state or packet field | JSON with goal, non_goals, constraints, scope boundaries, risks_to_monitor, suggested_delegation |
| `plan-specification-analyst` | Transform intake output into plan workspace specification content | Intake data JSON + plan_id_slug | JSON with goal_section, file_impact_analysis, validation_checkpoints ready for task rendering |
| `plan-workspace-creator` | Create `.plans/<timestamp>-<slug>/` workspace scaffold with 10-file taxonomy and tasks directory | Spec content JSON + target_workspace path | JSON with status, workspace_path, files_created array, verification_summary |
| `plan-task-writer` | Create numbered senior-to-intern task markdown files in tasks/ directory | Plan spec JSON + target_workspace path | Array of created task file paths with frontmatter/validation confirmation |
| `plan-review-analyst` | Validate complete plan artifact set against required taxonomy quality gates | workspace_path, proposal_path, expected_delegated_skills array | Validation report: status, files_checked, quality_gates_passed, recommendation ("accept"/"revise") |

## Orchestration Protocol

### When to Use This Skill
Use when a spawning orchestrator has accepted proposal artifacts and needs structured plan workspaces for downstream runbook execution. Trigger conditions:
- Proposal has `status: accepted` in metadata.md (workspace) or frontmatter (historical)
- Execution work is non-trivial requiring multi-phase coordination

### Do Not Use When
- User request is trivial (typo fix, surface change)—no proposal/plan needed
- No accepted proposal exists—request explicit acceptance first via original `proposal` skill path

## Serial Delegation Workflow

**Phase 1: Intake Lane Launch** → **Phase 2: Specification Analysis** → **Phase 3: Workspace Creation (Delegated)** → **Phase 4: Task Drafting** → **Phase 5: Review/QA Gate** → **Phase 6: Approval Handoff to Runbook Skill**

```
┌─────────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ plan-intake-lane │ → │ spec-analyst │ → │ workspace-   │ → │ task-writer  │
│ (worker skill)   │   │ (delegated)  │   │ creator      │   │ (delegated)  │
└─────────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
                                                          ↓
                                                ┌──────────────┐
                                                │ review-analyst│
                                                │              │
                                                └──────────────┘
                                                          ↓ pass/failing to runbook skill
```

### Phase Details

1. **Launch Intake Lane** — Spawn `plan-intake-lane` via delegation packet with proposal path and unix-timestamp slug for new plan workspace. Skill loads as `Skill to load` per delegation template requirement.

2. **Specification Analysis** — After intake completes, spawn `plan-specification-analyst` with intake_data JSON + plan_id_slug. Worker produces structured spec ready for task rendering.

3. **Workspace Creation (Delegated)** — Spawn `plan-workspace-creator` with spec_content JSON + target_workspace path. Worker creates `.plans/<timestamp>-<slug>/` directory structure with all 10 root files and tasks/ subdirectory.

4. **Task Drafting** — Spawn `plan-task-writer` with spec content and target_workspace path. Creates numbered senior-to-intern markdown files (e.g., `01-implementation.md`) in tasks/.

5. **Review/QA Gate** — Spawn `plan-review-analyst` to validate 10-file + tasks/ taxonomy completeness, frontmatter validity, no proposal duplication, delegated skills named correctly. Result is pass/fail recommendation.

6. **Approval Handoff** — On quality gate pass: Update state.xml step status, return handoff JSON with plan_workspace_path and approved_tasks list for runbook skill to consume. On failure: Return revision request with missing files/sections enumerated.

## Plan Artifact Contract (Required)

Plan workspaces are execution-focused artifacts at `.plans/<unix-timestamp>-<slug>/INDEX.md` containing **required** structure:

```text
.plans/<timestamp>-<slug>/
├── INDEX.md              # TOC-only navigation, no frontmatter/body
├── metadata.md           # id, title, status, created_at, proposal reference
├── source.md             # Link to accepted proposal with decision summary only
├── execution-overview.md # High-level approach for what's executing today
├── constraints.md        # Prerequisites, sequencing rules, hard boundaries
├── file-impact.md        # Files/dirs that will be created/modified/deleted
├── implementation-notes.md | OR "TBD" if omitted
├── validation.md         # Verification commands and checkpoints
├── rollback-recovery.md  # Undo instructions for partial execution failure
└── tasks/                # REQUIRED: numbered senior-to-intern instruction files
    ├── 01-description.md
    └── ...
```

## Tasks Directory Semantics (`tasks/*.md`)

Files in this directory are **human-facing senior-to-intern instructions**, not runbook XML or execution state. Each file must include Purpose, Files In Scope (exact paths), Actions with concrete steps/commands, Expected Observations, Common Mistakes & How to Avoid Them table, and Completion Criteria (pass/fail checklists).

Example frontmatter for task files:
```yaml
---
id: <unix-timestamp>-<slug>
title: "<Descriptive Task Title>"
status: draft
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: ".proposals/<timestamp>-<proposal-slug>/INDEX.md"
---
```

## Delegation Packet Requirements

All delegation packets must follow `skills/delegation/templates/delegation-packet.md`:
- **Skill to load** must be one of the five named delegated backing skills listed above
- Include bounded objective, context inputs, files in/out scope, Do/Do-not rules
- State ownership per step (or "none" for read-only workers)
- Verification command expecting valid JSON output

## Task Naming / Identity Mapping

Tasks are numbered and kebab-case (`01-core-refactor.md`). Suggested delegation assignments from proposal's `suggested_delegation` field map to worker capability recommendations within each task file. The orchestrator uses these hints but respects reviewer override via review-analyst quality gates.

## State Ownership & Failure Handling

| Phase | Owner | Mutable Paths | Notes |
|-------|-------|---------------|-------|
| Intake/Spec | Delegated workers | None (read-only from proposal) | Failure: return JSON with error_type, skip downstream steps |
| Workspace Creation | Delegated worker (`plan-workspace-creator`) | `.plans/<id>/INDEX.md`, `metadata.md` etc. | Worker creates taxonomy; orchestrator reconciles state |
| Task Writing/Review | Delegated workers | `tasks/*.md` creation | Worker may update state file path if specified in packet |

**Failure Strategy:** 
- If any delegated skill returns `"status": "failed"`, analyze error_type from worker output JSON. Options: repair delegation packet (iterate), skip dependent tasks with explanation, or escalate to user for clarification/decision.
- Partial artifacts are preserved under `.runbooks/<id>/evidence/` when available for inspection.

## Quality Gates Checklist

| Gate | Condition | Action if Fail |
|------|-----------|----------------|
| Intake Success | JSON output has all required keys (goal, constraints non-empty) | Skip spec phase; request clearer proposal data from user |
 |Workspace Exists | Directory `.plans/<slug>/` with 10 files minimum | Create missing structure before task writing |
| Tasks Valid | Each task file parses YAML frontmatter and contains all sections | Return to plan-task-writer for revision |
| Review Pass | `quality_gates_passed: true`, `recommendation: "accept"` | Proceed to runbook handoff; update state.xml |

## Validation Command

```bash
uv run --project scripts/python validate-skill-framework skills/plan/SKILL.md
# Grep verification checklist:
grep -E "^class:" skills/plan/SKILL.md  # should show: orchestrated (not planning)
grep "plan-intake-lane\|plan-specification-analyst\|plan-workspace-creator\|plan-task-writer\|plan-review-analyst" skills/plan/SKILL.md  # all five present
```

## Related Skills

- `proposal` — Creates accepted proposal artifacts this skill consumes
- `runbook` — Executes approved plans after plan approval handoff  
- `delegation` — Routes work via Worker Handoff Packets and template