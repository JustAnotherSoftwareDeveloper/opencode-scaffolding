# Required Frontmatter

Every `SKILL.md` must open with valid YAML frontmatter containing exactly three required fields (plus one optional field, `tags`):

```yaml
---
name: <<skill-name>>
description: "Use when <<trigger description>>."
class: <<one-of-six-classes>>
---
```

## `Name`

- **Regex**: `^[a-z][a-z0-9-]*$` — lowercase alphanumeric with hyphens, must start with a letter.
- **Must match** the directory name under `skills/`.
  If the directory is `skills/foo-bar/`, the name is `foo-bar`.
- **Stability**: Once published, renaming breaks skill references.
  Choose deliberately.

## `Description`

- **Must start** with `"Use when"` — this is the agent's primary selection signal.
- **Exception**: For the `planning` class, the description must start with `"Use as planning reference"` instead.
- **Must capture** the *trigger intent*, not a feature list.
  Bad: *"Use when needing to write files."*
  Good: *"Use when creating or rewriting all OpenCode skill files under skills/<name>/ (SKILL.md, reference/*.md, and templates/) from requirements and source material."*
- **Length**: Under 1024 characters.
  Prefer 60–200 characters; shorter is sharper.
- **Avoid** referencing specific filenames, paths, or future infrastructure.
- For trigger evaluation guidance, see `./trigger-evaluation.md`.

## `Class`

One of exactly six values:

- **`operation`**
- **`delegated`**
- **`inline`**
- **`orchestrated`**
- **`planning`**
- **`documentation`**

No other classes are valid.
If uncertain, lean toward `operation`.
If the skill is a passive data store consumed by other skills, choose `documentation`.

## `Tags` (optional)

- **Type**: `list[str]`
- **Status**: Optional. May be omitted entirely.
- **Format**: Flat string arrays `['str1', 'str2']`.
- **Count**: Use 4–7 tags per skill when tags are present.
- **Convention**: Tags are lowercase kebab-case strings with no spaces.
- **Vocabulary**: Tags are descriptive freeform labels; there is no fixed registry.
- **Scope**: Prefer concrete domain, action, tool, artifact, and workflow-context terms that help match the skill to user intent.
- **Avoid**: Overly broad filler tags, duplicated meaning, and tags that only restate the skill name.
- **Example**:
  ```yaml
  tags:
    - "code-generation"
    - "test-writing"
    - "node"
    - "bun"
    - "cli"
  ```
