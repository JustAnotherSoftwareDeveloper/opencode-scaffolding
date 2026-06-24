# Gotchas

- **`description` is too generic** — Agent loads skill for wrong tasks.
  Fix: Be specific: action + domain + qualifier.
- **Frontmatter YAML is invalid** — Agent fails to parse skill entirely.
  Fix: Validate YAML before finalizing.
- **`name` doesn't match directory** — Skill is unreachable or misrouted.
  Fix: Match exactly: `skills/<<name>>/SKILL.md` → `name: <<name>>`.
- **Body reads like a tutorial** — Bloated context, agent wastes tokens.
  Fix: Strip all explanation; keep only imperative steps.
- **Examples inline** — Violates convention, adds noise.
  Fix: Remove.

- **Class selected by habit** — Mismatch between class contract and actual behavior.
  Fix: Consult the class list and the decision prompts.
- **Assumes templates exist** — A reference file references nonexistent files.
  Fix: Use forward-looking relative paths; assume the file does not exist yet.
- **Old template sections remain** — Verification Checklist exists but Phases, Failure Handling, or Quality Gates sections linger from the old template.
  Fix: Remove all old-template sections.
  The canonical 7-section layout replaces them.
- **Silently deleting content** — An update removes existing lines without acknowledging the removal.
  Fix: Every deletion must be intentional.
  If the request does not call for removal, preserve surrounding content.
- **Overwriting user customizations** — An update replaces internal reference files wholesale, wiping user additions.
  Fix: Use targeted edits.
  Only modify sections the request targets.
  Preserve frontmatter, structure, and prose outside the edit scope.
- **Incomplete partial updates** — A partial update (e.g., SKILL.md only) accidentally modifies reference files.
  Fix: Scope each edit to exactly the files listed in the request.
  Verify only targeted files changed.
- **Cross-skill file path references** — A skill file contains a literal path to a file in another skill's directory.
  Fix: Use skill loading (the skill tool) instead of literal file paths.
  Scripts are the sole exception to this rule.