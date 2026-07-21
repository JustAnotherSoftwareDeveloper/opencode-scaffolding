# Implementation Format

## Required Structure

- Use one H2 heading for each affected area.
- Use one H3 heading for each concrete change within that area.
- Name the affected artifact, interface, workflow, or policy and its modification in the H3 heading.
- Add one or two short bullets that state the modification and its reason or intended effect.
- Use selective bolding for short labels only.

## Compliant Structure

```markdown
## Proposal Skill Contract

### `skills/proposal/SKILL.md` — Require concrete implementation changes

- **Change:** Replace the generic sequence requirement with a requirement to name affected artifacts and modifications.
- **Reason:** Keep generated implementation documents tied to the proposal decision and evidence.
```

## Rejected Structure

```markdown
## Implementation Changes

### Prepare

- Prepare the implementation.

### Integrate

- Integrate affected systems.
```

Reject this structure because it names lifecycle phases instead of affected targets and modifications.

## Evidence Boundaries

Include dependencies, decision gates, validation checks, rollout procedures, or stakeholder actions only when one of these conditions applies.

- A copied source document states the item.
- An explicit proposal assumption supports the item.
- An external constraint requires the item.

Exclude these unsupported items.

- Generic implementation steps.
- Unstated dependencies.
- Standard practices without source justification.
- Stakeholder actions without an explicit requirement.
