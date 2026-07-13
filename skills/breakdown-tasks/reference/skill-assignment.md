# Skill Assignment Procedure

Automatic weighted-average procedure for assigning skills to task drafts.
Executed by the `generate-task-json` Python script after the LLM writes `TaskDraft` objects.

## Design Rationale

The skill assignment system is designed as a deterministic, auditable, and controllable alternative to LLM-based skill selection. Key design decisions:

- **Weighted scoring** (vs. FlashRank or LLM-based): Provides deterministic, reproducible results without external model dependencies. Each run produces identical output given identical input.
- **Keyword overlap (0.50)** is weighted highest because task purpose and context text are the most reliable indicators of required skill. If a task says "add input validation", the keyword-triggered skill match is the strongest signal.
- **Class match (0.25)** and **tag similarity (0.25)** are supporting signals that refine the ranking. Class match ensures operation/documentation skills are preferred for executable tasks; tag similarity catches semantic matches the keyword overlap might miss.
- **Threshold gating** (vs. top-k) was chosen because it guarantees a minimum quality bar independent of the candidate pool size. With top-k, a large pool of low-quality matches would still produce assignments; threshold gating ensures only sufficiently relevant skills are assigned.
- The **class filter** restricts to `operation` and `documentation` because only these classes have executable worker workflows. Other classes (planning, inline, orchestrated, delegated) are handled at the delegator or orchestrator level and should not be assigned per-task.
- **No synthetic fallback**: If no skill reaches the threshold, the pipeline surfaces a discovery gap rather than silently assigning a misleading fallback. This makes skill inventory gaps visible and actionable.

## Prerequisites

1. Standard input contains a root `{summary, tasks}` object that matches `schema/task-input.schema.json`.
2. Each task is a `TaskDraft` and does **not** include a `skills` field.
3. Available skills can be discovered by `collect-skills`.

## Assignment Procedure

### 1. Validate TaskDraft Input

`generate-task-json` validates standard input against `schema/task-input.schema.json`.
Any task containing `skills` is invalid at this stage.

### 2. Discover Candidate Skills

By default, `generate-task-json` discovers all skills and filters candidates to these classes:

- `operation`
- `documentation`

The default class filter is canonical for production workflow runs.

### 3. Score Candidate Skills

By default, `generate-task-json` uses deterministic weighted scoring. Each skill
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

### 4. Select Skills

Selection rules:

1. Select every skill with score greater than or equal to the canonical threshold.
2. Select the highest-ranked skill when no candidate reaches the threshold.
3. Keep at most the three highest-ranked selected skills.
4. Every final task must have at least one skill.
5. Do not synthesize fallback skills; selected skills must come from discovered skills.

### 5. Write Final TaskPackets

`generate-task-json` writes the output path with `skills` arrays added to each task.
The resulting object validates against `schema/task-packet.schema.json`.

## Output Format

The final output is a JSON object with:

- `summary` — request summary from decomposition.
- `tasks` — ordered TaskPacket array, each with a non-empty `skills` array.

The delegator receives the relative `.tasks/<summary-slug>.json` path, not the raw JSON.
