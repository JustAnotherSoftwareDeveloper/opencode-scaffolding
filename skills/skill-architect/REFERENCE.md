# Skill Architect Reference

Depth material for planning-class skills in the skill-architect domain.
Provides philosophical grounding, per-section authoring guidance, a conformance gate checklist, and a class relationship matrix.
This file is consulted for depth, not procedure.
See `./SKILL.md` for the procedural body and frontmatter rules.

## Philosophical Overview

A planning skill is a reference context, not a procedure runner.
Load it during any planning or architecting activity to ground decisions in documented reality.
It answers "what exists, how it fits together, and what constraints apply" — not "what steps do I execute."
The primary consumer is a human or agent reasoning about structure, trade-offs, and placement of new work.
Planning skills do not produce side effects, modify files, or invoke tools.
They exist to prevent reasoning from fabricated facts.

Skill-architect specifically anchors skill-design reasoning to the five-class taxonomy, template conventions, and progressive disclosure pattern defined by the skill-writer platform.
It is the canonical reference for deciding where a new skill belongs, what shape its SKILL.md takes, and which invariants apply across all skills.

## Section Authoring Guidance

The following rules govern each section of the skill-architect SKILL.md.
Apply them when authoring or reviewing the body file.

### When To Use

Write 2-4 bullet points covering domain-specific triggers: planning or design discussion within skill architecture, code review affecting skills/, or onboarding to skill-authoring workflows.
Each trigger must be specific enough for an agent to decide yes/no within one sentence.
Do not include generic triggers that match every task — qualify by domain (skill design, class selection, ADR review).

### Decision Records

Record key architectural decisions within the skill-architect domain with rationale and trade-offs.
Use 2-5 bullet points.
Link to ADR files under `docs/adr/` or similar when they exist.
Explain why past domain choices were made and what alternatives were considered.
Every decision record must include a Trade-off: statement that acknowledges what was lost or deferred.

### Constraints & Assumptions

List domain-specific preconditions, invariants, non-goals, and known limitations.
Use 2-5 bullet points.
Explain what the skill-architect domain boundary does not include and why.
This section prevents downstream reasoning from assuming capabilities that do not exist (e.g., that planning skills can produce side effects or that class selection is fuzzy).

### Verification Criteria

Define 2-5 gate checks that the skill-architect SKILL.md must pass before handoff.
Each check must be a concrete, testable assertion — not a subjective guideline.
Prefer checks that an automated tool or agent can evaluate: YAML validity, regex matches, line counts, presence or absence of specific patterns.

## Conformance Gate

Run this checklist against a completed skill-architect SKILL.md before declaring it done.

- [ ] Frontmatter has `class: planning`.
- [ ] Frontmatter `description` starts with `"Use when planning or architecting"`.
- [ ] At minimum, When to Use and Verification Criteria sections exist.
- [ ] All variable placeholders (`<<...>>`) have been replaced with real content.
- [ ] Every claim is backed by the actual codebase — no invented facts.
- [ ] No procedure steps exist — planning skills describe structure, not execution.
- [ ] No tool invocation instructions exist — planning skills are read-only references.
- [ ] Cross-references to `./REFERENCE.md` or `./reference/*.md` point to files that exist.
- [ ] File is under 200 lines with one sentence per line and Title Case headings.

## Relationship To Other Skill Classes

| Class | Purpose | Output | Loaded When |
|---|---|---|---|
| **planning** | Reference context for reasoning | Structural knowledge, no side effects | Planning, design, review, onboarding |
| **operation** | Single bounded procedure | Side effects (file writes, tool calls) | A specific task needs executing |
| **delegated** | Subtask receiver in a pipeline | Delegation packet result | A delegator forwards a packet |
| **inline** | Single-pass reasoning by main agent | Reasoning result, optional tool calls | Complex reasoning step in current context |
| **orchestrated** | Coordinate sub-skills and phases | Collated results from workers | Multi-phase workflow with delegation |

A planning skill should never be loaded when the goal is to modify files or run a procedure.
An operation skill should never be loaded during reasoning-only tasks.
A delegated skill must accept a well-formed packet and return structured output.
An inline skill is ephemeral — load it for one reasoning pass, then discard.
An orchestrated skill owns sub-delegation and result collation.

When the boundary between classes is unclear, consult the Decision Records in `./SKILL.md` and trace the proposed skill's contract: does it produce side effects, does it delegate, does it run in a single pass? The answers map to exactly one class.

## Further Reading

- `./SKILL.md` — Procedural body and frontmatter rules for this skill.
- `../skill-writer/REFERENCE.md` — Platform-level class taxonomy and template rules.
- `../skill-writer/style-guide.md` — Editorial conventions for all SKILL.md files.
- `./reference/planning-reference.md` — Generic planning skill authoring guidance.