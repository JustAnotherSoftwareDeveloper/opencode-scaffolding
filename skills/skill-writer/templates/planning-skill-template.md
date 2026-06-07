---
name: <skill-name>
description: Use when creating or reviewing lifecycle artifacts such as proposals, plans, runbooks, reviews, decisions, and recovery paths.
class: planning
---

# <<Skill Name>> Skill Template (Planning)

Replace all `<placeholder>` values before using. Match `name` to the directory name exactly.

## Class Purpose

Planning skills create or review lifecycle artifacts such as proposals, plans, runbooks, reviews, decisions, and recovery paths. They establish structure for coordinated execution through defined handoff contracts.

## When to Use This Template

- You need to define a new workflow before executing it
  - Creating proposal → plan → runbook progression
    Establishing quality gates or acceptance criteria
    Designing rollback/recovery procedures

## Template Structure

```markdown
---
name: <skill-name>                    # Must match directory name, lowercase with hyphens
description: Use when ...            # Trigger for this planning activity
class: planning                      # Required class declaration
---

# <<Artifact Title>> Planning Guide

Brief description of the artifact being planned or reviewed.

## Artifact Contracts / Deliverables

Define expected outputs and their contracts at each stage.

| Stage | Output File | Success Criteria | Handoff State |
|-------|-------------|------------------|---------------|
| Create proposal | `.proposals/<id>/INDEX.md` | Accepted by stakeholders | Ready for plan step |
| Draft plan | `.plans/<id>/INDEX.md` | All tasks identified, dependencies mapped | Ready for runbook conversion |

## Decision Gates / Acceptance Criteria Mapping

List key decisions that must be made before progressing:

- **Gate**: <name>  
  - Condition: `<specific measurable criteria>`
  - Impact if not met: Stop/suspend or re-plan path
  - Approver role: `<stakeholder>`

## Handoff Requirements Documentation

Specify what state/state files, artifacts, and context must transfer between steps. Include ownership and validation responsibilities.

```text
From Step A → To Step B:
- Required inputs: <list>
- Expected outputs: <list with paths>  
- Validation needed before handoff: ...
```

## Rollback / Recovery Plan

Document how to reverse or recover from various failure scenarios. Include state file cleanup requirements and manual intervention points.

| Failure Mode | Recovery Action | Responsible Party | State Cleanup |
|--------------|-----------------|-------------------|---------------|
| Partial runbook execution | Remove created files, reset .state.xml checkpoints | Skill author | Delete artifacts in `/tmp/test-run/` |

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Acceptance criteria unclear mid-plan | Halt and revise proposal section with stakeholders before proceeding |
```

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: planning): Must be exactly this value for class identification

> **Warning**: This is a template file. Copy it to create actual skills; do not load `templates/planning-skill-template.md` as an active skill.