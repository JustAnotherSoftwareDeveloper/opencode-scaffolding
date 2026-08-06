# Validate Task Structure

Validate a JSON array of task objects against structural rules and the task-packet JSON Schema.

## CLI

```
uv run --project ~/.config/opencode/scripts/python validate-task-structure [file-path | --stdin] --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

- `--stdin` reads the task JSON array from stdin.
- `file-path` reads the task JSON array from a file.
- `--schema PATH` is required.
  Provide the path to the task-packet schema file.

## Input

A JSON array of task objects.
Each object contains `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, and `expectedOutput`.

## Output

On valid input, write:

```json
{"valid": true}
```

On invalid input, write:

```json
{"valid": false, "errors": ["Task 2: purpose exceeds maxLength 200", "Task 3: missing required key: filesToWrite"]}
```

With `--auto-fix --state-file`, valid output includes `"fixed": true` when the
script removed empty skills, deduplicated skills, or trimmed a skills array to three entries.

## Validation Rules

Apply these structural rules.

- Require all keys: `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`, `executionInstructions`, `expectedOutput`.
- Purpose must be a single sentence without line breaks.
  maxLength is 200.
- Context maxLength is 8000.
- ExpectedOutput maxLength is 2000.
- Execution instruction steps must be integers starting at 1 with no gaps.
- File array entries must be non-empty strings with no duplicates.
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
uv run --project ~/.config/opencode/scripts/python validate-task-structure --stdin --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json

# Validate from a file
uv run --project ~/.config/opencode/scripts/python validate-task-structure tasks.json --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json

# Pipe from a previous command
echo '[...tasks...]' | uv run --project ~/.config/opencode/scripts/python validate-task-structure --stdin --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

## Integration Point

Use after the generator publishes the packet. Use as the final validation gate before returning the task-file path.

## Auto-Fix

The breakdown workflow uses `--auto-fix --state-file` in a retry loop.

- Remove empty strings from `skills` arrays.
- Deduplicate `skills` arrays while preserving first-occurrence order.
- Trim `skills` arrays to three entries.
- Write fixes back to the state file when `--state-file` is passed.
- Report unresolved errors without adding fallback skills or removing unknown skill names.
