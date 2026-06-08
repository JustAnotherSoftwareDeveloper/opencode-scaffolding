---
name: skill-writer-coordinator
description: Use when orchestrating the creation of OpenCode skills by delegating to sub-skills for validation, documentation review, and template application.
class: orchestrated
---

# Skill Writer Coordinator (Orchestrated)

**Heavy-procedure coordinator-only.** Orchestrated skills own routing, state transitions, reconciliation, failure handling, and quality gates. **Does not perform worker tasks directly.** Everything is delegated to workers or delegated backing skills spawned via delegation packets.

Coordinates multi-phase workflow for creating new OpenCode skills following framework hygiene conventions through delegation to specialized worker skills.

## Delegated Backing Skills

List delegated skills that orchestrator spawns to perform worker-side work. Each has explicit input/output contracts defined by the coordinator:

| Delegated Skill | Purpose | Input From Orchestrator | Output To Orchestrator |
|-----------------|---------|------------------------|------------------------|
| `skill-writer` | Author SKILL.md files with proper frontmatter structure | Draft content, proposal directory path | Completed skill artifact at `.proposals/<id>/` |
| `validate-skill-framework` | Verify skill artifacts pass schema validation | File paths to validate | Validation result JSON with status/errors |
| `review-work` | Final quality check on completed skills | Skill file contents | Review complete signal or blocker issues |

## Delegation Boundaries

This orchestrator constructs delegation packets with explicit routing:

| Work Item | Delegated To (Worker) | Notes |
|-----------|----------------------|-------|
| Schema validation | delegated worker via `validate-skill-framework` packet | Run uv validator script on target files |
| Content review & structure | spawned reviewer skill (`review-work`) | Check prompt quality, permission safety |
| Skill loading verification | multimodal-looker (for skills with image/PDF) | Only for specific reference types |

## State Ownership Map

This coordinator owns state file transitions and reconciliation between phases. Delegated workers own execution within their bounded context:

- **Phase 1 (draft)**: Orchestrator owns `.proposals/<id>/` until delegation packet is constructed
- **Phase 2 (execute)**: Delegates to worker skill which owns input/output through completion  
- **Phase 3 (reconcile)**: Return to orchestrator ownership for state update and quality gate evaluation

## Quality Gates / Validation

These are coordinator-level gates that orchestrate quality checks before progression. Worker-side validation is handled within delegated skills:

```txt
Gate: Framework Compliance (Phase 1)
Condition: Valid frontmatter + proper trigger language + class-appropriate structure in skill artifact
Action if fail: Return to worker-delegation for corrections, preserve working sections only

Gate: Review Approval (Phase 2)  
Condition: Delegated `review-work` status = completed, no blocker issues identified in evidence file
Action if fail: Document findings in `.runbooks/<id>/evidence/`, request revision round from skill-writer worker
```

## Failure Handling Strategy

Recovery paths when delegated workers return failure signals. Orchestrator analyzes, repairs packets, and re-spawns as needed:

- **Template mismatch**: Worker returns structure error → Load `skill-hygiene` for taxonomy resolution; update packet template with correct guidance before re-delegating to skill-writer worker
- **Validation failure cascade**: Receive specific validator errors from delegated `validate-skill-framework` → Create minimal reproducer, fix artifact via skill-writer delegation  
- **Quality gate revert**: Worker reports blocker issues → Archive current version with timestamp suffix (e.g., `-v1-worker.md`) before spawning revision packet to skill-writer

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Subskills have conflicting guidance | Load `skill-hygiene` first for taxonomy resolution; document variance in evidence file |