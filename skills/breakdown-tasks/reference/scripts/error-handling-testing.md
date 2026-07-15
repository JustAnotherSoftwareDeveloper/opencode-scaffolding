# Error Handling And Testing

## Exit Code Matrix

### `generate-task-json`

- **0** — Relative local task path written to stdout.
- **1** — TaskDraft validation, assignment, or final TaskPacket validation failure.
- **2** — Parse, output-path, schema-load, or destination-option error.

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
- `jsonschema` installed in the Python environment.
- Entry points registered in `pyproject.toml`.

### Per-Script Unit Tests

Run all tests from the Python scripts project.

```bash
uv run --directory ~/.config/opencode/scripts/python pytest tests/
uv run --directory ~/.config/opencode/scripts/python pytest tests/test_generate_task_json.py tests/test_generate_task_json_cli.py -v
uv run --directory ~/.config/opencode/scripts/python pytest tests/test_generate_task_json.py tests/test_generate_task_json_cli.py -v
```

### Pipeline Integration Test (E2E)

Test the current pipeline end-to-end with a fresh TaskDraft state file.

```bash
#!/usr/bin/env bash
set -euo pipefail

cat > /tmp/draft.json <<'EOF'
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

SUMMARY_SLUG=e2e-pipeline-test
REL_FILE=$(uv run --project ~/.config/opencode/scripts/python generate-task-json \
  --summary-slug "$SUMMARY_SLUG" \
  --output-dir "$CWD/.tasks" < /tmp/draft.json)

python3 -c "import json; data=json.load(open('$REL_FILE')); assert data['tasks'][0]['skills']"
```

### Validation Checklist

- TaskDraft state contains no `skills` fields before assignment.
- `generate-task-json` adds non-empty `skills` arrays from discovered skills.
- `generate-task-json` writes only valid final output.
- The worker returns only `.tasks/<epoch-milliseconds>-<summary-slug>.json` to the delegator.
- Errors appear on stderr; stdout remains machine-consumable on success.
