# Scripts Workspace

This directory contains repeatable helper scripts for OpenCode skills and orchestration workflows. Keep helpers small, deterministic, and safe to call from automation.

## Layout

```text
scripts/
  shell/   # Bash/shell helpers, invoked through Make
  python/  # Python helpers, invoked through uv
  node/    # TypeScript helpers, invoked through Bun
```

Each runtime workspace uses the same convention:

- `src/`: executable entry points called by Make, uv, npm, or Bun.
- `lib/`: reusable modules/libraries imported or sourced by entry points.

## Invocation Patterns

Shell:

```bash
make -C scripts/shell help
make -C scripts/shell run
```

TypeScript/Node with Bun:

```bash
bun run --cwd scripts/node help
```

Python with uv:

```bash
uv run --directory scripts/python python --version
uv sync --project scripts/python
uv run --directory scripts/python src/example.py
uv run --project scripts/python validate-json opencode.json
uv run --project scripts/python validate-runbook .runbooks/<id>/main.xml
uv run --project scripts/python init-runbook-state .runbooks/<id>/main.xml  # v3 creates runbook-local state.xml and manifest indexes
```

Runbook validation is XML/XSD-first for the v3 target workflow. XSDs under `skills/runbook/schemas/` are the schema contract; validation must run through Python/bash helpers, not LLM judgment. Legacy JSON runbook schemas/templates are retired for new target workflows.

Run `uv sync --project scripts/python` after dependency or script-target changes. The Python workspace now has deliberate validation dependencies, so `scripts/python/uv.lock` should be kept with the workspace for reproducible validator execution.

## Script Contract

Scripts intended for skills should:

- Be non-interactive.
- Exit non-zero on failure.
- Write errors to stderr.
- Avoid reading or writing outside paths explicitly passed by the caller.
- Avoid hardcoded secrets or environment-specific paths.
- Prefer stable machine-readable output when a skill will parse results.

## Dependency Policy

Only add dependencies when a helper needs them and the dependency choice has been reviewed. The Python validators intentionally use `PyYAML`, `jsonschema`, `lxml`, and a dev `pyright` dependency; keep `scripts/python/uv.lock` updated when these dependencies change.
