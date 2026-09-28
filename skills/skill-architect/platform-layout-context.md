<!-- Historical and supporting reference only; current authority is platform-layout-and-discovery.md. -->
# Platform Layout Context

## Purpose

Provide historical layout context for the canonical platform-layout concern.

## Applicability

This passive reference applies when interpreting skill locations, entry points, and
class-oriented support-file conventions.

## Non-goals

It does not authorize discovery procedures, tool use, writes, migration, loading,
runtime enforcement, delegation, or completion. Cross-references and paths identify
context only: they do not create implicit or transitive loading or grant authority.

## Authority source

The current platform layout and script-placement authority is
[platform-layout-and-discovery.md](platform-layout-and-discovery.md). This document is
historical supporting context only and does not establish or override current policy.
An earlier version cited an approved architecture and migration ledger in a plan
workspace as authoritative; that statement is retained here as provenance of the former
text, not as a current competing authority.

## Evidence status

Historical supporting context is retained; current layout authority is consolidated in
the canonical concern document. The Python resolver details below reflect the checked-in
utility; earlier Python and host/origin assertions are explicitly identified as
historical and are not current policy.

## Historical context

**Status: historical.** The following class and layout material records conventions
from the earlier version of this supporting document. It is retained for reference,
not as current requirements, host policy, execution instructions, or authority.

