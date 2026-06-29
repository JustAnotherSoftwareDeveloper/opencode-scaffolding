# Generate UUIDs

Generate a JSON array of UUID v4 strings.

## CLI

```
uv run --directory "$SCRIPTS_PYTHON" generate-uuids <count>
```

- `<count>` is a positional integer from 1 to 100.
  It is required.
- The script does not read stdin.
  It takes a CLI argument only.

## Input

CLI argument only.
No stdin input.

## Output

Write a JSON array of UUID v4 strings.

```json
["a1b2c3d4-...", "e5f6g7h8-...", ...]
```

## Exit Codes

- **0** — UUIDs produced.
  Use the returned UUIDs.
- **1** — Invalid input.
  Count is less than 1, greater than 100, or not an integer.
  Fix `<count>` and retry.
- **2** — Internal error.
  Surface to the caller.

## Invocation Examples

```bash
# Generate 5 UUIDs
uv run --directory "$SCRIPTS_PYTHON" generate-uuids 5

# Capture UUIDs into a variable
UIDS=$(uv run --directory "$SCRIPTS_PYTHON" generate-uuids 3)

# Pipe into jq for assignment
uv run --directory "$SCRIPTS_PYTHON" generate-uuids 4 | jq -c '.[]'
```

## Integration Point

Call once with the task count after atomic tasks are identified.
Assign each UUID to a task's `id` field sequentially.