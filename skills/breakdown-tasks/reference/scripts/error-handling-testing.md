# Error Handling And Testing

## Exit Code Matrix

### `init-state-file`

- **0** — State file created and absolute path printed.
- **1** — Runtime error creating the directory or state file.
- **2** — User error from CLI argument parsing.

### `assign-skills`

- **0** — Skills assigned and state file written.
- **1** — Runtime error such as no matching candidate skills.
- **2** — User error such as invalid arguments or TaskDraft schema failure.

### `validate-and-format-output`

- **0** — Final TaskPacket JSON emitted to stdout.
- **1** — Schema violations.
- **2** — Parse, file, or schema-load error.

## Retry Behavior

- **Exit 0** — Accept output and proceed to the next pipeline step.
- **Exit 1** — Read error details, fix decomposition/assignment input when possible, and re-run the relevant step.
- **Exit 2** — Treat as a configuration, parse, or invocation error; surface to the caller.

## Local Testing

### Prerequisites

- Python environment with `uv` available.
- `~/.config/opencode/scripts/python` — Python scripts directory.
- `schema/task-input.schema.json` — TaskDraft schema path.
- `schema/task-packet.schema.json` — final TaskPacket schema path.
- `rerankers[flashrank]` and `jsonschema` installed in the Python environment.
- Entry points registered in `pyproject.toml`.

### Per-Script Unit Tests

Run all tests from the Python scripts project.

```bash
uv run --directory ~/.config/opencode/scripts/python pytest tests/
uv run --directory ~/.config/opencode/scripts/python pytest tests/test_init_state_file.py tests/test_init_state_file_cli.py -v
uv run --directory ~/.config/opencode/scripts/python pytest tests/test_assign_skills.py tests/test_assign_skills_cli.py -v
```

### Pipeline Integration Test (E2E)

Test the current pipeline end-to-end with a fresh TaskDraft state file.

```bash
#!/usr/bin/env bash
set -euo pipefail

STATE_FILE=$(uv run --directory ~/.config/opencode/scripts/python init-state-file \
  --output-dir /tmp/opencode/.tasks)
REL_FILE=".tasks/$(basename "$STATE_FILE")"

cat > "$STATE_FILE" <<'EOF'
{
  "summary": "E2E pipeline test",
  "tasks": [
    {
      "purpose": "Create Python tests for a helper.",
      "context": "Write pytest coverage for a small Python helper.",
      "filesToRead": ["scripts/python/src/lib/shared/slug.py"],
      "filesToWrite": ["scripts/python/tests/test_shared_slug.py"],
      "executionInstructions": [
        {"step": 1, "action": "Read the helper and write pytest tests."}
      ],
      "expectedOutput": "Pytest tests covering the helper."
    }
  ]
}
EOF

uv run --directory ~/.config/opencode/scripts/python assign-skills \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-input.schema.json

uv run --directory ~/.config/opencode/scripts/python validate-and-format-output \
  --state-file "$STATE_FILE" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json \
  >/tmp/breakdown-output.json

python3 -c "import json; data=json.load(open('/tmp/breakdown-output.json')); assert data['tasks'][0]['skills']"
printf '%s\n' "$REL_FILE"
```

### Validation Checklist

- `init-state-file` creates `<epoch>-decomposition.json` and prints its absolute path.
- TaskDraft state contains no `skills` fields before assignment.
- `assign-skills` adds non-empty `skills` arrays from discovered/indexed skills.
- `validate-and-format-output` accepts valid final output and emits raw JSON.
- The worker returns only `.tasks/<epoch>-decomposition.json` to the delegator.
- Errors appear on stderr; stdout remains machine-consumable on success.
