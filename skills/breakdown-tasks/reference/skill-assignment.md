# Direct Skill Selection

Both planning and task assignment use filtered collector output.

## Two Collector Calls

Run `collect-skills --class planning` before planning selection. Run `collect-skills --class operation --class documentation --output .tasks/skills.json` before task assignment. Each array is the sole authority for its phase.

## Planning Selection

Show the request and the planning array to the LLM. Load every materially relevant profile, with no numeric cap. Load only selected names through the skill tool. A planning load is passive context and does not grant execution or write authority. An empty selection is valid when no planning concern exists.

Block on a name absent from the planning array.

## Task Assignment

Show the complete draft and the operation/documentation array to the LLM. Select one to three semantically fitting skills per task. A no-match decision blocks. Inspect selected contracts and reconcile each name against the array.

Block on a name absent from the operation/documentation array.

## Prohibited Semantics

Do not score, rank, threshold, rerank, clip, use lexical or path fallback, or manually repair assignments. Do not recollect or rebuild metadata from names.
