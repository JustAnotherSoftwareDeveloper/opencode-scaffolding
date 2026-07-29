---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items. Separates planning from execution: the LLM decomposes, the script assigns skills."
tags: [task-decomposition, atomic-tasks, task-planning, request-analysis, generate-task-json, delegation-pipeline]
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
Operate in four self-contained phases.
Load each phase's dependencies separately.

## Input Contract

Read `## PURPOSE` and `## DETAILS`.
Return `BLOCKED` when either section is absent.

## Phase A — Decomposition

Produce a schema-valid `TaskDraftList` JSON object without skills or a slug.

1. Collect planning skills with `collect-skills --class planning`.
2. Read each materially relevant planning skill path from the returned metadata.
3. Read `reference/authoring/core-rules.md`.
4. Read `reference/authoring/task-granularity.md`.
5. Read `reference/authoring/anti-patterns.md`.
6. Read `reference/authoring/context-preservation.md`.
7. Produce `{summary, tasks}` with every required task field.
8. Keep each task atomic.
9. Omit skills and summary slugs.
10. Store the complete JSON in `TASK_DRAFT_JSON` for Phase B.

## Phase B — Frozen Inventory And Generation

Freeze one caller-root inventory.
Treat Python assignment as authoritative in `qwen` mode.

1. Preserve the caller root in `CALLER_ROOT` before invoking `uv --directory`.
2. Create one bounded run directory under `"$CALLER_ROOT/.tasks"`.
3. Set `SKILL_INVENTORY` to `"$RUN_DIR/skills.json"`.
4. Set `RANKING_DIAGNOSTICS` to `"$RUN_DIR/diagnostics.json"`.
5. Initialize those paths with this command:

```bash
CALLER_ROOT="$PWD"
mkdir -p "$CALLER_ROOT/.tasks"
RUN_DIR="$(mktemp -d "$CALLER_ROOT/.tasks/ranking.XXXXXX")"
SKILL_INVENTORY="$RUN_DIR/skills.json"
RANKING_DIAGNOSTICS="$RUN_DIR/diagnostics.json"
```

6. Run this inventory command once:

```bash
uv run --directory ~/.config/opencode/scripts/python collect-skills \
  --project-root "$CALLER_ROOT" \
  --config-dir ~/.config/opencode \
  --class operation \
  --class documentation \
  --output "$SKILL_INVENTORY"
```

7. Run authoritative Qwen assignment with the complete `TASK_DRAFT_JSON`:

```bash
uv run --directory ~/.config/opencode/scripts/python generate-task-json \
  --project-root "$CALLER_ROOT" \
  --skills-file "$SKILL_INVENTORY" \
  --assignment-mode qwen \
  --model-profile q8 \
  --diagnostics-file "$RANKING_DIAGNOSTICS" \
  --output-dir "$CALLER_ROOT/.tasks" <<'TASK_DRAFT_JSON'
<complete TaskDraftList JSON>
TASK_DRAFT_JSON
```

8. Use `--assignment-mode shadow` with the same diagnostics boundary for comparison runs.
9. Use `--assignment-mode lexical` only for explicit rollback.
10. Omit ranker and diagnostics options in lexical mode.
11. Capture stdout as `GENERATED_PATH`.
12. Read `GENERATED_PATH` into `TASK_PACKET_JSON`.
13. Preserve the inventory unchanged through Phases C and D.

## Phase C — Read-Only Audit

Audit the generated packet against the frozen inventory without mutating any skill array.
Do not mutate any other task field.

1. Read `SKILL_INVENTORY` from the Phase B path.
2. Do not invoke `collect-skills` again.
3. Check every assigned name against the frozen inventory.
4. Check semantic fit, atomicity, circular references, and cross-task consistency.
5. Require one to three assignments for `qwen` output.
6. Preserve zero-to-three compatibility for historical and lexical packets.
7. Treat unknown, duplicate, empty, excessive, or invalid Qwen assignments as blockers.
8. Do not replace or remove assignments.
9. Do not reorder or add assignments.
10. Preserve every non-skill field byte-identically.

## Phase D — Blocking Validation

Validate the generated file without repair.

1. Run this command:

```bash
uv run --directory ~/.config/opencode/scripts/python validate-task-structure \
  --state-file "$CALLER_ROOT/$GENERATED_PATH" \
  --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json
```

2. Do not pass `--auto-fix`.
3. Do not trim, deduplicate, remove, or reorder generated assignments.
4. Treat every validation error as blocking.
5. Require a new generator run after an assignment defect.
6. Remove `SKILL_INVENTORY` after validation succeeds.
7. Preserve `RANKING_DIAGNOSTICS` with the generated packet evidence.
8. Place `GENERATED_PATH` alone under `Deliverable`.

## Output Contract

- Produce `TaskDraftList` JSON in Phase A.
- Produce `.tasks/<epoch>-<slug>.json` in Phase B.
- Audit without mutation in Phase C.
- Validate without auto-fix in Phase D.
- Return `.tasks/<epoch>-<slug>.json` as the relative payload.

## Guardrails

- Do not populate or correct skills manually.
- Do not derive a summary slug.
- Do not read schema files during Phase A.
- Do not recollect the executable inventory.
- Do not mutate generated task fields.
- Do not pass `--auto-fix`.
- Do not load model configuration in lexical rollback mode.
- Return `BLOCKED` for malformed input, script failure, audit failure, or validation failure.

## Docs

See `./reference/README.md` for supporting documentation.
