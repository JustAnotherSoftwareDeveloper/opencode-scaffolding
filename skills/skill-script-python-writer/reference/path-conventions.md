# Path Conventions

Generated scripts live under `scripts/python/` within either the global or project-local root.
Both roots follow the same directory layout; the difference is their filesystem location and resolution priority.

> Do not load a planning skill during ordinary script execution; the checked-in resolver
> behavior is stated here for context. This file covers the script-writer-specific
> conventions for path resolution, directory layout, and `pyproject.toml`.

The checked-in Python resolver first honors a non-empty `OPENCODE_SCRIPTS_PYTHON`
override, then checks `./opencode/scripts/python` relative to the project root,
selecting it only when that directory exists. Otherwise, it returns the global fallback
`~/.config/opencode/scripts/python` without checking whether that directory exists.
These paths describe verified resolver behavior, not host-level skill discovery,
loading, or invocation policy; this file does not define skill-origin-based root
selection.

## Directory Layout (Both Roots)

Keep one `src/cli/` directory for thin command adapters and one `src/lib/` root for
internal library code. Organize implementation packages by cohesive feature or domain,
not one package per CLI command. Adapters handle command input, wiring, and the
established CLI contract; reusable behavior belongs to its canonical feature/domain
package.

**PLACE-001 fixture annotation:** In this layout, `<command_module>` is the `snake_case`
Python module name for a CLI command, `<feature_or_domain>` is a `snake_case` package
name for a cohesive capability, and `<test_module>` is a `snake_case` test subject.
Replace each placeholder with its concrete identifier before using the layout.

```text
scripts/python/
  src/
    cli/<command_module>.py     # thin Click command adapter
    lib/<feature_or_domain>/     # cohesive feature/domain implementation
      __init__.py
      core.py                   # canonical behavior, when needed
    lib/shared/                  # optional narrow shared primitives
  tests/
    test_<test_module>.py       # tests for the owning implementation
    test_<command_module>_cli.py # tests for the command contract
```

Preserve existing package and module names and paths unless an inventory-grounded
decision identifies a specific minimal change. Do not rename a package merely to match
an illustrative example or because another command consumes it.

Before adding behavior, locate the canonical implementation and its tests and check for
equivalent behavior. Extend the canonical implementation rather than copying it. Keep
`src/lib/shared/` only for small, domain-neutral primitives reused across domains; a
second command consumer alone does not justify extraction.

## Package Configuration

The current `scripts/python/pyproject.toml` lists `src/cli` and `src/lib` as wheel
package roots. That records the checked-in configuration; do not infer nested-package
or resource inclusion from the directory tree alone. This layout guidance does not
authorize additional package roots or assert built-artifact contents.

The `lib.*` import paths describe internal project dependencies. This layout does not
require a public `lib.*` API or a separate library distribution, and it does not
guarantee external imports or direct-source invocation modes.
