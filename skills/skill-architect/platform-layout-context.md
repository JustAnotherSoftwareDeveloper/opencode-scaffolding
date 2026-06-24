# Platform Context: Where Skills Live

- **Skill root**: `./` (the skill's base directory).
- **Entry point**: `SKILL.md` — the file the agent loads.
- **Support files**: `reference/*.md`, `templates/`, `schemas/`, `snippets/`.

## Skill Classes

Each skill has a `class` field in its frontmatter.
The six valid classes are:

- `operation` — `./templates/operation.SKILL.template.md`
  Broad/default class for single bounded procedures that are independent and self-validating.
- `delegated` — `./templates/delegated.SKILL.template.md`
  Receives delegation packets and performs bounded subtasks within a pipeline or orchestration.
- `inline` — `./templates/inline.SKILL.template.md`
  Single-pass reasoning-heavy skill executed directly by the main agent.
- `orchestrated` — `./templates/orchestrated.SKILL.template.md`
  Coordinates sub-skills, workers, phases, or quality gates.
- `planning` — `./templates/planning.SKILL.template.md`
  Reference sources loaded during planning or architecting activities.
  No side effects.
- `documentation` — `./templates/documentation.SKILL.template.md`
  Passive data store for domain-shared reference content.
  No side effects, no execution steps.
  Other skills consume its content via relative-path references.

Each template lives at `./templates/<class>.SKILL.template.md`.
It provides the canonical skeleton for that class.

## Platform Rules by Class

- **Side effects**: `operation`, `delegated`, `inline`, and `orchestrated` produce side effects (file writes, tool calls).
  `planning` and `documentation` must not.
- **Delegation**: `orchestrated` and `delegated` participate in delegation pipelines.
  `operation`, `inline`, `planning`, and `documentation` do not sub-delegate.
- **Execution steps**: All classes except `planning` and `documentation` define execution steps with numbered prefixes.
  `planning` and `documentation` use passive content sections instead.

## Discovery

The OpenCode agent selects a skill when its `description` field (in frontmatter) matches the current task context.
The `class` field further constrains behavior.

`planning` and `documentation` skills are loaded as passive references.
`operation` skills are loaded as executable procedures.
Skill files are not auto-indexed beyond their description field.
The match is string/relevance-based, not structural.

## Directory Layout Convention

Every documentation-class and planning-class skill must structure its entry-point `SKILL.md` with an index that lists every file within the skill's directory, each with a one-sentence description.
This convention enables callers to determine which internal files to read without needing to scan the directory or parse unfamiliar filenames.

Operation-class skills may omit the file index.
Their entry point defines a procedural workflow instead.

## Cross-Skill Interaction

Cross-skill interaction is represented exclusively through skill loading (using the skill tool or equivalent mechanism).
No skill file may contain a literal path to a file in another skill's directory.
Scripts are the sole exception — they may reference files in other directories since they are executed rather than read as skill content.