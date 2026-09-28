---
name: <<skill-name>>
description: "Use when referencing <<domain-context>>."
selection:
  role: reference
  tags:
    actions: [reference, explain]
    inputs: [<<source material>>]
    outputs: [reference context]
    topics: [<<reference-subject>>]
    environments: [<<environment>>]
     constraints: [passive, no side effects]
  aliases: [<<alias>>] # optional recognition-only wording
  use_when: [the request needs <<domain-context>> reference material]
  not_for: [executing a workflow or changing the referenced artifact]
class: documentation
---

<!--
Template-instantiation declarations (remove this comment after filling the template).
Before using the completed skill, replace every retained slot at every occurrence with
the value described below, including occurrences in this comment. For an inapplicable
optional field, directory row, or file-list entry, remove that template entry and its
corresponding declaration bullet instead of substituting it.
- `<<skill-name>>`: the canonical identifier approved for the skill being authored,
  supplied by the skill author; use it consistently in the `name` field.
- `<<domain-context>>`: the reference domain this skill covers, derived from the
  actual shared materials and their intended use; use the same context in `description`
  and `use_when`.
- `<<source material>>`: the kinds of source material the reference library covers,
  based on its actual contents and intended reference use.
- `<<reference-subject>>`: the subjects actually addressed by the library's reference
  materials.
- `<<environment>>`: the environment or applicability scope established by the
  materials; use a general-scope value when the materials impose no narrower
  environment requirement.
- `<<alias>>`: an established alternate phrase for the canonical skill name, sourced
  from real alternate wording; when none applies, remove the optional `aliases` field
  instead of retaining this slot.
- `<<domain>>`: a concise description of the shared-reference domain evidenced by the
  library's actual contents, consistent with the frontmatter domain context.
- `<<path/to/file-1>>` and `<<purpose of file 1>>`: the path, relative to the
  completed skill's base directory, of an actual included documentation file and a
  concise description of its purpose, verified from its contents.
- `<<path/to/file-2>>` and `<<purpose of file 2>>`: the path, relative to the
  completed skill's base directory, of an actual included documentation file and a
  concise description of its purpose, verified from its contents.
- `<<path/to/file-3>>` and `<<purpose of file 3>>`: the path, relative to the
  completed skill's base directory, of an actual included documentation file and a
  concise description of its purpose, verified from its contents.
- `<<path/to/file-4>>` and `<<purpose of file 4>>`: the path, relative to the
  completed skill's base directory, of an actual included documentation file and a
  concise description of its purpose, verified from its contents.
- `<<description of shared documentation>>`: an accurate summary of the actual shared
  documentation in `docs/`; source it from those files and remove the row if that
  directory is absent.
- `<<description of shared schemas, if present>>`: an accurate summary of actual
  shared schemas in `schemas/`; source it from those files and remove the row if that
  directory is absent.
- `<<description of shared templates, if present>>`: an accurate summary of actual
  shared templates in `templates/`; source it from those files and remove the row if
  that directory is absent.
- `<<description of script interface documentation, if present>>`: an accurate
  summary of actual script interface documentation in `scripts/`; source it from
  those files and remove the row if that directory is absent.
- `<<path-to-skill-directory>>`: the completed skill's actual absolute filesystem
  location, sourced from where that skill is stored. Supply the path text after the
  existing `file:///` prefix (omit the leading slash) so the resulting base-directory
  URI retains its current form.
-->

`aliases` is optional recognition-only metadata. Use it only for alternate wording
that should resolve to this skill's canonical `name`; it must not create another
skill, change ownership or class, or authorize routing, delegation, or loading.

# Shared Reference Library

> **Editorial constraint:** Do not use Markdown tables in filled content. Use bullets
> for peer rules, paragraphs for connected reasoning, definition lists for
> term-and-definition material, and subsection headings for separately reviewable
> concerns. Put executable ordered procedures in an active-class skill instead.

This skill is a passive data store for `<<domain>>` shared reference content.
It does not auto-read any files when loaded.

## Documentation Files

Read the documentation files listed below as needed for your current task.
The bulleted list provides the mapping of files to their purpose.

- `<<path/to/file-1>>` — <<purpose of file 1>>
- `<<path/to/file-2>>` — <<purpose of file 2>>
- `<<path/to/file-3>>` — <<purpose of file 3>>
- `<<path/to/file-4>>` — <<purpose of file 4>>

Choose the relevant files based on what you need to learn or reference.
Read only those files.
Do not read every file — read as needed.

## Contents

- `docs/` — <<description of shared documentation>>
- `schemas/` — <<description of shared schemas, if present>>
- `templates/` — <<description of shared templates, if present>>
- `scripts/` — <<description of script interface documentation, if present>>

## Self-Validation

- [ ] Filled content uses semantic prose forms and contains no Markdown tables.

## Docs

See the [Documentation Files](#documentation-files) listing above for file descriptions.
Base directory for this skill: `file:///<<path-to-skill-directory>>`
