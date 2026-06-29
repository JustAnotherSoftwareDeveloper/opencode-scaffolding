# Validate Dependencies

Validate the dependency graph of a task list for missing references, self-loops, and cycles.

## CLI

```
uv run --directory "$SCRIPTS_PYTHON" validate-dependencies [file-path | --stdin]
```

- `--stdin` reads the task JSON array from stdin.
- `file-path` reads the task JSON array from a file.
- No `--schema` flag is required.
  The script operates on `id` and `dependencies` fields only.

## Input

A JSON array of task objects.
Each object must have `id` and `dependencies` fields.

## Output

On valid input, write:

```json
{"valid": true}
```

On invalid input, write:

```json
{"valid": false, "errors": ["Task a1b2...: dependency e5f6... references unknown task", "Cycle detected: a1b2... -> c3d4... -> a1b2..."]}
```

## Validation Checks

Apply these dependency checks.

- Verify every UUID in every `dependencies` array references an existing task `id`.
- Detect cycles using DFS-based detection.
- Flag self-loops as errors.
- Accept empty `dependencies` arrays as valid.

## Exit Codes

- **0** — Valid graph.
  Proceed to topological sort.
- **1** — Dependency violations found.
  Read errors on stderr.
  Fix dependencies and retry.
- **2** — Parse or file error.
  Surface to the caller.

## Invocation Examples

```bash
# Validate piped task list
uv run --directory "$SCRIPTS_PYTHON" validate-dependencies --stdin

# Validate from file
uv run --directory "$SCRIPTS_PYTHON" validate-dependencies tasks.json

# Pipe from a JSON manipulator
cat tasks.json | uv run --directory "$SCRIPTS_PYTHON" validate-dependencies --stdin
```

## Integration Point

Use immediately after dependency arrays are populated on each task.
Run before topological sort.