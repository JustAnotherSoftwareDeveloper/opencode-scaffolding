# Validate Task Structure

Validate a JSON array of task objects against structural rules and the task-packet JSON Schema.

## CLI

```
uv run --directory "$SCRIPTS_PYTHON" validate-task-structure [file-path | --stdin] --schema "$TASK_SCHEMA_PATH"
```

- `--stdin` reads the task JSON array from stdin.
- `file-path` reads the task JSON array from a file.
- `--schema PATH` is required.
  Provide the path to the task-packet schema file.

## Input

A JSON array of task objects.
Each object contains `id`, `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, and `expectedOutput`.

## Output

On valid input, write:

```json
{"valid": true}
```

On invalid input, write:

```json
{"valid": false, "errors": ["Task 2: purpose exceeds maxLength 200", "Task 3: missing required key: filesToWrite"]}
```

## Validation Rules

Apply these structural rules.

- Require all keys: `id`, `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`.
- Purpose must be a single sentence without line breaks.
  maxLength is 200.
- Context maxLength is 8000.
- ExpectedOutput maxLength is 2000.
- Execution instruction steps must be integers starting at 1 with no gaps.
- File array entries must be non-empty strings with no duplicates.
- All `id` fields must match the UUID v4 pattern.
- Purpose, context, and expectedOutput must be strings.
- FilesToRead, filesToWrite, and skills must be arrays of strings.

## Exit Codes

- **0** — Valid structure.
  Proceed to the next pipeline step.
- **1** — Structural violations found.
  Read errors on stderr.
  Fix the input and retry.
- **2** — Parse, file, or schema error.
  Surface to the caller.

## Invocation Examples

```bash
# Validate piped task list from stdin
uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --stdin --schema "$TASK_SCHEMA_PATH"

# Validate from a file
uv run --directory "$SCRIPTS_PYTHON" validate-task-structure tasks.json --schema "$TASK_SCHEMA_PATH"

# Pipe from a previous command
echo '[...tasks...]' | uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --stdin --schema "$TASK_SCHEMA_PATH"
```

## Integration Point

Use after task fields are populated with UUIDs, purpose, and context.
Use as the second pipeline step before final output validation.