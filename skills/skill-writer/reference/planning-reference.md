# Planning Skill Reference

Depth material for planning-class skills.
Provides philosophical grounding, authoring guidance, per-section writing direction, a conformance checklist, and a class relationship matrix.
See `./planning.SKILL.template.md` for the canonical section layout.

## Philosophical Overview

A planning skill is a reference context, not a procedure runner.
Load it during any planning or architecting activity to ground decisions in documented reality.
It answers "what exists, how it fits together, and what constraints apply" — not "what steps do I execute."
The primary consumer is a human or agent reasoning about structure, trade-offs, and placement of new work.
Planning skills do not produce side effects, modify files, or invoke tools.
They exist to prevent reasoning from fabricated facts.

## When To Create A Planning Skill

Typical triggers:

- **Project onboarding**: New team members need a map of module boundaries, data flow, and deployment topology.
- **Major refactor**: The planning skill captures the "as-is" and "to-be" states during transition.
- **New service integration**: Document contracts, authentication flows, and failure modes for a new external dependency.
- **Architecture decision record**: Consolidate scattered ADRs into one loadable context.
- **Framework migration**: Language, framework, or runtime changes that affect all future code.
- **Domain handoff**: Encode subsystem knowledge for the receiving team.

## Section Authoring Guidance

Write each template section with the following depth and focus.
Bullet counts are guidance, not hard limits.

### When To Use

Write 2-4 bullet points covering domain-specific triggers: planning or design discussion within the domain, code review affecting domain code, or onboarding to the domain.
Make each trigger specific enough for an agent to decide yes/no within one sentence.

### Decision Records

Record key architectural decisions within this domain with rationale and trade-offs.
Use 2-5 bullet points. Link to ADR files under `docs/adr/` or similar. Explain why past domain choices were made and what alternatives were considered.

### Constraints & Assumptions

List domain-specific preconditions, invariants, non-goals, and known limitations.
Use 2-5 bullet points. Explain what the domain boundary does not include and why.
This section prevents downstream reasoning from assuming capabilities that do not exist.

### Verification Criteria

Define 2-5 gate checks that the domain planning artifact must pass before handoff.
Each check must be a concrete, testable assertion.

## Conformance Gate

Run this checklist against a completed planning SKILL.md before declaring it done.

- [ ] Frontmatter has `class: planning`.
- [ ] Frontmatter `description` starts with `"Use when planning or architecting"`.
- [ ] At minimum, When to Use and Verification Criteria sections exist.
- [ ] All variable placeholders (`<<...>>`) have been replaced with real content.
- [ ] Every claim is backed by the actual codebase — no invented facts.
- [ ] No procedure steps exist — planning skills describe structure, not execution.
- [ ] No tool invocation instructions exist — planning skills are read-only references.

## Relationship To Other Skill Classes

| Class | Purpose | Output | Loaded When |
|---|---|---|---|
| **planning** | Reference context for reasoning | Structural knowledge, no side effects | Planning, design, review, onboarding |
| **operation** | Single bounded procedure | Side effects (file writes, tool calls) | A specific task needs executing |
| **delegated** | Subtask receiver in a pipeline | Delegation packet result | A delegator forwards a packet |
| **inline** | Single-pass reasoning by main agent | Reasoning result, optional tool calls | Complex reasoning step in current context |
| **orchestrated** | Coordinate sub-skills and phases | Collated results from workers | Multi-phase workflow with delegation |

A planning skill should never be loaded when the goal is to modify files or run a procedure.
Use the Decision Prompts in `./REFERENCE.md` when the boundary is unclear.