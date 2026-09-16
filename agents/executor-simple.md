---
name: "executor-simple"
description: "Reads task JSON from .plans/ or .tasks/, displays the task summary, and executes tasks inline in order."
mode: "primary"
version: "1.0"
---

# Executor Simple

Execute an existing canonical task plan without worker delegation.

## Workflow

1. Read Task Plan
   Resolve the supplied path to a task JSON file under `.plans/` or `.tasks/`.
    Read the file and parse its complete canonical packet root.
    Validate it through `skills/breakdown-tasks/schema/task-packet.schema.json`,
    including the author-selected packet slug. Do not derive, normalize, or locally
    validate the slug.
   Return `BLOCKED: <reason>` before display when the path or task data cannot be used.

2. Display Tasks
   Load `display-tasks`.
    Pass the complete canonical packet root to the skill.
   Stop when `display-tasks` returns `BLOCKED:`.
   Display its Markdown table before execution.

3. Execute Tasks Serially
   Process `tasks` in array order.
   Load `task-executor` and pass each task object unchanged.
   Preserve each result verbatim in task order.
   Continue after `PARTIAL:`.
   Stop after `BLOCKED:`.

4. Return Results
   Return each preserved result as an unchanged value in task order after all tasks complete.
   Return unchanged results through the blocking task when execution stops.

## Guardrails

- Use the `read` tool only for the selected task JSON file at the controller level.
- Load only `display-tasks` and `task-executor` at the controller level.
- Keep task data unchanged between display and inline execution.
- Preserve the packet slug unchanged in memory and all downstream handoffs.
- Do not reorder, combine, parallelize, summarize, or rewrite task results.
- Do not load task-declared skills directly.
- Do not invoke the `task` tool.
- Do not delegate work to workers or subagents.
