### Philosophical Overview

A planning skill is a reference context, not a procedure runner.
Load it during any planning or architecting activity to ground decisions in documented reality.
It answers "what exists, how it fits together, and what constraints apply" — not "what steps do I execute."
The primary consumer is a human or agent reasoning about structure, trade-offs, and placement of new work.
Planning skills do not produce side effects, modify files, or invoke tools.
They exist to prevent reasoning from fabricated facts.

> **Note**: Planning-class design guidance previously in skill-architect has been folded into these reference files. skill-architect is deprecated.

# Required Frontmatter

Every `SKILL.md` must open with valid YAML frontmatter containing exactly three fields:

```yaml
---
name: <<skill-name>>
description: "Use when <<trigger description>>."
class: <<one-of-five-classes>>
---
```

### `name`

- **Regex**: `^[a-z][a-z0-9-]*$` — lowercase alphanumeric with hyphens, must start with a letter.
- **Must match** the directory name under `skills/`. If the directory is `skills/foo-bar/`, the name is `foo-bar`.
- **Stability**: Once published, renaming breaks skill references. Choose deliberately.

### `description`

- **Must start** with `"Use when"` — this is the agent's primary selection signal.
- **Exception**: For the `planning` class, the description must start with `"Use as planning reference"` instead.
- **Should capture** the *trigger intent*, not a feature list. Bad: *"Use when needing to write files."* Good: *"Use when creating or rewriting all OpenCode skill files under skills/<name>/ (SKILL.md, reference/*.md, and templates/) from requirements and source material."*
- **Length**: Under 1024 characters. Prefer 60–200 characters; shorter is sharper.
- **Avoid** referencing specific filenames, paths, or future infrastructure that may not exist.
- For task-mode guardrails, see `./trigger-eval.md`.

### `class`

One of exactly five values:

- **`operation`** — Broad/default class for single bounded procedures that are independent, self-validating, and do not sub-delegate. A Normalize Input step absorbs free-form input, structured packets, files, or tool outputs into one internal input, avoiding separate modes for different invocation shapes.
- **`delegated`** — Receives delegation packets and performs bounded subtasks within a pipeline or orchestration; includes final workers and workflow stages (including decomposers) invoked by a delegator
- **`inline`** — Single-pass reasoning-heavy skill executed directly by the main agent, optional direct tool calls, no worker/sub-skill orchestration as its own workflow
- **`orchestrated`** — Coordinates sub-skills, workers, phases, or quality gates. Orchestrated skills use the 7-section canonical layout (Frontmatter, Purpose/Intro, Execution Steps, Worker Strategy, Verification Checklist, Self-Validation, Cross-References). See `../templates/orchestrated.SKILL.template.md` for the canonical skeleton.
- **`planning`** — Reference sources loaded during planning or architecting activities (formal plan creation, informal discussion, design review, onboarding, code review) that document structural knowledge about the codebase. Planning skills must not produce side effects, modify files, invoke tools, or define execution steps.

No other classes are valid. If uncertain, lean toward `operation`.

### Planning Skill Authoring Guidance

The following rules govern each section of a planning-class `SKILL.md`.
Apply them when filling the `../templates/planning.SKILL.template.md`.

#### Domain Context

Capture structural knowledge about the domain: API architecture, testing setup, code architecture, data flow, deployment topology.
Use 2-5 bullet points or short paragraphs.

#### Key Considerations

Capture domain-specific constraints, assumptions, trade-offs, non-goals, and known limitations.
Use 2-5 bullet points.

#### Related Skills

List related skill names with one-sentence descriptions.
Format: `<skill-name>: <one-sentence description of when to use this skill>`.
This is for quick reference during planning.

#### Cross-References

Link to relevant docs, common workflows, examples, ADRs, or other reference material.
Use bullet list of links.

#### Triggers for Creating a Planning Skill

Typical domain-independent scenarios that warrant a planning skill:

- **Project onboarding**: New team members need a map of module boundaries, data flow, and deployment topology.
- **Major refactor**: The planning skill captures the as-is and to-be states during transition.
- **New service integration**: Document contracts, authentication flows, and failure modes for a new external dependency.
- **Architecture decision record**: Consolidate scattered ADRs into one loadable context.
- **Framework migration**: Language, framework, or runtime changes that affect all future code.
- **Domain handoff**: Encode subsystem knowledge for the receiving team.



### Class Decision Flow

Use these questions when uncertain. Start with operation as the default; only choose another class when a specific condition clearly applies:

- **Default — Single bounded, independent, self-validating, no sub-delegation?** → `operation`
- **Receives a delegation packet?** → `delegated`
- **Single-pass reasoning-heavy, main agent executes directly?** → `inline`
- **Coordinates phases, workers, or sub-skills?** → `orchestrated`

### Class Selection Rationale

Each of the five classes has a distinct contract for side effects, delegation, and output shape, enabling the agent to load the correct behavior without ambiguity.
A skill whose behavior spans multiple classes must be split or rewritten; hybrid classes are not supported.

Templates enforce structural consistency and reduce authoring errors (missing sections, wrong step prefixes).
Template divergence requires coordinated updates across all templates.

### Class Boundary Disambiguation

- A planning skill should never be loaded when the goal is to modify files or run a procedure.
- An operation skill should never be loaded during reasoning-only tasks.
- A delegated skill must accept a well-formed delegation packet and return structured output.
- An inline skill is ephemeral — load it for one reasoning pass, then discard.
- An orchestrated skill owns sub-delegation and result collation.

When the boundary between classes is unclear, trace the proposed skill's contract: does it produce side effects, does it delegate, does it run in a single pass?
The answers map to exactly one class.
