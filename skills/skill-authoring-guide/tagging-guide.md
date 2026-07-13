# Selecting Descriptive Tags

Create tags that let routing distinguish the skill from related skills.

## Selection Process

1. Read the trigger and expected output.
2. Select one primary capability tag that names the main work.
3. Add tags for the domain, artifact, tool, and workflow context that materially narrow selection.
4. Replace generic terms with terms that a task request would contain.
5. Remove duplicates and synonyms until 4–7 distinct tags remain.

## Quality Rules

- Include a primary capability tag such as `task-decomposition`, `markdown-linting`, or `python-testing`.
- Include material discriminators such as `yaml-frontmatter`, `worker-dispatch`, `cli-integration`, `bun`, or `typescript`.
- Do not use a tag that only repeats the skill name.
- Do not use filler values such as `general`, `helper`, `tool`, `skill`, `misc`, `utility`, `common`, or `default`.
- Do not use duplicate concepts such as `node` and `nodejs` unless they identify distinct supported targets.

## Examples

```yaml
tags:
  - node-script-generation
  - typescript
  - cli
  - cleye
  - bun
  - code-generation
```

```yaml
tags:
  - helper
  - tool
  - coding
  - node
  - nodejs
```

Reject the second list because it is generic and redundant.
