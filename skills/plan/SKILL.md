---
name: plan
description: Create directory-based markdown engineering plans from accepted proposals. Use when a proposal has been accepted and an execution blueprint is needed. Plans are required-execution workspaces with validation tasks/ directory for senior-dev-to-intern instructions.
class: planning
---

# Plan Skill

Use this skill after a proposal is accepted. Planning requires an accepted proposal artifact: prefer a proposal workspace at `.proposals/<timestamp>-<slug>/INDEX.md` with accepted status in `metadata.md`; historical single-file `.proposals/<timestamp>-<slug>.md` artifacts remain readable but must not be migrated. Direct planning from raw user requests is not supported.

**This skill does not implement changes.** It produces a markdown plan artifact that defines required execution-focused workspaces. Non-trivial execution proceeds by loading the **runbook** skill after the plan is approved.

## Plan Artifact Contract (Future Taxonomy)

Plan artifacts are **required-execution workspaces** with a mandatory file structure:

```text
.plans/<unix-timestamp>-<slug>/INDEX.md
```

Each plan workspace must contain all required files listed below. The `tasks/` directory is mandatory — it contains numbered senior-to-intern instruction files, not runbook XML execution state.

### Required Files

| File | Purpose |
|------|---------|
| **INDEX.md** | TOC-only navigation file; no frontmatter or prose body |
| **metadata.md** | YAML lifecycle/status/source metadata: id, title, status, created_at, proposal reference |
| **source.md** | Short link to source proposal with accepted-decision summary only — NOT rationale duplication |
| **execution-overview.md** | What we're executing today (high-level approach) |
| **constraints.md** | Prerequisites, sequencing rules, hard boundaries |
 | **file-impact.md** | Files/dirs that will be created, modified, or deleted |
| **implementation-notes.md** | OR document why omitted for this plan |
| **validation.md** | Verification commands and checkpoints |
| **rollback-recovery.md** | Undo instructions if execution fails partway through |
| **handoff.md** | Optional transition guidance to runbook/next owner |
| **tasks/** | REQUIRED: At least one numbered markdown file, e.g., `01-implementation.md` |

### Tasks Directory Semantics (`tasks/*.md`)

Files in this directory are **human-facing senior-to-intern instructions**. Each file must include:

- Purpose statement for the step
- Files in scope (exact paths)
- Concrete actions/edits with specific commands or edit specifications  
- Expected observations/outputs
- Common mistakes and how to avoid them
- Completion criteria (pass/fail conditions verifiable at that step)

**NOT runbook XML. NOT execution state.** These are markdown instructions workers follow directly.

Example structure for `tasks/01-update-skill-contract.md`:

```markdown
## Purpose
Update the Plan Skill contract to reflect required file structure and tasks/ directory purpose.

## Files in Scope
- `skills/plan/SKILL.md`

## Actions
1. Edit SKILL.md sections 4–6 ...
2. Run validation: uv run --project scripts/python validate-skill-framework skills/plan/SKILL.md

## Expected Observations
- Grep for legacy references finds zero matches
```

### Frontmatter (per file)

Every plan markdown file starts with YAML frontmatter:

```yaml
---
id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft  # draft | approved | superseded
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: ".proposals/<timestamp>-<proposal-slug>/INDEX.md"
---
```

## Required Sections in INDEX.md

The `INDEX.md` file must contain each section listed below. Sections not yet filled should state "TBD".

| Section | Purpose |
|---------|---------|
| **Goal** | Clear statement of what this plan accomplishes (from proposal goal) |
| **Non-Goals** | What this plan explicitly does NOT address |
| **Source Proposal** | Link to accepted proposal with summary of key decisions only |
 | **Accepted Decisions** | Planning-level decisions: phase ordering, worker routing, skill selection |
| **Workspace Contents** | File tree structure matching required taxonomy above |
 | **Constraints** | Prerequisites and sequencing rules (may duplicate constraints.md content) |
| **Artifact Impact** | Files that will be created, modified, or deleted |
| **Validation** | Commands to verify correctness (see also validation.md) |
| **Rollback / Recovery** | Steps to undo if execution fails; may reference rollback-recovery.md |
| **Acceptance Criteria** | Concrete pass/fail conditions for plan completion |

## Lifecycle Rule

**Plan skill does not implement changes.** It produces the execution-focused workspace. Non-trivial execution proceeds through the runbook skill after plan approval and validation.

Load `skill-hygiene` only if frontmatter or framework metadata changes; otherwise use documentation-mode instructions. Load `review-work` for reviewing completed work. Use `delegation` during runbook execution to select worker sizes dynamically.

## Validation Guidance (Future)

Once the validator is added, future plan workspaces validate with:

```bash
uv run --project scripts/python validate-plan .plans/<id>/INDEX.md
```

Until then, verify by file presence/readback checks and grep for legacy references.

---

## Proposal Intake

Before creating a plan, verify:
1. The proposal path exists as `.proposals/<timestamp>-<slug>/INDEX.md` workspace or historical `.md` file
2. The proposal has `status: accepted` in workspace `metadata.md` or historical frontmatter
3. Extract goal → Goal section; non-goals → Non-Goals; decisions → Accepted Decisions

## Rules

- Do not implement changes while using this skill; produce the plan artifact only
- Plan workspaces must follow required 10-file + tasks/ taxonomy (not proposal-like rationale)
- Do not create `.plans/*.json` executable artifacts  
- Do not reference schema_version, init-*state files, or plan state schemas — these were deprecated in May 2026.
- Tasks files are senior-to-intern instructions, NOT runbook XML/execution state
- For non-trivial execution routing, load the **runbook** skill after validation