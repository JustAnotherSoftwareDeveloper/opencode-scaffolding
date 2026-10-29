# Script Contracts

During initial creation, `init-task-packet` publishes the completed draft with its
LLM-assigned skills. Move that published packet to `tasks.json`, validate the state
file, then render `tasks.md` from it.

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

For a bounded plan-owned correction after an audit finding, validate the revised
`tasks.json` in the existing `$PLAN_DIR` without automatic edits. Inspect any diff and
apply only fixes authorized by the exact finding before retrying validation:

```bash
uv run --project ~/.config/opencode/scripts/python validate-task-structure \
  --state-file "$PLAN_DIR/tasks.json" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

After validation succeeds, rerender only that workspace's existing `tasks.md`:

```bash
uv run --project ~/.config/opencode/scripts/python render-task-markdown \
  --input "$PLAN_DIR/tasks.json" \
  --output "$PLAN_DIR/tasks.md" \
  --overwrite
```

`--overwrite` is limited to the existing rendered task document in the same plan
workspace. It is not used for initial publication or to replace any other artifact.
Correction does not invoke `init-task-packet` or create a new plan workspace.
