---
name: display-tasks
description: Render task delegation packets as a concise Markdown summary table.
schema_version: "1.0"
cues:
  - {facet: operation, value: render-tasks, primary: true}
  - {facet: outcome, value: markdown-table}
relationships:
  - {role: owner}
class: operation
version: 1.2.0
license: MIT
compatibility: ">=3.10"
metadata:
  author: opencode
  category: utility
permission: allow
location: /fake/path/should-be-overridden
---
# display-tasks

Display tasks in a clean markdown table format.