- **Skill root**: `./` (the skill's base directory).
- **Entry point**: `SKILL.md` — the earlier text described this as the file the agent loads.
- **Support files**: Varies by skill class and purpose. The earlier text stated that
  documentation skills commonly use `reference/*.md`, `templates/`, `schemas/`,
  `snippets/`, and that planning skills (e.g., skill-architect) place reference `.md`
  files at the skill root.
- **Templates**: The earlier text referred to `skill-template-library` for template files.

## Skill Classes

**Status: historical.** The earlier text described each skill as having a `class` field
in its frontmatter and listed the following five classes:

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

The earlier text said template skeletons for each class are maintained in
`skill-template-library`. Its class rules described `operation`, `delegated`, and
`inline` as producing side effects and using numbered execution steps; `delegated` as
participating in delegation pipelines; and `planning` and `documentation` as passive
content classes. These statements preserve the former class-oriented context only.

## Platform Rules by Class

**Status: historical.** The earlier class-oriented rules stated:

- **Side effects**: `operation`, `delegated`, and `inline` produce side effects (file writes, tool calls).
  `planning` and `documentation` must not.
- **Delegation**: `delegated` participates in delegation pipelines.
  `operation`, `inline`, `planning`, and `documentation` do not sub-delegate.
- **Execution steps**: `operation`, `delegated`, and `inline` define execution steps with numbered prefixes.
  `planning` and `documentation` use passive content sections instead.

These are retained as historical descriptions, not current execution or loading authority.

## Discovery

**Status: historical claims; not current host policy.** The earlier text stated:

> The OpenCode agent selects a skill when its `description` field (in frontmatter)
> matches the current task context. The `class` field further constrains behavior.
>
> `planning` and `documentation` skills are loaded as passive references.
> `operation` skills are loaded as executable procedures.
> Skill files are not auto-indexed beyond their description field.
> The match is string/relevance-based, not structural.

Those statements are preserved as provenance only; this document does not assert present
host skill discovery, selection, indexing, or loading behavior.

## Directory Layout Convention

**Status: historical convention.** The earlier text stated that every
documentation-class and planning-class skill must structure its entry-point `SKILL.md`
with an index that lists every file within the skill's directory, each with a
one-sentence description. It said this enabled callers to determine which internal
files to read without scanning the directory or parsing unfamiliar filenames.

The earlier text also said operation-class skills may omit the file index and that
their entry point defines a procedural workflow instead. These are recorded as former
conventions only.

## Cross-Skill Interaction

**Status: historical convention, not current loading authority.** The earlier text
described cross-skill interaction as represented exclusively through skill loading
(using the skill tool or equivalent mechanism). It stated that no skill file may
contain a literal path to a file in another skill's directory, except scripts: they
may reference files in other directories because they are executed rather than read as
skill content. This description does not authorize loading or create an implicit or
transitive load chain.

## Scripts Directory

**Status: historical layout and runtime claims.** The earlier text stated that scripts
live outside skill directories at `scripts/<lang>/` and that the OpenCode platform
recognizes three script runtimes. That host-level statement is retained as historical
provenance only, not as a current host claim. The earlier text recorded:

- `scripts/python/` — Python scripts managed by uv.
  Entry points registered in `pyproject.toml [project.scripts]`.
  Invoked via `uv run --project <path> <entry-point> [args]`.
- `scripts/node/` — Node.js scripts managed by Bun.
  Invoked via `bun run --cwd <path> <script>`.
- `scripts/shell/` — Shell scripts and Makefiles.
  Invoked via `make -C <path> <target>`.

## Python Script Resolution

### Current checked-in resolver behavior

The following describes the checked-in script-root utility only; it is not a claim about
host skill discovery, skill origin, skill loading, or invocation.

1. A non-empty `$OPENCODE_SCRIPTS_PYTHON` environment variable overrides the defaults.
2. Otherwise, the resolver checks `<project-root>/opencode/scripts/python` (that is,
   `./opencode/scripts/python` relative to the project root). The project root is the
   explicit `project_root` argument when supplied, or the current working directory;
   the local root is selected only when it is a directory.
3. Otherwise, the resolver returns the global fallback
   `~/.config/opencode/scripts/python` without checking whether that directory exists.

The resolver labels these sources `env-var`, `project-local`, and `global`, respectively.
These details match `scripts/python/src/lib/resolve_script_root/core.py`.

### Former path and origin assertions (historical, superseded)

The earlier version of this document recorded this resolution order:

1. `$OPENCODE_SCRIPTS_PYTHON` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/python` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/python` — Global root (mandatory default, fallback).

This list is historical, not current behavior. In particular, the `.opencode` path in
item 2 is not the current Python resolver path; the checked-in resolver uses
`<project-root>/opencode/scripts/python` as documented above. The earlier text also
asserted that skill origin determines root selection:

- If the skill is loaded from a **project-local** skills directory (e.g.,
  `<project>/.opencode/skills/<name>/`), use
  `<project-root>/.opencode/scripts/python` as the primary root. Resolution falls
  through to the global root if a script or shared lib module is not found locally.
- If the skill is loaded from the **global** skills directory
  (`~/.config/opencode/skills/<name>/`), use
  `~/.config/opencode/scripts/python` as the primary root.
- Project-local scripts may override or augment global scripts: when resolving a
  reusable script or a shared lib module (`lib.shared.*`), the project-local root is
  checked first, and only if absent does resolution fall through to the global root.

These origin-selection and shared-library-precedence assertions are preserved as
historical provenance only. They are not established by the checked-in resolver and
must not be read as current policy.

**Resolution mechanism in skill invocation steps (historical example only):** The
earlier document included this invocation example:

```shell
uv run --project ~/.config/opencode/scripts/python <entry-point> [args]
```

It also stated that if a project had no `.opencode/scripts/python/` directory,
resolution fell through silently to the global root. Both the command's association
with skill invocation and that hidden-path fallback statement are historical text;
neither changes the current resolver behavior documented above.

### Historical Python directory and invocation conventions

The earlier text recorded these conventions:

- `src/cli/` — CLI entry points, using click decorators.
- `src/lib/` — Library logic, organized by domain.
- `tests/` — Tests, using pytest with CliRunner for CLI integration tests.
- Coverage target: 100% (`fail_under = 100` in pyproject.toml).
- Non-interactive; exit non-zero on failure; errors to stderr.

It also gave this invocation pattern:

> Skills invoke Python scripts via the canonical pattern:
> `uv run --project <scripts-python-path> <entry-point> [args]`

The directory, tooling, and invocation statements are retained as historical context,
not current host-level invocation policy.

### Node Script Resolution

**Status: historical layout context.** These Node root strings remain distinct from the
Python project segment and agree with the checked-in resolver's Node branch; the
surrounding invocation and layout claims below are retained as historical context.

**Resolution order** (as recorded in the earlier document):

1. `$OPENCODE_SCRIPTS_NODE` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/node` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/node` — Global root (mandatory default, fallback).

**Directory layout conventions (historical):**

- `src/cli/<script-name>.ts` — CLI entry points, using cleye.
- `src/lib/<script-name>/` — Per-script library packages.
- `src/lib/shared/` — Shared utilities for cross-script use.
- `tests/<script-name>.test.ts` — Unit tests.
- `tests/<script-name>.cli.test.ts` — CLI integration tests.
- `package.json`, `tsconfig.json`, `biome.json` — Tooling configuration.
- Non-interactive; exit non-zero on failure; errors to stderr.

**Invocation pattern (historical):**

> Skills invoke Node scripts via the canonical pattern:
> `bun run --cwd <scripts-node-path> <script>`

**Cross-references retained from the earlier document:**

For detailed Node script conventions — including directory layout, canonical invocation,
tooling, testing, and coverage — see the shared conventions skill
`skill-node-script-conventions`.

For the decision framework that determines whether a Node script is appropriate, see
the `class-decision-flow.md` `Task Involves Deterministic, Repeatable, or Token-Heavy
Processing` section.

These descriptions do not authorize loading either referenced skill or establish
present host behavior.

### Shell Script Resolution

**Status: historical layout context.** The shell roots below are retained separately
from the Python and Node rules; their root strings agree with the checked-in resolver's
shell branch. Invocation and implementation details remain historical context.

**Resolution order** (as recorded in the earlier document):

1. `$OPENCODE_SCRIPTS_SHELL` — Environment variable explicit override (optional, highest priority).
2. `<project-root>/.opencode/scripts/shell` — Project-local root (mandatory default, checked second).
3. `~/.config/opencode/scripts/shell` — Global root (mandatory default, fallback).

**Directory layout conventions (historical):**

- `lib/` — Reusable shell libraries (functions sourced by entry-point scripts).
- `src/` — Executable entry-point scripts (shebang-based, `set -euo pipefail`).
- `Makefile` — Central Makefile defining targets for all entry-point scripts.
- Scripts target `/bin/bash` with `set -euo pipefail` for strict error handling.
- Non-interactive; exit non-zero on failure; errors to stderr.

**Invocation pattern (historical):**

> Skills invoke shell scripts via the canonical pattern:
> `make -C <scripts-shell-path> <target>`

The earlier text said this delegates to the Makefile, which runs the underlying script
with the correct environment and arguments. This is retained as historical wording,
not as a current host-level invocation claim.

**Cross-reference retained from the earlier document:**

For detailed Bash script conventions — including directory layout, shared library
patterns, and testing — see the `skill-bash-conventions` skill.

Mention of another skill does not load it. This historical reference grants no implicit
or transitive loading, execution, or completion authority.
