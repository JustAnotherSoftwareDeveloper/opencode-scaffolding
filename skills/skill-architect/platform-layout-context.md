# Platform Context: Where Skills Live

- **Skill root**: `./` (the skill's base directory).
- **Entry point**: `SKILL.md` — the file the agent loads.
- **Support files**: Varies by skill class and purpose. Documentation skills commonly use `reference/*.md`, `templates/`, `schemas/`, `snippets/`. Planning skills (e.g., skill-architect) place reference `.md` files at the skill root.
- **Templates**: Maintained in `skill-template-library` — see that skill for template files.

## Skill Classes

Each skill has a `class` field in its frontmatter.
The five valid classes are:

- `operation` — See skill-template-library for the class template skeleton.
  Broad/default class for single bounded procedures that are independent and self-validating.
- `delegated` — See skill-template-library for the class template skeleton.
  Receives delegation packets and performs bounded subtasks within a pipeline or orchestration.
- `inline` — See skill-template-library for the class template skeleton.
  Single-pass reasoning-heavy skill executed directly by the main agent.
- `planning` — See skill-template-library for the class template skeleton.
  Reference sources loaded during planning or architecting activities.
  No side effects.
- `documentation` — See skill-template-library for the class template skeleton.
  Passive data store for domain-shared reference content.
  No side effects, no execution steps.
  Other skills consume its content via relative-path references.

Template skeletons for each class are maintained in `skill-template-library`.

## Platform Rules by Class

- **Side effects**: `operation`, `delegated`, and `inline` produce side effects (file writes, tool calls).
  `planning` and `documentation` must not.
- **Delegation**: `delegated` participates in delegation pipelines.
  `operation`, `inline`, `planning`, and `documentation` do not sub-delegate.
- **Execution steps**: `operation`, `delegated`, and `inline` define execution steps with numbered prefixes.
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
  Invoked via `uv run --project <path> <entry-point> [args]`.
- `scripts/node/` — Node.js scripts managed by Bun.
  Invoked via `bun run --cwd <path> <script>`.
- `scripts/shell/` — Shell scripts and Makefiles.
  Invoked via `make -C <path> <target>`.

### Python Script Resolution

**Resolution order** (checked in sequence):

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
uv run --project ~/.config/opencode/scripts/python <entry-point> [args]
```

If a project has no `.opencode/scripts/python/` directory, resolution falls through silently to the global root.

**Directory layout conventions:**

- `src/cli/` — CLI entry points, using click decorators.
- `src/lib/` — Library logic, organized by domain.
- `tests/` — Tests, using pytest with CliRunner for CLI integration tests.
- Coverage target: 100% (`fail_under = 100` in pyproject.toml).
- Non-interactive; exit non-zero on failure; errors to stderr.

**Invocation pattern:**

Skills invoke Python scripts via the canonical pattern:
`uv run --project <scripts-python-path> <entry-point> [args]`

### Node Script Resolution

**Resolution order** (checked in sequence):

1. `$OPENCODE_SCRIPTS_NODE` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/node` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/node` — Global root (mandatory default, fallback).

**Directory layout conventions:**

- `src/cli/<script-name>.ts` — CLI entry points, using cleye.
- `src/lib/<script-name>/` — Per-script library packages.
- `src/lib/shared/` — Shared utilities for cross-script use.
- `tests/<script-name>.test.ts` — Unit tests.
- `tests/<script-name>.cli.test.ts` — CLI integration tests.
- `package.json`, `tsconfig.json`, `biome.json` — Tooling configuration.
- Non-interactive; exit non-zero on failure; errors to stderr.

**Invocation pattern:**

Skills invoke Node scripts via the canonical pattern:
`bun run --cwd <scripts-node-path> <script>`

**Cross-references:**

For detailed Node script conventions — including directory layout, canonical invocation, tooling, testing, and coverage — see the shared conventions skill `skill-node-script-conventions`.

For the decision framework that determines whether a Node script is appropriate, see the class-decision-flow.md `Task Involves Deterministic, Repeatable, or Token-Heavy Processing` section.

### Shell Script Resolution

**Resolution order** (checked in sequence):

1. `$OPENCODE_SCRIPTS_SHELL` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/shell` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/shell` — Global root (mandatory default, fallback).

**Directory layout conventions:**

- `lib/` — Reusable shell libraries (functions sourced by entry-point scripts).
- `src/` — Executable entry-point scripts (shebang-based, `set -euo pipefail`).
- `Makefile` — Central Makefile defining targets for all entry-point scripts.
- Scripts target `/bin/bash` with `set -euo pipefail` for strict error handling.
- Non-interactive; exit non-zero on failure; errors to stderr.

**Invocation pattern:**

Skills invoke shell scripts via the canonical pattern:
`make -C <scripts-shell-path> <target>`

This delegates to the Makefile which runs the underlying script with the correct environment and arguments.

**Cross-reference:**

For detailed Bash script conventions — including directory layout, shared library patterns, and testing — see the `skill-bash-conventions` skill.
