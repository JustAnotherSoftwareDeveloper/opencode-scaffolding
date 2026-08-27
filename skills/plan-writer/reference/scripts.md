# Script Contracts

The workflow writes the completed draft with LLM-assigned skills, publishes it in
the plan workspace, moves the published packet to `tasks.json`, validates that state
file, and renders `tasks.md` from the validated packet.

```bash
uv run --project ~/.config/opencode/scripts/python init-task-packet \
  --output-dir "$PLAN_DIR" < "$PLAN_DIR/draft.json"
mv "$PUBLISHED_PATH" "$PLAN_DIR/tasks.json"
uv run --project ~/.config/opencode/scripts/python validate-task-structure \
  --state-file "$PLAN_DIR/tasks.json" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json \
  --auto-fix
uv run --project ~/.config/opencode/scripts/python render-task-markdown \
  --input "$PLAN_DIR/tasks.json" \
  --output "$PLAN_DIR/tasks.md"
```

`PUBLISHED_PATH` is the path printed by `init-task-packet`. Validation uses the
state-file form only; do not combine a positional input path with `--state-file`.
