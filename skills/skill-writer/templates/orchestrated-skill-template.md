---
name: <skill-name>
description: Use when orchestrating subskills, workers, state ownership, or quality gates across multi-phase workflows.
class: orchestrated
---

# <<Skill Name>> Skill Template (Orchestrated)

Replace all `<placeholder>` values before using. Match `name` to the directory name exactly.

## Class Purpose

Orchestrated skills coordinate subskills, workers, state ownership, quality gates, and failure handling across multi-phase workflows. They delegate work and manage execution flow rather than perform tasks directly.

## When to Use This Template

- You need to coordinate multiple skills or steps
- Work spans phases with handoffs between them
  - Subskill dependencies exist (e.g., requires other skills)
  - State ownership transfers between steps
    Quality gates are needed before progression
    
## Template Structure

```markdown
---
name: <skill-name>                    # Must match directory name, lowercase with hyphens
description: Use when ...            # Trigger for orchestration scenario
class: orchestrated                  # Required class declaration
---

# <<Concrete Skill Name>>

A brief description of the workflow coordination this skill provides.

## Subskills / Dependencies

List skills that must run before/after or are called by this orchestration:

- `skill-one` — precondition step...
  - `skill-two` — core processing...
  
## Delegation Boundaries

Describe what work is delegated to workers vs orchestrated here:

| Work Item | Route To | Notes |
|-----------|----------|-------|
| Task A    | worker-md | ...   |
| Review    | multimodal-looker | For visuals only |

## State Ownership Map

Document which skill/steps own which state files during execution lifecycle.

- Phase 1: `skill-a` owns `<path>` until completion
- Phase 2: Transition to `skill-b` ownership

## Quality Gates / Validation

Specify checkpoints that must pass before progressing:

```text
Gate: <name>
Condition: ...
Action if fail: Return/pause with error state
```

## Failure Handling Strategy

Describe recovery paths for common failure scenarios. Include state cleanup or rollback requirements.

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Subskill fails partway through | Retry from last good checkpoint, preserve partial outputs |
```

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: orchestrated): Must be exactly this value for class identification

> **Warning**: This is a template file. Copy it to create actual skills; do not load `templates/orchestrated-skill-template.md` as an active skill.