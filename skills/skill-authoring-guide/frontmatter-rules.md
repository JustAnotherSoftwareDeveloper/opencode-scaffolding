# Required Frontmatter

Every `SKILL.md` must open with valid YAML frontmatter containing exactly three fields:

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
