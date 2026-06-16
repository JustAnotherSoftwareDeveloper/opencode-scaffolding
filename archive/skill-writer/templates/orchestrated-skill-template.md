---
name: <skill-name>
description: Use when coordinating delegated skills, state ownership, quality gates, or multi-phase workflows.
class: orchestrated
---

# <<Skill Name>> Skill Template (Orchestrated)

Replace all `<placeholder>` values before using. Match `name` to the directory name exactly.

## Class Purpose

**Heavy-procedure coordinator-only.** Orchestrated skills own routing, state transitions, reconciliation, failure handling, and quality gates. **Does not perform worker tasks directly.** Everything is delegated to workers or delegated backing skills spawned via delegation packets.

- Listens for trigger events requiring multi-phase coordination
- Constructs delegation packets with explicit input/output contracts
- Spawns delegated skills as specialized workers
- Owns state file transitions and reconciliation between phases

**Key distinction from `delegated`:** Orchestrated skills define coordination protocols; delegated skills execute them as isolated workers.

## When to Use This Template

- You need to coordinate multiple phases with handoffs between them
  - Subskill dependencies exist (e.g., requires other skills)
  - State ownership transfers between steps
  - Quality gates are needed before progression
  
**Required:** List all delegated backing skills in the [Delegated Backing Skills](#delegated-backing-skills) section below.

## Template Structure

```markdown
---
name: <skill-name>                    # Must match directory name, lowercase with hyphens
description: Use when ...            # Trigger for orchestration scenario  
class: orchestrated                  # Required class declaration
---

# <<Concrete Skill Name>>

A brief description of the workflow coordination this skill provides.

## Delegated Backing Skills

List delegated skills that orchestrator spawns to perform worker-side work. Each must have explicit input/output contracts.

| Delegated Skill | Purpose | Input From Orchestrator | Output To Orchestrator |
|-----------------|---------|------------------------|------------------------|
| `<skill-name>`  | <brief purpose> | JSON fields: `field1`, `path/to/state.xml` | Structured result via `/tmp/...`, stdout, or state update |

## Subskills / Dependencies

List skills that must run before/after in the orchestration sequence. Delegated skills are listed under [Delegated Backing Skills](#delegated-backing-skills) above.

- `<skill-name>` — precondition step...
  - `validate-skill-framework` — verify artifacts (non-worker phase)
  
## State Ownership Map

Document which skill/steps own which state files during execution lifecycle.

- Phase 1: Owned by this orchestrator until delegation packet is constructed
- Phase 2: Delegated skill `<name>` owns execution with input from orchestrator
- Phase 3: Return to orchestrator ownership for reconciliation  

## Quality Gates / Validation

Specify checkpoints that must pass before progressing. Runbook-level gates use `review-work`; delegated-side validation runs within worker context.

```txt
Gate: <name>
Condition: ...
Action if fail: Return/pause with error state
```

## Failure Handling Strategy

Describe recovery paths for common failure scenarios. Include state cleanup or rollback requirements. Note that delegated skills may return `failed` status requiring orchestrator retry/repair.

- **Delegated skill fails**: Receive failure JSON from worker, analyze error_type, decide: repair packet and retry, skip dependent tasks, or escalate to user
- **Packet defect detected**: Modify delegation-packet.md template and re-spawn delegated skill  

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Delegated skill fails validation | Inspect worker output JSON; check evidence requirements in its SKILL.md; update packet and retry |
```