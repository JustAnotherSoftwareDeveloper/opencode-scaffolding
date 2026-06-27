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

## Scripts Directory

Scripts live outside skill directories at `scripts/<lang>/`.
The OpenCode platform recognizes three script runtimes:

- `scripts/python/` — Python scripts managed by uv.
  Entry points registered in `pyproject.toml [project.scripts]`.
  Invoked via `uv run --directory <path> <entry-point> [args]`.
- `scripts/node/` — Node.js scripts managed by Bun.
  Invoked via `bun run --cwd <path> <script>`.
- `scripts/` (root) — Shell scripts and Makefiles.
  Invoked via `make -C <path> <target>`.

### Global vs Project-Local Resolution Order

Scripts are resolved from two mandatory roots with an optional explicit override.
This is an **architecture constraint**, not a future option — every script invocation must use this resolution order:

1. `$OPENCODE_SCRIPTS_PYTHON` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/python` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/python` — Global root (mandatory default, fallback).

**How skill origin determines root selection:**

- If the skill is loaded from a **project-local** skills directory (e.g., `<project>/.opencode/skills/<name>/`), use `<project-root>/.opencode/scripts/python` as the primary root.
  Resolution falls through to the global root if a script or shared lib module is not found locally.
- If the skill is loaded from the **global** skills directory (`~/.config/opencode/skills/<name>/`), use `~/.config/opencode/scripts/python` as the primary root.
- Project-local scripts may override or augment global scripts: when resolving a reusable script or a shared lib module (`lib.shared.*`), the project-local root is checked first, and only if absent does resolution fall through to the global root.

**Resolution mechanism in skill invocation steps:**

```shell
# Resolve scripts directory (see platform-layout-context.md for full rules)
SCRIPTS_PYTHON="${OPENCODE_SCRIPTS_PYTHON:-$PWD/.opencode/scripts/python}"
SCRIPTS_PYTHON="${SCRIPTS_PYTHON:-$HOME/.config/opencode/scripts/python}"
uv run --directory "$SCRIPTS_PYTHON" <entry-point> [args]
```

If a project has no `.opencode/scripts/python/` directory, resolution falls through silently to the global root.

Python scripts follow these conventions:
- CLI entry points in `src/cli/`, using click decorators.
- Library logic in `src/lib/`, organized by domain.
- Tests in `tests/`, using pytest with CliRunner for CLI integration tests.
- Coverage target: 100% (`fail_under = 100` in pyproject.toml).
- Non-interactive, exit non-zero on failure, errors to stderr.

Skills invoke scripts via the canonical pattern:
`uv run --directory <scripts-python-path> <entry-point> [args]`

### Node Script Resolution

Scripts written in TypeScript for Node/Bun follow their own resolution order and conventions.
This subsection documents how Node scripts are resolved, laid out, invoked, and tooled.

**Resolution order** (checked in sequence):

1. `$OPENCODE_SCRIPTS_NODE` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/node` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/node` — Global root (mandatory default, fallback).

For detailed Node script conventions — including directory layout, canonical invocation, tooling, testing, and coverage — see the shared conventions skill at `skills/skill-node-script-conventions/`.

For the decision framework that determines whether a Node script is appropriate, see the class-decision-flow.md `Task Involves Deterministic, Repeatable, or Token-Heavy Processing` section.