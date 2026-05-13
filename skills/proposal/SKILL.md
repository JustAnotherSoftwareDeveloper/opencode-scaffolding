---
name: proposal
description: Create a bounded proposal before planning or execution, covering scope, alternatives, risks, and acceptance criteria.
---

# Proposal Skill

Use this skill before planning or editing when the requested outcome is non-trivial, ambiguous, or likely to affect agents, skills, commands, permissions, state, or orchestration behavior.

## Artifact Contract

Proposal artifacts live at:

```text
.proposals/<unix-timestamp>-slug.md
```

- `<unix-timestamp>` is seconds since epoch at artifact creation time.
- `slug` is lowercase, hyphen-separated, and human-readable.
- Preserve the original timestamp and slug when updating an existing proposal unless superseding it is explicitly intended.

## Lifecycle

1. **Classify intent**: The orchestrator performs lightweight classification and identifies needed discovery, drafting, or critique.
2. **Create or update artifact**: Write the proposal to `.proposals/<unix-timestamp>-slug.md`.
3. **Run embedded critique**: Delegate critique to an appropriately sized `analysis-*` worker and record findings directly in the proposal.
4. **Revise**: Incorporate user feedback and critique into the same proposal artifact.
5. **Decision**: Mark the proposal `accepted`, `needs-clarification`, `rejected`, or `superseded`.
6. **Return summary**: Report artifact path, status, key tradeoffs, and the next user decision.

## Routing

| Work | Worker Family | Purpose |
| --- | --- | --- |
| Local discovery | `generic-*` | Inventory files, conventions, and constraints |
| External research | `websearch-*` | Gather current source-backed information |
| Proposal drafting and revision | `doc-writer-*` | Write clear proposal prose |
| Embedded critique | `analysis-*` | Identify gaps, risks, and acceptance problems |

Choose the smallest capable worker size for each bounded task. Escalate only when scope, ambiguity, or risk requires it.

## Proposal Artifact Format

Use the shared proposal artifact skeleton at:

```text
templates/proposal-template.md
```

Copy the template into `.proposals/<unix-timestamp>-slug.md`, fill all placeholders, and preserve the section order unless the proposal explicitly requires a justified deviation.

## Section Guidance

- **Goal**: Restate the outcome and what success means.
- **Intent Classification**: Classify work type, risk, needed research, needed discovery, and whether user choices are required.
- **Current State**: Summarize discovered facts, exact files, conventions, and constraints.
- **Problem / Opportunity**: Explain the pain or improvement target.
- **In Scope / Out of Scope**: Draw explicit boundaries.
- **Recommended Approach**: State the preferred path and why it is the smallest correct direction.
- **Alternatives Considered**: Compare viable alternatives and explain why they are not preferred.
- **Artifact and State Impact**: Identify files, artifact paths, and state areas that will be created or modified later.
- **Delegation Model**: Identify worker families, skills, and review approach at a high level; detailed steps belong in a plan.
- **Risks and Unknowns**: Capture uncertainty, compatibility concerns, permission concerns, state drift, and user choices.
- **Embedded Quality Check**: Record critique directly in this proposal artifact.
- **Acceptance Criteria**: Provide independently verifiable checks.
- **Decision**: Record current status, decision maker when known, and next action.

## Rules

- Do not implement changes while using this skill.
- Do not write the execution plan here; use the `plan` skill after acceptance or explicit direct-plan authorization.
- Keep critique embedded in the proposal artifact rather than creating a separate review lane.
- Use only currently available sized worker families for delegation, plus `multimodal-looker` only for visual/PDF/image work.
- Do not create new worker agents, change model IDs, alter provider configuration, or edit generated/runtime directories unless explicitly requested.
- Ask targeted questions when critical facts are missing.
