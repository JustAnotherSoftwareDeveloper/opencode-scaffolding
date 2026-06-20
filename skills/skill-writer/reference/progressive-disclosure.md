# Progressive Disclosure

Keep `SKILL.md` procedural and compact (under ~100 lines). Push reference material into `reference/*.md` files. The agent should be able to act on `SKILL.md` alone; support files are consulted on demand for depth.

**Pattern**: In `SKILL.md`, write something like:

> See `./reference/frontmatter-rules.md` for class selection guide and `./reference/platform-context.md` for platform rules.

Do **not** inline reference prose into `SKILL.md`.
