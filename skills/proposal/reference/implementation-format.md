# Implementation Format

Use this reference for `implementation.md`. Follow the sentence-case and plain
Markdown rules in [proposal-format.md](./proposal-format.md).

## Structure

- Use one H2 heading for each affected area: a component, interface, workflow,
  policy, or closely related set of artifacts.
- Use one H3 heading for each concrete change in that area.
- Name the affected target and its modification in each H3 heading.
- Add one or two concise bullets: the precise change, then its reason or effect
  when the heading does not make that clear.
- Use selective bolding for short labels only.

Group multiple changes under one H2 only when they affect the same area and are
reviewed together. Start a new H2 when the target area, owner-facing concern, or
reason for the change differs. Do not use lifecycle phases as area headings.

## Compliant Multi-Change Structure

```markdown
## Proposal skill contract

### `skills/proposal/SKILL.md` — Apply proportional document validation

- **Change:** Replace fixed section and sentence checks with semantic-core and optional-section checks.
- **Reason:** Keep validation aligned with the generated document format.

### `skills/proposal/SKILL.md` — Apply conditional navigation

- **Change:** Require a table of contents only when proposal complexity makes it useful.

## Proposal templates

### `skills/proposal/templates/PROPOSAL.md` — Use the semantic core

- **Change:** Replace decorative boxes with sentence-case headings and ordinary lists.
```

## Rejected Structure

```markdown
## Implementation changes

### Prepare

- Prepare the implementation.

### Integrate

- Integrate affected systems.
```

Reject this structure because it names lifecycle phases instead of affected
targets and modifications.

## Optional Content And Evidence

Include dependencies, decision gates, validation checks, rollout procedures, or
stakeholder actions only when a copied source, explicit proposal assumption, or
external constraint supports them. Omit their headings when no supported content
exists.

Exclude generic implementation steps, unstated dependencies, standard practices
without source justification, and stakeholder actions without an explicit
requirement.
