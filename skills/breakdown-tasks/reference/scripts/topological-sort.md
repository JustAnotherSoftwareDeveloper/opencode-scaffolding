# Topological Sort

Topologically sort a task dependency graph using Kahn's algorithm.
Produce a deterministic ordering with parallel tasks sorted by `id` lexicographically.

## CLI

```
uv run --directory "$SCRIPTS_PYTHON" topological-sort [file-path | --stdin]
```

- `--stdin` reads the task JSON array from stdin.
- `file-path` reads the task JSON array from a file.

## Input

A JSON array of task objects.
Each object must have `id` and `dependencies` fields.

## Output

Write a topologically sorted JSON array of the same task objects.

```json
[
  {"id": "aaa...", "dependencies": [], "purpose": "...", ...},
  {"id": "bbb...", "dependencies": [], "purpose": "...", ...},
  {"id": "ccc...", "dependencies": ["aaa..."], "purpose": "...", ...}
]
```

## Exit Codes

- **0** — Success.
  Replace the task list with the sorted output.
- **1** — Cycle detected.
  Read the cycle path from stderr.
  Fix dependencies, rerun validation, then sort.
- **2** — Parse or missing fields error.
  Surface to the caller.

## Invocation Examples

```bash
# Sort piped task list
uv run --directory "$SCRIPTS_PYTHON" topological-sort --stdin

# Sort from file and save to new file
uv run --directory "$SCRIPTS_PYTHON" topological-sort tasks.json > sorted-tasks.json

# Full pipeline: validate deps then sort
uv run --directory "$SCRIPTS_PYTHON" validate-dependencies --stdin \
  && uv run --directory "$SCRIPTS_PYTHON" topological-sort --stdin
```

## Algorithm

Use Kahn's algorithm with `collections.deque`.
Enqueue tasks with no remaining dependencies and process them in order.
When multiple tasks become available at the same depth, sort them by `id` lexicographically for deterministic output.

## Integration Point

Use after dependency validation passes.
The sorted output replaces the current task list.