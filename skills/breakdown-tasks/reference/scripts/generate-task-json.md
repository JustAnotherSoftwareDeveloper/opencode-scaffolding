# Generate Task Json

`generate-task-json` reads one `TaskDraftList` JSON object from standard input.
It loads `~/.config/opencode/skills/breakdown-tasks/schema/task-input.schema.json` and `~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json`.
It validates draft input before assignment and atomically creates a valid `BreakdownTasksOutput` JSON file in `--output-dir`.

## CLI

```bash
uv run --directory ~/.config/opencode/scripts/python generate-task-json \
  --output-dir "$PWD/.tasks" < input.json
```

`--summary-slug <kebab-case-slug>` is optional.
When omitted, the script derives the slug from the root `summary` field.

The breakdown pipeline uses this legacy destination mode exclusively.

Other consumers can use `--output-file <path>` instead of both legacy options.

The two destination modes are mutually exclusive.

## Exit Codes

- `0` writes the relative `.tasks/<epoch-milliseconds>-<summary-slug>.json` path to stdout.
- `1` reports input validation, assignment, or final validation failure.
- `2` reports malformed JSON, output-path, or schema-load failure.
