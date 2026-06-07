---
name: skill-writer-coordinator
description: Use when orchestrating the creation of OpenCode skills by delegating to sub-skills for validation, documentation review, and template application.
class: orchestrated
---

# Skill Writer Coordinator (Orchestrated)

Coordinates multi-phase workflow for creating new OpenCode skills following framework hygiene conventions through delegation to specialized worker skills.

## Subskills / Dependencies

- `skill-writer` — Author SKILL.md files with proper frontmatter structure
  - `validate-skill-framework` — Verify skill artifacts pass schema validation (atomic phase)
    - `review-work` — Final quality check on completed skills
  
## Delegation Boundaries

| Work Item | Route To | Notes |
|-----------|----------|-------|
| Schema validation | text/documentation/config-validation | Run uv validator script |
| Content review & structure | review-work | Check prompt quality, permission safety |
| Skill loading verification | multimodal-looker | Only for skills with image/PDF references |

## State Ownership Map

- Phase 1 (draft): `skill-writer` owns `.proposals/<id>/` until accepted
- Phase 2 (create templates): Transition to `templates/*.md` directory ownership  
- Phase 3 (finalize skill): State moves to created SKILL.md with validation evidence

## Quality Gates / Validation

```text
Gate: Framework Compliance
Condition: Valid frontmatter + proper trigger language + class-appropriate structure
Action if fail: Return to skill-writer for corrections, preserve working sections only

Gate: Review Approval  
Condition: review-work status = completed, no blocker issues identified
Action if fail: Document findings in `.runbooks/<id>/evidence/`, request revision round
```

## Failure Handling Strategy

- **Template mismatch**: Compare against closest matching class template from `skills/skill-writer/templates/` and update accordingly
- **Validation failure cascade**: Capture specific error messages, create minimal reproducer, then apply fix to the full file
- **Quality gate revert**: Archive current version with timestamp suffix (e.g., `-v1-draft.md`) before making changes

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Subskills have conflicting guidance | Load `skill-hygiene` first for taxonomy resolution; document variance in evidence file |