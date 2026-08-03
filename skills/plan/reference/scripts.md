# Script Contracts

The workflow passes the complete draft, final direct-LLM assignments, and one frozen inventory to the shared generator. The generator validates and atomically writes `tasks.json`; the renderer consumes only that validated packet.

```bash
printf '%s' "$TASK_PACKET_JSON" | uv run --directory ~/.config/opencode/scripts/python generate-task-json \
  --skills-file "$SKILL_INVENTORY" \
  --output-file "$PLAN_DIR/tasks.json"
uv run --directory ~/.config/opencode/scripts/python render-task-markdown \
  --input "$PLAN_DIR/tasks.json" \
  --output "$PLAN_DIR/tasks.md"
```

No assignment mode, ranker, model-specific fallback, discovery, or repair option is valid. A non-zero status blocks publication.
