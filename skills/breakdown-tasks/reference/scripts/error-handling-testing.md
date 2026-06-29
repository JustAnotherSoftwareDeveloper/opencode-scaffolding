# Error Handling And Testing

## Exit Code Matrix

Each script uses exit codes 0, 1, and 2.
The meaning is consistent across all scripts.

### `generate-uuids`

- **0** — UUIDs produced.
- **1** — Invalid count (less than 1, greater than 100, non-integer).
- **2** — Internal error.

### `validate-task-structure`
- **0** — Valid structure.
- **1** — Structural violations (missing keys, length, type).
- **2** — Parse, file, or schema-load error.

### `validate-dependencies`
- **0** — Valid graph.
- **1** — Orphan dependencies, cycles, self-loops.
- **2** — Parse or file error.

### `topological-sort`
- **0** — Sorted output.
- **1** — Cycle detected (path in stderr).
- **2** — Parse or missing fields error.

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
- All five scripts implemented and entry points registered in `pyproject.toml`.

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
uv run --directory "$SCRIPTS_PYTHON" pytest tests/test_generate_uuids.py -v
uv run --directory "$SCRIPTS_PYTHON" pytest tests/test_validate_task_structure.py -v
uv run --directory "$SCRIPTS_PYTHON" pytest tests/test_validate_dependencies.py -v
uv run --directory "$SCRIPTS_PYTHON" pytest tests/test_topological_sort.py -v
uv run --directory "$SCRIPTS_PYTHON" pytest tests/test_validate_and_format_output.py -v

# Check coverage
uv run --directory "$SCRIPTS_PYTHON" pytest tests/ --cov=lib --cov=cli -v
```

### Full Pipeline Integration Test
1. Create a test input JSON file with an unsorted task list of 3 to 5 tasks with dependencies.
2. Run each step manually and verify the chain.

```bash
# Step 1: Generate UUIDs
uv run --directory "$SCRIPTS_PYTHON" generate-uuids 4

# Step 2: Validate task structure
uv run --directory "$SCRIPTS_PYTHON" validate-task-structure test-tasks.json --schema "$TASK_SCHEMA_PATH"

# Step 3: Validate dependencies
uv run --directory "$SCRIPTS_PYTHON" validate-dependencies test-tasks.json

# Step 4: Topological sort
uv run --directory "$SCRIPTS_PYTHON" topological-sort test-tasks.json > sorted-tasks.json

# Step 5: Assemble and validate final output
echo '{"summary": "Test breakdown", "tasks": '$(cat sorted-tasks.json)'}' \
  | uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output --stdin --schema "$TASK_SCHEMA_PATH"
```

3. Verify outputs.
   - UUIDs match pattern `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` with `y` in `[89ab]`.
   - All UUIDs in a single generation call are unique.
   - Task structure validation passes on well-formed input.
   - Dependency graph validation catches orphan refs, cycles, and self-loops.
   - Topological sort respects dependency order.
     Parallel tasks are sorted by `id`.
   - Final output is raw JSON.
     No markdown fences, no leading or trailing whitespace.

### End-To-End Shell Test
```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_PYTHON="$HOME/.config/opencode/scripts/python"
TASK_SCHEMA_PATH="$HOME/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json"

echo "=== Step 1: Generate UUIDs ==="
UIDS=$(uv run --directory "$SCRIPTS_PYTHON" generate-uuids 3)
echo "UUIDs: $UIDS"

echo "=== Step 2: Create test tasks ==="
cat > /tmp/test-tasks.json << 'JSONEOF'
[{"id":"aaa","dependencies":[],"purpose":"First task.","context":"C1","filesToRead":[],"filesToWrite":[],"skills":[],"executionInstructions":[{"step":1,"action":"Do A"}],"expectedOutput":"A"},{"id":"bbb","dependencies":["aaa"],"purpose":"Second task.","context":"C2","filesToRead":[],"filesToWrite":[],"skills":[],"executionInstructions":[{"step":1,"action":"Do B"}],"expectedOutput":"B"}]
JSONEOF

echo "=== Step 3: Validate task structure ==="
uv run --directory "$SCRIPTS_PYTHON" validate-task-structure /tmp/test-tasks.json --schema "$TASK_SCHEMA_PATH"

echo "=== Step 4: Validate dependencies ==="
uv run --directory "$SCRIPTS_PYTHON" validate-dependencies /tmp/test-tasks.json

echo "=== Step 5: Topological sort ==="
uv run --directory "$SCRIPTS_PYTHON" topological-sort /tmp/test-tasks.json > /tmp/sorted-tasks.json
cat /tmp/sorted-tasks.json

echo "=== Step 6: Assemble and validate final output ==="
echo "{\"summary\":\"Test breakdown\",\"tasks\":$(cat /tmp/sorted-tasks.json)}" \
  | uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output --stdin --schema "$TASK_SCHEMA_PATH"

echo "=== All pipeline steps passed ==="
```

### Validation Checklist
After running the pipeline locally, verify these outcomes.
- `generate-uuids` produces valid UUID v4 strings.
- `validate-task-structure` accepts valid task lists and rejects malformed ones.
- `validate-dependencies` detects orphan references, cycles, and self-loops.
- `topological-sort` produces correct dependency-respecting order with deterministic tie-breaking.
- `validate-and-format-output` accepts valid full output and emits raw JSON.
  No preamble, no fences.
- All five scripts exit 0 on valid input, 1 on validation error, and 2 on parse or internal error.
- Errors appear on stderr.
  Errors never appear on stdout.