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
uv run --directory scripts/python --no-sync python --version
uv run --directory scripts/python src/example.py
```

Use `--no-sync` for validation-only commands that do not need project dependencies. Normal `uv run` may create `.venv/` and `uv.lock`; those are ignored in this initial zero-dependency workspace until dependencies are introduced deliberately.

## Script Contract

Scripts intended for skills should:

- Be non-interactive.
- Exit non-zero on failure.
- Write errors to stderr.
- Avoid reading or writing outside paths explicitly passed by the caller.
- Avoid hardcoded secrets or environment-specific paths.
- Prefer stable machine-readable output when a skill will parse results.

## Dependency Policy

The initial workspace is intentionally zero-dependency. Do not install dependencies or commit lockfiles until a helper actually needs them and the dependency choice has been reviewed. When Python dependencies are added, revisit whether `scripts/python/uv.lock` should be committed.
