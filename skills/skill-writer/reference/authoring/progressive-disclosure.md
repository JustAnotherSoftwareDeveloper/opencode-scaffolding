# Progressive Disclosure

Keep `SKILL.md` procedural and compact (under ~100 lines).
Push reference material into `reference/*.md` files.
The agent acts on `SKILL.md` alone.
Support files are consulted on demand for depth.

**Pattern**: In `SKILL.md`, write something like:

> See `./frontmatter-rules.md` for class selection guide and `../platform/platform-context.md` for platform rules.

Do **not** inline reference prose into `SKILL.md`.
