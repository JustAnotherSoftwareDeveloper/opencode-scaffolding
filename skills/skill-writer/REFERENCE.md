# Skill Writer Reference

Platform rules, authoring guidance, and on-demand reference for creating OpenCode skills. Complement to `SKILL.md` — read this for depth, not for procedure.
For editorial and authoring conventions (wording, formatting, conciseness, DRY rules), see `./style-guide.md`.

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
- **`delegated`** — Receives delegation packets and performs bounded subtasks within a pipeline or orchestration; includes final workers and workflow stages (including decomposers) invoked by a delegator
- **`inline`** — Single-pass reasoning-heavy skill executed directly by the main agent, optional direct tool calls, no worker/sub-skill orchestration as its own workflow
- **`orchestrated`** — Coordinates sub-skills, workers, phases, or quality gates. Orchestrated skills use the 7-section canonical layout (Frontmatter, Purpose/Intro, Execution Steps, Worker Strategy, Verification Checklist, Self-Validation, Cross-References). See `./templates/orchestrated.SKILL.template.md` for the canonical skeleton.
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

## Orchestrated Skill Structure

Orchestrated skills (`class: orchestrated`) follow a 7-section canonical layout. This layout is defined in `./templates/orchestrated.SKILL.template.md`.

### Seven Sections

1. **Frontmatter** — Standard `name`, `description`, `class` YAML block.
2. **Purpose / H1 Intro** — One-line description of the orchestrated workflow.
3. **Execution Steps** — Ordered sequence of steps, each prefixed with a step type.
4. **Worker Strategy** — Dispatch model, concurrency limits, data flow.
5. **Verification Checklist** — Assertions that every orchestrated run must pass.
6. **Self-Validation** — Structural checks for the SKILL.md itself.
7. **Cross-References** — Relative links to support files.

### Step Types

Each step in the Execution Steps section uses a type prefix in bold:

- **`Delegated: <Worker Skill>`** — Delegates a sub-task to a worker skill by forwarding a delegation packet. The worker is another SKILL.md that receives the packet and executes autonomously. Use when the sub-work is multi-step, domain-specific, or benefits from a separate skill's context.
- **`Inline: <Inline Skill Name>`** — Declares and executes a named inline reasoning step directly within the orchestrator's body. Inline steps are single-pass, non-delegated reasoning blocks that do not merit a standalone skill. Use when the work is a focused logical or transform step that runs in one pass.
- **`Decompose`** — Breaks a complex input or goal into multiple sub-packets, typically fanning out to parallel delegated workers. No worker name follows the prefix; the step body describes the decomposition strategy.
- **`Verify`** — Runs verification checks against the output of prior steps. No worker name follows the prefix; the step body describes what to verify and how.

### Inline Steps vs. Standalone Inline Skills

**Inline steps replace the old standalone Inline Skills section concept.** Do not create a separate Inline Skills section in an orchestrated skill. Instead, use `Inline:` prefixed steps inside Execution Steps. The `inline` class is still valid for standalone skills that are self-contained, but within an orchestrated skill, inline work is expressed as a step type, not a separate section.

## Collation Output Structure

Orchestrated skills that produce collated output use the following default format.

**Default format**: JSON.

**Top-level shape**:

```json
{
  "status": "success" | "partial" | "failure",
  "source_tags": ["<<tag-1>>", "<<tag-2>>"],
  "items": [ ... ]
}
```

- `status` — Overall collation result. `success`: all units succeeded. `partial`: some units failed. `failure`: all units failed.
- `source_tags` — Tag strings that identify which skills or workers produced this collation.
- `items` — Array of individual collation units. Each collation unit defines its own item shape; there is no fixed inner schema.

**Extensibility**: The top-level contract provides discovery and routing. Downstream consumers inspect `status` and `source_tags` to decide how to handle `items`. Collation units are free to define their own item schema.

For detailed collation conventions, see `./reference/collation-reference.md`.

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
- **7-section layout (orchestrated only)**: Orchestrated skills use the canonical 7-section layout. Verify all seven sections are present and in order.
- **No stale Inline Skills section**: Orchestrated skills must not contain a standalone Inline Skills section. Inline work goes into Execution Steps as `Inline:` steps.
- **No Exit Criteria section**: Exit Criteria has been replaced by Verification Checklist. Orchestrated skills must not contain an Exit Criteria section.
- **No general breakdown instructions**: Breakdown logic belongs only in `Decompose` step types. Do not add free-standing breakdown instructions elsewhere.

## Gotchas

- **`description` is too generic** — Agent loads skill for wrong tasks. Fix: Be specific: action + domain + qualifier.
- **Frontmatter YAML is invalid** — Agent fails to parse skill entirely. Fix: Validate YAML before finalizing.
- **`name` doesn't match directory** — Skill is unreachable or misrouted. Fix: Match exactly: `skills/<<name>>/SKILL.md` → `name: <<name>>`.
- **Body reads like a tutorial** — Bloated context, agent wastes tokens. Fix: Strip all explanation; keep only imperative steps.
- **Examples inline** — Violates convention, adds noise. Fix: Remove; put worked examples in `reference/` if essential.
- **Prose copied from archive** — Redundant, may be stale or incorrect. Fix: Rewrite from scratch using only shape inspiration.
- **Class selected by habit** — Mismatch between class contract and actual behavior. Fix: Consult the class list and the decision prompts below.
- **Assumes templates exist** — REFERENCE.md references nonexistent files. Fix: Use forward-looking relative paths; note the file may not exist yet.
- **Old template sections remain** — Verification Checklist exists but Phases, Failure Handling, or Quality Gates sections linger from the old template. Fix: Remove all old-template sections. The canonical 7-section layout replaces them.
- **Inline step used where delegated step needed** — `Inline:` is for single-pass reasoning that runs in one pass. `Delegated:` is for multi-step sub-work that merits its own skill context. Use the right type for the right granularity.

## Decision Prompts for Class Selection

Use these questions when uncertain. Start with operation as the default; only choose another class when a specific condition clearly applies:

- **Default — Single bounded, independent, self-validating, no sub-delegation?** → `operation`
- **Receives a delegation packet?** → `delegated`
- **Single-pass reasoning-heavy, main agent executes directly?** → `inline`
- **Coordinates phases, workers, or sub-skills?** → `orchestrated`
- **Primary output is a lifecycle artifact (proposal → plan → runbook)?** → `planning`