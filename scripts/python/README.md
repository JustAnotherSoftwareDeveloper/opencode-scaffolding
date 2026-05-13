# Python Scripts

Python helpers use uv in non-package project mode.

## Layout

- `src/`: executable Python entry points.
- `lib/`: shared modules imported by scripts in `src/`.

## Examples

```bash
uv sync --project scripts/python
uv run --directory scripts/python src/example.py
```

The example script runs `src/example.py`, which imports `lib/example.py` by adding the workspace root to `sys.path` at runtime.

## Validators

The workspace provides uv script targets for JSON and YAML validation:

```bash
uv sync --project scripts/python
uv run --project scripts/python validate-json opencode.json
uv run --project scripts/python validate-json path/to/data.json --schema path/to/schema.json
uv run --project scripts/python validate-json skills/plan/templates/plan.json --schema skills/plan/schema.json
uv run --project scripts/python validate-yaml skills/plan/schema.yaml  # legacy YAML artifacts only
uv run --project scripts/python pyright
```

Use `validate-json` for JSON syntax checks and add `--schema` when a local JSON Schema is available. Use `validate-yaml` for YAML syntax checks. These commands are intended for skills, agents, and harness workflows that create or edit JSON/YAML artifacts.

## Plan State Initializer

The `init-plan-state` command initializes a plan's state directory from a JSON plan file:

```bash
uv sync --project scripts/python
uv run --project scripts/python init-plan-state path/to/plan.json
```

This command:
- Validates the plan file against the plan schema
- Creates the state directory if it doesn't exist
- Checks that the state directory is empty or absent
- Creates metadata.json, MAIN.json, and step files
- Validates all generated files against their respective schemas
