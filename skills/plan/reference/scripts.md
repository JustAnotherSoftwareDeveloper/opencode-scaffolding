# Script Contracts

The workflow writes the completed draft with LLM-assigned skills, then publishes and validates.

```bash
uv run --directory ~/.config/opencode/scripts/python init-task-packet \
  --output-dir "$PLAN_DIR/.tasks" < "$PLAN_DIR/draft.json"
uv run --directory ~/.config/opencode/scripts/python render-task-markdown \
  --input "$PUBLISHED_PATH" \
  --output "$PLAN_DIR/tasks.md"
```
