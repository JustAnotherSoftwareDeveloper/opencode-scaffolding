---
name: lesson-writer
description: Capture reusable session lessons in `.lessons/` markdown files after meaningful orchestration work, failures, or recovery.
---

# Lesson Writer Skill

Use this skill after meaningful harness work, after failures, after recovery, or when a reusable orchestration insight emerges. Do not create lessons for routine trivial actions.

## Artifact Contract

Lesson files live at:

```text
.lessons/<unix-timestamp>-slug.md
```

## Lesson Frontmatter

```yaml
---
artifact_type: lesson
schema_version: 1
id: <unix-timestamp>-slug
session_id: <session id or null>
created_at: <iso timestamp>
source_plan: <path or null>
source_state: <path or null>
---
```

## Required Sections

```md
# Lesson: <title>

## Context
## What Happened
## Lesson
## Future Guidance
## Applies To
```

## Guidance

- Write at most one lesson per session unless the user requests otherwise.
- Capture durable guidance that should affect future orchestration behavior.
- Include source plan and state references when available.
- Keep the lesson concise and reusable.
- Avoid secrets, credentials, private tokens, excessive logs, and noisy routine observations.
- If no reusable lesson exists, report that no lesson is warranted.
