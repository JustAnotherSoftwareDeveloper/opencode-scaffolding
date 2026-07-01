# Validate And Format Output

Perform final schema validation against the full `BreakdownTasksOutput` JSON object.
Emit raw JSON if valid.
No preamble, no markdown fences, no commentary.

## CLI

```
uv run --directory ~/.config/opencode/scripts/python validate-and-format-output [file-path | --stdin] --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

- `--stdin` reads the full output object from stdin.
- `file-path` reads the full output object from a file.
- `--schema PATH` is required.
  Provide the path to the task-packet schema file.

## Input

A full `BreakdownTasksOutput` JSON object with `summary` and `tasks`.

```json
{
  "summary": "...",
  "tasks": [...]
}
```

## Output

On valid input, write the raw JSON literal via `json.dumps`.

```json
{"summary":"...","tasks":[...]}
```

On invalid input, write:

```json
{"valid": false, "errors": ["summary: maxLength 2000 exceeded", "tasks[0].purpose: maxLength 200 exceeded"]}
```

## Exit Codes

- **0** — Valid.
  Emit raw JSON from stdout as the final output.
- **1** — Schema validation failed.
  Read errors on stderr.
  Fix the input and retry.
- **2** — Parse, file, or schema-load error.
  Surface to the caller.

## Invocation Examples

```bash
# Validate and format piped full output
uv run --directory ~/.config/opencode/scripts/python validate-and-format-output --stdin --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json

# Validate from file
uv run --directory ~/.config/opencode/scripts/python validate-and-format-output output.json --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json

# Full pipeline: assemble summary and tasks then validate
echo '{"summary": "...", "tasks": [...]}' \
  | uv run --directory ~/.config/opencode/scripts/python validate-and-format-output --stdin --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

## Integration Point

Use as the final gate after the summary and sequentially ordered task list are assembled into the full output object.
On exit 0, emit stdout verbatim as the final deliverable.
No preamble, no fences, no commentary.