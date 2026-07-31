# Skill Authoring Guide Style

Apply these conventions to documentation under `skills/skill-authoring-guide/`.

## Wording

- Use imperative, active voice for instructions.
- Use exact field names and relative links.
- Use one term per concept.
- Omit filler, hedging, tutorial preambles, and choice rationales.

## Formatting

- Use one H1 per file and Title Case headings.
- Use ordered lists for procedures and bullets for unordered rules.
- Avoid tables in supporting documentation.
- Use simple Markdown, limited nesting, and fenced code blocks for YAML or commands.
- Keep each sentence focused on one decision or action.

## Metadata Documentation

- Describe `cues` as structured routing evidence, not category slots or tags.
- Require authors to begin with owned tasks and nearest competitors.
- Refer to `./tagging-guide.md` as the authority for the routing rubric, registries, lifecycle, and evaluation.
- Refer to `./frontmatter-rules.md` as the authority for metadata shape and validation boundaries.

## Completion Checks

- Confirm headings, links, YAML, and code fences parse correctly.
- Confirm every rule uses the open routing contract.
- Confirm examples distinguish neighboring owners across unrelated domains.
- Confirm no obsolete count, popularity, implementation, or metadata-shape rule remains.
