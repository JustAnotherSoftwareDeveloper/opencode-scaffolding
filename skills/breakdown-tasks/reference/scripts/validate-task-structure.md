# Validate Task Structure

Validate a complete canonical task-packet JSON object against its schema and
structural consistency checks. Structural success does not approve semantic
atomicity.

## CLI

```text
uv run --project ~/.config/opencode/scripts/python validate-task-structure \
  [FILE_PATH | --stdin | --state-file PATH] --schema PATH [--auto-fix]
```

- `FILE_PATH` reads one packet from a JSON file.
- `--stdin` reads one packet from standard input.
- `--state-file PATH` reads and validates a complete packet state file. It is
  mutually exclusive with `FILE_PATH` and `--stdin`.
- `--schema PATH` is required and selects the task-packet JSON Schema.
- `--auto-fix` requires `--state-file` and applies only the supported skills-array
  fixes.

Choose exactly one input mode. Every mode validates the complete root object,
including its required `summary`, `slug`, `tasks`, and `boundaryReview` fields;
a bare array of task objects is not a valid packet.

## Input

The input is a canonical JSON object with at least one task. The schema defines
the required root and task fields, nested boundary-review structure, types, and
constraints. The validator also checks structural consistency such as sequential
instruction steps and valid metadata references. It does not decide whether a
task is semantically atomic.

## Output

For a valid packet without diagnostics, the CLI writes:

```json
{"valid": true}
```

For an invalid packet, it writes errors:

```json
{"valid": false, "errors": ["ERROR [boundary-review-interface] $: malformed or missing required boundaryReview evidence: 'boundaryReview' is a required property", "$: 'slug' is a required property", "$: 'tasks' is a required property"]}
```

In `--auto-fix --state-file` mode, a valid result includes `"fixed": true` if
the command changed skills arrays, or `"fixed": false` if no fix was needed.
Any remaining errors produce `"valid": false` and an `errors` array.

## Exit Codes

- **0** — Structural validation succeeded.
- **1** — Schema or structural violations remain.
- **2** — Usage, input parsing, file access, or schema loading failed.

The command prints JSON results to stdout. Usage and input errors may also write
diagnostics to stderr.

## Auto-Fix

Use `--auto-fix` only with `--state-file`. It removes empty skill names,
deduplicates skills while preserving first occurrence, and trims skill arrays to
three entries. It does not add fallback skills, remove unknown skill names, or
repair other structural errors. The state file is rewritten only when fixes make
the packet valid.

## Examples

```bash
# Validate a complete packet from a file
uv run --project ~/.config/opencode/scripts/python validate-task-structure \
  tasks.json --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json

# Validate a complete packet from stdin
uv run --project ~/.config/opencode/scripts/python validate-task-structure \
  --stdin --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json

# Repair supported skills-array issues and validate the state file
uv run --project ~/.config/opencode/scripts/python validate-task-structure \
  --state-file tasks.json --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json \
  --auto-fix
```

## Integration Point

Run structural validation after the generator publishes the packet. Then perform
the separate request-aware boundary review before accepting the packet for display
or dispatch.
