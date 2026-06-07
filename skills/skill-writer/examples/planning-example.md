---
name: skill-creation-plan
description: Use when creating or reviewing lifecycle artifacts such as proposals, plans, runbooks, reviews, decisions, and recovery paths for new OpenCode skill implementations.
class: planning
---

# Skill Creation Planning Guide

Planning artifact for implementing a new OpenCode skill following framework hygiene conventions through the proposal→plan→runbook progression.

## Artifact Contracts / Deliverables

| Stage | Output File | Success Criteria | Handoff State |
|-------|-------------|------------------|---------------|
| Create proposal | `.proposals/<id>/INDEX.md` | Accepted by stakeholders, scope defined | Ready for plan step |
| Draft plan | `.plans/1780845-skill-writer/INDEX.md` | All tasks identified, dependencies mapped | Ready for runbook conversion |
 | Execute runbook | `skills/skill-writer/SKILL.md` + templates/examples | Validated skill artifact deployed | Skill ready in framework |

## Decision Gates / Acceptance Criteria Mapping

- **Gate**: Class Selection Finalized
  - Condition: Chosen class aligns with trigger patterns from reference/class-selection.md
  - Impact if not met: Return to proposal stage with revised scope
  - Approver role: skill-hygiene maintainers or delegated reviewer

- **Gate**: Template Match Confirmed  
  - Condition: One existing template sufficiently matches use case, OR new template required
  - Impact if no match: Extend templates/ directory before proceeding
  - Approver role: OpenCode core team for new class introduction

## Handoff Requirements Documentation

```text
From Step A → To Step B:
- Required inputs: Trigger description, working examples from similar skills (e.g., skill-writer itself)
- Expected outputs: Validated SKILL.md with proper frontmatter at skills/<name>/SKILL.md  
- Validation needed before handoff: uv validate-skill-framework passes without errors

From Plan → Runbook:
- Required inputs: Approved proposal, populated templates/ and reference/, evidence of prior completions
- Expected outputs: Four example files in examples/* showing real usage patterns
- Validation needed before handoff: All acceptance criteria from steps 01-05 verified complete
```

## Rollback / Recovery Plan

| Failure Mode | Recovery Action | Responsible Party | State Cleanup |
|--------------|-----------------|-------------------|---------------|
| Example creation incomplete | Document missing files, expand content with working examples from templates | Skill-writer maintainer | None needed - preserve partial work for review |
| Validation fails on created skill | Extract specific error messages to evidence file, note exact line/column issues | Reviewer (review-work) | Archive current version before retrying fixes |

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Acceptance criteria unclear mid-plan | Halt and revise proposal section with stakeholders before proceeding |