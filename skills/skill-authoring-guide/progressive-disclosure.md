# Progressive Disclosure

Keep `SKILL.md` compact (under ~100 lines) and serve as a file index.
Push reference material into separate `.md` files.
The agent reads `SKILL.md` to discover available files.
Support files are consulted on demand for depth.

**Pattern**: In `SKILL.md`, write something like:

> See `./frontmatter-rules.md` for frontmatter field definitions and `./trigger-evaluation.md` for trigger evaluation rules.

Do **not** inline reference prose into `SKILL.md`.
