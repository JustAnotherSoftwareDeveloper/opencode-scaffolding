# Selecting Descriptive Tags

Create tags that let routing distinguish the skill from related skills.

## Selection Process

1. Read the trigger and expected output.
2. Select one primary capability tag that names the main work.
3. Add tags for the domain, artifact, tool, and workflow context that materially narrow selection.
4. Replace generic terms with terms that a task request would contain.
5. Remove duplicates and synonyms until 4–7 distinct tags remain.

## Tag Taxonomy Categories

Select tags from the following categories. The minimum and maximum tag counts
per category provide a starting framework; the 4–7 total tag limit remains the
binding constraint.

### 1. Primary capability (1 tag)

The main action the skill performs. Use a verb-noun or concrete noun form.

Examples: `task-decomposition`, `evidence-analysis`, `bash-code-generation`,
`clarify`, `python-testing`, `markdown-linting`.

### 2. Domain (1 tag)

The subject area the skill operates in. Can be shared across closely related
skills but must not appear in more than 5 skills total.

Examples: `skill-authoring`, `tasking`, `testing`, `documentation`.

### 3. Tool / platform (1–2 tags)

The specific tools, runtimes, or platforms the skill uses.

Examples: `pytest`, `bun`, `bats`, `cleye`, `todowrite-tool`, `typescript`,
`click`.

### 4. Deliverable / artifact (1–2 tags)

What the skill produces.

Examples: `task-json`, `workspace-generation`, `markdown-output`,
`decision-record`, `code-generation`, `cli-output`.

### 5. Workflow context (0–1 tag)

How the skill fits into the pipeline. Use only when it materially
discriminates between otherwise similar skills.

Examples: `delegation-pipeline`, `stage-selection`, `worker-dispatch`.

## Quality Rules

1. Include a primary capability tag such as `task-decomposition`,
   `markdown-linting`, or `python-testing`.
2. Include material discriminators such as `yaml-frontmatter`,
   `worker-dispatch`, `cli-integration`, `bun`, or `typescript`.
3. Do not use a tag that only repeats the skill name.
4. Do not use filler values (see Filler-Tag Blacklist below).
5. Do not use duplicate concepts such as `node` and `nodejs` unless they
   identify distinct supported targets.
6. Do not use a tag found in more than 5 other skills within the same class or
   across all classes. If a tag would appear in 6+ skills, replace it with a
   more specific alternative.
7. Verify tag uniqueness by comparing against `collect-skills` output for
   sibling skills before finalizing.
8. Ensure at least one tag directly names a tool, script, or deliverable the
   skill uses or produces.

## Filler-Tag Blacklist

The following tags are too generic to aid routing and must not be used:

`general`, `helper`, `tool`, `skill`, `misc`, `utility`, `common`, `default`,
`other`, `miscellaneous`

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
