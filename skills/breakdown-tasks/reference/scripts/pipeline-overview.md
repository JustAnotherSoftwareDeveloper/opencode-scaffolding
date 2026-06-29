# Pipeline Overview

Chain all five scripts in a strict sequence.
Feed each script's output to the next stage.

## Script Order

1. **`generate-uuids`** — Produce UUID v4 identifiers, one per task.
   See `./generate-uuids.md`.
2. **`validate-task-structure`** — Validate required keys, types, lengths, and step numbering.
   See `./validate-task-structure.md`.
3. **`validate-dependencies`** — Verify all dependency references exist and the graph is acyclic.
   See `./validate-dependencies.md`.
4. **`topological-sort`** — Order tasks by dependency depth using Kahn's algorithm.
   See `./topological-sort.md`.
5. **`validate-and-format-output`** — Perform final schema validation and emit raw JSON.
   See `./validate-and-format-output.md`.

## Uniform CLI Convention

All scripts follow the same convention.

- Read JSON from stdin or a file argument.
- Write JSON to stdout.
- Write error messages to stderr.
  Never pollute stdout with errors.
- Exit 0 on success.
- Exit 1 on validation failure or semantic error.
- Exit 2 on parse, file, or internal error.

## Pipeline Walkthrough

The ordered steps below show the full pipeline flow.
Each step represents a script invocation or manual assembly step.

1. **Identify tasks** — Collect and list all tasks manually.
2. **Generate UUIDs** — Run `uv run --directory "$SCRIPTS_PYTHON" generate-uuids <N>`.
   Produces N UUIDs assigned to `task.id` fields.
3. **Populate task fields** — Fill in remaining task fields (title, description, priority) manually.
4. **Validate task structure** — Run `uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --stdin --schema "$TASK_SCHEMA_PATH"`.
   Loop on exit 1 until valid.
5. **Populate dependencies** — Add dependency references between tasks manually.
6. **Validate dependencies** — Run `uv run --directory "$SCRIPTS_PYTHON" validate-dependencies --stdin`.
   Loop on exit 1 until valid.
7. **Topological sort** — Run `uv run --directory "$SCRIPTS_PYTHON" topological-sort --stdin`.
   Replace the task list with sorted output.
8. **Assemble full output** — Combine sorted tasks with summary metadata manually.
9. **Validate and format output** — Run `uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output --stdin --schema "$TASK_SCHEMA_PATH"`.
   Loop on exit 1 until valid.
   On exit 0, emit raw JSON.
10. **Return raw JSON** — Emit stdout from validate-and-format-output verbatim.
    No preamble, no fences, no commentary.

## Shell Pipeline Integration

Use these commands to invoke each script step by step.

```bash
# Step 1: Generate UUIDs
UIDS=$(uv run --directory "$SCRIPTS_PYTHON" generate-uuids 5)

# Step 2: Validate task structure
echo "$TASKS_JSON" \
  | uv run --directory "$SCRIPTS_PYTHON" validate-task-structure --stdin --schema "$TASK_SCHEMA_PATH"

# Step 3: Validate dependencies
echo "$TASKS_JSON" \
  | uv run --directory "$SCRIPTS_PYTHON" validate-dependencies --stdin

# Step 4: Topological sort
SORTED=$(echo "$TASKS_JSON" \
  | uv run --directory "$SCRIPTS_PYTHON" topological-sort --stdin)

# Step 5: Assemble and final validate
echo "{\"summary\":\"$SUMMARY\",\"tasks\":$SORTED}" \
  | uv run --directory "$SCRIPTS_PYTHON" validate-and-format-output --stdin --schema "$TASK_SCHEMA_PATH"
```