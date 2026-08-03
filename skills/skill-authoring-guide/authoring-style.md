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

- Describe `selection` as the direct-selection profile, with grouped tags and request-facing conditions.
- Require authors to begin with the owned request and its nearest neighbors.
- Refer to `./tagging-guide.md` for grouped tags, aliases, and selection boundaries.
- Refer to `./frontmatter-rules.md` for profile shape and validation boundaries.

## Completion Checks

- Confirm headings, links, YAML, and code fences parse correctly.
- Confirm every rule uses the current direct-selection contract.
- Confirm examples distinguish neighboring owners across unrelated domains.
- Confirm no obsolete count, popularity, implementation, or metadata-shape rule remains.
