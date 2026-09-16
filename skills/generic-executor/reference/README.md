# Generic Executor Reference

Use this operation for one ordinary repository file-maintenance result with explicit
read paths, write paths, instructions, expected output, and verification. It may also
maintain one existing `skills/<name>/` workspace when the task limits writes to that
workspace's `SKILL.md`, `reference/**`, and `tests/**` files.

For skill maintenance, read the relevant `skill-maintenance-reference` documentation
as passive context, every existing target file before changing it, and run applicable
workspace tests, both shared skill validators for a changed `SKILL.md`, and Markdown
lint for changed Markdown files. Do not create skills, change taxonomy, perform
family-wide migrations, review skills, or change another workspace.
