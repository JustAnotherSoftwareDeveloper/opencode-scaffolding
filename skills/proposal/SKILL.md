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

1. **Classify intent and depth**: Determine proposal depth tier and intent classification before drafting.
2. **Run discovery protocol**: Conduct local discovery and/or external research as needed.
3. **Run clarification protocol**: Ask only critical questions to resolve blocking unknowns.
4. **Create or update artifact**: Write the proposal to `.proposals/<unix-timestamp>-slug.md`.
5. **Run embedded critique**: Delegate critique to an appropriately sized `analysis-*` worker and record findings directly in the proposal.
6. **Revise**: Incorporate user feedback and critique into the same proposal artifact.
7. **Decision**: Mark the proposal `accepted`, `needs-clarification`, `rejected`, or `superseded`.
8. **Return summary**: Report artifact path, status, key tradeoffs, and the next user decision.

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

## Proposal Depth Tiers

Use the following depth tiers to determine the appropriate level of effort:

| Depth | When to use | Discovery needed | Research needed | Planning notes |
| --- | --- | --- | --- | --- |
| `none` | Trivial/direct execution; no proposal needed | None | None | Direct execution without proposal |
| `light` | Narrow, low-risk change with a short proposal | Minimal local check (file existence, constraints) | None | No formal handoff required |
| `standard` | Normal non-trivial harness/product/code change | Local discovery of files, constraints, and conventions | Optional, for syntax/config conventions or comparable examples | Handoff section required |
| `deep` | Ambiguous, architecture-sensitive, high-risk, or cross-cutting change | Parallel local analysis/research to stabilize understanding | External research as needed for standards or breaking changes | Full handoff with traceability into plan gates |

Use `none` for trivial tasks (e.g., typo fixes, surface changes). Use `light` for narrow changes in one file. Use `standard` for normal non-trivial work. Use `deep` for architecture-sensitive or harness-wide changes.

## Discovery Protocol

Perform discovery based on depth tier:

- **Local discovery**: Inventory relevant files, existing artifacts, constraints, and conventions.
- **External research**: Gather source-backed information from documentation, standards, or comparable examples.
- **Prior-art/current-state**: Identify relevant previous proposals, plans, or state artifacts.

Record discovery results as facts, not assumptions. Use `explore` or `generic-*` workers for discovery tasks.

## Clarification/Interview Protocol

When critical unknowns exist:

- Ask only questions that block a correct proposal.
- Prefer recommended defaults when ambiguity is minor.
- Classify unresolved gaps as critical, minor, or ambiguous.
- Record assumptions explicitly in the proposal.
- Do not ask questions that can be resolved by discovery.

Use `analysis-sm` or `doc-writer-sm` workers for clarification tasks.

## Proposal-to-Plan Handoff

For `standard` and `deep` proposals, include a structured handoff section that planning can consume:

```md
## Planning Handoff

### Agreed Objective
<One or two sentences that become plan.objective.>

### Accepted Decisions
- <Decision and reason.>

### Scope Boundaries
In scope:
- ...

Out of scope:
- ...

### Constraints
- ...

### Acceptance Criteria to Preserve
- <Criterion that planning must map to gates/steps.>

### Risks to Monitor During Planning
- ...

### Suggested Delegation / Skills
- discovery: explore or generic-sm/md
- analysis: analysis-md/lg
- implementation: coding-md/lg
- docs/templates: doc-writer-sm/md

### OpenCode Docs Required for Handoff / Delegation Design
- Agents: <https://opencode.ai/docs/agents/>
- Skills: <https://opencode.ai/docs/skills/>
- Permissions: <https://opencode.ai/docs/permissions/>
- Tools: <https://opencode.ai/docs/tools/>
- Rules / AGENTS.md: <https://opencode.ai/docs/rules/>
- Commands, when command handoffs are in scope: <https://opencode.ai/docs/commands/>
- Config, when agent or permission registration is in scope: <https://opencode.ai/docs/config/>

### Required Planning Analysis
- problem breakdown
- dependency graph
- parallel groups
- delegation packet inventory
```

This section should be human-readable markdown with consistent headings so the planning skill can consume it reliably.

## Embedded Critique Criteria

Critique should check:

- Completeness: All required sections are filled
- Clarity: Language is precise and unambiguous
- Scope boundaries: In/out of scope are explicit
- Alternatives: At least one plausible non-trivial alternative is considered
- Risk handling: Risks are listed with severity and mitigation
- Acceptance criteria: Criteria are independently verifiable
- Plan-readiness: Standard/deep proposals contain a complete planning handoff section

Critique should not turn the proposal into an execution plan.

## Future Proposal Validity Criteria

A proposal is valid when:

- Depth and intent classification are fully populated
- Discovery results are recorded as facts rather than assumptions
- Clarification questions are asked only when critical to set boundaries
- Unresolved gaps are tagged as critical, minor, or ambiguous
- Assumptions are explicitly listed with rationale
- Standard/deep proposals contain a planning handoff section with agreed objective, scope boundaries, acceptance criteria, risks, and suggested delegation
- Alternatives include at least one plausible non-trivial alternative or an explicit explanation of why alternatives are not meaningful
- Risks are listed with severity and mitigation strategy

## Rules

- Do not implement changes while using this skill.
- Do not write the execution plan here; use the `plan` skill only after the proposal is accepted.
- Keep critique embedded in the proposal artifact rather than creating a separate review lane.
- Use only currently available sized worker families for delegation, plus `multimodal-looker` only for visual/PDF/image work.
- Do not create new worker agents, change model IDs, alter provider configuration, or edit generated/runtime directories unless explicitly requested.
- Ask targeted questions when critical facts are missing.
