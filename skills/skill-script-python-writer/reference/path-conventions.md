# Path Conventions

Generated scripts live under `scripts/python/` within either the global or project-local root.
Both roots follow the same directory layout; the difference is their filesystem location and resolution priority.

> **Path resolution rules are authoritative in `skill-architect` (platform-layout-context).**  
> This file provides only script-python-writer-specific conventions (directory layout, pyproject.toml).  
> See the platform-layout-context document for: Global/Project-Local resolution order, environment variable override (`$OPENCODE_SCRIPTS_PYTHON`), skill-origin-based root selection, resolution shell snippet, and shared-lib precedence rules.

## Directory Layout (Both Roots)

```text
scripts/python/
  src/
    cli/<script_name>.py        # click CLI (main entry point)
    lib/<script_name>/          # library package (one per script)
      __init__.py
      core.py                   # core logic
      formats.py                # I/O formatting (if needed)
      validators.py             # validation logic (if needed)
  tests/
    test_<script_name>.py       # unit tests for lib/
    test_<script_name>_cli.py   # integration tests for CLI
```

## pyproject.toml Hatchling Packages

Hatchling with explicit `packages` does not auto-discover subpackages.
`src/lib/shared/` is a subpackage of `lib` and must be explicitly listed:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/cli", "src/lib", "src/lib/shared"]
```

This is the only change needed in `pyproject.toml` for shared lib support.
The existing `[tool.coverage.run] source = ["cli", "lib"]` already covers `lib.shared.*` modules.
