# Skill Assignment Procedure

Automatic weighted-average procedure for assigning skills to task drafts.
Executed by the `assign-skills` Python script after the LLM writes `TaskDraft` objects.

## Design Rationale

The skill assignment system is designed as a deterministic, auditable, and controllable alternative to LLM-based skill selection. Key design decisions:

- **Weighted scoring** (vs. FlashRank or LLM-based): Provides deterministic, reproducible results without external model dependencies. Each run produces identical output given identical input.
- **Keyword overlap (0.50)** is weighted highest because task purpose and context text are the most reliable indicators of required skill. If a task says "add input validation", the keyword-triggered skill match is the strongest signal.
- **Class match (0.25)** and **tag similarity (0.25)** are supporting signals that refine the ranking. Class match ensures operation/documentation skills are preferred for executable tasks; tag similarity catches semantic matches the keyword overlap might miss.
- **Threshold gating** (vs. top-k) was chosen because it guarantees a minimum quality bar independent of the candidate pool size. With top-k, a large pool of low-quality matches would still produce assignments; threshold gating ensures only sufficiently relevant skills are assigned.
- The **class filter** restricts to `operation` and `documentation` because only these classes have executable worker workflows. Other classes (planning, inline, orchestrated, delegated) are handled at the delegator or orchestrator level and should not be assigned per-task.
- **No synthetic fallback**: If no skill reaches the threshold, the pipeline surfaces a discovery gap rather than silently assigning a misleading fallback. This makes skill inventory gaps visible and actionable.

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

### 3. Score Candidate Skills

By default, `assign-skills` uses the deterministic `weighted` backend. Each skill
is scored from three normalized criteria:

- keyword overlap between task text and skill `name`/`description`/`tags`
- class match bonus between inferred task class and skill `class`
- tag similarity between task tokens and skill `tags`

Default formula:

```text
final_score = 0.50 * keyword_overlap
            + 0.25 * class_match
            + 0.25 * tag_similarity
```

Task text is built from `purpose`, `context`, `filesToRead`, and `filesToWrite`.

### 4. Optional FlashRank Backend

The legacy FlashRank reranker is still selectable with `--backend flashrank`, but
it is not the default and requires installing the optional `rerankers[flashrank]`
dependency. FlashRank-only options such as `--floor` and `--model-name` do not
affect the weighted backend.

### 5. Select Skills

Selection rules:

1. For the weighted backend, select every skill with score greater than or equal to `--threshold`.
2. For the legacy FlashRank backend, select every skill with raw logit score greater than or equal to `--floor`.
3. There is no maximum skill count.
4. If fewer than `--min-skills` pass the threshold/floor, fill from the highest-ranked remaining skills.
5. Every final task must have at least one skill.
6. Do not synthesize fallback skills; selected skills must come from discovered/indexed skills.

### 6. Write Final TaskPackets

`assign-skills` writes the state file back with `skills` arrays added to each task.
The resulting object must validate against `schema/task-packet.schema.json`.

## Output Format

The final output is a JSON object with:

- `summary` — request summary from decomposition.
- `tasks` — ordered TaskPacket array, each with a non-empty `skills` array.

The delegator receives the relative `.tasks/<epoch>-decomposition.json` path, not the raw JSON.
