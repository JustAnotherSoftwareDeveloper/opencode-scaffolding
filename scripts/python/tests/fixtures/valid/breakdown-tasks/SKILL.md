---
name: breakdown-tasks
description: Decompose a request into the smallest possible task-delegation work items.
schema_version: "1.0"
cues:
  - {facet: operation, value: decompose-request, primary: true}
  - {facet: outcome, value: task-packets}
relationships:
  - {role: owner}
class: operation
---
# breakdown-tasks

Break down complex requests into manageable task units.
