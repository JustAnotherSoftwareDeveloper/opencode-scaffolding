# Script Contracts

Generate the final packet with this command.

```bash
printf '%s' "$TASK_DRAFT_JSON" | uv run --directory ~/.config/opencode/scripts/python generate-task-json \
  --output-file "$PLAN_DIR/tasks.json"
```

Render task Markdown with this command.

```bash
uv run --directory ~/.config/opencode/scripts/python render-task-markdown \
  --input "$PLAN_DIR/tasks.json" \
  --output "$PLAN_DIR/tasks.md"
```

`--input` must contain a `BreakdownTasksOutput` object that validates against the existing task-packet schema.

Treat non-zero script exit status as a blocker.
