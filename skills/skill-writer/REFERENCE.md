# Skill Writer Reference

Platform rules, authoring guidance, and on-demand reference for creating OpenCode skills. Complement to `SKILL.md` — read this for depth, not for procedure.

## Platform Context: Where Skills Live

- **Skill root**: `~/.config/opencode/skills/<<name>>/`
- **Entry point**: `SKILL.md` — the file the agent loads
- **Support files**: `REFERENCE.md`, `reference/*.md`, schemas, templates alongside `SKILL.md`
- **Archived versions**: `~/.config/opencode/archive/<<name>>/SKILL.md` — read for shape only, never prose
- **Templates**: `~/.config/opencode/skills/templates/<<class>>.SKILL.template.md` — e.g. `operation.SKILL.template.md`, `delegated.SKILL.template.md`, `inline.SKILL.template.md`, `orchestrated.SKILL.template.md`, `planning.SKILL.template.md`
- **Schemas (future)**: `~/.config/opencode/skills/skill-hygiene/schemas/*.xsd` — canonical class contracts

**Discovery**: The OpenCode agent selects a skill when its `description` field (in frontmatter) matches the current task context. Skill files are not auto-indexed beyond their description field — the match is string/relevance-based, not structural.

## Required Frontmatter

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
- **Should capture** the *trigger intent*, not a feature list. Bad: *"Use when needing to write files."* Good: *"Use when creating or rewriting an OpenCode SKILL.md from requirements and source material."*
- **Length**: Under 1024 characters. Prefer 60–200 characters; shorter is sharper.
- **Avoid** referencing specific filenames, paths, or future infrastructure that may not exist.
- For task-mode guardrails, see [Trigger / Non-Trigger Eval](#trigger--non-trigger-eval) below.

### `class`

One of exactly five values:

- **`operation`** — Broad/default class for single bounded procedures that are independent, self-validating, and do not sub-delegate. A Normalize Input step absorbs free-form input, structured packets, files, or tool outputs into one internal input, avoiding separate modes for different invocation shapes.
- **`delegated`** — Worker specialization designed to receive delegation packets
- **`inline`** — Single-pass reasoning-heavy skill executed directly by the main agent, optional direct tool calls, no worker/sub-skill orchestration as its own workflow
- **`orchestrated`** — Coordinates sub-skills, workers, phases, or quality gates
- **`planning`** — Proposal / plan / runbook lifecycle creation and review

No other classes are valid. If uncertain, lean toward `operation`.

## Progressive Disclosure

Keep `SKILL.md` procedural and compact (under ~100 lines). Push reference material here (`REFERENCE.md`) or into `reference/*.md` files. The agent should be able to act on `SKILL.md` alone; support files are consulted on demand for depth.

**Pattern**: In `SKILL.md`, write something like:

> See `REFERENCE.md` for class selection guide and frontmatter rules.

Do **not** inline reference prose into `SKILL.md`.

## Trigger / Non-Trigger Eval

When composing a skill's `description`, anticipate both **positive** and **near-miss** trigger scenarios:

### Positive trigger

- The description matches requests where the skill should activate.
- Phrase as: *"Use when <<action>> <<domain>> <<optional qualifier>>."*
- Be specific enough to avoid false negatives — generic descriptions cause misses.

### Near-miss negative

- The description should *not* match adjacent but unrelated requests.
- Example: A skill for *"creating SKILL.md files"* should not match *"editing an existing SKILL.md"* — those are different tasks.
- Test mentally: "Would this description match a request for X?" If yes for the wrong X, tighten.

### Manual eval procedure

1. Write plausible user requests that should trigger the skill.
2. Check if the description clearly covers them.
3. Write plausible near-miss requests that should NOT trigger.
4. Verify the description excludes them.

## Validation / Manual Checklist Guidance

Every authored skill should be verified against this checklist before declaring done:

- **Name match**: `name` in frontmatter matches directory under `skills/`.
- **Description prefix**: Starts with `"Use when"`, is specific, and captures trigger intent.
- **Class validity**: One of the five allowed values.
- **Original prose**: No text copied from archived versions, templates, or reference files.
- **Body is procedural**: Steps, conditions, decisions. Not a tutorial, not a reference.
- **No examples**: Do not add an examples section or inline example commands.
- **Reference links**: If `REFERENCE.md` or `templates/` are referenced, they are linked by relative path but their content is not inlined.
- **Valid YAML**: Frontmatter parses without errors.

## Gotchas

- **`description` is too generic** — Agent loads skill for wrong tasks. Fix: Be specific: action + domain + qualifier.
- **Frontmatter YAML is invalid** — Agent fails to parse skill entirely. Fix: Validate YAML before finalizing.
- **`name` doesn't match directory** — Skill is unreachable or misrouted. Fix: Match exactly: `skills/<<name>>/SKILL.md` → `name: <<name>>`.
- **Body reads like a tutorial** — Bloated context, agent wastes tokens. Fix: Strip all explanation; keep only imperative steps.
- **Examples inline** — Violates convention, adds noise. Fix: Remove; put worked examples in `reference/` if essential.
- **Prose copied from archive** — Redundant, may be stale or incorrect. Fix: Rewrite from scratch using only shape inspiration.
- **Class selected by habit** — Mismatch between class contract and actual behavior. Fix: Consult the class list and the decision prompts below.
- **Assumes templates exist** — REFERENCE.md references nonexistent files. Fix: Use forward-looking relative paths; note the file may not exist yet.

## Decision Prompts for Class Selection

Use these questions when uncertain. Start with operation as the default; only choose another class when a specific condition clearly applies:

- **Default — Single bounded, independent, self-validating, no sub-delegation?** → `operation`
- **Receives a delegation packet?** → `delegated`
- **Single-pass reasoning-heavy, main agent executes directly?** → `inline`
- **Coordinates phases, workers, or sub-skills?** → `orchestrated`
- **Primary output is a lifecycle artifact (proposal → plan → runbook)?** → `planning`



