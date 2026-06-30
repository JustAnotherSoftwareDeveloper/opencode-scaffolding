# Error Handling And Testing

## Exit Code Matrix

Each script uses exit codes 0, 1, and 2.
The meaning is consistent across all scripts.

### `validate-task-structure`
- **0** — Valid structure.
- **1** — Structural violations (missing keys, length, type).
- **2** — Parse, file, or schema-load error.

### `validate-and-format-output`
- **0** — Raw JSON output.
- **1** — Schema violations.
- **2** — Parse, file, or schema-load error.

## Retry Behavior

All scripts use the same retry strategy.
- **Exit 0** — Accept output and proceed to the next pipeline step.
- **Exit 1** — Read error details from stderr.
  Fix the input data.
  Re-invoke the same script.
  No fixed retry limit.
- **Exit 2** — Do not retry.
  Surface the issue to the caller.

## Error Recovery Pattern

Use this bash retry loop for exit-1 errors.

```bash
while true; do
  output=$(echo "$INPUT" \
    | uv run --directory "$SCRIPTS_PYTHON" <script-name> --stdin [--schema "$TASK_SCHEMA_PATH"] 2>err.txt)
  exit_code=$?
  if [ "$exit_code" -eq 0 ]; then
    echo "$output"
    break
  elif [ "$exit_code" -eq 1 ]; then
    echo "Fixing: $(cat err.txt)" >&2
  else
    echo "Fatal error: $(cat err.txt)" >&2
    exit 2
  fi
done
```

## Local Testing

### Prerequisites
- Python environment with `uv` available.
- `$SCRIPTS_PYTHON` set to `~/.config/opencode/scripts/python`.
- `$TASK_SCHEMA_PATH` set to `skills/breakdown-tasks/schema/task-packet.schema.json`.
- `jsonschema` package installed in the Python environment.
- All scripts implemented and entry points registered in `pyproject.toml`.

### Environment Variables
```bash
export SCRIPTS_PYTHON="$HOME/.config/opencode/scripts/python"
export TASK_SCHEMA_PATH="$HOME/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json"
```

### Per-Script Unit Tests
Run all tests from the `$SCRIPTS_PYTHON` directory.

```bash
# Run all script tests
uv run --directory "$SCRIPTS_PYTHON" pytest tests/

# Run tests for a specific script
uv run --directory "$SCRIPTS_PYTHON" pytest tests/test_validate_task_structure.py -v
uv run --directory "$SCRIPTS_PYTHON" pytest tests/test_validate_and_format_output.py -v

# Check coverage
uv run --directory "$SCRIPTS_PYTHON" pytest tests/ --cov=lib --cov=cli -v
```

### Pipeline Integration Test (E2E)

Test the full pipeline end-to-end using a shell script.
This exercises both scripts in sequence against sample input data.

```bash
#!/usr/bin/env bash
set -euo pipefail

# --- Setup ---
export SCRIPTS_PYTHON="$HOME/.config/opencode/scripts/python"
export TASK_SCHEMA_PATH="$HOME/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json"

STATE_FILE=$(mktemp)
trap 'rm -f "$STATE_FILE"' EXIT

# Write sample task data (valid minimal structure, no id/dependencies field)
cat > "$STATE_FILE" <<'EOF'
{
  "summary": "E2E pipeline test",
  "tasks": [
    {
      "purpose": "Create a test file.",
      "context": "Minimal test case.",
      "filesToRead": [],
      "filesToWrite": ["/tmp/e2e-test-output.txt"],
      "skills": [],
      "executionInstructions": [
        {"step": 1, "action": "Create /tmp/e2e-test-output.txt with content 'ok'"}
      ],
      "expectedOutput": "File /tmp/e2e-test-output.txt exists with content 'ok'."
    }
  ]
}
EOF

# Step 1: Validate task structure (expect exit 0)
uv run --directory "$SCRIPTS_PYTHON" validate-task-structure \
  --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH" || {
  echo "FAIL: validate-task-structure exited non-zero" >&2
  exit 1
}

# Step 2: Validate and format output (expect exit 0)
OUTPUT=$(uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output \
  --state-file "$STATE_FILE" --schema "$TASK_SCHEMA_PATH") || {
  echo "FAIL: validate-and-format-output exited non-zero" >&2
  exit 1
}

# Verify output is raw JSON (no fences, no preamble)
echo "$OUTPUT" | python3 -c "import json,sys; data=json.load(sys.stdin); assert 'summary' in data; assert 'tasks' in data" || {
  echo "FAIL: output is not valid BreakDownTasksOutput JSON" >&2
  exit 1
}

echo "PASS: Pipeline integration test completed successfully."
```

### Validation Checklist
After running the pipeline locally, verify these outcomes.
- `validate-task-structure` accepts valid task lists and rejects malformed ones.
- `validate-and-format-output` accepts valid full output and emits raw JSON.
  No preamble, no fences.
- All scripts exit 0 on valid input, 1 on validation error, and 2 on parse or internal error.
- Errors appear on stderr.
  Errors never appear on stdout.