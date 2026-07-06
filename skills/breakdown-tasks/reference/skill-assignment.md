# Skill Assignment Procedure

Automatic FlashRank-based procedure for assigning skills to task drafts.
Executed by the `assign-skills` Python script after the LLM writes `TaskDraft` objects.

## Prerequisites

1. The state file contains a root `{summary, tasks}` object that matches `schema/task-input.schema.json`.
2. Each task is a `TaskDraft` and does **not** include a `skills` field.
3. Available skills can be discovered by `collect-skills` or supplied via `--skills-json` for debugging.

## Assignment Procedure

### 1. Validate TaskDraft Input

`assign-skills` validates the state file against `schema/task-input.schema.json`.
Any task containing `skills` is invalid at this stage.

### 2. Discover Candidate Skills

By default, `assign-skills` discovers all skills and filters candidates to these classes:

- `operation`
- `documentation`

The default class filter is canonical for production workflow runs.

### 3. Render Skill and Task Text

Each skill is rendered as structured text containing:

- `name`
- `class`
- `description`
- `tags`

Each task query is built from:

- `purpose`
- `context`
- `filesToRead`
- `filesToWrite`

### 4. Rank with FlashRank

`assign-skills` ranks every candidate skill against each task draft with `rerankers[flashrank]`.
FlashRank's sigmoid-normalized scores are converted back to raw logits.
Raw logit scores are unbounded upward; the default floor is `0.0`.

### 5. Select Skills

Selection rules:

1. Select every skill with raw logit score greater than or equal to the floor.
2. There is no maximum skill count.
3. If fewer than `--min-skills` pass the floor, fill from the highest-ranked remaining skills.
4. Every final task must have at least one skill.
5. Do not synthesize fallback skills; selected skills must come from discovered/indexed skills.

### 6. Write Final TaskPackets

`assign-skills` writes the state file back with `skills` arrays added to each task.
The resulting object must validate against `schema/task-packet.schema.json`.

## Output Format

The final output is a JSON object with:

- `summary` — request summary from decomposition.
- `tasks` — ordered TaskPacket array, each with a non-empty `skills` array.

The delegator receives the relative `.tasks/<epoch>-decomposition.json` path, not the raw JSON.
